
import datetime
import json
import os

from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.template import loader

from run_duel.models import Duel, FightEvent, Round
from tournament.models import Group, Stage, Tournament

CURRENT_TOURNAMENT = 3


# Render new duel page
def new_duel(request):
    template = loader.get_template('run_duel/new.html')
    context = {}
    return HttpResponse(template.render(context, request))


# Move on to a different duel
def new_duel_api(request):
    data = json.loads(
        request.body.decode('utf-8')
    )
    # Basically, just make the selected
    # duel the current one
    duel = list(Duel.objects.filter(id__exact=data["id"]))[0]
    duel["current"] = True
    duel.save()
    return JsonResponse({
        "success": True
    })


# List pending duels
def pending_duel_api(request):
    # Get all groups for current tournament
    tournament = list(Tournament.objects.filter(id__exact=CURRENT_TOURNAMENT))
    stages = list(Stage.objects.filter(tournament__exact=tournament))
    groups = list()
    for stage in stages:
        groups += list(Group.objects.filter(stage__exact=stage))
    # Get all duels for current tournament
    duels = list()
    for group in groups:
        duels += list(Duel.objects.filter(group__exact=group))
    full_data = []
    for duel in duels:
        full_data.append(
            {
                "id": duel.id,
                "number": duel.sequence_number,
                "groupid": duel.group.id,
                "groupnumber": duel.group.number,
                "stageid": duel.group.stage.id,
                "stagenumber": duel.group.stage.number,
                "opponent1": duel.opponent1.battle_name,
                "opponent2": duel.opponent2.battle_name,
                "data": calculate_duel_data(duel)
            }
        )
    # Remove finished duels
    i = 0
    while i < len(full_data):
        is_finished = True
        for a_round in full_data[i]["data"]["rounds"]:
            if a_round["status"] != "FINISHED":
                is_finished = False
        if is_finished:
            full_data.pop(i)
            i -= 1
        i += 1
    return JsonResponse(
        {
            "success": True,
            "pending": full_data
        }
    )


# Render current duel page
def current_duel(request):
    template = loader.get_template('run_duel/current.html')
    context = {
        "websocket_protocol": os.environ["SCORE_KEEPER_WEBSOCKET_PROTOCOL"],
        "base_url": os.environ["SCORE_KEEPER_BASE_URL"]
    }
    return HttpResponse(template.render(context, request))


# Event recording api
def new_event_api(request):
    data = json.loads(
        request.body.decode('utf-8')
    )
    if 'type' not in data.keys():
        return JsonResponse({
            "success": False,
            "reason": "Required key missing from json request"
        })
    # Get the rounds for the current match
    this_duel = list(Duel.objects.filter(current__exact=True))[0]
    these_rounds = list(Round.objects.filter(duel__exact=this_duel))
    # Get the round for this event
    # Will depend upon event type
    if data['type'].upper() == "START-ROUND":
        # For start, want next round
        the_round = next_round(these_rounds)
    else:
        # For everything else, current round
        the_round = current_round(these_rounds)
    event = FightEvent(
        time=datetime.datetime.now(),
        type=data['type'].upper(),
        round=the_round
    )
    try:
        event.save()
        return JsonResponse({
            "success": True
        })
    except IntegrityError as e:
        return JsonResponse({
            "success": False,
            "reason": "Invalid event type"
        })


# Event stream api
def event_stream(request):
    current_duel_object = Duel.objects.filter(
        current__exact=True
    )[0]
    event_data = calculate_duel_data(current_duel_object)
    # TODO add latest event
    return JsonResponse(event_data)


# Used also in tournament app
def calculate_duel_data(duel):
    rounds = list(
        Round.objects.filter(
            duel__exact=duel
        )
    )
    # Get all events for current duel
    current_duel_events = []
    for a_round in rounds:
        current_duel_events += list(
            FightEvent.objects.filter(
                round__exact=a_round
            )
        )
    event_data = {
        "duel": {
            "duel_id": duel.id,
            "opponent1": duel.opponent1,
            "opponent2": duel.opponent2
        },
        "rounds": []
    }
    # Get round time, status data
    (
        round_time,
        round_status
    ) = time_remaining(
        rounds,
        current_duel_events
    )
    # Get score data
    round_scores = calculate_total_score(current_duel_events)
    for a_round in rounds:
        event_data["rounds"].append(
            {
                "round_id": a_round.id,
                "round_number": a_round.round_number,
                "status": round_status[a_round.round_number - 1],
                "time": round_time[a_round.round_number - 1],
                "score": round_scores[a_round.round_number - 1]
            }
        )
    return event_data


# Helper functions for events api

