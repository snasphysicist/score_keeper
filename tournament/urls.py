
from django.urls import path

from . import views

urlpatterns = [
    path('overview', views.overview, name='overview'),
    path('api/v1/<int:id>/overview', views.overview_api, name="overview_api"),
    path('setup_duels', views.setup_duels, name="setup_duels"),
    path('api/v1/setup_duels', views.setup_duels_groups_participants_api, name="set_duels_api"),
    path('api/v1/confirm_duels', views.generate_duels_api, name="generate_duels_api"),
    path('api/v1/<int:id>/stagesgroups', views.stages_groups_api, name="stagesgroups_api")
]
