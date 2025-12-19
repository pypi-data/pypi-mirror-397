import logging
import json
import time
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for structured logging.
    Compatible with SIEM tools (Splunk, ELK, Datadog).
    """
    def format(self, record):
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        
        # Merge extra fields if present
        if hasattr(record, "props"):
            log_obj.update(record.props)
            
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)

def setup_logger(name: str) -> logging.Logger:
    """
    Configures a professional logger with JSON formatting.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers if called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
    return logger

def log_audit(logger: logging.Logger, action: str, details: dict):
    """
    Helper for Security Audit Logs.
    """
    extra = {
        "props": {
            "event_type": "SECURITY_AUDIT",
            "action": action,
            **details
        }
    }
    logger.info(action, extra=extra)
