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
        cs.reset()

        # TODO Hm... this will be tough. Probably best to just remake each RS?
        cs.rses = None

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

    def get_next_room_schedule_for_placement(self: ConcoursSchedule) -> RoomSchedule:
        # TODO Optimize
        return min(self.rses, key=lambda rs: rs.projected_duration())

class ConcoursScheduler:
    c: Concours

    def __init__(self: ConcoursScheduler, c: Concours):
        self.c = c

    def create_valid_schedule(self: ConcoursScheduler):
        # TODO
        return ConcoursSchedule(self.c)
