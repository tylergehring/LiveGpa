#Tyler Gehring, 2025.
#Uses the canvas rest api to pull student grades

import json

import classroom

if __name__=="__main__":
    filename = "student_keys.json"
    with open(filename, 'r') as openfile:
        name_key_dict = json.load(openfile)

    class_rm = classroom.Classroom(name_key_dict) 
    for student in class_rm.students:
        try:
            print(student.data)
        except:
            pass
    

#TODO:
#
