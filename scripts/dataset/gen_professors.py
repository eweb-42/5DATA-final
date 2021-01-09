#!/usr/bin/python3

import csv, sys, getopt, random

man = '''
usage: ./gen_professors.py [arguments]

  Binds the professors to a subject and a campus.

  Parameters:
      -p, --professors  <path>  path of the companies input file
      -s, --subjects    <path>  path of the subjects file
      -c, --campuses    <int>   number of campuses   
      -h, --help                show this message
'''

def usage():
    print(man)
    sys.exit(2)

def map_opts(opts):
    professors = ''
    subjects = ''
    campuses = None
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-p', '--professors'):
            professors = a
        elif o in ('-c', '-campuses'):
            campuses = int(a)
        elif o in ('-s', '-subjects'):
            subjects = a
    if professors == '' or subjects == '' or campuses == None:
        usage()
    return professors, subjects, campuses

def get_professors(path):
    professors = []
    with open(path, 'rt') as f:
        reader = csv.reader(f)
        for line in reader:
            professors.append(line)
    return professors

def get_subjects(path):
    subjects = []
    with open(path, 'rt') as f:
        reader = csv.reader(f)
        for line in reader:
            subjects.append(line)
    subjects.pop(0)
    return subjects

def bind_professors_to_campuses_and_subjects(professors, subjects, campuses):
    i = 1
    binded_professors = []
    for c in range(campuses):
        for s in subjects:
            professors[i].append(c+1)
            professors[i].append(s[0])
            binded_professors.append(professors[i])
            i = i + 1
    return binded_professors

def write_lines(professors):
    writer = csv.writer(sys.stdout)
    writer.writerow(['id', 'first_name', 'last_name', 'email', 'gender', 'date_of_birth', 'campus_id', 'subject_id'])
    for p in professors:
        writer.writerow(p)

def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'p:s:c:h', ['professors=', 'subjects=', 'campuses=' 'help']
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
    professors_file, subjects_file, campuses_count = map_opts(opts)
    professors = get_professors(professors_file)
    subjects = get_subjects(subjects_file)
    binded_professors = bind_professors_to_campuses_and_subjects(professors, subjects, campuses_count)
    write_lines(binded_professors)

if __name__ == '__main__':
    main()