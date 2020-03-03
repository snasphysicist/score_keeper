
from django.db import models


# Duel object
class Duel(models.Model):
    current = models.BooleanField(default=False)
    opponent1 = models.CharField(max_length=100)
    opponent2 = models.CharField(max_length=100)
    sequence_number = models.IntegerField(default=1)


# Round object
class Round(models.Model):
    duel = models.ForeignKey(
        'Duel',
        on_delete=models.CASCADE,
        default=0
    )
    round_number = models.IntegerField(default=1)


# Event object
class FightEvent(models.Model):
    round = models.ForeignKey(
        'Round',
        on_delete=models.CASCADE,
        default=0
    )
    time = models.DateTimeField('Occurred At')
    type = models.CharField(max_length=20)

