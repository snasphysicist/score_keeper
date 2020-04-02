
from io import StringIO
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


# Will pre-load static
# files on first call
# Store here
# Like a manual cache
STATIC_LOADED = False
STATIC = None


def try_static(request):
    # Set up cache on first call
    if STATIC is None:
        load_static()
    path = request.get_full_path()
    # Path should be of format
    # /<module>/folders/filename
    # Ditch module bit
    path = "/".join(
        path.split("/")[1:]
    )
    print("Seeking path: ", path)
    # Try to get page content from 'cache'
    if path in list(STATIC):
        return FileResponse(
            STATIC[path]["content"].getvalue(),
            content_type=STATIC[path]["type"]
        )
    else:
        raise Http404


def load_static():
    global STATIC
    STATIC = {}
    static_paths = []
    # Find all files in static folders
    for root_directory, directories, files in os.walk(BASE_DIR):
        for file in files:
            if "/static/" in os.path.join(
                root_directory,
                file
            ):
                static_paths.append(
                    os.path.join(
                        root_directory,
                        file
                    )
                )
    # Load file content for each
    for path in static_paths:
        print("Adding file: ", path)
        # Path is everything 'south' of /static/
        uri_path = path.split("/static/")[-1]
        print("At uri: ", uri_path)
        with open(path, 'r') as file:
            content = file.read()
        file_like_content = StringIO()
        file_like_content.write(
            content
        )
        STATIC[uri_path] = {
            "content": file_like_content,
            "type": guess_type(path)
        }


def guess_type(path):
    if ".css" in path:
        return "text/css"
    if ".js" in path:
        return "text/javascript"
    if ".html" in path:
        return "text/html"
    return "text/plain"
