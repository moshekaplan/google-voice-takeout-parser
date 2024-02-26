import os.path
import google_voice_takeout_parser


TEST_DATA_DIR = os.path.join("tests", "test_data")


# Untested possibilities:
# Embedded audio
# Outgoing to a phone number, with no name stored, and no response.


def test_incoming_message() -> None:
    test_file = 'Text - Incoming, no name, no response.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_text = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'TEXT_MESSAGE', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Text - Incoming, no name, no response.html',
                        'originating_name': '', 'originating_phone_number': '54321',
                        'recipient_names': ['Google Voice Takeout Subject'], 'recipient_phone_numbers': [''],
                        'tags': 'Text,Inbox', 'timestamp': '2024-01-01 13:28:39 -0500',
                        'user_deleted': False, 'media_files': [], 'transcript': 'N/A', 'text_message': 'Hello'}]
    assert parsed_text == expected_result


def test_outgoing_message() -> None:
    test_file = 'Text - Outbound with name, no response.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_text = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'TEXT_MESSAGE', 'direction': 'OUTGOING', 'duration': 'N/A',
                        'filename': 'Text - Outbound with name, no response.html', 'originating_name': 'Me',
                        'originating_phone_number': '+11085550161', 'recipient_names': ['Anonymous Smith'],
                        'recipient_phone_numbers': [''], 'tags': 'Text', 'timestamp': '2023-01-19 17:45:15 -0500',
                        'user_deleted': False, 'media_files': [], 'transcript': 'N/A',
                        'text_message': 'Good afternoon.'}]
    assert parsed_text == expected_result


def test_outbound_with_name() -> None:
    test_file = 'Text - Outbound with name, yes response.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_text = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'TEXT_MESSAGE', 'direction': 'OUTGOING', 'duration': 'N/A',
                        'filename': 'Text - Outbound with name, yes response.html', 'originating_name': 'Me',
                        'originating_phone_number': '+11035550133', 'recipient_names': ['Joe Smith'],
                        'recipient_phone_numbers': ['+11025550122'], 'tags': 'Text,Inbox',
                        'timestamp': '2023-06-30 16:48:03 -0400', 'user_deleted': False, 'media_files': [],
                        'transcript': 'N/A', 'text_message': 'Good afternoon.'},
                       {'data_type': 'TEXT_MESSAGE', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Text - Outbound with name, yes response.html', 'originating_name': 'Joe Smith',
                        'originating_phone_number': '+11025550122', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Text,Inbox', 'timestamp': '2023-06-30 22:56:27 -0400',
                        'user_deleted': False, 'media_files': [], 'transcript': 'N/A', 'text_message': 'hello'}]
    assert parsed_text == expected_result


def test_outgoing_conversation() -> None:
    test_file = "Text - outgoing conversation.html"
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_text = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'TEXT_MESSAGE', 'direction': 'OUTGOING', 'duration': 'N/A',
                        'filename': 'Text - outgoing conversation.html', 'originating_name': 'Me',
                        'originating_phone_number': '+11015550111', 'recipient_names': [''],
                        'recipient_phone_numbers': ['+11025550122'], 'tags': 'Text,Inbox',
                        'timestamp': '2023-08-26 21:57:02 -0400', 'user_deleted': False, 'media_files': [],
                        'transcript': 'N/A', 'text_message': 'STOP'},
                       {'data_type': 'TEXT_MESSAGE', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Text - outgoing conversation.html', 'originating_name': '',
                        'originating_phone_number': '+11025550122', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Text,Inbox', 'timestamp': '2023-08-26 21:57:07 -0400',
                        'user_deleted': False, 'media_files': [], 'transcript': 'N/A',
                        'text_message': 'You have successfully been unsubscribed. You will not receive any more messages from this number. Reply START to resubscribe.'}]
    assert parsed_text == expected_result


def test_message_with_newlines() -> None:
    test_file = 'Text - Incoming with newlines.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_text = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'TEXT_MESSAGE', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Text - Incoming with newlines.html', 'originating_name': '',
                        'originating_phone_number': '+11035550133', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Text,Inbox', 'timestamp': '2022-08-22 12:34:01 -0400',
                        'user_deleted': False, 'media_files': [], 'transcript': 'N/A',
                        'text_message': 'Hi,\nHello\nGoodbye'}]
    assert parsed_text == expected_result


def test_group_text_names() -> None:
    test_file = "Text - Group text names.html"
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_text = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'TEXT_MESSAGE', 'direction': 'OUTGOING', 'duration': 'N/A',
                        'filename': 'Text - Group text names.html', 'originating_name': 'Me',
                        'originating_phone_number': '+11045550144', 'recipient_names': ['Bob Smith', 'Joe Smith'],
                        'recipient_phone_numbers': ['+11025550122', '+11035550133'], 'tags': 'Text',
                        'timestamp': '2024-01-19 00:19:34 -0500', 'user_deleted': False, 'media_files': [],
                        'transcript': 'N/A', 'text_message': 'test message'}]
    assert parsed_text == expected_result


