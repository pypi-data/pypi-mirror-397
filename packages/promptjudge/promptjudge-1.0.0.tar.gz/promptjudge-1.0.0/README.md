# PromptJudge Python SDK

[![PyPI version](https://badge.fury.io/py/promptjudge.svg)](https://badge.fury.io/py/promptjudge)
[![Python Versions](https://img.shields.io/pypi/pyversions/promptjudge.svg)](https://pypi.org/project/promptjudge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for the [PromptJudge](https://promptjudge.com) AI Security API. Protect your AI applications from prompt injection attacks and malicious inputs.

## Installation

```bash
pip install promptjudge
```

## Quick Start

```python
from promptjudge import PromptJudge

# Initialize the client with your API key
client = PromptJudge(api_key="your-api-key")

# Scan a prompt for security issues
result = client.scan("What is the weather today?")

if result.safe:
    print("✅ Prompt is safe to process")
else:
    print(f"⚠️ Warning: {result.reason}")
```

## Features

- 🔒 **Prompt Injection Detection** - Identify and block malicious prompt injection attempts
- ⚡ **Fast & Reliable** - Low-latency API responses with high availability
- 🐍 **Pythonic API** - Clean, intuitive interface following Python best practices
- 🔧 **Error Handling** - Comprehensive exception classes for robust error handling
- 📦 **Zero Dependencies** - Only requires the `requests` library

## Usage

### Basic Usage

```python
from promptjudge import PromptJudge

client = PromptJudge(api_key="your-api-key")
result = client.scan("Hello, how are you?")

print(result.safe)    # True or False
print(result.reason)  # Explanation string
```

### Using Context Manager

```python
from promptjudge import PromptJudge

with PromptJudge(api_key="your-api-key") as client:
    result = client.scan("Tell me a joke")
    print(result.to_dict())
```

### Quick Scan Function

For one-off scans without creating a client instance:

```python
from promptjudge import scan

result = scan(api_key="your-api-key", prompt_text="What is 2+2?")
print(result.safe)
```

### Custom Configuration

```python
from promptjudge import PromptJudge

client = PromptJudge(
    api_key="your-api-key",
    base_url="https://custom-api.promptjudge.com",  # Optional custom endpoint
    timeout=60  # Custom timeout in seconds
)
```

## Error Handling

The SDK provides specific exception classes for different error types:

```python
from promptjudge import (
    PromptJudge,
    PromptJudgeError,
    AuthenticationError,
    NetworkError,
    APIError
)

client = PromptJudge(api_key="your-api-key")

try:
    result = client.scan("Test prompt")
except AuthenticationError as e:
    print(f"Invalid API key: {e}")
except NetworkError as e:
    print(f"Network issue: {e}")
except APIError as e:
    print(f"API error (status {e.status_code}): {e}")
except PromptJudgeError as e:
    print(f"General error: {e}")
```

## Response Object

The `scan()` method returns a `ScanResult` object with the following properties:

| Property | Type | Description |
|----------|------|-------------|
| `safe` | `bool` | Whether the prompt is safe to process |
| `reason` | `str` | Explanation of the safety assessment |

### Methods

- `to_dict()` - Convert the result to a dictionary

## API Reference

### PromptJudge Class

#### Constructor

```python
PromptJudge(
    api_key: str,                    # Required: Your API key
    base_url: str = None,            # Optional: Custom API base URL
    timeout: int = 30                # Optional: Request timeout in seconds
)
```

#### Methods

| Method | Description |
|--------|-------------|
| `scan(prompt_text: str)` | Scan a prompt and return a `ScanResult` |
| `close()` | Close the HTTP session |

## Requirements

- Python 3.7+
- `requests` library

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📚 [Documentation](https://docs.promptjudge.com)
- 🐛 [Issue Tracker](https://github.com/promptjudge/promptjudge-python/issues)
- 📧 [Email Support](mailto:support@promptjudge.com)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
