import logging
import json
import pytest
from datetime import datetime
from json_logger import JSONFormatter

@pytest.fixture
def logger():
    log = logging.getLogger("test_logger")
    log.setLevel(logging.INFO)
    return log

@pytest.fixture
def formatter():
    return JSONFormatter()

def test_log_output_is_valid_json(formatter):
    """
    Verify that the formatter outputs valid JSON with expected fields.
    """
    record = logging.LogRecord(
        name="test_json",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Hello world",
        args=(),
        exc_info=None
    )
    
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    assert data["message"] == "Hello world"
    assert "timestamp" in data
    assert data["level"] == "INFO"

def test_log_with_extra_fields(formatter):
    """
    Verify that 'extra' fields are merged into the top-level JSON object.
    """
    record = logging.LogRecord(
        name="test_json",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Payment processed",
        args=(),
        exc_info=None
    )
    # Simulate adding extra fields like logger.info(..., extra={"user_id": 123})
    record.user_id = 123
    record.currency = "USD"
    
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    assert data["message"] == "Payment processed"
    assert data["user_id"] == 123
    assert data["currency"] == "USD"

def test_log_exception(formatter):
    """
    Verify that exceptions are captured and formatted properly.
    """
    try:
        raise ValueError("Something went wrong")
    except ValueError:
        import sys
        exc_info = sys.exc_info()
    
    record = logging.LogRecord(
        name="test_json",
        level=logging.ERROR,
        pathname=__file__,
        lineno=10,
        msg="Operation failed",
        args=(),
        exc_info=exc_info
    )
    
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    assert data["message"] == "Operation failed"
    assert "exception" in data
    assert "ValueError: Something went wrong" in data["exception"]

def test_log_serialization_fallback(formatter):
    """
    Verify that non-serializable objects (like sets) don't crash the logger
    and are converted to strings instead.
    """
    record = logging.LogRecord(
        name="test_json",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Complex object",
        args=(),
        exc_info=None
    )
    # Sets are not JSON serializable by default
    record.tags = {"tag1", "tag2"} 
    
    # This should not raise an exception
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    # Our default=str fallback in json.dumps should handle this
    # The string representation of a set looks like "{'tag1', 'tag2'}" (order varies)
    assert "tag1" in data["tags"]

def test_unicode_characters(formatter):
    """
    Verify that Unicode characters are handled correctly.
    """
    msg = "Hello 🌍, 안녕하세요"
    record = logging.LogRecord(
        name="test_json",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg=msg,
        args=(),
        exc_info=None
    )
    record.custom_field = "🔥"
    
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    assert data["message"] == msg
    assert data["custom_field"] == "🔥"

def test_message_formatting_args(formatter):
    """
    Verify that old-style % formatting in messages works.
    """
    record = logging.LogRecord(
        name="test_json",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Hello %s",
        args=("User",),
        exc_info=None
    )
    
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    assert data["message"] == "Hello User"

def test_attempt_to_overwrite_reserved_fields(formatter):
    """
    Verify that extra fields cannot overwrite standard reserved fields.
    """
    record = logging.LogRecord(
        name="test_json",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Original Message",
        args=(),
        exc_info=None
    )
    # Attempt to overwrite 'message' and 'level'
    record.message = "Overwritten Message" 
    record.level = "CRITICAL" 
    
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    # The formatter code sets 'message' from record.getMessage()
    assert data["message"] == "Original Message"
    # The formatter code sets 'level' from record.levelname
    assert data["level"] == "INFO"

def test_custom_object_serialization(formatter):
    """
    Test serialization of a custom object that implements __str__.
    """
    class User:
        def __init__(self, uid, name):
            self.uid = uid
            self.name = name
        
        def __str__(self):
            return f"User(id={self.uid})"

    user = User(1, "Alice")
    record = logging.LogRecord(
        name="test_json",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="User login",
        args=(),
        exc_info=None
    )
    record.user = user
    
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    assert data["user"] == "User(id=1)"

def test_datetime_serialization(formatter):
    """
    Test that datetime objects in extra fields are serialized (as strings).
    """
    now = datetime(2023, 1, 1, 12, 0, 0)
    record = logging.LogRecord(
        name="test_json",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Time check",
        args=(),
        exc_info=None
    )
    record.event_time = now
    
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    assert str(now) in data["event_time"]

def test_stack_info(formatter):
    """
    Verify that stack_info is included in the JSON output when available.
    """
    record = logging.LogRecord(
        name="test_json",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Debug info",
        args=(),
        exc_info=None,
        sinfo="Stack trace string..."
    )
    
    # stack_info is included by default now
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    assert "stack_info" in data
    assert data["stack_info"] == "Stack trace string..."

def test_process_and_thread_info_configured():
    """
    Verify that process and thread information is included only when configured.
    """
    formatter = JSONFormatter(include_fields={"process", "thread"})
    
    record = logging.LogRecord(
        name="test_json",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="System info",
        args=(),
        exc_info=None
    )
    # Mocking process and thread info which LogRecord captures automatically
    record.process = 12345
    record.thread = 67890
    
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    assert data["process"] == 12345
    assert data["thread"] == 67890

def test_process_and_thread_info_not_included_by_default():
    """
    Verify that process and thread information is NOT included by default.
    """
    formatter = JSONFormatter() # Default settings
    
    record = logging.LogRecord(
        name="test_json",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="System info",
        args=(),
        exc_info=None
    )
    record.process = 12345
    
    formatted_output = formatter.format(record)
    data = json.loads(formatted_output)
    
    assert "process" not in data
