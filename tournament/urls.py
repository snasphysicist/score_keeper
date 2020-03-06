from django.urls import path

from . import views

urlpatterns = [
    path('overview', views.tournament_overview, name='tournament_overview'),
]
