import os.path

import google_voice_takeout_parser

TEST_DATA_DIR = os.path.join("tests", "test_data")


def test_missed_call_number() -> None:
    test_file = 'Call - Missed with number.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_call = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'MISSED CALL', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Call - Missed with number.html', 'originating_name': '',
                        'originating_phone_number': '+11015550111', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Missed,Inbox',
                        'timestamp': '2022-03-15 16:52:10 -0400', 'user_deleted': False, 'media_files': [],
                        'transcript': 'N/A', 'text_message': 'N/A'}]
    assert parsed_call == expected_result


def test_missed_call_name() -> None:
    test_file = 'Call - Missed with name.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_call = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'MISSED CALL', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Call - Missed with name.html', 'originating_name': 'Joe Smith',
                        'originating_phone_number': '+11045550100', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Missed,Inbox',
                        'timestamp': '2023-05-18 21:02:28 -0400', 'user_deleted': False, 'media_files': [],
                        'transcript': 'N/A', 'text_message': 'N/A'}]
    assert parsed_call == expected_result


def test_received_call_number() -> None:
    test_file = "Call - Received with number.html"
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_call = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'INCOMING CALL', 'direction': 'INCOMING', 'duration': '(00:33:07)',
                        'filename': 'Call - Received with number.html', 'originating_name': '',
                        'originating_phone_number': '+11045550100', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Received', 'timestamp': '2024-01-16 09:59:54 -0500',
                        'user_deleted': False, 'media_files': [], 'transcript': 'N/A', 'text_message': 'N/A'}]
    assert parsed_call == expected_result


def test_received_call_name() -> None:
    test_file = 'Call - Received with name.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_call = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'INCOMING CALL', 'direction': 'INCOMING', 'duration': '(01:51:35)',
                        'filename': 'Call - Received with name.html', 'originating_name': 'Joe Smith',
                        'originating_phone_number': '+11045550100', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Received', 'timestamp': '2023-08-26 22:13:13 -0400',
                        'user_deleted': False, 'media_files': [], 'transcript': 'N/A', 'text_message': 'N/A'}]
    assert parsed_call == expected_result


def test_outgoing_call() -> None:
    test_file = 'Call - Outgoing.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_call = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'OUTGOING CALL', 'direction': 'OUTGOING', 'duration': '(00:00:04)',
                        'filename': 'Call - Outgoing.html', 'originating_name': 'Google Voice Takeout Subject',
                        'originating_phone_number': '', 'recipient_names': ['Joe Smith'],
                        'recipient_phone_numbers': ['+11025550163'], 'tags': 'Placed',
                        'timestamp': '2023-11-18 21:41:13 -0500', 'user_deleted': False, 'media_files': [],
                        'transcript': 'N/A', 'text_message': 'N/A'}]
    assert parsed_call == expected_result


def test_voicemail_with_audio() -> None:
    test_file = 'Call - Voicemail.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_call = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'VOICEMAIL', 'direction': 'INCOMING', 'duration': '(00:00:03)',
                        'filename': 'Call - Voicemail.html', 'originating_name': '',
                        'originating_phone_number': '+11025550122', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Voicemail,Inbox',
                        'timestamp': '2022-10-24 18:26:52 -0400', 'user_deleted': False,
                        'media_files': [('audio', '+11025550122 - Voicemail - 2022-10-24T22_26_52Z.mp3')],
                        'transcript': '', 'text_message': 'N/A'}]
    assert parsed_call == expected_result


def test_voicemail_with_transcript() -> None:
    test_file = 'Call - Voicemail, no name or number.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_call = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'VOICEMAIL', 'direction': 'INCOMING', 'duration': '(00:02:59)',
                        'filename': 'Call - Voicemail, no name or number.html', 'originating_name': '',
                        'originating_phone_number': '', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Voicemail,Inbox',
                        'timestamp': '2020-10-16 16:01:48 -0400', 'user_deleted': False,
                        'media_files': [('audio', ' - Voicemail - 2020-10-16T20_01_48Z.mp3')],
                        'transcript': 'Hello World Goodbye', 'text_message': 'N/A'}]
    assert parsed_call == expected_result


def test_recorded_call() -> None:
    test_file = 'Call - Recorded.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_call = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [
        {'data_type': 'RECORDED CALL', 'direction': 'UNKNOWN - LIKELY INCOMING', 'duration': '(00:01:30)',
         'filename': 'Call - Recorded.html', 'originating_name': '', 'originating_phone_number': '+11025550144',
         'recipient_names': ['Google Voice Takeout Subject'], 'recipient_phone_numbers': [''], 'tags': 'Recorded,Inbox',
         'timestamp': '2020-06-18 11:44:01 -0400', 'user_deleted': False,
         'media_files': [('audio', '+11025550144 - Recorded - 2020-06-18T15_44_01Z.mp3')], 'transcript': '',
         'text_message': 'N/A'}]
    assert parsed_call == expected_result
