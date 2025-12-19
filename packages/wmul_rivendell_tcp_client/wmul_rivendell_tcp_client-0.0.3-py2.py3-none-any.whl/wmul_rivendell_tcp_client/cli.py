"""
@Author = 'Mike Stanley'

Describe this file.

============ Change Log ============
2021-Dec-07 = Created.

============ License ============
MIT License

Copyright (c) 2021, 2025 Mike Stanley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import click
import multiprocessing
import signal
import sys
import wmul_logger
from wmul_rivendell_tcp_client import receiver

_logger = wmul_logger.get_logger()


@click.command()
@click.argument("host", type=str)
@click.argument("port", type=int)
@click.option('--log_name', type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True),
              default=None,required=False, help="The path to the log file for the printer process.")
@click.option('--log_level', type=click.IntRange(10,50, clamp=True), required=False, default=30,
              help="The log level: 10: Debug, 20: Info, 30: Warning, 40: Error, 50: Critical. "
                   "Intermediate values (E.G. 32) are permitted, but will essentially be rounded up (E.G. Entering 32 "
                   "is the same as entering 40. Logging messages lower than the log level will not be written to the "
                   "log. E.G. If 30 is input, then all Debug, Info, and Verbose messages will be silenced.")
def wmul_rivendell_tcp_client_cli(host, port, log_name, log_level):
    global _logger
    logging_queue = multiprocessing.Queue()
    stop_logger = wmul_logger.run_queue_listener_logger(
        logging_queue=logging_queue,
        file_name=log_name,
        log_level=log_level
    )
    _logger = wmul_logger.get_queue_handler_logger(logging_queue=logging_queue)

    _logger.debug("In command_line_interface")

    quit_event = multiprocessing.Event()

    def sigint_handler(signum, frame):
        quit_event.set()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    dss = Receiver.DeviceServerSettings(
        host=host,
        port=port
    )

    song_queue = multiprocessing.SimpleQueue()

    tcp_process = multiprocessing.Process(
        target=Receiver.connect_to_rivendell_tcp,
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

    print("Started. Waiting on first input.")
    while not quit_event.is_set():
        next_song = song_queue.get()
        print(next_song)

    stop_logger()
