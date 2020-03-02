from django.template import loader

# Create your views here.
def new_duel(request):
    template = loader.get_template('run_duel/new_duel.html')
    context = {}
    return HttpResponse(template.render(context, request))

