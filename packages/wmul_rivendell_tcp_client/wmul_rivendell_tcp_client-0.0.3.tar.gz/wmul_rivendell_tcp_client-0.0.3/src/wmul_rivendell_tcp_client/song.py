"""
@Author = 'Mike Stanley'

Data classes to describe a played song from Rivendell. Method to parse a string into a _Song class.

============ Change Log ============
2018-Jul-24 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2018, 2021, 2025 Michael Stanley

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
import datetime
import json
from dataclasses import dataclass
import wmul_logger

_logger = wmul_logger.get_logger()


@dataclass
class Song:
    artist: str
    title: str
    duration: datetime.timedelta
    actual_start_time: datetime.datetime

    def __str__(self):
        return f"A: {self.actual_start_time}\t\tDuration: {self.duration}\t\tArtist: {self.artist:<30} Title: {self.title:<30}"

    @classmethod
    def parse_song_from_rivendell_json(cls, rivendell_json: str):
        _logger.info(f"Received: {rivendell_json}")
        rivendell_json = cls._remove_extra_updates(rivendell_json)
        try:
            rivendell_json_parsed = json.loads(rivendell_json)
            now = rivendell_json_parsed["padUpdate"]["now"]
            return cls._parse_song_from_now(now)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            _logger.debug(error)
            return None

    @classmethod
    def _parse_song_from_now(cls, now: dict):
        actual_start_time = now["startDateTime"]
        title = now["title"]
        artist = now["artist"]
        duration = now["length"]
        song_duration = cls._get_duration_rounded(duration)

        song = cls(
            actual_start_time=actual_start_time,
            title=title,
            artist=artist,
            duration=song_duration,
        )
        _logger.info(song)
        return song

    @classmethod
    def _get_duration_rounded(cls, duration) -> datetime.timedelta:
        try:
            duration = round(int(duration) / 1000, 0)
            return datetime.timedelta(
                seconds=duration
            )
        except ValueError:
            return datetime.timedelta(seconds = 10)
    
    @classmethod
    def _remove_extra_updates(cls, rivendell_json):
        count_of_updates = rivendell_json.count("padUpdate")
        if count_of_updates > 1:
            index_of_final_padUpdate = rivendell_json.rfind("padUpdate") # Find the final padUpdate in the string
            index_of_open_brace_before_final_padUpdate = rivendell_json.rfind("{", 0, index_of_final_padUpdate) # Find the opening curly brace that starts the final padUpdate.
            rivendell_json = rivendell_json[index_of_open_brace_before_final_padUpdate:] # Extract just the final padUpdate.
        return rivendell_json
