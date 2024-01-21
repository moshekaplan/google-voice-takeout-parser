import re

import google-voice-takeout-parser


def test_version() -> None:
    assert isinstance(google-voice-takeout-parser.__version__, str)
    assert re.match(r"^[0-9][0-9\.]*[0-9]$", google-voice-takeout-parser.__version__)
