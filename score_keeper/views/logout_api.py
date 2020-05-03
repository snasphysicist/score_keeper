
from django.contrib.auth import logout
from django.shortcuts import redirect


# API to log user out
def handle(request):
    logout(request)
    return redirect('login')
