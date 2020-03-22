
import datetime
import json

from django.db import models

from run_duel.models import FightEvent

STARTING_HP = 5
ROUND_TIME = 30000   # ms


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
        events = self.all_events()
        return {
            "duel": self.duel.json(),
            "number": self.round_number,
            "status": determine_status(events),
            "score": calculate_score(events),
            "time": time_remaining(events)
        }

    def json(self):
        return json.dumps(
            self.dictionary()
        )

    def all_events(self):
        return list(FightEvent.objects.filter(round__exact=self))


#
# # # Functions used to determine round status
#

def determine_status(events):
    time_events = [
        x for x in events if x.is_time_event()
    ]
    # If there are no time based
    # events for this round
    # then it didn't start yet
    if len(time_events) == 0:
        return "READY"
    elif time_events[-1].type == "PAUSE-ROUND":
        return "PAUSED"
    elif (
        (time_events[-1].type == "CONTINUE-ROUND")
        or (time_events[-1].type == "START-ROUND")
    ):
        return "RUNNING"
    # Last event must be 'finish'
    else:
        return "FINISHED"


#
# # # Functions used to determine round score
#

def calculate_score(events):
    score_events = [
        x for x in events if x.is_score_event()
    ]
    scores = {
        "opponent1": STARTING_HP,
        "opponent2": STARTING_HP
    }
    for event in score_events:
        value = 5
        if "HAND" in event.type:
            value = 2
        elif "HEAD" in event.type:
            value = 1
        elif "BODY" in event.type:
            value = 3
        elif "ADJUST-UP" in event.type:
            # NOTE since we start with
            # a +ve HP and subtract,
            # to adjust up use negative
            # value (will be subtracted later)
            value = -1
        elif "ADJUST-DOWN" in event.type:
            # Similarly need positive value
            # to reduce the score
            value = +1
        if "OPPONENT-1" in event.type:
            scores["opponent1"] -= value
        elif "OPPONENT-2" in event.type:
            scores["opponent2"] -= value
    # HP cannot be depleted below zero
    for opponent in scores.keys():
        if scores[opponent] < 0:
            scores[opponent] = 0
    return scores


#
# # #   Functions used in the calculation of round time
#

# Calculate round time remaining
def time_remaining(events):
    time_events = [
        x for x in events if x.is_time_event()
    ]
    # If the event has not started, ROUND_TIME ms
    # If the event has finished, 0 ms
    has_started = False
    has_finished = False
    for event in time_events:
        if event.type == "START-ROUND":
            has_started = True
        if event.type == "FINISH-ROUND":
            has_finished = True
    if has_finished:
        return 0
    if not has_started:
        return ROUND_TIME
    # Otherwise, need to calculate
    return calculate_total_time(
        events
    )


# Given a set of time events
# calculate total time
# that a duel has been active
def calculate_total_time(events):
    total_time = 0
    while len(events) > 0:
        (
            interval,
            events
        ) = next_time_interval(events)
        if interval is None:
            return total_time
        # The pause/finish is left
        # in the array by the
        # next_time_interval
        # function so pop it
        if len(events) > 0:
            events.pop(0)
        total_time += interval
    return total_time


# Get the length in ms
# of the next active time period
# in this set of events
# Return is a tuple (time interval, remaining events)
def next_time_interval(events):
    # If there is no start or resume
    # event then no more active time intervals
    if not has_start_or_resume(events):
        return None
    # Get index of next start/resume
    start_index = index_of_next_start_or_resume(events)
    # Get index of subsequent stop, if any
    stop_index = index_of_subsequent_pause_or_finish(
        events,
        start_index
    )
    # If stop index is None
    # active period is still ongoing
    if stop_index is None:
        return (
            difference_in_ms(
                datetime.datetime.now(),
                events[start_index].time
            ),
            []
        )
    else:
        return (
            difference_in_ms(
                events[stop_index].time,
                events[start_index].time
            ),
            events[stop_index:]
        )


# The difference in ms between two datetimes
def difference_in_ms(later, earlier):
    later = make_naive(later)
    earlier = make_naive(earlier)
    timedelta = later - earlier
    return timedelta.total_seconds() * 1000


# Recast a datetime object to make it naive
def make_naive(dt):
    return datetime.datetime(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second,
        dt.microsecond
    )


# Is there a start/resume in events?
def has_start_or_resume(events):
    return len([x for x in events if x.type == "START-ROUND" or x.type == "CONTINUE-ROUND"]) > 0


# Find next start or resume event
def index_of_next_start_or_resume(events):
    for i in range(len(events)):
        if events[i].type == "START-ROUND" or events[i].type == "CONTINUE-ROUND":
            return i
    return None


# Find next pause or finish event
# after a certain point
# (start or resume index)
def index_of_subsequent_pause_or_finish(events, start_index):
    for i in range(start_index, len(events)):
        if events[i].type == "PAUSE-ROUND" or events[i].type == "FINISH-ROUND":
            return i
    return None
