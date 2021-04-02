import os
import json
import datetime as dt
import pytz
from pathlib import Path


def get_local_time(date_str):
    # converting the given date format (ISO 8601) to a usable python object
    date_obj = dt.datetime.fromisoformat(date_str)

    # INSERT YOUR TIMEZONE HERE, RUN print_timezones() TO LIST ALL AND FIND YOURS, UTC used by default
    your_tz = pytz.timezone('UTC')

    # changing time according to provided timezone, returning datetime object
    date_your_tz = date_obj.astimezone(your_tz)
    return date_your_tz


# returns string to be written on the file when a message is 'liked'
def get_liked_message(likes):
    return f"[{likes['username']}][{get_local_time(likes['date']).strftime('%H:%M:%S')}]"


# when animated media is sent by a user, returning only post-media owner username and display-name
def get_animated_media_msg(user):
    return f"Sent a post by @{user.get('username')} - f{user.get('display_name')}"


# writing into a given unique file for every conversation
def create_message_file(conversation, file):
    previous_date = None
    previous_sender = None

    # json provided stores messages in the order LATEST = TOP
    # LATEST = BOTTOM easier to read top-down
    for message in reversed(conversation.get('conversation')):

        # date & time at which message was sent
        date_string = message.get('created_at')

        message_sender = message.get('sender')

        dt_obj = get_local_time(date_string)

        # writing new date first if a message is sent on a day different from the previous
        if previous_date != dt_obj.date():
            file.write(f"\n{dt_obj.strftime('%B %d, %Y')}")
            file.write('\n')
            previous_date = dt_obj.date()

        readable_message = f"[{message_sender}][{dt_obj.strftime('%H:%M')}]"

        # a message is liked by a user
        if message.get('likes') is not None:
            file.write(f"{readable_message} liked a message {get_liked_message(message.get('likes')[0])}\n")

        # leaving blank lines between texts from different users for better readability
        if previous_sender != message_sender:
            file.write('\n')
            previous_sender = message_sender

        # media-link is sent by a user
        if message.get('media') is not None:
            readable_message += f": {message['media']}"

        # an instagram post is shared by a user
        elif message.get('media_owner') is not None:
            readable_message += f": Sent a post by @{message.get('media_owner')}\n" \
                                f"Caption: {message.get('media_share_caption')}\n"  \
                                f"Link: {message.get('media_share_url')}"

        # personal media is shared - link not reachable mostly
        elif message.get('media_url') is not None:
            readable_message += f": Sent a photo: {message.get('media_url')}"

        elif message.get('animated_media_images') is not None:
            readable_message += f": {get_animated_media_msg(message.get('user'))}"

        # a regular text is sent
        elif message.get('text') is not None:
            readable_message += f": {message.get('text')}"

        # any cases missed by the above conditions
        else:
            readable_message += "*sent a message*"

        file.write(readable_message + '\n')


# returning a suitable unique filename for every conversation
def get_file_name(participants):
    filename = ''
    for participant in participants[:-1]:
        filename += participant + '_'
    return filename + participants[-1]


# use if you want to find your timezone in the pytz module
def print_timezones():
    for tz in pytz.all_timezones:
        print(tz)


def main():
    with open("sample_input.json") as f:
        conversations = json.load(f)

    # all output files stored in a new folder
    os.mkdir('output_files')
    data_folder = Path('output_files')

    for conversation in conversations:
        filename = get_file_name(conversation.get('participants')) + '.txt'
        file_to_open = data_folder / filename
        with open(file_to_open, 'w') as fr:
            create_message_file(conversation, fr)


main()
