from __future__ import annotations

 # Minutes for duration calculation
TRANSITION_BW_SPEAKERS = 2
TRANSITION_BW_CATEGORIES = 4

class Concours:
    name: str
    periods: set[Period]
    rooms: set[Room]
    schools: set[School]
    volunteers: set[Volunteer]
    categories: set[Category]
    target_rs_duration: int

    def __init__(self: Concours, name: str):
        self.name = name
        self.periods = set()
        self.rooms = set()
        self.schools = set()
        self.categories = set()

        self.target_rs_duration = 0 # To be filled in by parser

        # Redundant
        self.contestants = set()
        self.judges = set()

        # Not used in scheduling
        self.volunteers = set()

    def __repr__(self: Concours) -> str:
        return f'Concours: {self.name}'
    
    def __hash__(self: Concours) -> int:
        return hash(('Concours', self.name))
    
    def projected_duration(self: Concours) -> int:
        return sum(c.projected_duration() for c in self.categories)
    
    def set_target_rs_duration(self: Concours) -> int:
        n_rses = sum(len(p.rooms) for p in self.periods)
        self.target_rs_duration = self.projected_duration() // n_rses

class Category:
    format: str
    age: str
    french: str
    base_duration: int
    contestants: set[Contestant]

    def __init__(self: Category, format: str, age: str, french: str, base_duration: int):
        self.format, self.age, self.french = format, age, french
        self.base_duration = base_duration
        self.contestants = set()

    def name(self: Category) -> str:
        return f' {self.format} {self.age} {self.french}'
    
    def projected_duration(self: Category) -> int:
        return max(0, ((self.base_duration + TRANSITION_BW_SPEAKERS) * len(self.contestants)) - TRANSITION_BW_SPEAKERS)
    
    def eligible_for_judge(self: Category, judge: Judge) -> bool:
        return all(c.eligible_for_judge(judge) for c in self.contestants)
    
    def get_eligible_judges(self: Category, available: set[Judge]) -> set[Judge]:
        return set(filter(lambda j: self.eligible_for_judge(j), available))
    
    def get_schools(self: Category) -> set[School]:
        return set(cont.school for cont in self.contestants)
    
    def get_eligible_judges(self: Category, judges: set[Judge]) -> set[Judge]:
        schools = self.get_schools()
        return set(filter(lambda j: j.school not in schools, judges))

    def shortname(self: Category) -> str:
        age = 'J' if self.age == '9/10' else 'S'
        fre = {
            'Cad.': 'C',
            'Inten.': 'E',
            'Imm.': 'M',
            'Fr.': 'F'
        }

        return f'{self.format}{age}{fre[self.french]}'

    def __repr__(self: Category) -> str:
        # return f'Cat: {self.name()}'
        return f'{self.shortname()}'

    def __hash__(self: Category) -> int:
        return hash(('Cat', self.shortname()))

class School:
    name: str
    shortname: str
    judges: set[Judge]
    contestants: set[Contestant]

    def __init__(self: School, name: str, shortname: str):
        self.name = name
        self.shortname = shortname
        self.judges = set()
        self.contestants = set()

    def __repr__(self: School) -> str:
        return f'School: {self.name}'

    def __hash__(self: School) -> int:
        return hash(('School', self.name))

class Person:
    name: str

    def __init__(self: Person, name: str):
        self.name = name

    def __repr__(self: Person) -> str:
        # return f'Person: {self.name}'
        return f'{self.name}'

    def __hash__(self: Person) -> int:
        return hash(('Person', self.name))

class Volunteer(Person):
    pass

class SchoolPerson(Person):
    school: School

    def __init__(self: SchoolPerson, name: str, school: School):
        super().__init__(name)
        self.school = school

class Judge(SchoolPerson):
    period: Period # Because a judge can be in different places in each period

    def __init__(self: Judge, name: str, school: School, period: Period):
        super().__init__(name, school)
        self.period = period
    
    def eligible_for_contestant(self: Judge, contestant: Contestant) -> bool:
        return self.school != contestant.school
    
    def eligible_for_category(self: Judge, cat: Category) -> bool:
        return all(self.eligible_for_contestant(c) for c in cat.contestants)

    def __repr__(self: Judge) -> str:
        return f'[J:{self.school.shortname:<3}] {self.name}'

    def __hash__(self: Judge) -> int:
        return hash(('Judge', self.name, self.period))

class Contestant(SchoolPerson):
    category: Category

    def __init__(self: Contestant, name: str, school: School, category: Category):
        super().__init__(name, school)
        self.category = category
    
    def eligible_for_judge(self: SchoolPerson, judge: Judge) -> bool:
        return self.school != judge.school

    def __repr__(self: Contestant) -> str:
        # return f'Contestant: {self.name}'
        return f'[C] {self.name}'

    def __hash__(self: Contestant) -> int:
        return hash(('Contestant', self.school, self.category, self.name))

class Period:
    name: str
    rooms: set[Room]

    def __init__(self: Period, name: str):
        self.name = name
        self.rooms = set()

    def __repr__(self: Period) -> str:
        # return f'Period: {self.name}'
        return f'PER {self.name}'
    
    def __eq__(self: Period, other: object) -> bool:
        return isinstance(other, Period) and (other.name == self.name)

    def __hash__(self: Period) -> int:
        return hash(('Period', self.name))

class Room:
    name: str
    periods: set[Period]

    def __init__(self: Room, name: str):
        self.name = name
        self.periods = set()

    def __repr__(self: Room) -> str:
        # return f'Room: {self.name}'
        return f'RM {self.name}'

    def __hash__(self: Room) -> int:
        return hash(('Room', self.name))
    