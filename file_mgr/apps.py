# Python base imports - Default ones
import logging

# Dependent software imports
from django.apps import AppConfig

# Custom created imports

class FileMgrConfig(AppConfig):
    name = "file_mgr"

    def ready(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"{self.name} Initializing Started")
