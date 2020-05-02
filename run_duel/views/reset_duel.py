
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from .shared import can_administer_duels_all


def handle(request):
    if not can_administer_duels_all(request):
        return redirect('/score_keeper/login')
    template = loader.get_template('run_duel/administration/reset_duel.html')
    context = {}
    return HttpResponse(
        template.render(
            context,
            request
        )
    )
