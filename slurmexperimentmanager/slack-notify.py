import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import sys
from glob import glob
import itertools
import time

client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
scan_pattern = sys.argv[1]
stop = False

def send_status(message):
    print(f"sending {message}")
    try:
        response = client.chat_postMessage(
            channel='U0179C2FQHY', text=message)
    
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        # str like 'invalid_auth', 'channel_not_found'
        assert e.response["error"]
        print(f"Got an error: {e.response['error']}")

def reverse_readline(filename, buf_size=8192):
    """A generator that returns the lines of a file in reverse order"""
    with open(filename, errors='ignore') as fh:
        segment = None
        offset = 0
        fh.seek(0, os.SEEK_END)
        file_size = remaining_size = fh.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            fh.seek(file_size - offset)
            buffer = fh.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split('\n')
            # The first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # If the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk.
                # Instead, yield the segment first 
                if buffer[-1] != '\n':
                    lines[-1] += segment
                else:
                    yield segment
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index]
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment

def check_if_finished(filename):
    state = "notfinished"
    for l in itertools.islice(reverse_readline(fn), 40):
        if l == "The output (if any) is above this job summary.":
            state = "terminated"
        if l == "Successfully completed.":
            state = "succesful"
    return state


last_message = None

while not stop:
    emojidict = {"notfinished" : "💪",
                "terminated": "🆘",
                "succesful": "🏁"}

    message = f"status of {scan_pattern}\n"
    stop = True
    for fn in glob(scan_pattern):
        status = check_if_finished(fn)
        if status == "notfinished":
            stop = False
        message += emojidict[status]
    
    if message != last_message:
        send_status(message)
    last_message = message
    
    if not stop:
        time.sleep(60)
