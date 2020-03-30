
import json

from django.db import models
from django.utils import timezone

from run_duel.models import Duel


# Tournament model
class Tournament(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)

    def dictionary(self):
        return {
            "name": self.name,
            "date": str(self.date)
        }

    def json(self):
        return json.dumps(
            self.dictionary()
        )

    def all_stages(self):
        return list(Stage.objects.filter(tournament__exact=self))

    def all_groups(self):
        groups = list()
        for stage in self.all_stages():
            groups += list(Group.objects.filter(stage__exact=stage))
        return groups

    def all_duels(self):
        duels = list()
        for group in self.all_groups():
            duels += list(Duel.objects.filter(group__exact=group))

    def all_participants(self):
        return list(Participant.objects.filter(tournaments=self))

    def by_id(self, identifier):
        results = list(Tournament.objects.filter(id__exact=identifier))
        if len(results) > 0:
            return results[0]
        else:
            return None


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

    def all_groups(self):
        return list(Group.objects.filter(stage__exact=self))


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

    def by_id(self, identifier):
        group = list(Group.objects.filter(id__exact=identifier))
        if len(group) > 0:
            return group[0]
        else:
            return None

    def all_duels(self):
        return list(Duel.objects.filter(group__exact=self))


class Participant(models.Model):
    battle_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    tournaments = models.ManyToManyField(Tournament)

    def dictionary(self):
        return {
            "battle_name": self.battle_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

    def json(self):
        return json.dumps(
            self.dictionary()
        )

    def by_id(an_id):
        participant = list(Participant.objects.filter(id__exact=an_id))
        if len(participant) > 0:
            return participant[0]
        else:
            return None
