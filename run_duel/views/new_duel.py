
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader

from .shared import can_start_duels


# Render new duel page
def handle(request):
    if not can_start_duels(request):
        return redirect('/score_keeper/login')
    template = loader.get_template('run_duel/new.html')
    context = {}
    return HttpResponse(template.render(context, request))