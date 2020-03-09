
from django.urls import path

from . import views

urlpatterns = [
    path('overview', views.tournament_overview, name='tournament_overview'),
    path('api/v1/<int:id>/overview', views.overview_api, name="overview_api"),
    path('setup_duels', views.setup_duels, name="setup_duels"),
    path('api/v1/setup_duels', views.setup_duels_groups_participants_api, name="set_duels_api"),
]
