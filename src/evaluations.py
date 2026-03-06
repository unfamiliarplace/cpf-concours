from __future__ import annotations
from typing import Iterable

import openpyxl
from openpyxl.workbook.workbook import Workbook
from pathlib import Path
from concours import *

PATH_BASE = Path('./src')
PATH_OUTPUT = PATH_BASE / 'output'
PATH_TEMPLATES = PATH_BASE / 'templates'

PATH_REPORT_TEMPLATE = PATH_TEMPLATES / 'report.xlsx'

PERIOD_ANY = ''

def assign_cells(ws, cols: str, row: int, values: Iterable):
    for (c, v) in zip(cols, values):
            ws[f'{c}{row}'] = v

class ConcoursReport:
    concours: Concours
    judge_to_sp: dict[Judge, Scorepad]
    judge_to_sp_adj: dict[Judge, Scorepad]
    contestant_to_sp: dict[Contestant, Scorepad]
    contestant_to_sp_adj: dict[Contestant, Scorepad]
    sformat_to_sp: dict[str, Scorepad]
    grade_to_sp: dict[str, Scorepad]
    level_to_sp: dict[str, Scorepad]
    duration_to_sp_by_bucket: dict[int, Scorepad] # Bucket by # of minutes
    category_to_sp: dict[int, Scorepad]
    category_to_places: dict[Category, list[Scorepad]]
    school_to_sp_given: dict[School, Scorepad]
    school_to_sp_received: dict[School, Scorepad]

    def __init__(self: ConcoursReport, c: Concours):
        self.concours = c
        self.judge_to_sp = {}
        self.judge_to_sp_adj = {}
        self.contestant_to_sp = {}
        self.contestant_to_sp_adj = {}
        self.sformat_to_sp = {}
        self.grade_to_sp = {}
        self.level_to_sp = {}
        self.duration_to_sp_by_bucket = {}
        self.category_to_sp = {}
        self.category_to_places = {}
        self.school_to_sp_given = {}
        self.school_to_sp_received = {}

        es = set(filter(lambda e: e.scores != None, c.scoreboard.evaluations))
       
        # Must be done first for adjustment
        for cat in c.categories:
            self.category_to_sp[cat] = Scorepad(cat, set(filter(lambda e: e.category == cat, es)))

        # Must precede category places
        for cont in c.contestants:
            sp = Scorepad(cont, set(filter(lambda e: e.speech.contestant == cont, es)))
            self.contestant_to_sp[cont] = sp
            self.contestant_to_sp_adj[cont] = sp.adjust_to_category(self.category_to_sp)

        for judge in c.judges:
            # Hackish solution to different periods
            judge = Judge(judge.name, judge.school, PERIOD_ANY)

            sp = Scorepad(judge, set(filter(lambda e: e.judge == judge, es)))
            self.judge_to_sp[judge] = sp
            self.judge_to_sp_adj[judge] = sp.adjust_to_category(self.category_to_sp)

        # Places
        for cat in c.categories:
            conts = set(filter(lambda sp: sp.item.category == cat, self.contestant_to_sp.values()))
            self.category_to_places[cat] = sorted(conts, key=lambda cont: cont.average(), reverse=True)

        for sformat in SFORMATS:
            self.sformat_to_sp[sformat] = Scorepad(sformat, set(filter(lambda e: e.sformat == sformat, es)))

        for grade in GRADES:
            self.grade_to_sp[grade] = Scorepad(grade, set(filter(lambda e: e.grade == grade, es)))

        for level in LEVELS:
            self.level_to_sp[level] = Scorepad(level, set(filter(lambda e: e.level == level, es)))

        for e in es:
            bucket = round(e.speech.duration / 60)
            self.duration_to_sp_by_bucket.setdefault(bucket, Scorepad(bucket, set())).evaluations.add(e) # Hackish

        for school in c.schools:
            self.school_to_sp_given[school] = Scorepad(school, set(filter(lambda e: e.judge.school == school, es)))
            self.school_to_sp_received[school] = Scorepad(school, set(filter(lambda e: e.contestant.school == school, es)))

    def save(self: ConcoursReport):
        wb = openpyxl.load_workbook(PATH_REPORT_TEMPLATE)

        self._save_judges(wb)
        self._save_contestants(wb)
        self._save_categories(wb)
        self._save_sformats(wb)
        self._save_grades(wb)
        self._save_levels(wb)
        self._save_durations(wb)
        self._save_places(wb)
        self._save_schools_given(wb)
        self._save_schools_received(wb)

        path = PATH_OUTPUT / f'statistics_{self.concours.name}.xlsx'
        wb.save(path)

    @staticmethod
    def sorted_sps(d: dict[object, Scorepad]) -> list[Scorepad]:
        return ConcoursReport.sort_sps(d.values())

    @staticmethod
    def sort_sps(sps: Iterable[Scorepad]) -> list[Scorepad]:
        return sorted(sps, key=lambda sp: sp.average(), reverse=True)

    def _save_judges(self: ConcoursReport, wb: Workbook):
        for (key, sps) in zip(
            ('judges'           , 'judges_adjust'       ),
            (self.judge_to_sp   , self.judge_to_sp_adj  )
        ):

            ws = wb[key]
            for (i, sp) in enumerate(self.sorted_sps(sps)):
                n = i + 2
                j = sp.item

                spt = sp.filter_traditional()
                spi = sp.filter_impromptu()
                
                ws[f'A{n}'] = j.name
                ws[f'B{n}'] = sp.n
                ws[f'C{n}'] = sp.average()

                ws[f'D{n}'] = spt.n
                ws[f'E{n}'] = spt.average()
                assign_cells(ws, 'FGHIJ', n, spt.averages())

                ws[f'K{n}'] = spi.n
                ws[f'L{n}'] = spi.average()
                assign_cells(ws, 'MNOPQ', n, spi.averages())

    def _save_contestants(self: ConcoursReport, wb: Workbook):
        for (key, sps) in zip(
            ('contestants'          , 'contestants_adjust'      ),
            (self.contestant_to_sp  , self.contestant_to_sp_adj )
        ):

            ws = wb[key]
            for (i, sp) in enumerate(self.sorted_sps(sps)):
                n = i + 2
                c = sp.item

                spt = sp.filter_traditional()
                spi = sp.filter_impromptu()
                
                ws[f'A{n}'] = c.name
                ws[f'B{n}'] = sp.average()

                ws[f'C{n}'] = spt.average()
                assign_cells(ws, 'DEFGH', n, spt.averages())

                ws[f'I{n}'] = spi.average()
                assign_cells(ws, 'JKLMN', n, spi.averages())

    def _save_categories(self: ConcoursReport, wb: Workbook):
        pass

    def _save_sformats(self: ConcoursReport, wb: Workbook):
        pass

    def _save_grades(self: ConcoursReport, wb: Workbook):
        pass

    def _save_levels(self: ConcoursReport, wb: Workbook):
        pass

    def _save_durations(self: ConcoursReport, wb: Workbook):
        pass

    def _save_places(self: ConcoursReport, wb: Workbook):
        pass

    def _save_schools_given(self: ConcoursReport, wb: Workbook):
        pass

    def _save_schools_received(self: ConcoursReport, wb: Workbook):
        pass

