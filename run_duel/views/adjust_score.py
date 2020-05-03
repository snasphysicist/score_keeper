
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from .shared import can_administer_duels_all, can_record_score


def handle(request):
    if not (can_administer_duels_all(request) or can_record_score(request)):
        return redirect('/score_keeper/login')
    template = loader.get_template('run_duel/administration/adjust_score.html')
    context = {}
    return HttpResponse(
        template.render(
            context,
            request
        )
    )
