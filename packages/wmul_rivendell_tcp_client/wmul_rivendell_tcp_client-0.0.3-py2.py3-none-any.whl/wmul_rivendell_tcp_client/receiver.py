"""
@Author = 'Mike Stanley'

Client to receive now playing information from Rivendell, parse it into a Song object, and add the new song to a queue.

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
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, create_connection, timeout
import wmul_logger
import time
from dataclasses import dataclass
from wmul_rivendell_tcp_client.song import Song

_logger = wmul_logger.get_logger()


@dataclass
class DeviceServerSettings:
    host: str
    port: int

    @property
    def host_port(self):
        return self.host, self.port


class _SocketManager:

    def __init__(self, device_server_settings, byte_limit=2048):
        self._device_server_settings = device_server_settings
        self._socket = None

    def create_connection(self):
        if self._socket:
            self.close()
        _logger.debug("Beginning to create connection.")
        this_socket = create_connection(self._device_server_settings.host_port)
        self._socket = this_socket

    def close(self):
        _logger.debug("Closing connection.")
        if self._socket:
            self._socket.shutdown(SHUT_RDWR)
            self._socket.close()
            self._socket = None

    def get_song(self):
        timeouts = 0
        while timeouts < 10:
            try:
                raw_song = self._socket.recv(4096)
                _logger.info(f'Received From Rivendell: {raw_song}')
                string_song = bytes.decode(raw_song)
                return string_song
            except timeout:
                _logger.debug("Socket timed out. Restarting.")
                self.restart_connection()
        _logger.debug("Socket still times out after 10 retries.")
        self.close()
        raise RuntimeError("Socket still times out after 10 retries.")

    def restart_connection(self):
        self.close()
        time.sleep(10)
        self.create_connection()


def connect_to_rivendell_tcp(device_server_settings, quit_event, song_queue, loggging_queue):
    global _logger
    _logger = wmul_logger.get_queue_handler_logger(logging_queue=loggging_queue)
    try:
        sm = _SocketManager(device_server_settings=device_server_settings)
        _logger.debug("SocketManager initted")
        sm.create_connection()
        _logger.debug("SocketManager connection created")
        _logger.debug("Beginning Loop")
        while not quit_event.is_set():
            try:    
                raw_song = sm.get_song()
            except RuntimeError:
                quit_event.set()
                return
            if raw_song and (len(raw_song) > 4):
                song = Song.parse_song_from_rivendell_json(rivendell_json=raw_song)
                _logger.debug("Got Song!")
                song_queue.put(song)
        _logger.debug("Quit Event tripped.")
    except Exception as e:
        _logger.error(e)
        raise
