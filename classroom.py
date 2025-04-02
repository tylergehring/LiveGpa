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
        
            

    def get_pc_average(pc_year):
        pass
    def get_student_grade(first_name, last_name):
        pass
    def get_class_average():
        pass
    
    def cache_errors(self):
        with open(self.error_cache_file, 'w') as outfile:
            json.dump(self.errors, outfile)
    
            