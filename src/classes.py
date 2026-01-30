from __future__ import annotations

class Concours:
    name: str
    periods: set[Period]
    rooms: set[Room]
    schools: set[School]
    volunteers: set[Volunteer]

    def __init__(self: Concours, name: str):
        self.name = name
        self.periods = set()
        self.rooms = set()
        self.schools = set()
        self.volunteers = set()

    def __repr__(self: Concours) -> str:
        return f'Contest: {self.name}'
    
    def __hash__(self: Concours) -> int:
        return hash(('Concours', self.name))

class Category:
    format: str
    age: str
    french: str
    duration: int
    contestants: set[Contestant]

    def __init__(self: Category, format: str, age: str, french: str, duration: int):
        self.format, self.age, self.french = format, age, french
        self.duration = duration
        self.contestants = set()

    def name(self: Category) -> str:
        return f' {self.format} {self.age} {self.french}'

    def __repr__(self: Category) -> str:
        return f'Cat: {self.name()}'

    def __hash__(self: Category) -> int:
        return hash(('Cat', self.name()))

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
        return hash(('School', self.name))

class Person:
    name: str
    school: School

    def __init__(self: Person, name: str, school: str):
        self.name, self.school = name, school

    def __repr__(self: Person) -> str:
        return f'Person: {self.name}'

    def __hash__(self: Person) -> int:
        return hash(('Person', self.name))

class Judge(Person):
    pass

class Volunteer(Person):
    pass

class Contestant(Person):
    category: Category

    def __init__(self: Contestant, name: str, school: School, category: Category):
        super().__init__(name, school)
        self.category = category
        category.contestants.add(self)

    def __repr__(self: Contestant) -> str:
        return f'Contestant: {self.name}'

    def __hash__(self: Contestant) -> int:
        return hash(('Contestant', self.name))

class Period:
    name: str
    rooms: set[Room]
    schedules: set[RoomSchedule]

    def __init__(self: Period, name: str):
        self.name = name
        self.rooms = set()
        self.reset()

    def reset(self: Period):
        self.schedules = set()

    def __repr__(self: Period) -> str:
        return f'Period: {self.name}'

    def __hash__(self: Period) -> int:
        return hash(('Period', self.name))

class Room:
    name: str
    periods: set[Period]
    schedules: list[RoomSchedule]

    def __init__(self: Room, name: str):
        self.name = name
        self.periods = set()
        self.reset()

    def reset(self: Room):
        self.schedules = set()

    def __repr__(self: Room) -> str:
        return f'Room: {self.name}'

    def __hash__(self: Room) -> int:
        return hash(('Room', self.name))

class RoomSchedule:
    period: Period
    room: Room
    judges: set[Judge]
    volunteers: set[Volunteer]
    categories: set[Category]

    def __init__(self: RoomSchedule, period: Period, room: Room):
        self.period, self.room = period, room
        self.judges = set()
        self.volunteers = set()
        self.categories = set()

    def __repr__(self: Room) -> str:
        return f'RoomSchedule: {self.period} / {self.room}'

    def __hash__(self: Room) -> int:
        return hash(('RoomSchedule', self.period, self.room))
