
import os

from django.apps import AppConfig

from .score_keeper_websocket import start_websocket_thread


class WebsocketAppConfig(AppConfig):
    name = "score_keeper"
    
    def ready(self):
        # We only want to start the websocket in the actual
        # main Django process, not the reload process
        if os.environ.get("RUN_MAIN") is not None:
            WebsocketAppConfig.websocket_server_started = True
            start_websocket_thread()
