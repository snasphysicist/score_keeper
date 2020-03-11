
import json

from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.template import loader


def login_page(request):
    template = loader.get_template("score_keeper/login.html")
    context = {}
    return HttpResponse(template.render(context, request))


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

