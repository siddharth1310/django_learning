from django.apps import AppConfig
import logging

class App1Config(AppConfig):
    name = "app1"

    def ready(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"{self.name} Initializing Started")

