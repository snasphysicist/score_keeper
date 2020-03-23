
import datetime
import json

from django.http import JsonResponse
from django.db import IntegrityError

from run_duel.models import Duel
from run_duel.models import FightEvent

from .shared import *


# Event recording api
def handle(request):
    if not can_record_score(request):
        return JsonResponse({
            "success": False,
            "reason": "You do not have permission to perform this operation"
        })
    data = json.loads(
        request.body.decode('utf-8')
    )
    if 'type' not in data.keys():
        return JsonResponse({
            "success": False,
            "reason": "Required key missing from json request"
        })
    # Get the rounds for the current match
    this_duel = Duel.current_duel()
    if this_duel is None:
        return JsonResponse({
            "success": False,
            "reason": "No duel is currently active"
        })
    # Get the round for this event
    # Will depend upon event type
    if data['type'].upper() == "START-ROUND":
        # For start, want next round
        the_round = this_duel.next_round()
    else:
        # For everything else, current round
        the_round = this_duel.current_round()
    if the_round is None:
        return JsonResponse({
            "success": False,
            "reason": "Could not determine round to which to apply event"
        })
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
