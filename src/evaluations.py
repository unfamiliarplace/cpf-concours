from __future__ import annotations

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
        er = EvaluationsReport()

        for judge in c.judges:
            er.judge_to_es = set(filter(lambda e: e.judge == judge, es))

        for contestant in c.contestants:
            er.contestant_to_es = set(filter(lambda e: e.speech.contestant == contestant, es))
            # by_contestant[contestant] = (et.average(_es), et.averages(_es))
            # for con in sorted(by_contestant, key=lambda c: c.name):
            #     print(con, by_contestant[con])

        for format in FORMATS:
            pass

class EvaluationsReport:
    judge_to_es: dict[Judge, set[Evaluation]]
    contestant_to_es: dict[Contestant, set[Evaluation]]
    format_to_es: dict[str, set[Evaluation]]
    grade_to_es: dict[str, set[Evaluation]]
    level_to_es: dict[str, set[Evaluation]]
    duration_to_es_by_bucket: dict[int, set[Evaluation]] # Bucket by # of minutes?
    category_to_places: dict[Category, list[Contestant]]
    school_to_es_given: dict[School, set[Evaluation]]
    school_to_es_received: dict[School, set[Evaluation]]

    def __init__(self: EvaluationsReport):
        self.judge_to_es = {}
        self.contestant_to_es = {}
        self.format_to_es = {}
        self.grade_to_es = {}
        self.level_to_es = {}
        self.duration_to_es_by_bucket = {}
        self.category_to_places = {}
        self.school_to_es_given = {}
        self.school_to_es_received = {}

