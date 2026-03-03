# Python base imports - Default ones
import logging
from os import path
from logging.handlers import RotatingFileHandler

# Dependent software imports

# Custom created imports



# ------------------------------------------------------------
# Dynamic App Routing Logging Handler
# ------------------------------------------------------------
# Purpose:
#   Automatically route logs to per-app JSONL files.
#
# Example:
#   logger name: app1.views
#   → file: logs/app1.jsonl
#
# Design Goals:
#   - Avoid repetitive logger config in settings
#   - Automatically support new apps
#   - Maintain central logging simultaneously
#   - Prevent duplicate handler creation
# ------------------------------------------------------------
class AppFileRoutingHandler(logging.Handler):
    """
    Routes logs dynamically to app-specific JSONL files.

    Mechanism:
    - Extract top-level namespace from logger name
      (app1.views → app1)
    - Create rotating file handler if not already created
    - Reuse handler for future logs
    """

    def __init__(self, base_log_dir, max_bytes = 5 * 1024 * 1024, backup_count = 5):
        super().__init__()
        
        # Base directory where log files will be stored
        self.base_log_dir = base_log_dir

        # Rotation configuration
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Dictionary to cache per-app handlers
        # Prevents:
        # - Recreating handlers repeatedly
        # - File descriptor leaks
        self.handlers = {}

    def emit(self, record):
        """
        Called automatically for each log record.

        Steps:
        1. Extract app name from logger namespace
        2. Create handler if first time seeing this app
        3. Emit record to appropriate file
        """
        PROJECT_APPS = {"app1", "app2", "_utils"}  # or import from settings
        # Extract top-level logger name
        # Example:
        #   app1.views → app1
        logger_name = record.name.split(".")[0]
        if logger_name not in PROJECT_APPS:
            return  # ignore non-project logs

        file_path = path.join(self.base_log_dir, f"{logger_name}.jsonl")

        # If handler not already created for this app
        if logger_name not in self.handlers:
            handler = RotatingFileHandler(file_path, 
                                          maxBytes = self.max_bytes, 
                                          backupCount = self.backup_count, 
                                          encoding = "utf-8")

            # Reuse same formatter defined in settings
            handler.setFormatter(self.formatter)

            # Cache handler for reuse
            self.handlers[logger_name] = handler
        
        # Emit record to the correct app file
        self.handlers[logger_name].emit(record)
