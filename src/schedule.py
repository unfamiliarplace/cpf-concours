from __future__ import annotations
from typing import Iterator
from concours import *
import random

# TODO Keep judges in same room??

# Test
NO_VALIDATION = False
NO_VALIDATION = True # TEST

# Max time in period
MAX_TIME = 60

# The maximum eligible time imbalance: how many multiples of the mean are allowed?
# e.g. Concours = 180 min; 6 rooms; mean per room = 30; value of 1.25 = max time 37.5 min
MAX_TIME_IMBALANCE = 1.25

# Maximum cats per room/schedule
MAX_CATS = 3
MIN_CATS = 1

MAX_JUDGES = 2
MIN_JUDGES = 2

MAX_ATTEMPTS = 100_000

class TooManyAttemptsException(Exception):
    pass

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
        return max(0, sum((c.projected_duration() + TRANSITION_BW_CATEGORIES) for c in self.categories) - TRANSITION_BW_CATEGORIES)
    
    def can_accommodate_cat_duration(self: RoomSchedule, target: int, cat: Category) -> bool:
        potential_duration = self.projected_duration() + cat.projected_duration()
        # print(target, potential_duration, potential_duration <= MAX_TIME, (potential_duration / target <= MAX_TIME_IMBALANCE))
        return (potential_duration <= MAX_TIME) and (potential_duration / target <= MAX_TIME_IMBALANCE)
    
    def get_cat_schools(self: RoomSchedule) -> set[School]:
        schools = set()
        for cat in self.categories:
            schools |= cat.get_schools()
        return schools

    def get_eligible_judges(self: RoomSchedule, available: set[Judge]) -> set[Judge]:
        schools = self.get_cat_schools()
        return set(filter(lambda j: j.school not in schools, available))
    
    def validate_min_judges(self: RoomSchedule) -> bool:
        return self.categories and (len(self.judges) >= MIN_JUDGES)
    
    def clone(self: RoomSchedule) -> RoomSchedule:
        rs = RoomSchedule(self.period, self.room)
        rs.judges = self.judges.copy()
        rs.categories = self.categories.copy()
        return rs

    def __repr__(self: RoomSchedule) -> str:
        # return f'RoomSchedule: {self.period} / {self.room}'
        return f'RS: {self.period} / {self.room}'

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

    rses_to_eligible_judges: dict[RoomSchedule, Judge]
    rses_to_eligible_cats: dict[RoomSchedule, Category]

    placeable_judges: set[Judge]
    placeable_cats: set[Category]

    def __init__(self: ConcoursSchedule, c: Concours):
        self.c = c
        self.reset()

    def clone(self: ConcoursSchedule) -> ConcoursSchedule:
        cs = ConcoursSchedule(self.c)

        # Surely this is bad

        cs.rses = ConcoursScheduler.clone_rses(self.rses)
        
        cs.rses_to_eligible_judges = {}
        for rs in self.rses_to_eligible_judges:
            cs.rses_to_eligible_judges[rs] = self.rses_to_eligible_judges[rs].copy()

        cs.rses_to_eligible_cats = {}
        for rs in self.rses_to_eligible_cats:
            cs.rses_to_eligible_cats[rs] = self.rses_to_eligible_cats[rs].copy()

        cs.placeable_judges = self.placeable_judges.copy()
        cs.placeable_cats = self.placeable_cats.copy()

        return cs

    def reset(self: ConcoursSchedule):
        self.make_initial_room_schedules()
        self.make_initial_rs_relationships()
        self.make_initial_placeabilities()
    
    def make_initial_room_schedules(self: ConcoursSchedule):        
        self.rses = set()

        for period in self.c.periods:
            for room in period.rooms:
                rs = RoomSchedule(period, room)
                self.rses.add(rs)

    def make_initial_rs_relationships(self: ConcoursSchedule):
        self.rses_to_eligible_judges = {rs: self.c.judges.copy() for rs in self.rses}
        self.rses_to_eligible_cats = {rs: self.c.categories.copy() for rs in self.rses}
        
    def make_initial_placeabilities(self: ConcoursSchedule):
        self.placeable_judges = self.c.judges.copy()
        self.placeable_cats = self.c.categories.copy()

    def filter_rses_for_placement_of_category(self: ConcoursSchedule, cat: Category) -> set[RoomSchedule]:
        """
        Is the cat eligible for this RS?
        Would adding the cat make it impossible to add a judge to this RS? (i.e., the RS's eligible judges overlaps with the cat's.)
        """
        def _terms(rs: RoomSchedule) -> bool:
            return all([
                cat in self.rses_to_eligible_cats[rs],
                (len(rs.judges) < MIN_JUDGES) and cat.get_eligible_judges(self.rses_to_eligible_judges[rs])
            ])

        return filter(_terms, self.rses)

    def filter_rses_for_placement_of_judge(self: ConcoursSchedule, j: Judge) -> set[RoomSchedule]:
        def _terms(rs: RoomSchedule) -> bool:
            return all([
                j in self.rses_to_eligible_judges[rs]
            ])

        return filter(_terms, self.rses)
    
    def get_rses_for_placement_of_category(self: ConcoursSchedule, cat: Category) -> list[RoomSchedule]:
        """
        Get and sort.

        1. Shortest duration already
        2. Fewest categories already
        3. Most overlap in schools (but what about judges?)
        4. Most categories sharing a format with this one
        5. Most categories sharing an age group with this one
        6. Most categories sharing a French level with this one
        """
        def _terms(rs: RoomSchedule) -> tuple[int]:
            return (
                rs.projected_duration(),                
                len(rs.categories),
                -len(rs.get_cat_schools().intersection(cat.get_schools())),
                -len([other for other in rs.categories if other.format == cat.format]),
                -len([other for other in rs.categories if other.age == cat.age]),
                -len([other for other in rs.categories if other.french == cat.french]),
            )

        rses = self.filter_rses_for_placement_of_category(cat)
        return sorted(rses, key=_terms)

    def get_rses_for_placement_of_judge(self: ConcoursSchedule, j: Judge) -> list[RoomSchedule]:
        """
        Get and sort.

        1. Does not have min judges yet (possibly remove)
        2. Fewest eligible judges available
        3. Fewest judges already
        4. Fewest judges from the same school
        """
        def _terms(rs: RoomSchedule) -> tuple[int]:
            return (
                (len(rs.judges) < MIN_JUDGES),
                len(rs.get_eligible_judges(self.unmatched_judges())),
                len(rs.judges),
                len([other for other in rs.judges if other.school == j.school])
            )

        rses = self.filter_rses_for_placement_of_judge(j)
        return sorted(rses, key=_terms)
    
    def unmatched_judges(self: ConcoursSchedule) -> set[Judge]:
        """
        TODO Inefficient (can just store them when making a CS) but for now
        """
        judges = self.c.judges
        for rs in self.rses:
            judges -= rs.judges
        return judges
    
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
            lambda j: j.eligible_for_category(cat),
            self.rses_to_eligible_judges[rs]
        ))

        new_cs.placeable_cats.remove(cat)

        # Update eligibility based on # of cats and time
        if len(new_rs.categories) >= MAX_CATS:
            new_cs.rses_to_eligible_cats[new_rs] = set()

        else:
            new_cs.rses_to_eligible_cats[new_rs] = set(filter(
                lambda cat: new_rs.can_accommodate_cat_duration(self.c.target_rs_duration, cat),
                self.rses_to_eligible_cats[new_rs]
            ))

        return new_cs

    def add_judge_to_rs(self: ConcoursSchedule, j: Judge, rs: RoomSchedule) -> ConcoursSchedule:
        new_cs = self.clone()
        new_rs = new_cs.match_rs(rs)

        new_rs.judges.add(j)
        new_cs.rses_to_eligible_cats[rs] = set(filter(
            lambda cat: cat.eligible_for_judge(j),
            self.rses_to_eligible_cats[rs]
        ))

        new_cs.placeable_judges.remove(j)
        
        # Update eligibility based on # of judges
        if len(new_rs.judges) >= MAX_JUDGES:
            new_cs.rses_to_eligible_judges[new_rs] = set()
        
        return new_cs
    
    def get_ways_to_add_cat(self: ConcoursSchedule, cat: Category) -> Iterator[ConcoursSchedule]:
        rses = self.get_rses_for_placement_of_category(cat)
        # if not rses:
        #     print(f"Couldn't place {cat}")

        for rs in rses:
            yield self.add_cat_to_rs(cat, rs)
    
    def get_ways_to_add_judge(self: ConcoursSchedule, j: Judge) -> Iterator[ConcoursSchedule]:
        rses = self.get_rses_for_placement_of_judge(j)
        # if not rses:
        #     print(f"Couldn't place {j}")

        for rs in rses:
            yield self.add_judge_to_rs(j, rs)

    def validate_rses_sufficient_judges(self: ConcoursSchedule) -> bool:
        for rs in self.rses:

            # TODO This could perhaps be improved by not rejecting outright
            # but by moving an eligible judge? Might defeat the purpose...
            if not rs.validate_min_judges():
                return False

        return True

    def is_valid(self: ConcoursSchedule) -> bool:
        """
        This is the last-ditch effort. It only gets run after all
        distribution has been made. Thus, it does not short-circuit
        and is not efficient. TODO It's more of a stand-in for better
        guardrails during computation. But it might work for now!
        """

        if NO_VALIDATION:
            return True
        
        return self.validate_rses_sufficient_judges()

    def pretty_print(self: ConcoursSchedule):
        def _terms(rs: RoomSchedule) -> int:
            return (str(rs.period), str(rs.room))

        def format_cat_long(cat: Category) -> str:
            return f'{cat} {(cat.projected_duration())} <{" ".join((p.school.shortname for p in cat.contestants))}>'

        for rs in sorted(self.rses, key=_terms):
            # print(rs, rs.judges, rs.categories)
            print(f'{str(rs):<22} {rs.projected_duration():<3} {", ".join((format_cat_long(cat) for cat in rs.categories))}')
            print('\t', rs.judges)
            print()

