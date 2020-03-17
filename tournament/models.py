
import json

from django.db import models
from django.utils import timezone


# Tournament model
class Tournament(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)

    def dictionary(self):
        return {
            "name": self.name,
            "date": self.date
        }

    def json(self):
        return json.dumps(
            self.dictionary()
        )


# Stage of a tournament
class Stage(models.Model):
    number = models.IntegerField(default=0)
    # ROUND-ROBIN, KNOCKOUT
    stage_format = models.CharField(
        default="ROUND-ROBIN",
        max_length=20
    )
    tournament = models.ForeignKey(
        'Tournament',
        on_delete=models.CASCADE,
        default=0
    )

    def dictionary(self):
        return {
            "number": self.number,
            "format": self.stage_format,
            "tournament": self.tournament.json()
        }

    def json(self):
        return json.dumps(
            self.dictionary()
        )


class Group(models.Model):
    number = models.IntegerField(default=0)
    contestant_number = models.IntegerField(default=0)
    stage = models.ForeignKey(
        'Stage',
        on_delete=models.CASCADE,
        default=0
    )

    def dictionary(self):
        return {
            "number": self.number,
            "contestant_number": self.contestant_number,
            "stage": self.stage.json()
        }

    def json(self):
        return json.dumps(
            self.dictionary()
        )


class Participant(models.Model):
    battle_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    tournaments = models.ManyToManyField(Tournament)
