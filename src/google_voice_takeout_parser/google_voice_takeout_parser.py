import argparse
import csv
import datetime
import os.path

import html5lib


def parse_timestamp(timestamp_text):
    # Sample value: '2022-09-30T14:36:36.127-04:00'
    # %z is the UTC offset, but in the form +/-HHMM, not HH:MM
    # To work around this, strip out the colon between them
    # In Python 3.12, it is possible to use %:z to allow the colon separator
    # between the HH and MM of the UTC offset
    timestamp_text_nocolon = "".join(timestamp_text.rsplit(':', 1))
    timestamp = datetime.datetime.strptime(timestamp_text_nocolon, '%Y-%m-%dT%H:%M:%S.%f%z')
    return timestamp


def parse_tags(root):
    tags_nodes = root.findall(".//div[@class='tags']/*")
    if not tags_nodes:
        raise Exception("Unable to find HTML nodes with tags!")
    tag_node_texts = []
    for tag_node in tags_nodes:
        tag_node_texts.append(tag_node.text)
    return tag_node_texts


def parse_deleted_status(root):
    deleted_status_node = root.find(".//div[@class='deletedStatusContainer']")
    if deleted_status_node is None:
        raise Exception("Unable to find HTML node with deleted status!")
    deleted_status_text = deleted_status_node.text
    if deleted_status_text == 'User Deleted:\nFalse':
        user_deleted = False
    elif deleted_status_text == 'User Deleted:\nTrue':
        user_deleted = True
    else:
        raise Exception(f"Unexpected value for deleted status! {deleted_status_text}")
    return user_deleted


def create_dict_parsed_data(filename=''):
    # TODO: Should this be a dataclass with enum's?
    call_data = {
        'data_type': None,
        'direction': None,  # Direction from the perspective of the Google Voice user
        'duration': None,
        'filename': filename,
        'originating_name': None,
        'originating_phone_number': None,
        # recipient_names and recipient_phone_numbers are lists, as a text message can have multiple recipients
        'recipient_names': None,
        'recipient_phone_numbers': None,
        'tags': None,
        'timestamp': None,
        'user_deleted': None,
        'media_files': None,
        'transcript': None,
        'text_message': None
    }
    return call_data


def extract_anchornode_name_number(anchor_node):
    href = anchor_node.get('href')
    if href.startswith('tel:'):
        # Note: Shockingly, it's possible for this data to be missing
        # and for the entire string to be 'tel:'
        number = href[len('tel:'):]
    else:
        raise Exception("Unable to parse telephone number!")
    name = anchor_node.find('span').text
    if name is None:
        name = ''
    return name, number


