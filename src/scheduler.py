from __future__ import annotations
from classes import *

class ConcoursScheduler:
    c: Concours

    def __init__(self: ConcoursScheduler, c: Concours):
        self.c = c

    def reset_schedules(self: ConcoursScheduler):
        for period in self.c.periods:
            period.reset()

        for room in self.c.rooms:
            room.reset()
    
    def make_empty_schedules(self: ConcoursScheduler):
        self.reset_schedules()

        for period in self.c.periods:
            for room in period.rooms:
                rs = RoomSchedule(period, room)
                period.schedules.add(rs)
                room.schedules.append(rs)
