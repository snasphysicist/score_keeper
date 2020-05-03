
import os

from django.http import HttpResponse
from django.template import loader

from .shared import can_record_score


# Render current duel page
def handle(request):
    template = loader.get_template('run_duel/current.html')
    context = {
        "websocket_protocol": os.environ["SCORE_KEEPER_WEBSOCKET_PROTOCOL"],
        "base_url": os.environ["SCORE_KEEPER_BASE_URL"],
        "websocket_port": os.environ["SCORE_KEEPER_WEBSOCKET_PORT"],
        # Only enable scoring for umpires
        "can_record_score": can_record_score(request)
    }
    return HttpResponse(template.render(context, request))