#Tyler Gehring, 2025.
#Uses the canvas rest api to pull student grades

import json

import student

if __name__=="__main__":
    filename = "student_keys.json"
    with open(filename, 'r') as openfile:
        data = json.load(openfile)
    key = data[0]['apiKey']
    tyler = student.Student(key)
    print(tyler.data)
