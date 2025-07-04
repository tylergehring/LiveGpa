#Tyler Gehring 2025
#Purpose get and store student data

import requests
import datetime


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class Student():
    """Grabs data about a student from Canvas Rest Api"""
    def __init__(self, apiKey, grab_all=True):
        self.apiKey = apiKey
        self.url = "https://canvas.uidaho.edu/api/v1"
        self.headers = {'Authorization' : 'Bearer ' + self.apiKey}
        self.key_errors = list()

        self.data = DotDict({
            'first_name': "None",
            'last_name': "None",
            'id': 0,
            'email': None,
            'avatar_url': None,
            'bio': None,
            'pronouns': None,
            'locale': None,
            'last_login': None,
            'courses': [], # Enhanced course data structure
            'gpa': 0,
            'total_credits': 0,
            'term_data': {},  # Store data by term
            'updated_at': None
        })
        self.year = None
        self.month = None
        
        ### ---- Filling Data ----
        if(grab_all):
            func_err = {
                'get_date': 0, 
                'get_user_profile': 0,
                'get_courses': 0, 
                'get_detailed_enrollments': 0, 
                'calc_gpa': 0
            }
            try:
                func_err['get_date'] = self.get_date()
                func_err['get_user_profile'] = self.get_user_profile()
                func_err['get_courses'] = self.get_courses()
                func_err['get_detailed_enrollments'] = self.get_detailed_enrollments()
                func_err['calc_gpa'] = self.calc_gpa()
                self.data.updated_at = datetime.datetime.now().isoformat()
            except Exception as e:
                print(f"Cannot create student obj: {str(e)}")
                raise
    

    def get_date(self):
        """gets the current year and month and saves it to self.year and self.month. returns 1 if successful"""
        current_date = datetime.datetime.now()
        self.year = int(current_date.year)
        self.month = int(current_date.month)
        return 1
        
    def get_user_profile(self):
        """Fetches and saves comprehensive user profile data. Returns 1 if successful."""
        response = requests.get(f"{self.url}/users/self/profile", headers=self.headers)
        if not response.ok:
            self.key_errors.append({'apiKey': self.apiKey, 'error': response.text})
            return 0
            
        profile = DotDict(response.json())
        
        # Update user profile data
        self.data.first_name = profile.get('first_name')
        self.data.last_name = profile.get('last_name')
        self.data.id = profile.get('id')
        self.data.email = profile.get('email')
        self.data.avatar_url = profile.get('avatar_url')
        self.data.bio = profile.get('bio')
        self.data.pronouns = profile.get('pronouns')
        self.data.locale = profile.get('locale')
        
        # Get last login time
        response = requests.get(f"{self.url}/users/self/page_views?per_page=1", headers=self.headers)
        if response.ok:
            page_views = response.json()
            if page_views:
                self.data.last_login = page_views[0].get('created_at')
                
        return 1
            
    
    def get_courses(self):
        """Gets detailed information about current courses. Returns 1 if successful."""
        response = requests.get(f"{self.url}/courses/?include[]=term&include[]=total_scores&per_page=50", 
                              headers=self.headers)
        if not response.ok:
            self.key_errors.append({'apiKey': self.apiKey, 'error': response.text})
            return 0

        courses = response.json()
        self.data.courses = []
        
        for course in courses:
            try:
                # Check if the course is active
                if not course.get('end_at'):
                    continue
                    
                year = int(course['end_at'][:4])
                month = int(course['end_at'][5:7])
                
                if year >= self.year and month >= self.month:
                    course_data = {
                        'name': course.get('name'),
                        'id': course.get('id'),
                        'course_code': course.get('course_code'),
                        'term': course.get('term', {}).get('name'),
                        'start_at': course.get('start_at'),
                        'end_at': course.get('end_at'),
                        'grade': None,
                        'credits': None,  # Will be updated in get_detailed_enrollments
                        'assignments': [],
                        'weighted_total': course.get('weighted_total', False)
                    }
                    
                    # Initialize term data if not exists
                    term_name = course_data['term']
                    if term_name and term_name not in self.data.term_data:
                        self.data.term_data[term_name] = {
                            'courses': [],
                            'term_gpa': 0,
                            'term_credits': 0
                        }
                    
                    self.data.courses.append(course_data)
                    if term_name:
                        self.data.term_data[term_name]['courses'].append(course_data)
                        
            except Exception as e:
                print(f"Error processing course: {str(e)}")
                continue
                
        return 1

        
    def get_detailed_enrollments(self):
        """Fetches detailed enrollment information including grades and credit hours. Returns 1 if successful."""
        for course in self.data.courses:
            try:
                # Get enrollment details
                response = requests.get(
                    f"{self.url}/courses/{course['id']}/enrollments",
                    params={'user_id': self.data.id, 'include[]': ['current_grading_period_scores']},
                    headers=self.headers
                )
                
                if not response.ok:
                    print(f"Error fetching enrollment for course {course['id']}")
                    continue
                    
                enrollments = response.json()
                if not enrollments:
                    continue
                    
                enrollment = enrollments[0]
                grades = enrollment.get('grades', {})
                
                # Update course grade information
                course['grade'] = {
                    'current_score': grades.get('current_score'),
                    'current_grade': grades.get('current_grade'),
                    'final_score': grades.get('final_score'),
                    'final_grade': grades.get('final_grade'),
                    'unposted_current_score': grades.get('unposted_current_score'),
                    'unposted_final_score': grades.get('unposted_final_score')
                }
                
                # Try to get course credit hours
                response = requests.get(
                    f"{self.url}/courses/{course['id']}",
                    params={'include[]': ['total_students']},
                    headers=self.headers
                )
                
                if response.ok:
                    course_details = response.json()
                    course['credits'] = float(course_details.get('course_credit_hours', 3))  # Default to 3 if not specified
                else:
                    course['credits'] = 3.0  # Default credits
                    
                # Update term data
                if course.get('term') and course['term'] in self.data.term_data:
                    self.data.term_data[course['term']]['term_credits'] += course['credits']
                    
            except Exception as e:
                print(f"Error processing enrollment: {str(e)}")
                continue
                
        return 1


    def calc_gpa(self):
        """
        Calculates overall GPA and term GPAs using actual credit hours when available.
        Returns 1 if successful.
        """
        def calculate_grade_points(score):
            if score is None:
                return None
            if score >= 93: return 4.0
            elif score >= 90: return 3.7
            elif score >= 87: return 3.3
            elif score >= 83: return 3.0
            elif score >= 80: return 2.7
            elif score >= 77: return 2.3
            elif score >= 73: return 2.0
            elif score >= 70: return 1.7
            elif score >= 67: return 1.3
            elif score >= 63: return 1.0
            elif score >= 60: return 0.7
            else: return 0.0

        total_credits = 0
        total_grade_points = 0

        # Calculate term GPAs and overall GPA
        for term_name, term_data in self.data.term_data.items():
            term_credits = 0
            term_grade_points = 0
            
            for course in term_data['courses']:
                if course['grade'] and course['grade']['current_score'] is not None:
                    credits = course['credits']
                    grade_points = calculate_grade_points(course['grade']['current_score'])
                    
                    if credits and grade_points is not None:
                        term_credits += credits
                        term_grade_points += credits * grade_points
                        
                        # Add to overall totals
                        total_credits += credits
                        total_grade_points += credits * grade_points
            
            # Calculate term GPA
            if term_credits > 0:
                term_data['term_gpa'] = round(term_grade_points / term_credits, 3)
                term_data['term_credits'] = term_credits
            
        # Calculate overall GPA
        self.data.gpa = round(total_grade_points / total_credits, 3) if total_credits > 0 else 0
        self.data.total_credits = total_credits
        
        return 1

    def get_assignments(self, course_id=None):
        """
        Fetches assignment data for specified course or all courses.
        Returns 1 if successful.
        """
        courses_to_check = [c for c in self.data.courses if c['id'] == course_id] if course_id else self.data.courses
        
        for course in courses_to_check:
            try:
                # Get assignments
                response = requests.get(
                    f"{self.url}/courses/{course['id']}/assignments",
                    params={
                        'include[]': ['submission', 'score_statistics'],
                        'order_by': 'due_at',
                        'per_page': 100
                    },
                    headers=self.headers
                )
                
                if not response.ok:
                    print(f"Error fetching assignments for course {course['id']}")
                    continue
                    
                assignments = response.json()
                course['assignments'] = []
                
                for assignment in assignments:
                    # Only include assignments that affect the grade
                    if not assignment.get('omit_from_final_grade'):
                        assignment_data = {
                            'id': assignment.get('id'),
                            'name': assignment.get('name'),
                            'due_at': assignment.get('due_at'),
                            'points_possible': assignment.get('points_possible'),
                            'submission': None,
                            'score_statistics': assignment.get('score_statistics')
                        }
                        
                        # Get submission data if available
                        submission = assignment.get('submission', {})
                        if submission:
                            assignment_data['submission'] = {
                                'score': submission.get('score'),
                                'grade': submission.get('grade'),
                                'submitted_at': submission.get('submitted_at'),
                                'late': submission.get('late'),
                                'missing': submission.get('missing')
                            }
                            
                        course['assignments'].append(assignment_data)
                
            except Exception as e:
                print(f"Error processing assignments: {str(e)}")
                continue
                
        return 1



