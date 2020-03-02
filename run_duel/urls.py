from django.urls import path

from . import views

urlpatterns = [
    path('new', views.new_duel, name='new_duel'),
    path('api/v1/new_duel', views.new_duel_api, name='new_duel_api')
]