def parse_text(data, root, filename=''):
    # Parse all messages
    # We can infer the direction from the title
    # and also use that to extract the recipient info.
    # This will be for all messages in the file.
    # Incoming from an unknown number: <title></title>
    # Incoming from a known contact: <title>Joe Smith</title>
    # Incoming to a group conversation: ????
    # Outgoing to an unknown number: <title>Me to</title>
    # Outgoing to a known contact: <title>Me to Anonymous Smith</title>
    # Outgoing to a group conversation: <title>Group Conversation</title>

    # Each message will have the sender's info, but not the recipient's.
    # So we need to build a list of all parties in the text message so that we can easily list the
    # other parties in the call

    # For group messages, this is easy, as they are listed as "Group Conversation with ..."
    # For one-on-one messages, we can do a best-effort by extracting the name and number of all parties
    # that send a message to the Google Voice number. For non-group messages, this will only be one party.
    # Note that we will not be able to determine the recipient if the Google voice subscriber sends a message and
    # the other party never responds to it.

    # We need the title to determine if it's a group conversation
    title_node = root.find('./head/title')
    if title_node is None:
        raise Exception("Unable to extract title node!")
    title = title_node.text

    names_and_numbers = set()
    # Group message first:
    is_group_conversation = (title == "Group Conversation")
    if is_group_conversation:
        anchor_nodes = root.findall('.//div[@class="participants"]/cite/a')
        for anchor_node in anchor_nodes:
            name, number = extract_anchornode_name_number(anchor_node)
            if name or number:
                names_and_numbers.add((name, number))
    # Then one-on-one conversation
    else:
        anchor_nodes = root.findall('.//cite/a/span[@class="fn"]...')
        for anchor_node in anchor_nodes:
            name, number = extract_anchornode_name_number(anchor_node)
            if name or number:
                names_and_numbers.add((name, number))
        # If the other party never responds, we won't have a node with their contact info
        # But, there's a chance we can still grab it from the title
        # This is less preferred, because it is only the name, not the number.
        # But that is still better than nothing
        # As written above:
        # Outgoing to a known contact: <title>Me to Anonymous Smith</title>
        if not names_and_numbers and title.startswith('Me to\n'):
            other_name = title[len('Me to\n'):]
            names_and_numbers.add((other_name, ''))

    # Extract the other party names and numbers to lists so that
    # the entries are synced
    other_party_names = []
    other_party_numbers = []
    # Sort these so we have consistent ordering for our unit tests.
    for name, number in sorted(names_and_numbers):
        other_party_names += [name]
        other_party_numbers += [number]

    # Now we can parse the messages themselves
    text_messages = []
    message_nodes = root.findall("./body/div[@class='hChatLog hfeed']/div[@class='message']")
    for message_node in message_nodes:
        # Each message has its own timestamp, name, and content
        # The best option may be one row per message
        call_data = create_dict_parsed_data(filename)

        call_data['data_type'] = "TEXT_MESSAGE"
        call_data['duration'] = "N/A"
        call_data['media_files'] = []
        call_data['transcript'] = "N/A"
        # Parse the timestamp
        timestamp_node = message_node.find('./abbr[@class="dt"]')
        if timestamp_node is None:
            raise Exception("Unable to find message timestamp!")
        timestamp_text = timestamp_node.get('title')
        timestamp = parse_timestamp(timestamp_text)
        call_data['timestamp'] = timestamp.strftime('%Y-%m-%d %H:%M:%S %z')

        # Parse the sender/recipient info
        # Interestingly, the easiest way to differentiate is that
        # outgoing text messages use <abbr class="fn"> while
        # incoming text messages use <span class="fn">
        # This needs to be done first because other fields depend
        # on whether it was INCOMING or OUTGOING
        name_node = message_node.find('./cite/a/*[@class="fn"]')
        if name_node is None:
            raise Exception("Unable to find HTML with name!")

        # Note: the node may not have any text and so be None
        name = ''
        if name_node.text is not None:
            name = name_node.text

        # Parse telephone number
        telephone_node = message_node.find('./cite/a[@class="tel"]')
        if telephone_node is None:
            raise Exception("Unable to find HTML with telephone number!")
        href_value = telephone_node.get('href')
        if href_value.startswith('tel:'):
            # Note: Shockingly, it's possible for this data to be missing
            # and for the entire string to be 'tel:'
            phone_number = href_value[len('tel:'):]
        else:
            raise Exception("Unable to parse telephone number!")

        call_data['originating_name'] = name
        call_data['originating_phone_number'] = phone_number

        if name_node.tag == 'abbr':
            # For texts send by the Google Voice user, the recipients are all other names and numbers
            call_data['direction'] = "OUTGOING"
            call_data['recipient_names'] = other_party_names
            call_data['recipient_phone_numbers'] = other_party_numbers
        elif name_node.tag == 'span':
            # For texts received by the Google Voice user, the only significant recipient is the Google voice user
            # But we'll still add them all
            call_data['direction'] = "INCOMING"
            call_data['recipient_names'] = ["Google Voice Takeout Subject"]
            call_data['recipient_phone_numbers'] = ['']
            # for group conversations, add everyone besides the sender:
            if is_group_conversation:
                for name, number in zip(other_party_names, other_party_numbers):
                    if number == call_data['originating_phone_number']:
                        continue
                    call_data['recipient_names'] += [name]
                    call_data['recipient_phone_numbers'] += [number]

        # Parse the message itself
        message_q_node = message_node.find('./q')
        if message_q_node is None:
            raise Exception("Unable to find HTML with message content!")

        # Text messages can contain <br> tags
        # We'll need to recombine everything following the <br> tags to ensure
        # we have the complete message
        if message_q_node.text is None:
            text_message = ''
        else:
            text_message = message_q_node.text
        for node in message_q_node.findall('./*'):
            if node.tail is not None:
                text_message += "\n" + node.tail
        call_data['text_message'] = text_message

        # Add any embedded images
        for img_node in message_node.findall('./div/img'):
            # The IMG src doesn't include the extension, which can be jpg, gif, or possibly more
            media_file = img_node.get('src')
            call_data['media_files'] += [('image', media_file)]

        # Add any embedded videos
        for video_node in message_node.findall('./div/a[@class="video"]'):
            media_file = video_node.get('href')
            call_data['media_files'] += [('video', media_file)]

        # Add any embedded contact cards
        for video_node in message_node.findall('./div/a[@class="vcard"]'):
            media_file = video_node.get('href')
            call_data['media_files'] += [('contact', media_file)]

        # Parse tags
        call_data['tags'] = ',' .join(parse_tags(root))

        # Parse deleted status:
        call_data['user_deleted'] = parse_deleted_status(root)

        # Validate that all values were set
        for k, v in call_data.items():
            if v is None:
                print(data)
                print(filename)
                print(call_data)
                print(k)
                raise Exception(f"Value {k} was not set!")

        text_messages += [call_data]

    return text_messages


