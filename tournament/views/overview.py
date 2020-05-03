
from django.http import HttpResponse
from django.template import loader

CURRENT_TOURNAMENT = 3


# Tournament overview page
def handle(request):
    template = loader.get_template('tournament/overview.html')
    context = {
        "current_tournament": CURRENT_TOURNAMENT
    }
    return HttpResponse(
        template.render(
            context,
            request
        )
    )
