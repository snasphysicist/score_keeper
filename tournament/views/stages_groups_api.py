
from django.http import JsonResponse

from tournament.models import Tournament


def handle(request, **kwargs):
    # Get tournament from id in url
    tournament_id = kwargs["id"]
    tournament = Tournament.by_id(
        None,
        tournament_id
    )
    # Assemble data into format front end expects
    stagesgroups = {"stages": []}
    # Get stages and groups for stages
    stages = tournament.all_stages()
    for stage in stages:
        current_stage = {
            "stage": stage.dictionary(),
            "group": []
        }
        groups = stage.all_groups()
        for group in groups:
            current_stage["groups"].append(
                group.dictionary()
            )
        stagesgroups["stages"].append(
            current_stage
        )
    stagesgroups["success"] = True
    return JsonResponse(stagesgroups)
