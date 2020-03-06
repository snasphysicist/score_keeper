
from django.http import HttpResponse
from django.template import loader


# Tournament overview page
def tournament_overview(request):
    template = loader.get_template('tournament/overview.html')
    context = {}
    return HttpResponse(template.render(context, request))
