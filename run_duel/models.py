
import json

from django.db import models


# Duel object
class Duel(models.Model):
    current = models.BooleanField(default=False)
    opponent1 = models.ForeignKey(
        'tournament.Participant',
        related_name="opponent1",
        on_delete=models.CASCADE,
        default=0
    )
    opponent2 = models.ForeignKey(
        'tournament.Participant',
        related_name="opponent2",
        on_delete=models.CASCADE,
        default=0
    )
    sequence_number = models.IntegerField(default=1)
    group = models.ForeignKey(
        'tournament.Group',
        null=True,
        on_delete=models.SET_NULL,
        default=None
    )

    def dictionary(self):
        return {
            "current": self.current,
            "opponent1": self.opponent1.json(),
            "opponent2": self.opponent2.json(),
            "number": self.sequence_number,
            "group": self.group.json()
        }

    def json(self):
        return json.dumps(
            self.dictionary()
        )

    def all_rounds(self):
        return list(Round.objects.filter(duel__exact=self))

    def all_events(self):
        events = list()
        for a_round in self.all_rounds():
            events += a_round.all_events()
        return events


# Round object
class Round(models.Model):
    duel = models.ForeignKey(
        'Duel',
        on_delete=models.CASCADE,
        default=0
    )
    round_number = models.IntegerField(default=1)
    status = models.CharField(
        max_length=20,
        default="NOT STARTED"   # RUNNING, PAUSED, FINISHED
    )

    def dictionary(self):
        return {
            "duel": self.duel.json(),
            "number": self.round_number,
            "status": self.status
        }

    def json(self):
        return json.dumps(
            self.dictionary()
        )

    def all_events(self):
        return list(FightEvent.objects.filter(round__exact=self))


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
