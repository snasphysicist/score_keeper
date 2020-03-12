
from django.urls import path

from . import views

urlpatterns = [
    path('new', views.new_duel, name='new_duel'),
    path('api/v1/new_duel', views.new_duel_api, name='new_duel_api'),
    path('api/v1/pending_duels', views.pending_duel_api, name='pending_duel_api'),
    path('current', views.current_duel, name='current_duel'),
    path('api/v1/event', views.new_event_api, name='new_event_api'),
    path('api/v1/event_stream', views.event_stream, name='event_stream'),
    # Administration urls
    path('administration/delete_duel', views.delete_duel_page, name="delete_duel"),
    path('api/v1/<int:id>/duel/list', views.get_all_duels_api, name="get_all_duels_api"),
    path('api/v1/duel/delete', views.delete_duel_api, name="delete_duel_api"),
    path('administration/reset_duel', views.reset_duel_page, name="reset_duel"),
    path('api/v1/duel/reset', views.reset_duel_api, name="reset_duel_api")
]
