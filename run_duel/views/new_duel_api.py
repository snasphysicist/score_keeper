
import json

from django.http import JsonResponse

from run_duel.models import Duel
from .shared import can_start_duels


# Move on to a different duel
def handle(request):
    if not can_start_duels(request):
        return JsonResponse(
            {
                "success": False,
                "reason": "You do not have permission to perform this operation"
            }
        )
    data = json.loads(
        request.body.decode('utf-8')
    )
    # Basically, just make the selected
    # duel the current one
    duel = Duel.by_id(
        None,
        data["id"]
    )
    if duel is None:
        return JsonResponse(
            {
                "success": False,
                "reason": "The selected duel does not appear to exist"
            }
        )
    # For any other duel marked
    # as current, make it not so
    old_duels = Duel.marked_as_current(None)
    for old_duel in old_duels:
        old_duel.current = False
        old_duel.save()
    duel.current = True
    duel.save()
    return JsonResponse({
        "success": True
    })
