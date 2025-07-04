#Tyler Gehring 2025
#Purpose: Handle several student objects
import json

import student

class Classroom:
    def __init__(self, name_key_dict):
        """creates student objects for every apiKey in list"""
        self.name_key_dict = name_key_dict
        self.errors = list()
        self.error_cache_file = "error_cache.json"
        self.students = list()
        self.add_students()
        self.cache_errors()
    
    def add_students(self):
        """creates student obj and saves to self.students list"""
        for i in range(len(self.name_key_dict)):
            try:
                obj = student.Student(self.name_key_dict[i]['key'])
                self.errors.append(obj.key_errors) 

                self.students.append({'name': self.name_key_dict[i]['name'], 
                                      'pc_year': self.name_key_dict[i]['pc_year'],
                                      'id' : self.name_key_dict[i]['ID'],  
                                      'obj': obj})
            except Exception as e:
                print(f"Unknown Error::Classroom: key: {self.name_key_dict[i]['key']} Name: {self.name_key_dict[i]['name']}")
                raise(e)
        print(f"ERRORS: {len(self.errors)}")
        
            

    def get_pc_average(self, pc_year):
        """Returns the average GPA for students in the given pc_year."""
        gpas = [s['obj'].data.gpa for s in self.students if s['pc_year'] == pc_year and s['obj'].data.gpa > 0]
        if not gpas:
            return 0
        return round(sum(gpas) / len(gpas), 3)

    def get_student_grade(self, first_name, last_name):
        """Returns the GPA and course grades for a student by name."""
        for s in self.students:
            obj = s['obj']
            if obj.data.first_name == first_name and obj.data.last_name == last_name:
                return {
                    'gpa': obj.data.gpa,
                    'courses': [
                        {
                            'name': c['name'],
                            'grade': c['grade'],
                            'credits': c['credits']
                        } for c in obj.data.courses
                    ]
                }
        return None

    def get_class_average(self):
        """Returns the average GPA for the entire class."""
        gpas = [s['obj'].data.gpa for s in self.students if s['obj'].data.gpa > 0]
        if not gpas:
            return 0
        return round(sum(gpas) / len(gpas), 3)

    def get_term_averages(self):
        """Returns a dict of average GPA per term for the class."""
        term_totals = {}
        term_counts = {}
        for s in self.students:
            for term, tdata in s['obj'].data.term_data.items():
                if tdata['term_gpa'] > 0:
                    term_totals[term] = term_totals.get(term, 0) + tdata['term_gpa']
                    term_counts[term] = term_counts.get(term, 0) + 1
        return {term: round(term_totals[term]/term_counts[term], 3) for term in term_totals if term_counts[term] > 0}

    def get_assignment_stats(self):
        """Returns stats on assignments (e.g., missing, late) for the class."""
        stats = {'total': 0, 'missing': 0, 'late': 0, 'completed': 0}
        for s in self.students:
            for course in s['obj'].data.courses:
                for a in course.get('assignments', []):
                    stats['total'] += 1
                    sub = a.get('submission')
                    if sub:
                        if sub.get('missing'):
                            stats['missing'] += 1
                        elif sub.get('late'):
                            stats['late'] += 1
                        elif sub.get('score') is not None:
                            stats['completed'] += 1
        return stats

    def list_students(self):
        """Returns a list of all students with summary info."""
        return [
            {
                'name': s['name'],
                'pc_year': s['pc_year'],
                'id': s['id'],
                'gpa': s['obj'].data.gpa,
                'total_credits': s['obj'].data.total_credits
            }
            for s in self.students
        ]
    
    def cache_errors(self):
        with open(self.error_cache_file, 'w') as outfile:
            json.dump(self.errors, outfile)

