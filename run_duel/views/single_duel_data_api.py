
from django.http import JsonResponse

from run_duel.models import Duel


def handle(request, **kwargs):
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