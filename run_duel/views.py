
import json

from django.template import loader
from django.http import HttpResponse, JsonResponse

from run_duel.models import Duel

# Render new duel page
def new_duel(request):
    template = loader.get_template('run_duel/new.html')
    context = {}
    return HttpResponse(template.render(context, request))

# Create a new duel
def new_duel_api(request):
    data = json.loads(
        request.body.decode('utf-8')
    )
    if (
        'opponent1' not in data.keys()
        or 'opponent2' not in data.keys()
    ):
        return JsonResponse({
            "success": False,
            "reason": "Required key missing from json request"
        })
    if (
        len(data['opponent1']) == 0
        or len(data['opponent2']) == 0
    ):
        return JsonResponse({
            "success": False,
            "reason": "The opponents' names cannot be empty"
        })
    new_duel = Duel(
        opponent_1=data['opponent1'],
        opponent_2=data['opponent2']
    )
    new_duel.save()
    return JsonResponse({
        "success": True
    })
