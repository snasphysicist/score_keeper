
from django.http import HttpResponse, JsonResponse
from django.template import loader

from run_duel.models import Duel
from run_duel.views import calculate_duel_data
from tournament.models import Group, Stage, Tournament


# Tournament overview page
def tournament_overview(request):
    template = loader.get_template('tournament/overview.html')
    context = {}
    return HttpResponse(template.render(context, request))


def overview_api(request, **kwargs):
    # Get tournament from id in url
    tournament_id = kwargs["id"]
    tournament = list(
        Tournament.objects.filter(id__exact=tournament_id)
    )[0]
    # Get duels for this tournament
    # via Stages then Groups
    # Get stages
    stages = list(
        Stage.objects.filter(tournament__exact=tournament)
    )
    # Get groups
    groups = list()
    for stage in stages:
        groups += list(
            Group.objects.filter(stage__exact=stage)
        )
    # Get duels
    duels = list()
    for group in groups:
        duels += list(
            Duel.objects.filter(group__exact=group)
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
        for a_round in duel_data_raw["rounds"]:
            total_score["opponent1"] += a_round["score"]["opponent1"]
            total_score["opponent2"] += a_round["score"]["opponent2"]
        duel_data_processed["opponent1"] = duel_data_raw["duel"]["opponent1"]
        duel_data_processed["opponent2"] = duel_data_raw["duel"]["opponent2"]
        duel_data_processed["score1"] = total_score["opponent1"]
        duel_data_processed["score2"] = total_score["opponent2"]
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
        participant["completed"] = len(participant_duels)
        # participant["remaining"] = 15 * len(participant_duels)
        for duel in participant_duels:
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
