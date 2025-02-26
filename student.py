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
        self.errors = list()

        self.data = DotDict({
            'first_name' : "None",
            'last_name' : "None",
            'id' : 0,
            'courses' : [], #list of dicts {'class_name': class, 'class_id': id, 'grade' : grade}
            'gpa' : 0
        })
        self.year = None
        self.month = None
        
        ### ---- Filling Data ----
        if(grab_all):
            func_err = {'get_date': 0, 'get_name_and_id':0, 'get_course':0, 'get_grades': 0, 'calc_gpa': 0}
            try:
                func_err['get_date'] =self.get_date()
                func_err['get_name_and_id'] =self.get_name_and_id()
                func_err['get_course'] =self.get_courses()
                func_err['get_grades'] =self.get_grades()
                func_err['calc_gpa'] =self.calc_gpa()
            except Exception as e:
                self.errors.append({'key' : self.apiKey, 'func_err' : func_err})
                print("Cannot create student obj...")
    

    def get_date(self):
        """gets the current year and month and saves it to self.year and self.month. returns 1 if successful"""
        current_date = datetime.datetime.now()
        self.year = int(current_date.year)
        self.month = int(current_date.month)
        return 1
        
    def get_name_and_id(self):
        """saves first_name, last_name, and id to self.data. returns 1 if successful"""
        rec = requests.get((f"{self.url}/users/self"), headers = self.headers) 
        rec = rec.json()
        rec = DotDict(rec)
        self.data.first_name = rec.first_name
        self.data.last_name = rec.last_name
        self.data.id = rec.id
        return 1
            
    
    def get_courses(self):
        """gets a list of current courses and adds them to self.data.courses. format is a dict of name, id, and grade. grade is not added here. returns 1 if successful"""
        rec = requests.get((f"{self.url}/courses/?per_page=50"), headers = self.headers) #request to student courses "?per_page=50" takes 50 results. the default is 10 due to the http pagination
        rec = rec.json()
        for course in rec:
            try:
                #if the end date of the course is in the future, you are currently taking the class
                year = int(course['end_at'][:4]) 
                month = int(course['end_at'][5:7])
                if ((year >= self.year) and (month >= self.month)):
                    self.data.courses.append({'name': course['name'], 'id': course['id'], 'grade' : None})
            except: # some entries wont be actual classes so we skip over them using a try/except block
                pass
        return 1

        
    def get_grades(self):
        """grabs grades for every class and adds it to self.data. returns 1 if successful"""
        for course in self.data.courses:
            rec = requests.get((f"{self.url}/courses/{course['id']}/enrollments/?user_id={self.data.id}"), headers = self.headers) 
            rec = rec.json()
            course['grade'] = {'current_score': rec[0]['grades']['current_score'], 'current_grade': rec[0]['grades']['current_grade']}
        return 1


    def calc_gpa(self):
        """Calculates overall gpa, assumes all classes are three credits. returns 1 if successful"""
        assumed_credits = 3
        total_credits = 0
        total_score = 0
        for course in self.data.courses:
            if course['grade']['current_grade'] == 'A':
                total_score += (4 * assumed_credits)
            elif course['grade']['current_grade'] == 'B':
                total_score += (3 * assumed_credits)
            elif course['grade']['current_grade'] == 'C':
                total_score += (2 * assumed_credits)
            elif course['grade']['current_grade'] == 'D':
                total_score += (1 * assumed_credits)
            elif course['grade']['current_grade'] == 'F':
                pass
            elif course['grade']['current_grade'] == None:
                pass
            else:
                self.errors.append(f"Unknown Grade for {self.data.first_name} {self.data.last_name}, course {course['name']}")
            total_credits += 3

        self.data.gpa = (total_score/total_credits)
        return 1


        
