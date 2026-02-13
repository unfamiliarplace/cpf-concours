from __future__ import annotations
from concours import *

class RoomSchedule:
    period: Period
    room: Room
    judges: set[Judge]
    categories: set[Category]

    def __init__(self: RoomSchedule, period: Period, room: Room):
        self.period, self.room = period, room
        self.judges = set()
        self.categories = set()
    
    def projected_duration(self: RoomSchedule) -> int:
        return sum(c.projected_duration() for c in self.categories)
    
    def clone(self: RoomSchedule) -> RoomSchedule:
        rs = RoomSchedule(self.period, self.room)
        rs.judges = self.judges.copy()
        rs.categories = self.categories.copy()
        return rs

    def __repr__(self: RoomSchedule) -> str:
        return f'RoomSchedule: {self.period} / {self.room}'

    def __hash__(self: RoomSchedule) -> int:
        return hash(('RoomSchedule', self.period, self.room))

class ConcoursSchedule:
    c: Concours
    rses: set[RoomSchedule]

    judges_to_eligible_cats: dict[Judge, Category]
    cats_to_eligible_judges: dict[Category, Judge]

    judges_to_eligible_rses: dict[Judge, RoomSchedule]
    rses_to_eligible_judges: dict[RoomSchedule, Judge]

    cats_to_eligible_rses: dict[Category, RoomSchedule]
    rses_to_eligible_cats: dict[RoomSchedule, Category]

    def __init__(self: ConcoursSchedule, c: Concours):
        self.c = c
        self.reset()

    def clone(self: ConcoursSchedule) -> ConcoursSchedule:
        cs = ConcoursSchedule(self.c)

        # Surely this is bad

        cs.rses = ConcoursScheduler.clone_rses(cs.rses)
        
        cs.judges_to_eligible_rses = {}
        cs.cats_to_eligible_rses = {}
        cs.rses_to_eligible_judges = {}
        cs.rses_to_eligible_cats = {}

        for j in self.judges_to_eligible_rses:
            cs.judges_to_eligible_rses[j] = ConcoursScheduler.clone_rses(self.judges_to_eligible_rses[j])

        for cat in self.cats_to_eligible_rses:
            cs.cats_to_eligible_rses[cat] = ConcoursScheduler.clone_rses(self.cats_to_eligible_rses[cat])

        for rs in self.rses_to_eligible_judges:
            cs.rses_to_eligible_judges[rs] = self.rses_to_eligible_judges[rs].copy()

        for rs in self.rses_to_eligible_cats:
            cs.rses_to_eligible_cats[rs] = self.rses_to_eligible_cats[rs].copy()

        return cs

    def reset(self: ConcoursSchedule):
        self.make_initial_room_schedules()
        self.make_initial_rs_relationships()
        self.make_judge_category_relationships()

    def make_judge_category_relationships(self: ConcoursSchedule):
        self.judges_to_eligible_cats = dict()
        for j in self.c.judges:
            self.judges_to_eligible_cats[j] = set(filter(lambda c: j.eligible_for_category(c), self.c.categories))

        self.cats_to_eligible_judges = dict()
        for c in self.c.categories:
            self.cats_to_eligible_judges[c] = set(filter(lambda j: j.eligible_for_category(c), self.c.judges))

    def make_initial_rs_relationships(self: ConcoursSchedule):
        self.judges_to_eligible_rses = {j: self.rses.copy() for j in self.c.judges}
        self.rses_to_eligible_judges = {rs: self.c.judges.copy() for rs in self.rses}

        self.cats_to_eligible_rses = {c: self.rses.copy() for c in self.c.categories}
        self.rses_to_eligible_cats = {rs: self.c.categories.copy() for rs in self.rses}
    
    def make_initial_room_schedules(self: ConcoursSchedule):        
        self.rses = set()

        for period in self.c.periods:
            for room in period.rooms:
                rs = RoomSchedule(period, room)
                self.rses.add(rs)
    
    def sort_rses_for_placement_of_category(self: ConcoursSchedule, cat: Category) -> list[RoomSchedule]:
        """
        1. Most categories sharing a format with this one
        2. Most categories sharing an age group with this one
        3. Most categories sharing a French level with this one
        4. Fewest categories already
        5. Shortest duration already
        """
        def _terms(rs: RoomSchedule) -> tuple[int]:
            return (
                -len([other for other in rs.categories if other.format == cat.format]),
                -len([other for other in rs.categories if other.age == cat.age]),
                -len([other for other in rs.categories if other.french == cat.french]),
                len(rs.categories),
                rs.projected_duration()
            )

        return sorted(self.rses, key=_terms)

    def sort_rses_for_placement_of_judge(self: ConcoursSchedule, j: Judge) -> list[RoomSchedule]:
        """
        1. Fewest judges already
        2. Fewest judges from the same school
        """
        def _terms(rs: RoomSchedule) -> tuple[int]:
            return (
                len(rs.judges),
                len([other for other in rs.judges if other.school == j.school])
            )

        return sorted(self.rses, key=_terms)

class ConcoursScheduler:        

    @staticmethod
    def clone_rses(rses: set[RoomSchedule]) -> set[RoomSchedule]:
        return set(rs.clone() for rs in rses)

    @staticmethod
    def create_valid_schedule(c: Concours) -> ConcoursSchedule:
        # TODO
        s = ConcoursSchedule(c)
        
        # for cat in c.categories:
        #     print(cat)
        #     rses = s.sort_rses_for_placement_of_category(cat)
        #     print(rses)
        #     print(rses[0])
        #     rses[0].categories.add(cat)
        
        return s
