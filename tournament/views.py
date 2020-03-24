
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader

from run_duel.models import Duel, Round
from tournament.models import Group, Participant, Stage, Tournament

CURRENT_TOURNAMENT = 3


# Tournament overview page
def tournament_overview(request):
    template = loader.get_template('tournament/overview.html')
    context = {
        "current_tournament": CURRENT_TOURNAMENT
    }
    return HttpResponse(template.render(context, request))


def overview_api(request, **kwargs):
    # Group id comes from url
    group_id = kwargs["id"]
    group = Group.by_id(
        None,
        group_id
    )
    if group is None:
        return JsonResponse({
            "success": False,
            "reason": "Could not find group with this identifier"
        })
    # Get duels
    duels = group.all_duels()
    # Start assembling response object
    response_data = {
        "group": group.dictionary(),
        "duels": []
    }
    for duel in duels:
        response_data["duels"].append(
            duel.with_round_data()
        )
    # Have the duels
    # Work out the participants
    participants = set(
        [x["opponent1"] for x in duels]
        + [x["opponent2"] for x in duels]
    )
    # Cast to dictionaries
    participants = map(
        lambda p: p.dictionary(),
        participants
    )
    for participant in participants:
        duel_scores = (
                [
                    d["score"]["opponent1"] for d in duels
                    if d["opponent1"]["id"] == participant["id"]
                    and d["status"] == "FINISHED"
                ] +
                [
                    d["score"]["opponent2"] for d in duels
                    if d["opponent2"]["id"] == participant["id"]
                    and d["status"] == "FINISHED"
                ]
        )
        participant["remaining"] = reduce(
            lambda s1, s2: s1 + s2,
            duel_scores
        )
        participant["completed"] = len(duel_scores)
    return JsonResponse({
        "duels": duels_processed,
        "participants": participants,
        "success": True
    })


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
    tournament = list(Tournament.objects.all())[0]
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
    context = {}
    context["currentstage"] = {
        "id": current_stage.id,
        "number": current_stage.number,
        "format": current_stage.stage_format
    }
    context["groups"] = []
    for group in groups:
        context["groups"].append(
            {
                "id": group.id,
                "number": group.number,
                "index": len(context["groups"]),
                "members": [],
                "duels": []
            }
        )
    context["participants"] = []
    for participant in participants:
        context["participants"].append(
            {
                "id": participant.id,
                "battlename": participant.battle_name
            }
        )
    context["allduels"] = []
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
        group = list(Group.objects.filter(id__exact=duel["group"]))[0]
        opponent1 = list(Participant.objects.filter(id__exact=duel["opponent1"]["participantid"]))[0]
        opponent2 = list(Participant.objects.filter(id__exact=duel["opponent2"]["participantid"]))[0]
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
