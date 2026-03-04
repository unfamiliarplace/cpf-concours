from concours import *

class EvaluationsTool:
    
    @staticmethod
    def evaluations_with_scores(sb: Scoreboard) -> set[Evaluation]:
        return set(filter(lambda e: e.scores != None, sb.evaluations))
    
    @staticmethod
    def do_report(sb: Scoreboard):
        es = EvaluationsTool.evaluations_with_scores(sb)

        # By judge

        # By participant

        # By format

        # By grade

        # By French level

        # By duration (bucket by # of minutes?)

        # Places by score per category

        # Judge deviation per participant
