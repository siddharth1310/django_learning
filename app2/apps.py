# app2/apps.py - NO DATABASE ACCESS!
from django.apps import AppConfig
import logging

class App2Config(AppConfig):
    name = "app2"
    
    def ready(self):
        """✅ NO DB → NO WARNING!"""
        logger = logging.getLogger(__name__)
        logger.info("🎛️ App2 ready - SecurityConfigManager auto-initializes on first use")
        # Lazy loading handles everything!
