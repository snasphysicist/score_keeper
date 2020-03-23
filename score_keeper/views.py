
import json
import os

from django.contrib.auth import authenticate, login, logout
from django.http import Http404
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader

from .settings import BASE_DIR


def login_page(request):
    # If user already logged in, redirect
    if request.user.is_authenticated:
        return redirect('/score_keeper/main')
    else:
        template = loader.get_template("score_keeper/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


# API to handle username/password login
def login_api(request):
    data = json.loads(
        request.body.decode('utf-8')
    )
    print(data)
    user = authenticate(
        request,
        username=data["username"],
        password=data["password"]
    )
    if user is not None:
        login(request, user)
        response_json = {
            "success": True
        }
    else:
        response_json = {
            "success": False
        }
    return JsonResponse(
        response_json
    )


# API to log user out
def logout_api(request):
    logout(request)
    return redirect('login')


def main_page(request):
    template = loader.get_template("score_keeper/main.html")
    context = {}
    return HttpResponse(template.render(context, request))


def try_static(request):
    path = request.get_full_path()
    file_path = BASE_DIR + path
    if os.path.isfile(file_path):
        the_file = open(file_path, 'rb')
        return FileResponse(the_file)
    else:
        raise Http404
