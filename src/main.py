from pathlib import Path
from parser import ConcoursParser

PATH_BASE = Path('./src')
PATH_INPUT = PATH_BASE / 'input'
PATH_OUTPUT = PATH_BASE / 'output'

# TODO
PATH_HARDCODED_INPUT_FILE = PATH_INPUT / 'concours.xlsx'

def run():
    contest = ConcoursParser.parse(PATH_HARDCODED_INPUT_FILE)

if __name__ == '__main__':
    run()
