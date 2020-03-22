
import json

from django.db import models


# Event object
class FightEvent(models.Model):
    round = models.ForeignKey(
        'Round',
        on_delete=models.CASCADE,
        default=0
    )
    time = models.DateTimeField('Occurred At')
    type = models.CharField(max_length=20)

    def dictionary(self):
        return {
            "round": self.round.json(),
            "time": str(self.time),
            "type": self.type
        }

    def json(self):
        return json.dumps(
            self.dictionary()
        )

    # Determine whether this
    # fight event is related
    # to fight timing
    def is_time_event(self):
        return (
                (self.type == "START-ROUND")
                or (self.type == "PAUSE-ROUND")
                or (self.type == "CONTINUE-ROUND")
                or (self.type == "FINISH-ROUND")
        )

    # Determine whether this event
    # if of a type related to scoring
    def is_score_event(self):
        return (
                ("HEAD" in self.type)
                or ("HAND" in self.type)
                or ("BODY" in self.type)
                or ("ADJUST" in self.type)
        )
