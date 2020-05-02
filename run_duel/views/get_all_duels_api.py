
from django.http import JsonResponse

from .shared import tournament_all_duels


def handle(request, **kwargs):
    if "id" not in kwargs.keys():
        return JsonResponse(
            {
                "success": False,
                "reason": "No tournament exists with the provided identifier"
            }
        )
    duels = tournament_all_duels(kwargs["id"])
    duels["success"] = True
    return JsonResponse(duels)