def parse_call(data, root, filename=''):
    '''Parses an audio calls'''
    call_data = create_dict_parsed_data(filename)
    # Only applies to text messages
    call_data['text_message'] = "N/A"
    # type and direction (incoming or outgoing)
    title_node = root.find('./head/title')
    if title_node is None:
        raise Exception("Unable to extract title node!")
    title = title_node.text
    if title.startswith('Placed call to'):
        call_data['data_type'] = "OUTGOING CALL"
        call_data['direction'] = "OUTGOING"
        call_data['media_files'] = []
        call_data['transcript'] = "N/A"
        call_data['originating_name'] = "Google Voice Takeout Subject"
        call_data['originating_phone_number'] = ''
    elif title.startswith('Received call from'):
        call_data['data_type'] = "INCOMING CALL"
        call_data['direction'] = "INCOMING"
        call_data['media_files'] = []
        call_data['transcript'] = "N/A"
        call_data['recipient_names'] = ["Google Voice Takeout Subject"]
        call_data['recipient_phone_numbers'] = ['']
    elif title.startswith('Missed call from'):
        call_data['data_type'] = "MISSED CALL"
        call_data['direction'] = "INCOMING"
        call_data['duration'] = "N/A"
        call_data['media_files'] = []
        call_data['transcript'] = "N/A"
        call_data['recipient_names'] = ["Google Voice Takeout Subject"]
        call_data['recipient_phone_numbers'] = ['']
    elif title.startswith('Voicemail from'):
        call_data['data_type'] = "VOICEMAIL"
        call_data['direction'] = "INCOMING"
        call_data['recipient_names'] = ["Google Voice Takeout Subject"]
        call_data['recipient_phone_numbers'] = ['']
    elif title.startswith('Recorded call with'):
        call_data['data_type'] = "RECORDED CALL"
        call_data['direction'] = "UNKNOWN - LIKELY INCOMING"
        call_data['recipient_names'] = ["Google Voice Takeout Subject"]
        call_data['recipient_phone_numbers'] = ['']
    else:
        raise Exception(f"Unable to detect call direction! title: {title}")

    # The name and number will depend on whether it's incoming or outgoing, so
    # we'll parse both and then set the appropriate field.
    # Parse name:
    name_node = root.find("./body/div/div/a/span[@class='fn']")
    if name_node is None:
        raise Exception("Unable to find HTML node with name!")
    # Note: the node may not have any text
    if name_node.text is None:
        name = ''
    else:
        name = name_node.text

    # Parse telephone number
    telephone_node = root.find('./body/div/div/a[@class="tel"]')
    if telephone_node is None:
        raise Exception("Unable to find HTML with telephone number!")
    href_value = telephone_node.get('href')
    if href_value.startswith('tel:'):
        # Note: Shockingly, it's possible for this data to be missing
        # and for the entire string to be 'tel:'
        phone_number = href_value[len('tel:'):]
    else:
        raise Exception("Unable to parse telephone number!")

    if 'INCOMING' in call_data['direction']:
        call_data['originating_name'] = name
        call_data['originating_phone_number'] = phone_number
    else:
        call_data['recipient_names'] = [name]
        call_data['recipient_phone_numbers'] = [phone_number]

    # Parse timestamp
    timestamp_node = root.find("./body/div/abbr[@class='published']")
    if timestamp_node is None:
        raise Exception("Unable to find HTML node with timestamp!")
    timestamp_text = timestamp_node.get('title')
    timestamp = parse_timestamp(timestamp_text)
    call_data['timestamp'] = timestamp.strftime('%Y-%m-%d %H:%M:%S %z')

    # Parse duration
    # Does not apply to missed calls
    if call_data['data_type'] != "MISSED CALL":
        duration_node = root.find("./body/div/abbr[@class='duration']")
        if duration_node is None:
            raise Exception("Unable to find HTML node with duration!")
        call_data['duration'] = duration_node.text

    # Parse deleted status:
    call_data['user_deleted'] = parse_deleted_status(root)

    # Parse tags
    call_data['tags'] = ',' .join(parse_tags(root))

    # Parse voicemail filename
    if call_data['data_type'] == 'VOICEMAIL' or call_data['data_type'] == 'RECORDED CALL':
        media_files_node = root.find("./body/div/audio/[@controls='controls']")
        # Note: Not all voicemails have MP3s associated, but if they do have
        # content containing 'mp3', we probably have a bug
        if media_files_node is None and '.mp3' in data:
            raise Exception("Unable to find HTML node with voicemail filename!")
        if media_files_node is not None:
            call_data['media_files'] = [('audio', media_files_node.get('src'))]
        else:
            call_data['media_files'] = []

    # Parse voicemail transcript
    if call_data['data_type'] == 'VOICEMAIL' or call_data['data_type'] == 'RECORDED CALL':
        transcript_node = root.find("./body/div/span/span[@class='full-text']")
        # Note: Not all voicemails have transcripts, but if they do have
        # content containing 'class="full-text"', we probably have a bug
        if transcript_node is None and 'class="full-text"' in data:
            raise Exception("Unable to find HTML node with voicemail transcript!")
        if transcript_node is None:
            call_data['transcript'] = ''
        else:
            call_data['transcript'] = transcript_node.text

    # Validate that all values were set
    for k, v in call_data.items():
        if v is None:
            print(k)
            raise Exception(f"Value {k} was not set!")
    return [call_data]


