from __future__ import annotations

class Contest:
    periods: set[Period]
    schools: set[School]
    volunteers: set[Volunteer]

    def __init__(self: Contest):
        self.periods = set()
        self.schools = set()
        self.volunteers = set()

class Category:
    name: str
    contestants: set[Contestant]

    def __init__(self: Category, name: str):
        self.name = name
        self.contestants = set()

    def __repr__(self: Category) -> str:
        return f'Cat: {self.name}'

    def __hash__(self: Category) -> int:
        return hash('Cat', self.name)

class School:
    name: str
    judges: set[Judge]
    contestants: set[Contestant]

    def __init__(self: School, name: str):
        self.name = name
        self.judges = set()
        self.contestants = set()

    def __repr__(self: School) -> str:
        return f'School: {self.name}'

    def __hash__(self: School) -> int:
        return hash('School', self.name)

class Person:
    name: str
    school: School

    def __init__(self: Person, name: str, school: str):
        self.name, self.school = name, school

    def __repr__(self: Person) -> str:
        return f'Person: {self.name}'

    def __hash__(self: Person) -> int:
        return hash('Person', self.name)

class Judge(Person):
    pass

class Volunteer(Person):
    pass

class Contestant(Person):
    category: Category

    def __init__(self, name: str, school: School, category: Category):
        super().__init__(name, school)
        self.category = category
        category.contestants.add(self)

class Period:
    name: str
    rooms: set[Room]

    def __init__(self: Period, name: str):
        self.name = name
        self.rooms = []

    def __repr__(self: Period) -> str:
        return f'Period: {self.name}'

    def __hash__(self: Period) -> int:
        return hash('Period', self.name)

class Room:
    name: str
    judges: set[Judge]
    volunteers: set[Volunteer]
    categories: set[Category]

    def __init__(self: Room, name: str):
        self.name = name
        self.judges = set()
        self.volunteers = set()
        self.categories = set()

    def __repr__(self: Room) -> str:
        return f'Room: {self.name}'

    def __hash__(self: Room) -> int:
        return hash('Room', self.name)
