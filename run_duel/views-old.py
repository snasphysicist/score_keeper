
import datetime
import json
import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader

from run_duel.models import Duel, FightEvent, Round

CURRENT_TOURNAMENT = 3


#
# Administration pages
#








#
# Authorisation helper functions
#

# Can a user start duels?
def can_start_duels(request):
    return request.user.groups.filter(name="umpire").exists()


# Can a user decide scores?
def can_record_score(request):
    return request.user.groups.filter(name="umpire").exists()


# Can a user administer duels all powerfully?
def can_administer_duels_all(request):
    return request.user.groups.filter(name="duel_administrator").exists()
