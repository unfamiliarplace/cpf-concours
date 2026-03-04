from pathlib import Path
from concours import *
import openpyxl
import warnings

SFORMAT_TRADITIONAL = 'Traditionnel'
SFORMAT_IMPROMPTU = 'Impromptu'

class ConcoursParser:
    
    @staticmethod
    def parse(path: Path) -> Concours:
        c = Concours(path.stem)
        wb = openpyxl.load_workbook(path)

        ConcoursParser.parse_rooms(c, wb)
        # ConcoursParser.parse_volunteers(c, wb)
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

                grade, level = cat_id.split()
                sformat, level = INPUT_SFORMAT_TO_FULL[prefix], INPUT_LEVEL_TO_FULL[level]
                cat = Category(sformat, grade, level, dur)
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

class ScoreboardParser:
    
    @staticmethod
    def parse(path: Path, c: Concours):
        """Adds the scoreboard to the concours and vice-versa rather than returning."""
        sb = Scoreboard(path.stem)
        sb.concours = c
        c.scoreboard = sb

        # Ignore data validation warning
        with warnings.catch_warnings(action='ignore', category=UserWarning):
            wb = openpyxl.load_workbook(path)

        ScoreboardParser.parse_evaluations(sb, wb)

    @staticmethod
    def parse_evaluations(sb: Scoreboard, wb: openpyxl.Workbook):
        sheet = wb['Evaluations']
        rows = [r for r in sheet.rows]
        
        speeches = {}

        # Skip first 3
        rows = rows[3:]

        for row in rows:
            judge_name = row[0].value
            if not judge_name:
                break

            contestant_name = row[4].value
            
            judge = sb.concours.get_judge(judge_name)
            contestant = sb.concours.get_contestant(contestant_name)

            sformat = row[1].value
            if sformat == SFORMAT_TRADITIONAL:
                scores = tuple(c.value for c in row[11:16])
                title = "" # TODO

                speech = speeches.setdefault(contestant, TraditionalSpeech(contestant, title))

            else:
                scores = tuple(c.value for c in row[17:22])
                photo = row[5].value
                phrase = row[6].value

                if photo:
                    prompt_type = PROMPT_PHOTO
                    prompt = photo
                elif phrase:
                    prompt_type = PROMPT_PHRASE
                    prompt = phrase
                else:
                    prompt_type = None
                    prompt = None

                speech = speeches.setdefault(contestant, ImpromptuSpeech(contestant, prompt_type, prompt))

            duration_str = row[7].value
            if duration_str:
            # Reparse this garbage. It's supposed to be minute:second but Excel interpets it as hour:minute
                duration_str = f'{duration_str.hour}:{duration_str.minute}'
                speech.add_duration_from_str(duration_str)

            # TODO Some judges gave no scores
            if set(scores) == {None}:
                scores = None

            e = Evaluation(judge, speech, scores)

            comments = row[8].value
            if comments:
                e.comments = comments
            
            sb.evaluations.add(e)
