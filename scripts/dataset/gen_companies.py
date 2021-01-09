#!/usr/bin/python3

import csv, sys, getopt, random

man = '''
usage: ./gen_companies.py [arguments]

  Generates the companies email addresses, city, zip and country (to the stdout, can redirect to a file)

  Parameters:
      -c, --companies   <path>  path of the companies input file
      -h, --help                show this message           

  Input:
      input companies csv file with the following fields : name, phone, domain, address

  Output:
      csv output with the following fields : name, phone, email, domain, address, city, zip, country
'''

def usage():
    print(man)
    sys.exit(2)

cities = {'Paris': '75000', 'Nantes':'44000', 'Rennes':'35000', 'Lille':'59000'}
country = 'France'

def map_opts(opts):
    file = ''
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-c', '--companies'):
            file = a
    if file == '':
        usage()
    return file

# Creates the email of the company, selects the first word of the name, removes ",./'", lowercases and add "contact@" and ".com"
def get_email(name):
    bad_chars = [',', '.', '/', "'"]
    suffix = name.split(' ')[0].translate({ord(x): '' for x in bad_chars}).lower()
    return 'contact@' + suffix + '.com'

def write_line(line, writer):
    id, name, phone, domain, address = line
    city = random.choice(list(cities.items()))[0]
    zip = cities.get(city)
    email = get_email(name)
    writer.writerow([id,name,phone,email,domain,address,city,zip,country])

def read_input_and_print_output(path):
    with open(path, 'rt') as f:
        reader = csv.reader(f)
        next(reader)
        writer = csv.writer(sys.stdout)
        writer.writerow(['id', 'name', 'phone', 'email', 'domain', 'address', 'city', 'zip', 'country'])
        for line in reader:
            write_line(line, writer)

def main():
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'c:h', ['companies=', 'help']
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
    file = map_opts(opts)
    read_input_and_print_output(file)

if __name__ == '__main__':
    main()