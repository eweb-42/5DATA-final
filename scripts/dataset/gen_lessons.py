#!/usr/bin/python3

import csv, sys, getopt
from random import randrange
from datetime import timedelta, datetime

man = '''
usage: ./gen_lessons.py [arguments]

  Generates 5 consecutive lessons for each subject (thus by professor, by campus)

  Parameters:
      -p, --professors  <path>  path of the audiences input file
      -h, --help                show this message
'''

def usage():
    print(man)
    sys.exit(2)

def map_opts(opts):
    professors = ''
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-p', '--professors'):
            professors = a
    if professors == '':
        usage()
    return professors

def random_date():
    start = datetime(2012,1,1)
    end = datetime(2020,1,1)
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

def get_professors(path):
    professors = []
    with open(path, 'rt') as f:
        reader = csv.reader(f)
        for line in reader:
            professors.append(line)
    professors.pop(0)
    return professors

def generate_lessons(professors):
    lessons = []
    lesson_id = 1
    for p in professors:
        date = random_date()
        for i in range(5):
            professor_id, _, _, _, _, _, campus, subject = p
            date = date + timedelta(1)
            lesson = [lesson_id, date, subject, professor_id, campus]
            lessons.append(lesson)
            lesson_id = lesson_id + 1
    return lessons

def write_lines(lessons):
    writer = csv.writer(sys.stdout)
    writer.writerow(['id', 'date','subject_id', 'professor_id', 'campus_id'])
    for l in lessons:
        writer.writerow(l)

def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'p:h', ['audiences=', 'help']
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
    professors_file = map_opts(opts)
    professors = get_professors(professors_file)
    lessons = generate_lessons(professors)
    write_lines(lessons)

if __name__ == '__main__':
    main()