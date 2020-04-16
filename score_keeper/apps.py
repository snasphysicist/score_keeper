
from django.apps import AppConfig

from .score_keeper_websocket import get_websocket_thread


class WebsocketAppConfig(AppConfig):
    name = "score_keeper"
    
    def ready(self):
        websocket_thread = get_websocket_thread()
        websocket_thread.start()
