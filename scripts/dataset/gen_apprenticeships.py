#!/usr/bin/python3

import csv, sys, getopt, json
from random import randrange, choice
from datetime import timedelta, datetime
import pandas as pd

man = '''
usage: ./gen_apprenticeships.py [arguments]

  maps 1/3rd of the students to companies of their city

  Parameters:
      -c, --companies   <path>  path of the companies input file
      -s, --students    <path>  path to the students input file
      -h, --help                show this message
'''

def usage():
    print(man)
    sys.exit(2)

def map_opts(opts):
    companies = ''
    students = ''
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-c', '--companies'):
            companies = a
        elif o in ('-s', '--students'):
            students = a
    if companies == '' or students == '':
        usage()
    return companies, students

def sort_companies_by_city(companies):
    sorted_companies = {}
    for city in companies.city.unique():
        sorted_companies[city] = companies[companies['city']==city].values.tolist()
    return sorted_companies

def decision(probability):
    '''
        parameter : probability, must be within 0, 100

        randomly returns true or false with a probability
    '''
    return randrange(0, 100) < probability

def generate_apprenticeships(students, companies, campuses):
    '''
        maps 1/3rd of the students to a company of their city
    '''
    apprenticeships = []
    sorted_companies = sort_companies_by_city(companies)
    for student in students:
        student_id, _, _, _, _, _, _, _, _, campus_id, _ = student
        if decision(33):
            campus_name = campuses.get(campus_id)
            company_id = choice(sorted_companies[campus_name])[0]
            apprenticeships.append([student_id, company_id])
    return apprenticeships

def write_lines(header, records):
    writer = csv.writer(sys.stdout)
    writer.writerow(header)
    for r in records:
        writer.writerow(r)

def main():
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], 'c:s:h', ['companies=', 'students=' 'help']
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
    
    lessons_file, students_file = map_opts(opts)

    companies = pd.read_csv(lessons_file)
    students = pd.read_csv(students_file).values.tolist()

    campuses = {1:'Rennes', 2:'Nantes', 3:'Paris', 4:'Lille'}

    apprenticeships = generate_apprenticeships(students, companies, campuses)
    write_lines(['student_id', 'company_id'], apprenticeships)

if __name__ == '__main__':
    main()