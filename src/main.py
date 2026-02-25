from pathlib import Path
from parser import ConcoursParser as CP
from schedule import ConcoursScheduler as CS

PATH_BASE = Path('./src')
PATH_INPUT = PATH_BASE / 'input'
PATH_OUTPUT = PATH_BASE / 'output'

# TODO
PATH_HARDCODED_INPUT_FILE = PATH_INPUT / 'concours.xlsx'

def run():
    c = CP.parse(PATH_HARDCODED_INPUT_FILE)

    # for cat in c.categories:
    #     print(cat, cat.base_duration, len(cat.contestants), cat.projected_duration())

    sched = CS.create_valid_schedule(c)
    if sched:
        sched.pretty_print()
    else:
        print('Could not create a valid schedule.')

if __name__ == '__main__':
    run()
