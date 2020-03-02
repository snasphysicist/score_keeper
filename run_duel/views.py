from django.template import loader
from django.http import HttpResponse

# Create your views here.
def new_duel(request):
    template = loader.get_template('run_duel/new.html')
    context = {}
    return HttpResponse(template.render(context, request))

