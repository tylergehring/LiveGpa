import requests

class DotDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

class Student():
    """Student object contains data about the student"""
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
            'gpa' : 0
        })

        operation_list = [self.get_name_and_id, self.get_courses]
        for op in operation_list:
            success = op()
            if success == False:
                break

        
    def get_name_and_id(self):
        try:
            headers = {'Authorization' : 'Bearer ' + self.apiKey}
            rec = requests.get((f"{self.url}/users/self"), headers = headers) 
            rec = rec.json()
            rec = DotDict(rec)
            self.data.first_name = rec.first_name
            self.data.last_name = rec.last_name
            self.data.id = rec.id
            return True
        except Exception as e:
            self.errors.append(e)
            print("ERROR::Student:get_name_and_id")
            print(e)
            return False
    
    def get_courses(self):
        pass
