#!/usr/bin/python3

import csv, sys, getopt, json
from random import randrange
from datetime import timedelta, datetime
import pandas as pd

man = '''
usage: ./gen_attendances.py [arguments]

  Maps 4/5th of the students to the lessons of their level and their campus

  Parameters:
      -l, --lessons     <path>  path of the audiences input file
      -s, --students    <path>  path to the students input file
      -h, --help                show this message
'''

def usage():
    print(man)
    sys.exit(2)

def map_opts(opts):
    lessons = ''
    students = ''
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-l', '--lessons'):
            lessons = a
        elif o in ('-s', '--students'):
            students = a
    if lessons == '' or students == '':
        usage()
    return lessons, students

def sort_lessons(lessons):
    '''
        Sorts lessons in a tree by campus, by level

        sorted_lessons => {
        campus_1 : {
            ASC1 : [
                ['date', '1PROG'],
                ['date', '1WDEV']
            ],
            ASC2 : [
                ['date', '2JAVA']
            ]
        },
        campus_2 : {
        . . .
        }
        }
    '''
    sorted_lessons = {}
    for campus in lessons.campus_id.unique():
        sorted_lessons[str(campus)] = {}
        this_campus_lessons = lessons[lessons.campus_id == campus]
        for i, level in enumerate(['ASC1', 'ASC2','BSC','MSC1','MSC2']):
            sorted_lessons[str(campus)][level] = this_campus_lessons.loc[lessons['subject_id'].str.startswith(str(i+1))].values.tolist()
    return sorted_lessons

def decision(probability):
    '''
        parameter : probability, must be within 0, 100

        randomly returns true or false with a probability
    '''
    return randrange(0, 100) < probability

def generate_attendances(students, lessons):
    '''
        maps students to lessons of their level and campus, with 15% absence
    '''
    attendances = []
    sorted_lessons = sort_lessons(lessons)
    for student in students:
        student_id, _, _, _, _, _, _, _, _, campus_id, promotion = student
        for lesson in sorted_lessons[str(campus_id)][promotion]:
            lesson_id, _, _, _, _, = lesson
            attendances.append([lesson_id, student_id, decision(85)])
    return attendances

def write_lines(lessons):
    writer = csv.writer(sys.stdout)
    writer.writerow(['lesson_id', 'student_id', 'present'])
    for l in lessons:
        writer.writerow(l)

def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'l:s:h', ['audiences=', 'help']
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
    
    lessons_file, students_file = map_opts(opts)

    lessons = pd.read_csv(lessons_file)
    students = pd.read_csv(students_file).values.tolist()

    attendances = generate_attendances(students, lessons)
    write_lines(attendances)

if __name__ == '__main__':
    main()