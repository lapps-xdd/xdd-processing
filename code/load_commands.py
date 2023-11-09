'''load_commands.py

Utility to build and print the command or commands that can be used to load data
into the ElasticSearch database.

Usage:

$ python load_commands.py      "print default commands"
$ python load_commands.py -h   "print other options"

Commands will look like:

curl http://localhost:9200/xdd-bio/_doc/_bulk \
    -o /dev/null \
    -H "Content-Type: application/json" \
    -X POST --data-binary @elastic-biomedical.json

'''


import os, sys, getopt
from config import TOPICS_DIR

ELASTIC_HOST = 'localhost'
ELASTIC_PORT = 9200

ELA_DIR = 'processed_ela'

DEFAULTS = [
    ('xdd-bio', f'{TOPICS_DIR}/biomedical/{ELA_DIR}/elastic-biomedical.json'),
    ('xdd-geo', f'{TOPICS_DIR}/geoarchive/{ELA_DIR}/elastic-geoarchive.json'),
    ('xdd-mol', f'{TOPICS_DIR}/molecular_physics/{ELA_DIR}/elastic-molecular_physics.json')
]


def print_help():
    print('\nPrint a command that can be used to load data into ElasticSearch')
    print('\n$ python load_data.py (-h | --help) (--dev) --index INDEX --input FILE')
    print('\n    -h | --help        print help message and exit')
    print('    --default          print list of default commands and exit')
    print('    --input FILENAME   use file name as the input file')
    print('    --index INDEX      add contents of the input file to the index')
    print('    --messages         print messages from ElasticSearch\n')


def build_command(db_index: str, input_file: str, messages: bool):
    url = f'http://{ELASTIC_HOST}:{ELASTIC_PORT}/{db_index}/_doc/_bulk'
    dev_null = '' if messages else '-o /dev/null'
    headers = '-H "Content-Type: application/json"'
    data = f'--data-binary @{input_file}'
    return f'curl {url} {dev_null} {headers} -X POST {data}'


def default_commands():
    commands = []
    for index, input_file in DEFAULTS:
        commands.append(build_command(index, input_file, False))
    return '\n'.join(commands)


if __name__ == '__main__':

    (options, args) = getopt.getopt(sys.argv[1:], "h", ["help", "message", "index=", "input="])

    messages = False
    input_file = ''
    db_index = ''

    if not options:
        print(default_commands())
        exit()

    for option, value in options:
        if option in ('-h', '--help'):
            print_help()
            exit()
        if option == '--default':
            print(default_commands())
            exit()
        if option == '--index':
            db_index = value
        if option == '--input':
            input_file = value
        if option == '--messages':
            messages = True

    print(build_command(db_index, input_file, messages))
