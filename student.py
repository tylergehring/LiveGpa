#Tyler Gehring 2025
#Class to get and store student data

import requests
import datetime

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class Student():
    """Grabs data about a student from Canvas Rest Api"""
    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.url = "https://canvas.uidaho.edu/api/v1"
        self.headers = {'Authorization' : 'Bearer ' + self.apiKey}
        self.errors = list()

        self.data = DotDict({
            'first_name' : "None",
            'last_name' : "None",
            'id' : 0,
            'courses' : [], #list of dicts {'class_name': class, 'class_id': id, 'grade' : grade}
            'grades' : []
        })
        self.year = None
        self.month = None

        self.get_date()
        self.get_name_and_id()
        self.get_courses()
        self.get_grades()

    def get_date(self):
        current_date = datetime.datetime.now()
        self.year = int(current_date.year)
        self.month = int(current_date.month)
        
    def get_name_and_id(self):
        try:
            headers = {'Authorization' : 'Bearer ' + self.apiKey}
            rec = requests.get((f"{self.url}/users/self"), headers = headers) 
            rec = rec.json()
            rec = DotDict(rec)
            self.data.first_name = rec.first_name
            self.data.last_name = rec.last_name
            self.data.id = rec.id
        except Exception as e:
            self.errors.append(e)
            print("ERROR::Student:get_name_and_id")
            raise(e)
            
    
    def get_courses(self):
        rec = requests.get((f"{self.url}/courses/?per_page=30"), headers = self.headers) #request to student courses "?per_page=30" takes 30 results. the default is 10 due to the http pagination
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

        
    def get_grades(self):
        """grabs grades for every class and adds it to self.data"""
        for course in self.data.courses:
            rec = requests.get((f"{self.url}/courses/{course['id']}/enrollments/?user_id={self.data.id}"), headers = self.headers) 
            rec = rec.json()
            course['grade'] = {'current_score': rec[0]['grades']['current_score'], 'current_grade': rec[0]['grades']['current_grade']}
            

        
