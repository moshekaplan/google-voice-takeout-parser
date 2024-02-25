import re
import google_voice_takeout_parser


def test_version() -> None:
    assert isinstance(google_voice_takeout_parser.__version__, str)
    assert re.match(r"^[0-9][0-9\.]*[0-9]$", google_voice_takeout_parser.__version__)
