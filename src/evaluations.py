from __future__ import annotations

from concours import *

class ConcoursReport:
    judge_to_sp: dict[Judge, Scorepad]
    contestant_to_sp: dict[Contestant, Scorepad]
    sformat_to_sp: dict[str, Scorepad]
    grade_to_sp: dict[str, Scorepad]
    level_to_sp: dict[str, Scorepad]
    duration_to_sp_by_bucket: dict[int, Scorepad] # Bucket by # of minutes
    category_to_places: dict[Category, list[Scorepad]]
    school_to_sp_given: dict[School, Scorepad]
    school_to_sp_received: dict[School, Scorepad]

    def __init__(self: ConcoursReport, c: Concours):
        self.judge_to_sp = {}
        self.contestant_to_sp = {}
        self.sformat_to_sp = {}
        self.grade_to_sp = {}
        self.level_to_sp = {}
        self.duration_to_sp_by_bucket = {}
        self.category_to_places = {}
        self.school_to_sp_given = {}
        self.school_to_sp_received = {}

        es = set(filter(lambda e: e.scores != None, c.scoreboard.evaluations))

        for judge in c.judges:
            self.judge_to_sp[judge] = Scorepad(judge, set(filter(lambda e: e.judge == judge, es)))

        for cont in c.contestants:
            self.contestant_to_sp[cont] = Scorepad(cont, set(filter(lambda e: e.speech.contestant == cont, es)))

        for sformat in SFORMATS:
            self.sformat_to_sp[sformat] = Scorepad(sformat, set(filter(lambda e: e.sformat == sformat, es)))

        for grade in GRADES:
            self.grade_to_sp[grade] = Scorepad(grade, set(filter(lambda e: e.grade == grade, es)))

        for level in LEVELS:
            self.level_to_sp[level] = Scorepad(level, set(filter(lambda e: e.level == level, es)))

        for e in es:
            bucket = round(e.speech.duration / 60)
            self.duration_to_sp_by_bucket.setdefault(bucket, Scorepad(bucket, set())).evaluations.add(e) # Hackish
        
        for cat in c.categories:
            conts = set(filter(lambda sp: sp.item.category == cat, self.contestant_to_sp.values()))
            self.category_to_places[cat] = sorted(conts, key=lambda cont: cont.average(), reverse=True)

        for school in c.schools:
            self.school_to_sp_given[school] = Scorepad(school, set(filter(lambda e: e.judge.school == school, es)))
            self.school_to_sp_received[school] = Scorepad(school, set(filter(lambda e: e.contestant.school == school, es)))

class Scorepad:
    item: object
    evaluations: set[Evaluation]

    def __init__(self: Scorepad, item: object, evaluations: set[Evaluation]):
        self.item, self.evaluations = item, evaluations
    
    def averages(self: Scorepad) -> list[float]:
        totals = [0, 0, 0, 0, 0]
        if not self.evaluations:
            return totals

        for e in self.evaluations:
            for i in range(5):
                totals[i] += e.scores[i]

        for i in range(5):
                totals[i] = round(totals[i] / len(self.evaluations), 1)

        return totals
    
    def average(self: Scorepad) -> float:
        if not self.evaluations:
            return 0.0
        else:
            return round(sum(sum(e.scores) for e in self.evaluations) / len(self.evaluations), 1)
