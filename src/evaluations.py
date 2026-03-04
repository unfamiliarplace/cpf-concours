from __future__ import annotations

from concours import *

class EvaluationTools:
    
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
            if not es:
                totals[i] = 0.0
            else:
                totals[i] = round(totals[i] / len(es), 1)

        return totals
    
    @staticmethod
    def average(es: set[Evaluation]) -> float:
        if not es:
            return 0.0
        else:
            return round(sum(sum(e.scores) for e in es) / len(es), 1)

class ConcoursReport:
    judge_to_es: dict[Judge, set[Evaluation]]
    contestant_to_es: dict[Contestant, set[Evaluation]]
    sformat_to_es: dict[str, set[Evaluation]]
    grade_to_es: dict[str, set[Evaluation]]
    level_to_es: dict[str, set[Evaluation]]
    duration_to_es_by_bucket: dict[int, set[Evaluation]] # Bucket by # of minutes?
    category_to_places: dict[Category, list[Contestant]]
    school_to_es_given: dict[School, set[Evaluation]]
    school_to_es_received: dict[School, set[Evaluation]]

    def __init__(self: ConcoursReport, c: Concours):
        self.judge_to_es = {}
        self.contestant_to_es = {}
        self.sformat_to_es = {}
        self.grade_to_es = {}
        self.level_to_es = {}
        self.duration_to_es_by_bucket = {}
        self.category_to_places = {}
        self.school_to_es_given = {}
        self.school_to_es_received = {}

        ET = EvaluationTools
        es = ET.evaluations_with_scores(c.scoreboard)

        for judge in c.judges:
            self.judge_to_es[judge] = set(filter(lambda e: e.judge == judge, es))

        for cont in c.contestants:
            self.contestant_to_es[cont] = set(filter(lambda e: e.speech.contestant == cont, es))
            # by_contestant[contestant] = (et.average(_es), et.averages(_es))
            # for con in sorted(by_contestant, key=lambda c: c.name):
            #     print(con, by_contestant[con])

        for sformat in SFORMATS:
            self.sformat_to_es[sformat] = set(filter(lambda e: e.sformat == sformat, es))

        for grade in GRADES:
            self.grade_to_es[grade] = set(filter(lambda e: e.grade == grade, es))

        for level in LEVELS:
            self.level_to_es[level] = set(filter(lambda e: e.level == level, es))

        for e in es:
            bucket = round(e.speech.duration / 60)
            self.duration_to_es_by_bucket.setdefault(bucket, {e}).add(e)
        
        for cat in c.categories:
            conts = set(filter(lambda cont: cont.category == cat, c.contestants))
            self.category_to_places[cat] = sorted(conts, key=lambda cont: ET.average(self.contestant_to_es[cont]), reverse=True)

        for school in c.schools:
            self.school_to_es_given[school] = set(filter(lambda e: e.judge.school == school, es))
            self.school_to_es_received[school] = set(filter(lambda e: e.contestant.school == school, es))

