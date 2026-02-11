from pathlib import Path
from parser import ConcoursParser as CP
from scheduler import ConcoursScheduler as CS

PATH_BASE = Path('./src')
PATH_INPUT = PATH_BASE / 'input'
PATH_OUTPUT = PATH_BASE / 'output'

# TODO
PATH_HARDCODED_INPUT_FILE = PATH_INPUT / 'concours.xlsx'

def run():
    cs = CS(CP.parse(PATH_HARDCODED_INPUT_FILE))
    


if __name__ == '__main__':
    run()
