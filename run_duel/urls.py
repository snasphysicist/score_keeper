
from django.urls import path

from . import views

urlpatterns = [
    path('new', views.new_duel, name='new_duel'),
    path('api/v1/new_duel', views.new_duel_api, name='new_duel_api'),
    path('current', views.current_duel, name='current_duel'),
    path('api/v1/event', views.new_event_api, name='new_event_api'),
    path('api/v1/event_stream', views.event_stream, name='event_stream'),
]
