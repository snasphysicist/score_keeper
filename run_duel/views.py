
import datetime
import json

from django.template import loader
from django.http import HttpResponse, JsonResponse

from run_duel.models import Duel, FightEvent, Round


# Render new duel page
def new_duel(request):
    template = loader.get_template('run_duel/new.html')
    context = {}
    return HttpResponse(template.render(context, request))


# Create a new duel
def new_duel_api(request):
    data = json.loads(
        request.body.decode('utf-8')
    )
    if (
        'opponent1' not in data.keys()
        or 'opponent2' not in data.keys()
    ):
        return JsonResponse({
            "success": False,
            "reason": "Required key missing from json request"
        })
    if (
        len(data['opponent1']) == 0
        or len(data['opponent2']) == 0
    ):
        return JsonResponse({
            "success": False,
            "reason": "The opponents' names cannot be empty"
        })
    # Ensure no other duels are current
    old_duels = list(
        Duel.objects.filter(current__exact=True)
    )
    for old_duel in old_duels:
        old_duel.current = False
        old_duel.save()
    new_duel_object = Duel(
        opponent1=data['opponent1'],
        opponent2=data['opponent2'],
        current=True   # This is now current duel
    )
    new_duel_object.save()
    # Also need to create three rounds in this duel
    for i in [1, 2, 3]:
        next_round = Round(
            duel=new_duel_object,
            round_number=i
        )
        next_round.save()
    return JsonResponse({
        "success": True
    })


# Render current duel page
def current_duel(request):
    template = loader.get_template('run_duel/current.html')
    context = {}
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
    event = FightEvent(
        time=datetime.datetime.now(),
        type=data['type']
    )
    if event.save():
        return JsonResponse({
            "success": True
        })
    else:
        return JsonResponse({
            "success": False,
            "reason": "Invalid event type"
        })


# Event stream api
def event_stream(request):
    current_duel_object = Duel.objects.filter(
        current__exact=True
    )[0]
    rounds = list(
        Round.objects.filter(
            duel__exact=current_duel_object
        )
    )
    # Get all events for current duel
    # current_duel_events = FightEvent.objects.filter(
    #     round__exact=current_round.id
    # )
    # TODO assemble into useful json format
    event_data = {
        "duel": {
            "duel_id": current_duel_object.id,
            "opponent1": current_duel_object.opponent1,
            "opponent2": current_duel_object.opponent2
        },
        "rounds": []
    }
    for round in rounds:
        event_data["rounds"].append(
            {
                "round_id": round.id,
                "round_number": round.round_number,
                "status": round.status
            }
        )
    # TODO add latest event
    return JsonResponse(event_data)
