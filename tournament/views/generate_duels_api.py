
import json

from django.http import JsonResponse

from run_duel.models import Duel, Round
from .shared import can_administer_duels
from tournament.models import Group, Participant


def handle(request):
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