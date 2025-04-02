import json
import requests
import datetime

import student
from student import DotDict

def get_error_cache(filename):
    """reads error_cache and returns dict"""
    with open(filename, 'r') as openfile:
        errors = json.load(openfile)
        return errors

def get_apiKeys(filename):
    with open(filename, 'r') as openfile:
        name_key_dict = json.load(openfile)
        return name_key_dict

class Tests():
    """given a key, creates a student object data fromat and attempts to fill it with data using its test methods."""
    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.url = "https://canvas.uidaho.edu/api/v1"
        self.headers = {'Authorization' : 'Bearer ' + self.apiKey}
        self.student = student.Student(apiKey, grab_all=False) #we will fill this data manualy... we just want the data format
        self.year = None
        self.month = None
        self.get_date()

    def get_date(self):
        """gets the current year and month and saves it to self.year and self.month. returns 1 if successful"""
        current_date = datetime.datetime.now()
        self.year = int(current_date.year)
        self.month = int(current_date.month)
        return 1
    
    def key_test(self, print_data=False):
        """trys to grab id. returns string of error or "success"""
        
        rec = requests.get((f"{self.url}/users/self"), headers = self.headers) 
        rec = rec.json()
        rec = DotDict(rec)
    
        if(print_data):
            print(rec.errors)
        
        if 'Expired access token.' in str(rec.errors):
            return "expired_token"
        elif 'Revoked access' in str(rec.errors):
            return "revoked_access"
        
        try:
            self.student.id = rec.id
            self.student.data.first_name = rec.first_name
            self.student.data.last_name = rec.last_name
            return "success"
        except:
            return "failed"
        

    def course_test(self, print_data=False):
        """test to see if we can caputre what classes the student is taking"""
        rec = requests.get((f"{self.url}/courses/?per_page=50"), headers = self.headers) #request to student courses "?per_page=50" takes 50 results. the default is 10 due to the http pagination
        rec = rec.json()
        if(print_data):
            print(rec)
        for course in rec:
            try:
                #if the end date of the course is in the future, you are currently taking the class
                year = int(course['end_at'][:4]) 
                month = int(course['end_at'][5:7])
                if ((year >= self.year) and (month >= self.month)):
                    self.student.data.courses.append({'name': course['name'], 'id': course['id'], 'grade' : None})
            except: # some entries wont be actual classes so we skip over them using a try/except block
                pass
        if (len(self.student.data.courses) == 0):
            print("no classes were collected")
            return 0
        return 1

    def gpa_test(self):
        """test if we can calculate the students gpa"""
        pass



if __name__=="__main__":
    #errors = get_error_cache("error_cache.json")
    keys_dict = get_apiKeys("apiKeys.json")
    for i in range(len(keys_dict)):
        test = Tests(keys_dict[i]['apiKey'])
        test.key_test(print_data=True)
   
    
    #for student_err in errors:
    #    for error in student_err:
    #        test = Tests(error['key'])
    #        print(f"key_test: {test.key_test(print_data=True)}")
            #print(f"STUDENT NAME: {test.student.data.first_name} {test.student.data.last_name}")
            #print(f"course_test: {test.course_test(print_data=False)}")

