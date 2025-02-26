#Tyler Gehring, 2025.
#Uses the canvas rest api to pull student grades

import json

import classroom

if __name__=="__main__":
    filename = "student_keys.json"
    with open(filename, 'r') as openfile:
        name_key_dict = json.load(openfile)

    class_rm = classroom.Classroom(name_key_dict) #make this the dict instead of just keys for catching errors
    for student in class_rm.students:
        try:
            print(student.data)
        except:
            pass
    

#TODO:
#add errors to error cache. make test script exicutable on error cache to get more detail
