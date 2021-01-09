#!/usr/bin/python3

import csv, sys, getopt, json
from random import randrange
import pandas as pd
import numpy as np

man = '''
usage: ./gen_grades.py [arguments]

  Generates a random grade (0-100, Gaussian distribution) for the matters corresponding to the student's level

  Parameters:
      -s, --students   <path>  path of the students input file
      -j, --subjects   <path>  path to the subjects input file
      -h, --help                show this message
'''

def usage():
    print(man)
    sys.exit(2)

def map_opts(opts):
    students = ''
    subjects = ''
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-s', '--students'):
            students = a
        elif o in ('-j', '--subjects'):
            subjects = a
    if students == '' or subjects == '':
        usage()
    return students, subjects


# Generates grades with a Gaussian distribution
def gen_grades(students, subjects):
    students = students.drop(['first_name', 'last_name', 'left_date', 'email', 'personal_email', 'gender', 'date_of_birth', 'join_date', 'campus_id'], axis=1)
    subjects = subjects.drop(['name'], axis=1)
    grades = students.merge(subjects, how='outer', left_on='promotion', right_on='level')
    grades = grades.drop(['promotion', 'level'], axis = 1)
    grades = grades.rename({'id_x': 'student_id', 'id_y': 'subject_id'}, axis='columns')
    grades['grade'] = np.floor(np.random.normal(60, 15, len(grades)))
    grades.loc[(grades['grade']>100) | (grades['grade']<0), 'grade'] = randrange(1,100)
    return grades

def write_lines(lessons):
    writer = csv.writer(sys.stdout)
    writer.writerow(['lesson_id', 'student_id', 'present'])
    for l in lessons:
        writer.writerow(l)

def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 's:j:h', ['students=', 'subjects=', 'help']
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
    
    students_path, subjects_path = map_opts(opts)

    students = pd.read_csv(students_path)
    subjects = pd.read_csv(subjects_path)

    grades = gen_grades(students, subjects)
    print(grades.to_csv(index=False))

if __name__ == '__main__':
    main()