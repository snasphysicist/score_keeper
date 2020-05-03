
from functools import reduce

from django.http import JsonResponse

from tournament.models import Group


def handle(request, **kwargs):
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
    response_data["participants"] = participants
    response_data["success"] = True
    return JsonResponse(response_data)
