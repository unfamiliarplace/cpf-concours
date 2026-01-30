from pathlib import Path
from classes import *
import openpyxl

class ConcoursParser:
    
    @staticmethod
    def parse(path: Path) -> Concours:
        c = Concours(path.stem)
        wb = openpyxl.load_workbook(path)

        ConcoursParser.parse_rooms(c, wb)
    
    @staticmethod
    def parse_rooms(c: Concours, wb: openpyxl.Workbook):
        sheet = wb['rooms']

        periods = {}
        rooms = {}

        rows = [r for r in sheet.rows][1:]
        for row in rows:
            period_id, room_id = (c.value.strip() for c in row)
            periods[period_id] = periods.get(period_id, Period(period_id))
            periods[period_id].add(Room(room_id))

            # TODO ruh roh... concept of unique room per period or continuity of rooms?
