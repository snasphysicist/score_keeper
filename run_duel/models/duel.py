
from functools import reduce
import json

from django.db import models

from run_duel.models import Round


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
            "id": self.id,
            "current": self.current,
            "opponent1": self.opponent1.dictionary(),
            "opponent2": self.opponent2.dictionary(),
            "number": self.sequence_number,
            "group": self.group.dictionary(),
            "status": self.status()
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

    def by_id(self, identifier):
        results = list(Duel.objects.filter(id__exact=identifier))
        if len(results) > 0:
            return results[0]
        else:
            return None

    def marked_as_current(self):
        return list(Duel.objects.filter(current__exact=True))

    def current_duel(self):
        marked_as_current = Duel.marked_as_current(self)
        if len(marked_as_current) == 1:
            return marked_as_current[0]
        else:
            return None

    def status(self):
        statuses = [
            x.dictionary()["status"] for x in self.all_rounds()
        ]
        started = [
            x for x in statuses if x != "READY"
        ]
        if len(started) == 0:
            return "READY"
        unfinished = [
            x for x in started if x != "FINISHED"
        ]
        if len(unfinished) == 0:
            return "FINISHED"
        return "RUNNING"

    def with_round_data(self):
        all_data = self.dictionary()
        rounds = [
            x.dictionary() for x in self.all_rounds()
        ]
        all_data["rounds"] = rounds
        all_data["score"] = {
            "opponent1": reduce(
                lambda s1, s2: s1 + s2,
                map(
                    lambda d: d["score"]["opponent1"],
                    rounds
                )
            ),
            "opponent2": reduce(
                lambda s1, s2: s1 + s2,
                map(
                    lambda d: d["score"]["opponent2"],
                    rounds
                )
            )
        }
        return all_data

    # This and next method
    # assume rounds are sorted
    # by round number
    def current_round(self):
        current = [
            x for x in self.all_rounds() if (
                x.status() == "RUNNING"
                or x.status() == "PAUSED"
            )
        ]
        if len(current) > 0:
            return current[0]
        else:
            return None

    def next_round(self):
        unstarted = [
            x for x in self.all_rounds() if x.status() == "READY"
        ]
        if len(unstarted) > 0:
            return unstarted[0]
        else:
            return None

    def delete_all_events(self):
        rounds = self.all_rounds()
        for a_round in rounds:
            a_round.delete_all_events()
