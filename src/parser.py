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
            period_id, room_id = (str(c.value).strip() for c in row)
            
            period = periods.setdefault(period_id, Period(period_id))
            room = rooms.setdefault(room_id, Room(room_id))
            
            period.rooms.add(room)
            room.periods.add(period)

            c.periods.add(period)
            c.rooms.add(room)
       
