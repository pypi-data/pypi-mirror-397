# wmul_rivendell_tcp_client

A TCP client module to connect to Rivendell Radio Automation and receive Now Playing information. Intended to be run as
a module inside your code. A CLI is provided for testing purposes.

Connects to the Rivendell PAD TCP port, usually on 34289. See 15.1.1. The JSON Interface in the Rivendell Operations
Guide.

## CLI Operation

`.venv\Scripts\wmul_now_playing.exe [Rivendell IP Address] 34289 --log_name "E:\Temp\rivendell_tcp_client.log"`

The CLI will print the Start Time, Duration (rounded to full seconds), Artist, and Title as each song is received from
Rivendell.

## Module Operation

```Python
import click
import multiprocessing
import wmul_logger
from wmul_rivendell_tcp_client import receiver

_logger = wmul_logger.get_logger()
logging_queue = multiprocessing.Queue()
stop_logger = wmul_logger.run_queue_listener_logger(
    logging_queue=logging_queue,
    file_name=log_name,
    log_level=log_level
)
_logger = wmul_logger.get_queue_handler_logger(logging_queue=logging_queue)

quit_event = multiprocessing.Event()
song_queue = multiprocessing.SimpleQueue()
if host and port:
    dss = receiver.DeviceServerSettings(
        host=host,
        port=port
    )
    tcp_process = multiprocessing.Process(
        target=receiver.connect_to_rivendell_tcp,
        name="Rivendell TCP Client",
        kwargs={
            "device_server_settings": dss,
            "quit_event": quit_event,
            "song_queue": song_queue,
            "loggging_queue": logging_queue
        },
        daemon=True
    )
    tcp_process.start()

## Here's where your code consumes the songs from song_queue. 
```
