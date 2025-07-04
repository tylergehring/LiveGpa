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
    
    def add_key(self, apiKey, pc_year):
        """saves student pc_year, first_name, last_name, key, and ID to self.file"""

        self.pc_year = pc_year
        self.apiKey = apiKey

        if (self.get_student_data(self.apiKey)): #returns 1 if successful
            token = {"first_name": self.first_name, "last_name": self.last_name, "pc_year": self.pc_year, "apiKey" : self.apiKey, "id" : self.student_ID}
            self.json_data.append(token)
            
            #save updated json to the file
            with open(self.filename, "w") as outfile:
                json.dump(self.json_data, outfile)

            print("---ADDED KEY SUCCESSFULLY---")
        else:
            print("--- ERROR::KEY WAS NOT ADDED::KEY NOT VALID->KeySystem.py")

    def remove_key(self, apiKey):
        """search key by id and remove the dict entry"""
        try:
            for entry in self.json_data:
                if entry['apiKey'] == apiKey:
                    self.json_data.remove(entry)
            print("Removed Key Successfuly...")
        except Exception as e:
            print("Did not remove Key successfuly..")

      
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
        

    def get_key(self, first_name, last_name):
        """returns studnet key based on given student name"""
        for i in range(len(self.json_data)):
            if (self.json_data[i]['first_name'] == first_name) and (self.json_data[i]['last_name'] == last_name):
                return self.json_data[i]['key'] 
        return "0"   
    
    def get_all_keys(self):
        """returns a list of all keys"""
        keys = list()
        for entry in self.json_data:
            keys.append(entry['key'])
        return keys
    
    def get_dict(self):
        """returns the dict we read from file"""
        return self.json_data
    

if __name__=="__main__":
    temp = KeyManagement("apiKeys.json")
    #key = obj.get_key("Zachary", "Stefanich")
    #obj.remove_key()
