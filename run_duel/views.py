
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
    new_duel_object = Duel(
        opponent_1=data['opponent1'],
        opponent_2=data['opponent2'],
        current=True   # This is now current duel
    )
    new_duel_object.save()
    # Also need to create three rounds in this duel

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
    )
    current_round = Round.objects.filter(
        duel__exact=current_duel_object.id
    ).exclude(
        status__exact='FINISHED'
    ).exclude(
        status__exact='NOT STARTED'
    )
    # Get all events for current duel
    current_duel_events = FightEvent.objects.filter(
        round__exact=current_round.id
    )
    # TODO assemble into useful json format
    # TODO add latest event
    return JsonResponse({

    })