class ConcoursScheduler:

    @staticmethod
    def clone_rses(rses: set[RoomSchedule]) -> set[RoomSchedule]:
        return set(rs.clone() for rs in rses)
    
    @staticmethod
    def cat_sort_terms(cat: Category) -> int:
        """
        Duration and # of unique candidate schools (decreasing order for both)
        """
        return [
            -cat.projected_duration(),
            -len(set(p.school for p in cat.contestants))
        ]
    
    @staticmethod
    def judge_sort_terms(j: Judge) -> int:
        """
        # of unique candidate schools (decreasing order)
        """
        return [
            -len(set(p.school for p in j.school.contestants))
        ]

    @staticmethod
    def create_valid_schedule(c: Concours) -> ConcoursSchedule:

        n = [0]
        cat_or_judge = [0] # 0 = cat, 1 = judge

        def add_next_item(s: ConcoursSchedule, cats: list[Category], judges: list[Judge]) -> tuple[bool, ConcoursSchedule|None]:
            # print(len(cats) + len(judges))
            
            # Base case 1: nothing more to place. Done! Note: leftover judges are OK.
            if (not cats) and (not judges):
                    
                # Purge empty rses
                s.rses = set(filter(lambda rs: rs.categories or rs.judges, s.rses))
            
                if s.is_valid():
                    return True, s
                else:
                    return False, None
            
            # Randomly choose whether to place a cat or a judge
            if cats and (not judges or cat_or_judge[0] == 0):
                cat, cats = cats[0], cats[1:]
                for new_s in s.get_ways_to_add_cat(cat):
                    success, candidate = add_next_item(new_s, cats[:], judges[:])
                    if success: # Only finds one successful candidate
                        return True, candidate
                    
                # Judge next
                cat_or_judge[0] = 1

            # Same logic for judge
            else:
                
                j, judges = judges[0], judges[1:]
                for new_s in s.get_ways_to_add_judge(j):
                    success, candidate = add_next_item(new_s, cats[:], judges[:])
                    if success:
                        return True, candidate
                    
                # Cat next
                cat_or_judge[0] = 0
                
            # Somehow failed everywhere
            n[0] += 1

            if not (n[0] % 1_000):
                print(f'Tested {n[0]}...')

            if n[0] > MAX_ATTEMPTS:
                raise TooManyAttemptsException(n[0])

            return False, None

        # Sort
        cats_ = list(c.categories)
        judges_ = list(c.judges)
        
        # strategy 1...
        random.shuffle(cats_)
        random.shuffle(judges_)

        # strategy 2...
        cats_.sort(key=ConcoursScheduler.cat_sort_terms)
        judges_.sort(key=ConcoursScheduler.judge_sort_terms)

        try:
            _, candidate = add_next_item(ConcoursSchedule(c), cats_, judges_)
            return candidate
        
        except TooManyAttemptsException:
            print('Too many attempts. Gave up')
