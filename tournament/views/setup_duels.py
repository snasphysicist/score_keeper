
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from .shared import can_administer_duels


def handle(request):
    if not can_administer_duels(request):
        return redirect('/score_keeper/login')
    template = loader.get_template('tournament/setup_duels.html')
    context = {}
    return HttpResponse(
        template.render(
            context,
            request
        )
    )
