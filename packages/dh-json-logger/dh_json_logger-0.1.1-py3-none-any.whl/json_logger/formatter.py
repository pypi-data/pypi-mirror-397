import logging
import json
import datetime
from typing import Any, Dict, Set, Optional

class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for log records.
    """
    
    # Default fields that are always included
    CORE_FIELDS = {
        "timestamp", "level", "name", "message", "module", 
        "filename", "funcName", "lineno"
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = '%',
        include_fields: Optional[Set[str]] = None
    ):
        """
        Initialize the formatter.
        
        :param include_fields: A set of optional fields to include in the output.
                               Options: 'process', 'processName', 'thread', 'threadName', 'taskName', 'stack_info'
                               If None, defaults to {'taskName', 'stack_info'}
        """
        super().__init__(fmt, datefmt, style)
        
        self.include_fields = include_fields if include_fields is not None else {
            'taskName', 'stack_info'
        }

    def format(self, record: logging.LogRecord) -> str:
        # 1. Start with the core log record
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "filename": record.filename,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        
        # 2. Add optional system fields based on configuration
        if 'taskName' in self.include_fields:
            log_record["taskName"] = getattr(record, "taskName", None)
            
        if 'process' in self.include_fields:
            log_record["process"] = record.process
            
        if 'processName' in self.include_fields:
            log_record["processName"] = record.processName
            
        if 'thread' in self.include_fields:
            log_record["thread"] = record.thread
            
        if 'threadName' in self.include_fields:
            log_record["threadName"] = record.threadName

        if 'stack_info' in self.include_fields and record.stack_info:
             log_record["stack_info"] = self.formatStack(record.stack_info)
        
        # 3. Handle extra fields (context)
        # We need to filter out standard LogRecord attributes to find the "extra" ones.
        # This set includes EVERYTHING standard to avoid duplication.
        standard_attributes = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
            'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process', 'message', 'asctime', 'taskName'
        }
        
        for key, value in record.__dict__.items():
            # Only add if it's NOT a standard attribute AND we haven't already added it
            if key not in standard_attributes and key not in log_record:
                log_record[key] = value

        # 4. Handle exceptions (always included if present)
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record, default=str)
