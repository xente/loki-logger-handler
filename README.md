# loki_logger_handler

A logging handler that sends log messages to Loki in JSON format

## Features

* Logs pushed in JSON format
* Custom labels definition
* Allows defining loguru and logger extra keys as labels
* Logger extra keys added automatically as keys into pushed JSON
* Publish in batch of Streams
* Publis logs compressed

## Args

* url (str): The URL of the Loki server.
* labels (dict): A dictionary of labels to attach to each log message.
* labelKeys (dict, optional): A dictionary of keys to extract from each log message and use as labels. Defaults to None.
* timeout (int, optional): The time in seconds to wait before flushing the buffer. Defaults to 10.
* compressed (bool, optional): Whether to compress the log messages before sending them to Loki. Defaults to True.
* defaultFormatter (logging.Formatter, optional): The formatter to use for log messages. Defaults to LoggerFormatter().

## Formatters
* LoggerFormatter: Formater for default python logging implementation
* LoguruFormatter: Formater for Loguru python library

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
    labels={"application": "Test", "envornment": "Develop"},
    labelKeys={},
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
    labels={"application": "Test", "envornment": "Develop"},
    labelKeys={},
    timeout=10,
    defaultFormatter=LoguruFormatter(),
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
 {envornment="Develop"} |= `` | json
 ```

Filter by level:

```
{envornment="Develop", level="INFO"} |= `` | json
```
Filter by extra:

```
{envornment="Develop", level="INFO"} |= `` | json | code=`200`
```

## License
The MIT License