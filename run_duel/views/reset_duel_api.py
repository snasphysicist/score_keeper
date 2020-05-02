
import json

from django.http import JsonResponse

from run_duel.models import Duel
from .shared import can_administer_duels_all


def handle(request):
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
