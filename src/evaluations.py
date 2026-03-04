from concours import *

class EvaluationsTool:
    
    @staticmethod
    def evaluations_with_scores(sb: Scoreboard) -> set[Evaluation]:
        return set(filter(lambda e: e.scores != None, sb.evaluations))
    
    @staticmethod
    def averages(es: set[Evaluation]) -> float:
        totals = [0, 0, 0, 0, 0]

        for e in es:
            for i in range(5):
                totals[i] += e.scores[i]

        for i in range(5):
            totals[i] = round(totals[i] / len(es), 1)

        return totals
    
    @staticmethod
    def average(es: set[Evaluation]) -> float:
        return round(sum(sum(e.scores) for e in es) / len(es), 1)
    
    @staticmethod
    def do_report(c: Concours):
        et = EvaluationsTool
        es = et.evaluations_with_scores(c.scoreboard)

        # By judge

        # By contestant
        by_contestant = {}
        for contestant in c.contestants:
            print(contestant)
            _es = set(filter(lambda e: e.speech.contestant == contestant, es))
            if _es:
                by_contestant[contestant] = (et.average(_es), et.averages(_es))
            else:
                by_contestant[contestant] = 'No scores available'
        
        for con in sorted(by_contestant, key=lambda c: c.name):
            print(con, by_contestant[con])

        # By format

        # By grade

        # By French level

        # By duration (bucket by # of minutes?)

        # Places by score per category

        # Judge deviation per contestant
