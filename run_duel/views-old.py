
import datetime
import json
import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader

from run_duel.models import Duel, FightEvent, Round

CURRENT_TOURNAMENT = 3


#
# Administration pages
#

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
    duel_id = data["id"]
    duel = Duel.by_id(
        None,
        duel_id
    )
    if duel is None:
        result = {
            "success": False,
            "reason": "Could not find duel with provided identifier"
        }
    else:
        duel.delete_all_events()
        result = {"success": True}
    return JsonResponse(result)


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
    the_round = Round.by_id(
        None,
        data["roundid"]
    )
    if the_round is None:
        return JsonResponse(
            {
                "success": False,
                "reason": "Could not find specified round"
            }
        )
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
    duel = Duel.by_id(duel_id)
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
