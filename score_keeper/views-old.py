
from io import StringIO
import json
import os

from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader

from .settings import BASE_DIR