# Current round should be RUNNING or PAUSED
def current_round(rounds):
    for a_round in rounds:
        status = determine_round_status(a_round)
        if status == "RUNNING" or status == "PAUSED":
            return a_round


def next_round(rounds):
    # Get round numbers of all complete rounds
    rounds_complete = []
    for a_round in rounds:
        if determine_round_status(a_round) == "FINISHED":
            rounds_complete.append(
                a_round.round_number
            )
    # If none is complete, next round is first round
    if len(rounds_complete) == 0:
        next_round_number = 1
    else:
        # Otherwise, highest finished + 1
        sorted(rounds_complete)
        next_round_number = rounds_complete[-1] + 1
    for a_round in rounds:
        if a_round.round_number == next_round_number:
            return a_round


#
# Helper functions to create event stream data
#

#
# Functions to calculate round time
#

# Calculate time and round status
def time_remaining(rounds, events):
    milliseconds_remaining = [0, 0, 0]
    status = ["", "", ""]
    # For each round
    for a_round in rounds:
        # Get the events for that round
        applicable_events = [x for x in events if x.round == a_round]
        # If the event has not started, 30000 ms
        # If the event has finished, 0 ms
        has_started = False
        has_finished = False
        for event in applicable_events:
            if event.type == "START-ROUND":
                has_started = True
            if event.type == "FINISH-ROUND":
                has_finished = True
                break
        if has_finished:
            # Record 0 and go to next round calculation
            milliseconds_remaining[a_round.round_number - 1] = 0
            status[a_round.round_number - 1] = "FINISHED"
            continue
        if not has_started:
            # Record 30000 and go to next round calculation
            milliseconds_remaining[a_round.round_number - 1] = 30000
            status[a_round.round_number - 1] = "READY"
            continue
        # Otherwise, need to do the calculation
        # Only keep time related events
        applicable_events = [
            x for x in applicable_events
            if (
                (x.type == "START-ROUND")
                or (x.type == "PAUSE-ROUND")
                or (x.type == "CONTINUE-ROUND")
                or (x.type == "FINISH-ROUND")
            )
        ]
        # The final one will set the status
        if applicable_events[-1].type == "PAUSE-ROUND":
            status[a_round.round_number - 1] = "PAUSED"
        else:
            status[a_round.round_number - 1] = "RUNNING"
        # Get the time for the round
        milliseconds_remaining[a_round.round_number - 1] = calculate_total_time(applicable_events)
    return (
        milliseconds_remaining,
        status
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


# Determine a round's status
# based on events
def determine_round_status(a_round):
    events = FightEvent.objects.filter(
        round__exact=a_round
    )
    # Only get status changing events
    applicable_events = [
        x for x in events
        if (
                (x.type == "START-ROUND")
                or (x.type == "PAUSE-ROUND")
                or (x.type == "CONTINUE-ROUND")
                or (x.type == "FINISH-ROUND")
        )
    ]
    if len(applicable_events) == 0:
        return "READY"
    elif applicable_events[-1].type == "PAUSE-ROUND":
        return "PAUSED"
    elif applicable_events[-1].type == "CONTINUE-ROUND" or applicable_events[-1].type == "START-ROUND":
        return "RUNNING"
    else:
        return "FINISHED"


#
# Functions to calculate round score
# Note we work on 'points lost'
# so the two opponents start with
# the maximum amount and get points
# subtracted when hit
#
def calculate_total_score(events):
    scores = [{}, {}, {}]
    score_events = filter_only_score_events(events)
    for i in [1, 2, 3]:
        round_score_events = filter_one_rounds_events(
            score_events,
            i
        )
        round_scores = {
            "opponent1": 5,
            "opponent2": 5
        }
        for event in round_score_events:
            value = 5
            if "HAND" in event.type:
                value = 2
            elif "HEAD" in event.type:
                value = 1
            elif "BODY" in event.type:
                value = 3
            if "OPPONENT-1" in event.type:
                round_scores["opponent1"] -= value
            elif "OPPONENT-2" in event.type:
                round_scores["opponent2"] -= value
        scores[i - 1] = round_scores
    # Impose maximum score of 5
    for opponent in ["opponent1", "opponent2"]:
        for round_scores in scores:
            if round_scores[opponent] < 0:
                round_scores[opponent] = 0
    return scores


# Take an array of FightEvents
# and return only those which
# relating to scoring
def filter_only_score_events(events):
    return [
        x for x in events
        if "HEAD" in x.type
           or "HAND" in x.type
           or "BODY" in x.type
    ]


# Take an array of FightEvents
# and return only those which
# occurred in a certain round number
def filter_one_rounds_events(events, round_number):
    return [
        x for x in events
        if x.round.round_number == round_number
    ]