class Scorepad:
    item: object
    evaluations: set[Evaluation]
    n: int

    def __init__(self: Scorepad, item: object, evaluations: set[Evaluation]):
        self.item, self.evaluations = item, evaluations
        self.n = len(self.evaluations)

    def filter_evaluations(self: Scorepad, cb: callable) -> Scorepad:
        return Scorepad(self.item, set(filter(cb, self.evaluations)))

    def filter_traditional(self: Scorepad) -> Scorepad:
        return self.filter_evaluations(lambda e: e.sformat == 'Traditionnel')

    def filter_impromptu(self: Scorepad) -> Scorepad:
        return self.filter_evaluations(lambda e: e.sformat == 'Impromptu')
    
    def adjust_to_category(self: Scorepad, cat_sps: dict[Category, set[Scorepad]]) -> Scorepad:
        """
        Take this Scorepad's evaluations and adjust them by subtracting the average
        of any other Scorepads whose item matches this one's category.
        """

        new_es = []
        for e in self.evaluations:
            cat_avgs = cat_sps[e.category].averages()

            new_scores = []
            for i in range(5):
                new_scores.append(e.scores[i] - cat_avgs[i])
            
            new_e = Evaluation(e.judge, e.speech, new_scores)
            new_es.append(new_e)
        
        return Scorepad(self.item, new_es)
    
    def averages(self: Scorepad) -> list[float]:
        totals = [0, 0, 0, 0, 0]
        if not self.n:
            return totals

        for e in self.evaluations:
            for i in range(5):
                totals[i] += e.scores[i]

        for i in range(5):
                totals[i] = round(totals[i] / self.n, 1)

        return totals
    
    def average(self: Scorepad) -> float:
        if not self.evaluations:
            return 0.0
        else:
            return round(sum(sum(e.scores) for e in self.evaluations) / self.n, 1)
