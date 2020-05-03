
from django.http import JsonResponse

from tournament.models import Tournament
from .shared import can_administer_duels

CURRENT_TOURNAMENT = 3


def handle(request):
    if not can_administer_duels(request):
        return JsonResponse({
            "success": False,
            "reason": "You do not have permission to perform this operation"
        })
    # Get group and participant details
    tournament = Tournament.by_id(
        None,
        CURRENT_TOURNAMENT
    )
    if tournament is None:
        return JsonResponse({
            "success": False,
            "reason": "There appears to be no currently active tournament"
        })
    stages = tournament.all_stages()
    groups = list()
    current_stage = None
    for stage in stages:
        groups += stage.all_groups()
        duels = list()
        for group in groups:
            duels += group.all_duels()
        if len(duels) == 0:
            current_stage = stage
            break
    participants = tournament.all_participants()
    context = {
        "stage": current_stage.dictionary(),
        "groups": [],
        "participants": []
    }
    for group in groups:
        context["groups"].append(
            group.dictionary()
        )
    for participant in participants:
        context["participants"].append(
            participant.dictionary()
        )
    context["success"] = True
    return JsonResponse(context)
