# JSON Logger

A robust, production-ready JSON logging library for Python. This library makes it easy to output logs in JSON format, which is essential for modern observability stacks (ELK, Datadog, CloudWatch, etc.).

## Installation

```bash
pip install json_logger
```

## Usage

### Basic Usage

```python
import logging
import sys
from json_logger import JSONFormatter

# Setup logger
logger = logging.getLogger("my_app")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Log something
logger.info("Application started", extra={"user_id": 42})
```

**Output:**
```json
{"timestamp": "2023-10-27 10:00:00,123", "level": "INFO", "name": "my_app", "message": "Application started", "module": "test", "filename": "test.py", "funcName": "<module>", "lineno": 10, "user_id": 42}
```

### Advanced Configuration

You can configure which system fields to include in the JSON output:

```python
# Include process and thread information
formatter = JSONFormatter(include_fields={"process", "thread", "taskName"})

# The default includes 'taskName' and 'stack_info'
```

## Features

- **JSON Output**: Properly formatted JSON for all log records.
- **Extra Fields**: Automatically merges `extra={...}` dictionary into the top-level JSON object.
- **Exception Handling**: Formats exceptions and stack traces into the `exception` field.
- **System Info**: Optional support for `process`, `thread`, `taskName`, and `stack_info`.
- **Robustness**: Handles non-serializable objects gracefully by converting them to strings.
- **Unicode Support**: Correctly handles emojis and special characters.

## Contributing

We welcome contributions! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/amazing-feature`).
3.  Install development dependencies:
    ```bash
    pip install -e .[dev]
    ```
4.  Run tests to ensure everything is working:
    ```bash
    pytest
    ```
5.  Commit your changes.
6.  Push to the branch.
7.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
