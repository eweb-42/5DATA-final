#!/usr/bin/python3
import socket, threading, time, getopt, sys
from os import path

man = '''
usage: ./stream-server.py [arguments]

  Streams the specified file on a TCP socket

  Parameters:
      -p, --port    <0-65535>   Port to stream on (8080 by default)
      -f, --file    <path>      path of the file to stream
      -h, --help                show this message
'''

file = ''

def usage():
    print(man)
    sys.exit(2)

def map_opts(opts):
    port = 8080
    file = ''
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
        elif o in ('-p', '--port'):
            port = a
        elif o in ('-f', '--file'):
            file = a
    if file == '':
        usage()
    return int(port), file

def handle(conn, file_path):
    while True:
        with open(file_path, 'rt') as f:
            for line in f:
                try:
                    conn.send(line.encode())
                    time.sleep(0.3)
                except:
                    print('Connection interrupted by client, closing thread')
                    sys.exit()
            print('Reached EOF, closing conn')
            sys.exit()
            conn.close()

def main():
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], 'p:f:h', ['port=', 'file=' 'help']
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
    
    port, file_path = map_opts(opts)

    if path.exists(file_path):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', port))
        server.listen()

        while True:
            print(f'listening on port {port}')
            conn, addr = server.accept()
            print('handling connection from ' + str(addr))
            threading.Thread(target=handle, args=(conn, file_path)).start()
    else:
        print('file ' + file_path + ' does not exist')
        usage()

if __name__ == "__main__":
    main()