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
        print(c)

