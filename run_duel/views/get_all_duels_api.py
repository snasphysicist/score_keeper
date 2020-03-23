
from django.http import JsonResponse

from .shared import tournament_all_duels


def handle(tournament_id):
    duels = tournament_all_duels(tournament_id)
    duels["success"] = True
    return JsonResponse(duels)
