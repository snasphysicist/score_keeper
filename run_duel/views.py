
import datetime
import json
import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader

from run_duel.models import Duel, FightEvent, Round

from .views.get_all_duels_api import handle as get_all_duels_api_handler
from .views.new_event_api import handle as new_event_api_handler
from .views.pending_duel_api import handle as pending_duel_api_handler

CURRENT_TOURNAMENT = 3


# Render new duel page
def new_duel(request):
    if not can_start_duels(request):
        return redirect('/score_keeper/login')
    template = loader.get_template('run_duel/new.html')
    context = {}
    return HttpResponse(template.render(context, request))


# Move on to a different duel
def new_duel_api(request):
    if not can_start_duels(request):
        return JsonResponse(
            {
                "success": False,
                "reason": "You do not have permission to perform this operation"
            }
        )
    data = json.loads(
        request.body.decode('utf-8')
    )
    # Basically, just make the selected
    # duel the current one
    duel = list(Duel.objects.filter(id__exact=data["id"]))[0]
    # All other duels not current
    old_duels = list(Duel.objects.filter(current__exact=True))
    for old_duel in old_duels:
        old_duel.current = False
        old_duel.save()
    duel.current = True
    duel.save()
    return JsonResponse({
        "success": True
    })


# List pending duels
def pending_duel_api(request):
    return pending_duel_api_handler(request)


# Render current duel page
def current_duel(request):
    template = loader.get_template('run_duel/current.html')
    context = {
        "websocket_protocol": os.environ["SCORE_KEEPER_WEBSOCKET_PROTOCOL"],
        "base_url": os.environ["SCORE_KEEPER_BASE_URL"],
        "websocket_port": os.environ["SCORE_KEEPER_WEBSOCKET_PORT"],
        # Only enable scoring for umpires
        "can_record_score": can_record_score(request)
    }
    return HttpResponse(template.render(context, request))


# Event recording api
def new_event_api(request):
    return new_event_api_handler(request)


# Event stream api
def event_stream(request):
    current_duel_object = Duel.current_duel()
    if current_duel_object is None:
        return JsonResponse({})
    return JsonResponse(
        current_duel_object.with_round_data()
    )


#
# Administration pages
#

def delete_duel_page(request):
    if not can_administer_duels_all(request):
        return redirect('/score_keeper/login')
    template = loader.get_template('run_duel/administration/delete_duel.html')
    context = {}
    return HttpResponse(template.render(context, request))


def get_all_duels_api(request, **kwargs):
    tournament_id = kwargs["id"]
    return get_all_duels_api_handler(tournament_id)


def delete_duel_api(request):
    if not can_administer_duels_all(request):
        return JsonResponse(
            {
                "success": False,
                "reason": "You do not have permission to perform this operation"
            }
        )
    data = json.loads(
        request.body.decode("utf-8")
    )
    duel_id = data["duelid"]
    duels = list(Duel.objects.filter(id__exact=duel_id))
    if len(duels) == 0:
        result = {
            "success": False,
            "reason": "Could not find duel with provided identifier"
        }
    else:
        duels[0].delete()
        result = {"success": True}
    return JsonResponse(result)


def reset_duel_page(request):
    if not can_administer_duels_all(request):
        return redirect('/score_keeper/login')
    template = loader.get_template('run_duel/administration/reset_duel.html')
    context = {}
    return HttpResponse(template.render(context, request))


def reset_duel_api(request):
    if not can_administer_duels_all(request):
        return JsonResponse(
            {
                "success": False,
                "reason": "You do not have permission to perform this operation"
            }
        )
    data = json.loads(
        request.body.decode("utf-8")
    )
    duel_id = data["duelid"]
    duels = list(Duel.objects.filter(id__exact=duel_id))
    if len(duels) == 0:
        result = {
            "success": False,
            "reason": "Could not find duel with provided identifier"
        }
    else:
        delete_all_events(duels[0])
        result = {"success": True}
    return JsonResponse(result)


def delete_all_events(duel):
    events = get_all_events(duel)
    for event in events:
        event.delete()


def get_all_events(duel):
    rounds = list(Round.objects.filter(duel__exact=duel))
    events = list()
    for a_round in rounds:
        events += list(FightEvent.objects.filter(round__exact=a_round))
    return events


def adjust_score_page(request):
    if not (can_administer_duels_all(request) or can_record_score(request)):
        return redirect('/score_keeper/login')
    template = loader.get_template('run_duel/administration/adjust_score.html')
    context = {}
    return HttpResponse(template.render(context, request))


def adjust_score_api(request):
    if not (can_administer_duels_all(request) or can_record_score(request)):
        return JsonResponse(
            {
                "success": False,
                "reason": "You do not have permission to perform this operation"
            }
        )
    data = json.loads(
        request.body.decode("utf-8")
    )
    print(data)
    the_round = list(Round.objects.filter(id__exact=data["roundid"]))
    if len(the_round) == 0:
        return JsonResponse(
            {
                "success": False,
                "reason": "Could not find specified round"
            }
        )
    the_round = the_round[0]
    adjustment_type = ""
    if data["opponent"] == 1:
        adjustment_type = "OPPONENT-1-ADJUST-"
    elif data["opponent"] == 2:
        adjustment_type = "OPPONENT-2-ADJUST-"
    else:
        return JsonResponse(
            {
                "success": False,
                "reason": "Opponent must be 1 or 2"
            }
        )
    if data["action"] == "UP":
        adjustment_type += "UP"
    elif data["action"] == "DOWN":
        adjustment_type += "DOWN"
    else:
        return JsonResponse(
            {
                "success": False,
                "reason": "Adjustment must be UP or DOWN"
            }
        )
    adjustment = FightEvent(
        time=datetime.datetime.now(),
        type=adjustment_type,
        round=the_round
    )
    adjustment.save()
    return JsonResponse(
        {
            "success": True
        }
    )


def single_duel_data_api(request, **kwargs):
    duel_id = kwargs["id"]
    duel = Duel. by_id(duel_id)
    if duel is None:
        return JsonResponse(
            {
                "success": False,
                "reason": "Could not find duel with provided id"
            }
        )
    data = duel.with_round_data()
    data["success"] = True
    return JsonResponse(data)


#
# Authorisation helper functions
#

# Can a user start duels?
def can_start_duels(request):
    return request.user.groups.filter(name="umpire").exists()


# Can a user decide scores?
def can_record_score(request):
    return request.user.groups.filter(name="umpire").exists()


# Can a user administer duels all powerfully?
def can_administer_duels_all(request):
    return request.user.groups.filter(name="duel_administrator").exists()
