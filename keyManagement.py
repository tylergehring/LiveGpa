#Tyler Gehring 2025
#Operations related to key management

import json
import student


class KeyManagement():
    """operations related to key maintenance and management"""
    def __init__(self, filename):
        self.student_year = 0
        self.first_name = ""
        self.last_name = ""
        self.apiKey = ""
        self.student_ID = ""
        self.filename = filename
        with open(filename, 'r') as openfile:
            self.json_data = json.load(openfile)
    
    def addKey(self):
        """saves student pc_year, first_name, last_name, key, and ID to self.file"""

        self.pc_year = int(input("What is the students pc year?(int): "))
        self.apiKey = (input("What is their Canvas API Key?: ")).strip()

        if (self.get_student_data(self.apiKey)): #returns 1 if successful
            token = {"first_name": self.first_name, "last_name": self.last_name, "pc_year": self.pc_year, "apiKey" : self.apiKey, "id" : self.student_ID}
            self.json_data.append(token)
            
            #save updated json to the file
            with open(self.filename, "w") as outfile:
                json.dump(self.json_data, outfile)

            print("---ADDED KEY SUCCESSFULLY---")
        else:
            print("--- ERROR::KEY WAS NOT ADDED::KEY NOT VALID->KeySystem.py")
      
    # Saves name and ID to class variables. 1 if successful. 0 if not
    def get_student_data(self, apiKey):
        """creates a student obj and grabs first_name, last_name, and id"""
        try:
            std = student.Student(self.apiKey, grab_all=False)
            std.get_name_and_id()
            self.first_name = std.data['first_name']
            self.last_name = std.data['last_name']
            self.id = std.data['id']
            return 1
        except:
            return 0 
        

    
    def getKey(self, first_name, last_name):
        """returns studnet key based on given student name"""
        for i in range(len(self.json_data)):
            if (self.json_data[i]['first_name'] == first_name) and (self.json_data[i]['last_name'] == last_name):
                return self.json_data[i]['key'] 
        return "0"    
    

