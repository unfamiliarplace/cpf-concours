from __future__ import annotations
from typing import Iterator
from concours import *
import random

# The maximum eligible time imbalance: how many multiples of the mean are allowed?
# e.g. Concours = 180 min; 6 rooms; mean per room = 30; value of 1.25 = max time 37.5 min
MAX_TIME_IMBALANCE = 1.25

class CannotAddJudgeException(Exception):
     def __init__(self: CannotAddJudgeException, j: Judge):
        self.message = f'Cannot add judge {j}'
        super().__init__(self.message)

class CannotAddCategoryException(Exception):
     def __init__(self: CannotAddCategoryException, cat: Category):
        self.message = f'Cannot add category {cat}'
        super().__init__(self.message)

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
    
    def can_accommodate_cat_duration(self: RoomSchedule, target: int, cat: Category) -> bool:
        return ((self.projected_duration() + cat.projected_duration()) / target) <= (target * MAX_TIME_IMBALANCE)
    
    def clone(self: RoomSchedule) -> RoomSchedule:
        rs = RoomSchedule(self.period, self.room)
        rs.judges = self.judges.copy()
        rs.categories = self.categories.copy()
        return rs

    def __repr__(self: RoomSchedule) -> str:
        return f'RoomSchedule: {self.period} / {self.room}'

    def __hash__(self: RoomSchedule) -> int:
        return hash(('RoomSchedule', self.period, self.room))
    
    def __eq__(self: RoomSchedule, other: object) -> bool:
        if not isinstance(other, RoomSchedule):
            return False
        
        return hash(self) == hash(other)
    
    def __ne__(self: RoomSchedule, other: object) -> bool:
        return not (self == other)

class ConcoursSchedule:
    c: Concours
    rses: set[RoomSchedule]

    target_rs_duration: int

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
        self.target_rs_duration = self.c.projected_duration() // len(self.rses)

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

        rses = filter(lambda rs: cat in self.rses_to_eligible_cats[rs], self.rses)
        return sorted(rses, key=_terms)

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

        rses = filter(lambda rs: j in self.rses_to_eligible_judges[rs], self.rses)
        return sorted(rses, key=_terms)
    
    def match_rs(self: ConcoursSchedule, rs: RoomSchedule) -> RoomSchedule:
        """
        Seems very dumb... My reasoning is this:
        - new CS is created that has clones of all the RSes
        - functions like add_cat_to_rs that are given an RS need to identify which clone to act on
        """
        
        for other in self.rses:
            if other == rs:
                return other

    def add_cat_to_rs(self: ConcoursSchedule, cat: Category, rs: RoomSchedule) -> ConcoursSchedule:
        new_cs = self.clone()
        new_rs = new_cs.match_rs(rs)

        new_rs.categories.add(cat)
        new_cs.rses_to_eligible_judges[rs] = set(filter(
            lambda j: j.eligible_for_category(cat), self.rses_to_eligible_judges[rs]
        ))
        
        # Update eligibility based on time
        new_cs.rses_to_eligible_cats[rs] = set(filter(
            lambda cat: rs.can_accommodate_cat_duration(self.target_rs_duration, cat), self.rses_to_eligible_cats[rs]
        ))

        return new_cs

    def add_judge_to_rs(self: ConcoursSchedule, j: Judge, rs: RoomSchedule) -> ConcoursSchedule:
        new_cs = self.clone()
        new_rs = new_cs.match_rs(rs)

        new_rs.judges.add(j)
        new_cs.rses_to_eligible_cats[rs] = set(filter(
            lambda cat: cat.eligible_for_judge(j), self.rses_to_eligible_cats[rs]
        ))
        
        return new_cs
    
    def get_ways_to_add_cat(self: ConcoursSchedule, cat: Category) -> Iterator[ConcoursSchedule]:
        rses = self.sort_rses_for_placement_of_category(cat)
        if not rses:
            raise CannotAddCategoryException(cat)

        for rs in rses:
            yield self.add_cat_to_rs(cat, rs)
    
    def get_ways_to_add_judge(self: ConcoursSchedule, j: Judge) -> Iterator[ConcoursSchedule]:
        rses = self.sort_rses_for_placement_of_judge(j)
        if not rses:
            raise CannotAddJudgeException(j)

        for rs in rses:
            yield self.add_judge_to_rs(j, rs)

class ConcoursScheduler:

    @staticmethod
    def clone_rses(rses: set[RoomSchedule]) -> set[RoomSchedule]:
        return set(rs.clone() for rs in rses)

    @staticmethod
    def create_valid_schedule(c: Concours) -> ConcoursSchedule:

        def add_next_item(s: ConcoursSchedule, cats: list[Category], judges: list[Judge]) -> tuple[bool, ConcoursSchedule|None]:
            
            # Base case 1: nothing more to place. Done!
            if (not cats) and (not judges):
                return True, s
            
            # Randomly choose whether to place a cat or a judge
            if (cats and not judges) or random.randint(0, 1):
                cat, cats = cats[0], cats[1:]                
                try:

                    # For each potential way of adding it,
                    # a new schedule object is created
                    for new_s in s.get_ways_to_add_cat(cat):
                        success, candidate = add_next_item(new_s, cats[:], judges[:])
                        if success:
                            return True, candidate

                except CannotAddCategoryException:
                    return False, None

            # Same logic for judge
            else:
                j, judges = judges[0], judges[1:]
                try:
                    for new_s in s.get_ways_to_add_judge(j):
                        success, candidate = add_next_item(new_s, cats[:], judges[:])
                        if success:
                            return True, candidate

                except CannotAddJudgeException:
                    return False, None
                
            # Somehow failed everywhere
            return False, None

        # TODO Consider ordering categories and judges optimally
        success, candidate = add_next_item(ConcoursSchedule(c), list(c.categories), list(c.judges))

        # TODO Test
        if success:
            for rs in candidate.rses:
                print(rs, rs.judges, rs.categories)
                print()
            
            return candidate

        else:
            return None
