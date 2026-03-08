# Python base imports - Default ones
import logging

# Dependent software imports
from django.apps import AppConfig

# Custom created imports

class App1Config(AppConfig):
    name = "app1"

    def ready(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"{self.name} Initializing Started")

