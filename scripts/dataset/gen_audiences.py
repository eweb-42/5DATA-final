#!/usr/bin/python3

import csv, sys, getopt, random
import pandas as pd

man = '''
usage: ./gen_professors.py [arguments]

  Maps input audience file ( 1/4th of students) to the corresponding events they have first learned about the campus.

  Parameters:
      -a, --audiences   <path>  path of the audiences input file
      -e, --events      <path>  path of the events input file
      -h, --help                show this message
'''

def usage():
    print(man)
    sys.exit(2)

def map_opts(opts):
    audiences = ''
    events = ''
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-a', '--audiences'):
            audiences = a
        elif o in ('-e', '--events'):
            events = a
    if audiences == '' or events == '':
        usage()
    return audiences, events

def bind_audiences_to_events(audiences, event_count):
    i = 1
    binded_audiences = []
    for a in audiences:
        a.append(random.randint(1, event_count))
        binded_audiences.append(a)
    return binded_audiences

def write_lines(audiences):
    writer = csv.writer(sys.stdout)
    writer.writerow(['first_name', 'last_name', 'email', 'gender', 'date_of_birth', 'event_id'])
    for a in audiences:
        writer.writerow(a)

def main():
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], 'a:e:h', ['audiences=', 'events=' 'help']
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
    audiences_file, events_file = map_opts(opts)

    audiences = pd.read_csv(audiences_file).values.tolist()
    event_count = len(pd.read_csv(events_file).values.tolist())

    binded_audiences = bind_audiences_to_events(audiences, event_count)

    write_lines(binded_audiences)

if __name__ == '__main__':
    main()