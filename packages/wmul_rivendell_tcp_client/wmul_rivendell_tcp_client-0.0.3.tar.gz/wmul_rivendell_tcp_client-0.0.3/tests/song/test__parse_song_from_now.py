"""
@Author = 'Mike Stanley'

============ Change Log ============
2025-Dec-18 = Created.

============ License ============
The MIT License (MIT)

Copyright (c) 2025 Michael Stanley

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
from datetime import datetime, timedelta, timezone
from wmul_rivendell_tcp_client.song import Song


def test_regular():
    now_dict = {
        "agency": "",
        "album": "",
        "artist": "Lorem ipsum",
        "cartNumber": 119587,
        "cartType": "Audio",
        "client": "dolor sit",
        "composer": "",
        "conductor": "",
        "cutNumber": 1,
        "description": "amet consectetur ",
        "eventType": "Audio",
        "externalAnncType": "",
        "externalData": "",
        "externalEventId": "",
        "groupName": "adipiscing ",
        "isci": "",
        "isrc": "",
        "label": "",
        "length": 211332,
        "lineId": 310,
        "lineNumber": 309,
        "outcue": "",
        "publisher": "",
        "recordingMbId": "",
        "releaseMbId": "",
        "songId": "",
        "startDateTime": "2025-12-18T11:19:12-05:00",
        "title": "Pretium tellus",
        "userDefined": "",
        "year": None
    }

    result = Song._parse_song_from_now(now=now_dict)

    expected_duration = timedelta(minutes = 3, seconds = 31)

    assert result.artist == now_dict["artist"]
    assert result.title == now_dict["title"]
    assert result.duration == expected_duration
    assert result.actual_start_time == now_dict["startDateTime"]