def test_group_text_numbers() -> None:
    test_file = "Text - Group text numbers.html"
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_text = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'TEXT_MESSAGE', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Text - Group text numbers.html', 'originating_name': '+11085550119',
                        'originating_phone_number': '+11085550119',
                        'recipient_names': ['Google Voice Takeout Subject', '+11035550112', '+11085550100',
                                            '+11085550180', '+11085550194'],
                        'recipient_phone_numbers': ['', '+11035550112', '+11085550100', '+11085550180', '+11085550194'],
                        'tags': 'Text,Inbox', 'timestamp': '2021-04-20 15:42:39 -0400', 'user_deleted': False,
                        'media_files': [], 'transcript': 'N/A', 'text_message': 'hello'},
                       {'data_type': 'TEXT_MESSAGE', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Text - Group text numbers.html', 'originating_name': '+11085550180',
                        'originating_phone_number': '+11085550180',
                        'recipient_names': ['Google Voice Takeout Subject', '+11035550112', '+11085550100',
                                            '+11085550119', '+11085550194'],
                        'recipient_phone_numbers': ['', '+11035550112', '+11085550100', '+11085550119', '+11085550194'],
                        'tags': 'Text,Inbox', 'timestamp': '2021-04-20 15:43:54 -0400', 'user_deleted': False,
                        'media_files': [], 'transcript': 'N/A', 'text_message': 'goodbye'}]
    assert parsed_text == expected_result


def test_embedded_emoji() -> None:
    test_file = 'Text - Emoji embedded.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_text = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'TEXT_MESSAGE', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Text - Emoji embedded.html', 'originating_name': 'Joe Smith',
                        'originating_phone_number': '+11085550153', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Text,Inbox', 'timestamp': '2023-12-20 13:49:36 -0500',
                        'user_deleted': False,
                        'media_files': [('video', 'Joe Smith - Text - 2023-12-20T18_49_36Z-1-1')], 'transcript': 'N/A',
                        'text_message': '😁'}]
    assert parsed_text == expected_result


def test_embedded_audio() -> None:
    # No sample data; so a dead test.
    pass


def test_embedded_image() -> None:
    test_file = 'Text - Name with images.html'
    'Joe Smith - Cell - Text - 2022-03-23T18_17_2.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_text = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'TEXT_MESSAGE', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Text - Name with images.html', 'originating_name': '',
                        'originating_phone_number': '', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Text', 'timestamp': '2022-03-23 14:17:22 -0400',
                        'user_deleted': False,
                        'media_files': [('image', 'Joe Smith - Cell - Text - 2022-03-23T18_17_22Z-1-1'),
                                        ('image', 'Joe Smith - Cell - Text - 2022-03-23T18_17_22Z-1-2')],
                        'transcript': 'N/A', 'text_message': ''},
                       {'data_type': 'TEXT_MESSAGE', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Text - Name with images.html', 'originating_name': 'Joe Smith - Cell',
                        'originating_phone_number': '+11005550138', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Text', 'timestamp': '2022-03-23 14:18:01 -0400',
                        'user_deleted': False,
                        'media_files': [('image', 'Joe Smith - Cell - Text - 2022-03-23T18_17_22Z-2-1')],
                        'transcript': 'N/A', 'text_message': 'MMS Received'}]
    assert parsed_text == expected_result


def test_embedded_video() -> None:
    test_file = 'Text - Video Attachment.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_text = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'TEXT_MESSAGE', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Text - Video Attachment.html', 'originating_name': 'Joe Smith',
                        'originating_phone_number': '+11085550153', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Text,Inbox', 'timestamp': '2023-12-20 13:49:36 -0500',
                        'user_deleted': False,
                        'media_files': [('video', 'Joe Smith - Text - 2023-12-20T18_49_36Z-1-1')], 'transcript': 'N/A',
                        'text_message': '😁'}]
    assert parsed_text == expected_result


def test_embedded_contact() -> None:
    test_file = 'Text - contact embedded.html'
    test_fpath = os.path.join(TEST_DATA_DIR, test_file)
    parsed_text = google_voice_takeout_parser.parse_file(test_fpath)
    expected_result = [{'data_type': 'TEXT_MESSAGE', 'direction': 'INCOMING', 'duration': 'N/A',
                        'filename': 'Text - contact embedded.html', 'originating_name': 'Joe Smith',
                        'originating_phone_number': '+11085550153', 'recipient_names': ['Google Voice Takeout Subject'],
                        'recipient_phone_numbers': [''], 'tags': 'Text,Inbox', 'timestamp': '2023-05-12 17:25:09 -0400',
                        'user_deleted': False,
                        'media_files': [('contact', 'Joe Smith - Text - 2023-05-12T21_25_09Z-1-1')],
                        'transcript': 'N/A', 'text_message': 'MMS Received'}]
    assert parsed_text == expected_result
