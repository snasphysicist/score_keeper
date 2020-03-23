
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
            "current": self.current,
            "opponent1": self.opponent1.json(),
            "opponent2": self.opponent2.json(),
            "number": self.sequence_number,
            "group": self.group.json(),
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
        marked_as_current = self.marked_as_current()
        if marked_as_current is not None:
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
        all_data["rounds"] = [
            x.dictionary() for x in self.all_rounds()
        ]
        return all_data

    # This and next method
    # assume rounds are sorted
    # by round number
    def current_round(self):
        current = [
            x for x in self.all_rounds() if (
                x.determine_status() == "RUNNING"
                or x.determine_status() == "PAUSED"
            )
        ]
        if len(current) > 0:
            return current[0]
        else:
            return None

    def next_round(self):
        unstarted = [
            x for x in self.all_rounds() if x.determine_status == "READY"
        ]
        if len(unstarted) > 0:
            return unstarted[0]
        else:
            return None
