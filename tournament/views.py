
import json

from django.http import HttpResponse, JsonResponse
from django.template import loader

from run_duel.models import Duel, Round
from run_duel.views import calculate_duel_data
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
    group = list(
        Group.objects.filter(id__exact=group_id)
    )[0]
    # Get duels
    duels = list(
        Duel.objects.filter(group__exact=group_id)
    )
    # Get data for all duels
    # and calculate overall scores
    duels_processed = []
    for duel in duels:
        duel_data_raw = calculate_duel_data(duel)
        duel_data_processed = {}
        total_score = {
            "opponent1": 0,
            "opponent2": 0
        }
        # Also check if duel complete
        is_finished = True
        for a_round in duel_data_raw["rounds"]:
            total_score["opponent1"] += a_round["score"]["opponent1"]
            total_score["opponent2"] += a_round["score"]["opponent2"]
            if a_round["status"] != "FINISHED":
                is_finished = False
        duel_data_processed["opponent1"] = duel_data_raw["duel"]["opponent1"]
        duel_data_processed["opponent2"] = duel_data_raw["duel"]["opponent2"]
        duel_data_processed["score1"] = total_score["opponent1"]
        duel_data_processed["score2"] = total_score["opponent2"]
        duel_data_processed["finished"] = is_finished
        duels_processed.append(duel_data_processed)
    # Have the duels
    # Work out the participants
    participants = []
    participant_names = set(
        [x["opponent1"] for x in duels_processed]
        + [x["opponent2"] for x in duels_processed]
    )
    for name in participant_names:
        participant = {
            "name": name,
            "completed": 0,
            "remaining": 0
        }
        participant_duels = [
            x for x in duels_processed
            if x["opponent1"] == name
            or x["opponent2"] == name
        ]
        for duel in participant_duels:
            # Only count duels that have finished
            if not duel["finished"]:
                continue
            participant["completed"] += 1
            if duel["opponent1"] == name:
                participant["remaining"] += duel["score1"]
            else:
                participant["remaining"] += duel["score2"]
        participants.append(participant)
    return JsonResponse({
        "duels": duels_processed,
        "participants": participants,
        "success": True
    })


def setup_duels(request):
    if not can_administer_duels(request):
        return JsonResponse({
            "success": False,
            "reason": "You do not have permission to perform this operation"
        })
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
    stages = list(Stage.objects.filter(tournament__exact=tournament))
    groups = list()
    current_stage = None
    for stage in stages:
        groups += list(Group.objects.filter(stage__exact=stage))
        duels = list()
        for group in groups:
            duels += list(Duel.objects.filter(group__exact=group))
        if len(duels) == 0:
            current_stage = stage
            break
    participants = list(Participant.objects.filter(tournaments=tournament))
    context = {}
    context["currentstage"] = {
        "id": current_stage.id,
        "number": current_stage.number
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
    tournament = list(
        Tournament.objects.filter(id__exact=tournament_id)
    )[0]
    # Assemble data into format front end expects
    stagesgroups = {
        "stages": [],
    }
    # Get stages and groups for stages
    stages = list(
        Stage.objects.filter(tournament__exact=tournament)
    )
    for stage in stages:
        current_stage = {
            "id": stage.id,
            "number": stage.number,
            "groups": []
        }
        groups = list(
            Group.objects.filter(stage__exact=stage)
        )
        for group in groups:
            current_stage["groups"].append(
                {
                    "id": group.id,
                    "number": group.number
                }
            )
        stagesgroups["stages"].append(
            current_stage
        )
    stagesgroups["success"] = True
    return JsonResponse(stagesgroups)


# Can a user start duels?
def can_administer_duels(request):
    return request.user.groups.filter(name="duel_administrators").exists()
