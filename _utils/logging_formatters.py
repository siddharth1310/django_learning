# Python base imports - Default ones
from logging import Formatter
from json import dumps as json_dumps

# Dependent software imports

# Custom created imports

# ------------------------------------------------------------
# Custom JSON Line Formatter
# ------------------------------------------------------------
# Purpose:
#   Converts a LogRecord into a JSON string.
#
# Why custom?
#   - Full control over JSON structure
#   - Easy extension with extra fields
#   - Consistent structured logging format
#
# Output format:
#   One JSON object per line (JSONL format).
# ------------------------------------------------------------

class JSON_LINE_FORMATTER(Formatter):
    """
    Formats log records into structured JSON objects.

    Each log entry contains:
    - timestamp
    - level
    - message
    - thread/process info
    - logger metadata (module, function, line)
    """
    def format(self, record):
        # Construct structured log dictionary
        log_obj = {
            "timestamp" : self.formatTime(record, self.datefmt), 
            "level" : record.levelname, 
            "message" : record.getMessage(), 
            "thread" : record.threadName, 
            "process" : record.processName, 
            "logger" : record.name, 
            "module" : record.module, 
            "function" : record.funcName, 
            "line" : record.lineno
        }

        # ----------------------------------------------------
        # Support for structured extra fields
        #
        # Example usage:
        # logger.info("User created", extra={"additional_data": {"user_id": 123}})
        #
        # These fields get merged into final JSON output.
        # ----------------------------------------------------
        if hasattr(record, "additional_data"):
            log_obj.update(record.additional_data) # type: ignore
        
        # Convert dictionary to JSON string
        return json_dumps(log_obj)