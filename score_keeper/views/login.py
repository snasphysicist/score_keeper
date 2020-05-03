
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader


def handle(request):
    # If user already logged in, redirect
    if request.user.is_authenticated:
        return redirect('/score_keeper/main')
    else:
        template = loader.get_template("score_keeper/login.html")
        context = {}
        return HttpResponse(
            template.render(
                context,
                request
            )
        )
