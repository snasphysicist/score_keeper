
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
    duel_id = data["duelid"]
    duels = list(
        Duel.objects.filter(
            id__exact=duel_id
        )
    )
    if len(duels) == 0:
        result = {
            "success": False,
            "reason": "Could not find duel with provided identifier"
        }
    else:
        duels[0].delete()
        result = {"success": True}
    return JsonResponse(result)
