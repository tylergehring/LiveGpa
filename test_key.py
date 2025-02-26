import json

import student

def key_test(apiKey):
    stud = student.Student(apiKey, grab_all =False)
    
    stud.get_date()
    stud.get_name_and_id()
    stud.get_courses()
    stud.get_grades()
    print(stud.data)
    #stud.calc_gpa()


if __name__=="__main__":
    key_test('19317~CcEBxV2T87a6eUVryHLyT42F7UzB9N2mU7RUxRD8aYA47NwB2nWLVt7BFaQaMxAJ')