def parse_str(data, fname):
    root = html5lib.parse(data, namespaceHTMLElements=False)
    # Attempt to detect the file's content type based on the class
    file_class = root.find('./body/div').attrib.get('class')
    if not file_class:
        raise Exception("No file_class detected! Please submit a pull request with how this file type should be parsed")
    if file_class not in ['haudio', 'hChatLog hfeed']:
        print()
        raise Exception(f"Unknown file_class {file_class} detected! Please submit a pull request with how this file type should be parsed")

    if file_class == 'haudio':
        return parse_call(data, root, fname)
    elif file_class == 'hChatLog hfeed':
        return parse_text(data, root, fname)
    else:
        raise Exception("Unsupported content type!")


def parse_file(fpath):
    """Loads a file"""
    with open(fpath, encoding='utf-8') as fh:
        data = fh.read()
        return parse_str(data, os.path.basename(fpath))


def write_to_csv(csv_fpath, parsed_files):
    with open(csv_fpath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = sorted(create_dict_parsed_data().keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(parsed_files)


def process_directory(indir):
    csv_entries = []
    file_count = 0
    for f in os.listdir(indir):
        if not f.endswith('html'):
            continue
        try:
            file_count += 1
            result = parse_file(os.path.join(indir, f))
            if result:
                csv_entries += result
        except Exception as E:
            print(f"Exception when processing file {f}: {E}")
    return file_count, csv_entries
