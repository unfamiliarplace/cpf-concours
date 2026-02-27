from pathlib import Path
from concours import *
import openpyxl

class ConcoursParser:
    
    @staticmethod
    def parse(path: Path) -> Concours:
        c = Concours(path.stem)
        wb = openpyxl.load_workbook(path)

        ConcoursParser.parse_rooms(c, wb)
        ConcoursParser.parse_volunteers(c, wb)
        ConcoursParser.parse_participants(c, wb)

        c.set_target_rs_duration()

        return c
    
    @staticmethod
    def parse_volunteers(c: Concours, wb: openpyxl.Workbook):
        sheet = wb['volunteers']

        # TODO For now we'll ignore everything but name

        rows = [r for r in sheet.rows][1:]
        for row in rows:
            last, first = (c.value.strip() for c in row[2:4])
            vol = Volunteer(f'{first} {last}')
            c.volunteers.add(vol)
    
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

    @staticmethod
    def parse_participants(c: Concours, wb: openpyxl.Workbook):
        sheet = wb['participants']
        rows = [r for r in sheet.rows]

        # Use a list to preserve index for mapping contestants
        categories = []

        # First iteration: categories
        for (offset, prefix) in enumerate('TI'):
            start = 12 + (offset * 8)
            for col in range(start, start + 8):
                cat_id = rows[1][col].value.replace('\n', ' ')
                dur = int(rows[3][col].value)

                age, french = cat_id.split()
                cat = Category(prefix, age, french, dur)
                categories.append(cat)
                c.categories.add(cat)
        
        # Second iteration: schools, judges, participants
        for row in rows[5:]:
            cells = [c.value for c in row]

            if not cells[0]:
                continue

            school = School(cells[0].strip(), cells[1].strip())
            c.schools.add(school)

            if cells[11]:
                for j in cells[11].split(','):
                    for p in c.periods:
                        judge = Judge(j, school, p)
                        school.judges.add(judge)
                        c.judges.add(judge)
            
            for (i, contestant_id) in enumerate(cells[12:28]):
                if contestant_id:
                    cat = categories[i]
                    contestant = Contestant(contestant_id, school, cat)
                    school.contestants.add(contestant)
                    cat.contestants.add(contestant)
                    c.contestants.add(contestant)
