
import datetime
import json

from django.http import JsonResponse

from run_duel.models import FightEvent, Round
from .shared import can_administer_duels_all, can_record_score


def handle(request):
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