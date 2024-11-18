# loki_logger_handler

[![PyPI](https://img.shields.io/pypi/v/loki_logger_handler?color=blue&label=pypi%20version)]()
[![PyPI](https://img.shields.io/pypi/pyversions/loki_logger_handler.svg)]()
[![Downloads](https://pepy.tech/badge/loki_logger_handler)](https://pepy.tech/project/loki_logger_handler)

A logging handler that sends log messages to **(Grafana) Loki** in JSON format.

## Features

* Logs pushed in JSON format by default
* Custom labels definition
* Allows defining *loguru* and *logger* extra keys as labels
* Logger extra keys added automatically as keys into pushed JSON
* Publish in batch of Streams
* Publish logs compressed

## Args

* url (str): The URL of the Loki server.
* labels (dict): A dictionary of labels to attach to each log message.
* label_keys (dict, optional): A dictionary of keys to extract from each log message and use as labels. Defaults to None.
* additional_headers (dict, optional): Additional headers for the Loki request. Defaults to None.
* timeout (int, optional): Timeout interval in seconds to wait before flushing the buffer. Defaults to 10 seconds.
* compressed (bool, optional): Whether to compress the log messages before sending them to Loki. Defaults to True.
* loguru (bool, optional): Whether to use `LoguruFormatter`. Defaults to False.
* default_formatter (logging.Formatter, optional): Formatter for the log records. If not provided,`LoggerFormatter` or `LoguruFormatter` will be used.

## Formatters
* **LoggerFormatter**: Formatter for default python logging implementation
* **LoguruFormatter**: Formatter for Loguru python library

## How to use 

### Logger
```python
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler,
import logging
import os 

# Set up logging
logger = logging.getLogger("custom_logger")
logger.setLevel(logging.DEBUG)

# Create an instance of the custom handler
custom_handler = LokiLoggerHandler(
    url=os.environ["LOKI_URL"],
    labels={"application": "Test", "environment": "Develop"},
    label_keys={},
    timeout=10,
)
# Create an instance of the custom handler

logger.addHandler(custom_handler)
logger.debug("Debug message", extra={'custom_field': 'custom_value'})
```


### Loguru

```python
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler, LoguruFormatter
from loguru import logger
import os 

os.environ["LOKI_URL"]="https://USER:PASSWORD@logs-prod-eu-west-0.grafana.net/loki/api/v1/push"

custom_handler = LokiLoggerHandler(
    url=os.environ["LOKI_URL"],
    labels={"application": "Test", "environment": "Develop"},
    label_keys={},
    timeout=10,
    default_formatter=LoguruFormatter(),
)
logger.configure(handlers=[{"sink": custom_handler, "serialize": True}])

logger.info(
    "Response code {code} HTTP/1.1 GET {url}", code=200, url="https://loki_handler.io"
)
```

## Loki messages samples

### Without extra

```json
{
  "message": "Starting service",
  "timestamp": 1681638266.542849,
  "process": 48906,
  "thread": 140704422327936,
  "function": "run",
  "module": "test",
  "name": "__main__"
}

```

### With extra

```json
{
  "message": "Response code  200 HTTP/1.1 GET https://loki_handler.io",
  "timestamp": 1681638225.877143,
  "process": 48870,
  "thread": 140704422327936,
  "function": "run",
  "module": "test",
  "name": "__main__",
  "code": 200,
  "url": "https://loki_handler.io"
}
```

### Exceptions

```json
{
  "message": "name 'plan' is not defined",
  "timestamp": 1681638284.358464,
  "process": 48906,
  "thread": 140704422327936,
  "function": "run",
  "module": "test",
  "name": "__main__",
  "file": "test.py",
  "path": "/test.py",
  "line": 39
}
```

## Loki Query Sample

Loki query sample :

 ```
 {environment="Develop"} |= `` | json
 ```

Filter by level:

```
{environment="Develop", level="INFO"} |= `` | json
```
Filter by extra:

```
{environment="Develop", level="INFO"} |= `` | json | code=`200`
```

## **Development Environment: Dev Container**

This project uses a **Dev Container** to provide a consistent and reproducible development environment. A Dev Container ensures all team members have the same tools, dependencies, and configurations, avoiding "works on my machine" issues.

---

### **Why Use a Dev Container?**

- **Consistency**: Ensures everyone works in the same environment, regardless of the host OS.
- **Isolation**: Keeps project dependencies separate from your system.
- **Portability**: Easily onboard new developers by setting up the environment with a single command.
- **Pre-configured Tools**: Includes all required tools and dependencies for the project.

---

### **Getting Started with the Dev Container**

To start working with the Dev Container, follow these steps:

#### **Prerequisites**
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop) (required for running containers).
2. Install [Visual Studio Code (VS Code)](https://code.visualstudio.com/).
3. Install the **Dev Containers** extension in VS Code:
   - Go to Extensions (`Ctrl+Shift+X` / `Cmd+Shift+X`) and search for `Dev Containers`.
   - Install the extension by Microsoft.

#### **Setup Instructions**
1. Clone the repository
2. Open in VS Code
3. Open the Command Palette (Ctrl+Shift+P / Cmd+Shift+P) and select: **Dev Containers: Reopen in Container**

- VS Code will:
  - Pull the Dev Container image. 
  - Install all dependencies and tools specified.


#### Resources

The loki_logger_handler Dev Container provides the following resources:

- Grafana: Accessible externally at http://localhost:3000.
- Loki: Accessible internally at http://loki:3100/loki/api/v1/push.
You can use this URL in your code as the publish endpoint for logs.
Logs can be viewed and queried via the Grafana interface.

```
os.environ["LOKI_URL"]=http://loki:3100/loki/api/v1/push
````

## License
The MIT License