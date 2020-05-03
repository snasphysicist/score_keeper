
from functools import reduce
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader

from run_duel.models import Duel, Round
from tournament.models import Group, Participant, Tournament





def setup_duels(request):
    if not can_administer_duels(request):
        return redirect('/score_keeper/login')
    template = loader.get_template('tournament/setup_duels.html')
    context = {}
    return HttpResponse(template.render(context, request))


def setup_duels_groups_participants_api(request):
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


def generate_duels_api(request):
    if not can_administer_duels(request):
        return JsonResponse({
            "success": False,
            "reason": "You do not have permission to perform this operation"
        })
    data = json.loads(
        request.body.decode('utf-8')
    )
    for duel in data:
        # Find group
        group = Group.by_id(
            None,
            duel["group"]["id"]
        )
        opponent1 = Participant.by_id(duel["opponent1"]["id"])
        opponent2 = Participant.by_id(duel["opponent2"]["id"])
        next_duel = Duel(
            sequence_number=(data.index(duel) + 1),
            group=group,
            opponent1=opponent1,
            opponent2=opponent2,
            current=False
        )
        next_duel.save()
        # Each duel also needs three rounds
        for i in [1, 2, 3]:
            next_round = Round(
                round_number=i,
                duel=next_duel
            )
            next_round.save()
    return JsonResponse(
        {
            "success": True
        }
    )


def stages_groups_api(request, **kwargs):
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


# Can a user start duels?
def can_administer_duels(request):
    return request.user.groups.filter(name="duel_administrator").exists()
