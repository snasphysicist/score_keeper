
from django.http import JsonResponse

from run_duel.models import Duel


# Event stream api
def handle(request):
    current_duel_object = Duel.current_duel(None)
    if current_duel_object is None:
        return JsonResponse({})
    return JsonResponse(
        current_duel_object.with_round_data()
    )
