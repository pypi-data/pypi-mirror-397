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
from datetime import timedelta
from wmul_rivendell_tcp_client.song import Song


def test_no_milliseconds():
    test_duration = "1000000"
    expected_duration = timedelta(minutes=16, seconds=40)

    result = Song._get_duration_rounded(test_duration)
    assert result == expected_duration


def test_rounded_down_milliseconds():
    test_duration = "1000499"
    expected_duration = timedelta(minutes=16, seconds=40)

    result = Song._get_duration_rounded(test_duration)
    assert result == expected_duration


def test_rounded_up_milliseconds():
    test_duration = "1001500"
    expected_duration = timedelta(minutes=16, seconds=42)

    result = Song._get_duration_rounded(test_duration)
    assert result == expected_duration


def test_not_an_int():
    test_duration = "foo"
    expected_duration = timedelta(seconds=10)

    result = Song._get_duration_rounded(test_duration)
    assert result == expected_duration
