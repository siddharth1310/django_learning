from django.apps import AppConfig
import logging

class App2Config(AppConfig):
    name = "app2"

    def ready(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"{self.name} Initializing Started")
