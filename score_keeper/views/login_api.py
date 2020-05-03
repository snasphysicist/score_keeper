
import json

from django.contrib.auth import authenticate, login
from django.http import JsonResponse


# API to handle username/password login
def handle(request):
    data = json.loads(
        request.body.decode('utf-8')
    )
    user = authenticate(
        request,
        username=data["username"],
        password=data["password"]
    )
    if user is not None:
        login(
            request,
            user
        )
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

