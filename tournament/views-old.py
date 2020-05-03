
from functools import reduce
import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader

from run_duel.models import Duel, Round
from tournament.models import Group, Participant, Tournament

