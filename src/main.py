from pathlib import Path
from parser import ConcoursParser, ScoreboardParser
from schedule import ConcoursScheduler as CS
from evaluations import ConcoursReport as CR

PATH_BASE = Path('./src')
PATH_INPUT = PATH_BASE / 'input'
PATH_OUTPUT = PATH_BASE / 'output'
PATH_TEMPLATES = PATH_BASE / 'templates'

# TODO
PATH_HARDCODED_CONCOURS_FILE = PATH_INPUT / 'concours.xlsx'
PATH_HARDCODED_EVALUATIONS_FILE = PATH_INPUT / 'evaluations.xlsx'

def run():
    c = ConcoursParser.parse(PATH_HARDCODED_CONCOURS_FILE)

    # for cat in c.categories:
    #     print(cat, cat.base_duration, len(cat.contestants), cat.projected_duration())

    # sched = CS.create_valid_schedule(c)
    # if sched:
    #     sched.pretty_print()
    # else:
    #     print('Could not create a valid schedule.')

    ScoreboardParser.parse(PATH_HARDCODED_EVALUATIONS_FILE, c)
    report = CR(c)
    report.save()

if __name__ == '__main__':
    run()
