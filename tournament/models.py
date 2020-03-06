
from django.db import models
from django.utils import timezone


# Tournament model
class Tournament(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)


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


class Group(models.Model):
    number = models.IntegerField(default=0)
    contestant_number = models.IntegerField(default=0)
    stage = models.ForeignKey(
        'Stage',
        on_delete=models.CASCADE,
        default=0
    )
