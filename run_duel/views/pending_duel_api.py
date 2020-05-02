
from django.http import JsonResponse

from .shared import *


def handle(request):
    if not can_start_duels(request):
        return JsonResponse(
            {
                "success": False,
                "reason": "You do not have permission to perform this operation"
            }
        )
    # Get duel information as JSON
    all_duels = tournament_all_duels(CURRENT_TOURNAMENT)
    unfinished_duels = remove_finished_duels(all_duels)
    unfinished_duels["success"] = True
    return JsonResponse(
        unfinished_duels
    )
