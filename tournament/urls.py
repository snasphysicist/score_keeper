
from django.urls import path

from . import views

urlpatterns = [
    path('overview', views.tournament_overview, name='tournament_overview'),
    path('api/v1/<int:id>/overview', views.overview_api, name="overview_api")
]
