import json
import logging

import datetime
import time

import argparse

from pprint import pprint

from google.apps import chat_v1 as google_chat
from google.cloud import pubsub_v1
from google.oauth2.service_account import Credentials

from config_bot import SUBSCRIPTION_PATH

from chat_bot_tools import send_message
from summary_tools import breakdown_for_user, wrapped2024


SCOPES          = ["https://www.googleapis.com/auth/chat.bot"]
CREDENTIALS     = Credentials.from_service_account_file(
    "credentials.json",
)

chat = google_chat.ChatServiceClient(
    credentials     = CREDENTIALS,
    client_options  = {"scopes": SCOPES}
)

subscriber = pubsub_v1.SubscriberClient(
    credentials     = CREDENTIALS
)

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--email', help='email address of the user you want a summary for')
parser.add_argument('-w', '--week', help='week you want a summary for')

def run_app():
    """
    listen for events and respond to them
    """
    # setup callback function
    def callback(message):
        try:
            event = json.loads(message.data)
            print()
            pprint(event)
            react(event)
            message.ack()
        except Exception as e:
            logging.error('error:', e)
            logging.error('this error occurred while processing the message:', message)
            message.ack()

    # subscribe to the topic
    subscriber.subscribe(SUBSCRIPTION_PATH, callback = callback)
    logging.info('listening on %s', SUBSCRIPTION_PATH)

    while True:
        time.sleep(60)


def react(event):
    """
    appropriately respond to an event
    """
    # get details about event
    space_name = event['space']['name']
    event_type = event['type']

    if event_type == 'MESSAGE':
        sender_email = event['message']['sender']['email']

    # check if the event removed us from the space
    if event_type == 'REMOVED_FROM_SPACE':
        logging.info('app removed rom space %s', space_name)
        return
    # check if the event added us to the space
    elif event_type == 'ADDED_TO_SPACE':
        send_message(
            space_name = space_name,
            message = 'Thank you for adding me! Remember that I can only see direct messages.'
        )
        return
    # check for slash command
    elif "slashCommand" in event['message']:
        command_id      = int(event['message']['slashCommand']['commandId'])

        # get arguments
        if "argumentText" in event['message']:
            argument_text   = event['message']['argumentText']
        else:
            argument_text = ''

        try:
            arguments = parser.parse_args(argument_text.split())
        except:
            send_message(
                space_name = space_name,
                message = 'I could not understand your arguments. Please try again.'
            )
            return

        if arguments.email is not None:
            user_email = arguments.email
        else:
            user_email = sender_email

        if arguments.week is not None:
            week_number = int(arguments.week)
        else:
            week_number = int(datetime.datetime.now().isocalendar()[1])
            if week_number == 1:
                send_message(
                    space_name = space_name,
                    message = 'This is the first week of the year. Please wait for data to accumulate. I currently cannot see previous years'
                )
                return
            else:
                week_number -= 1

        try:
            if command_id == 1:
                breakdown_for_user(user_email, week_number, space_name)
            elif command_id == 24:
                wrapped2024(user_email, space_name)
            else:
                send_message(
                    space_name = space_name,
                    message = 'I do not recognize that command. Try using the /weeklySummary command.'
                )
                return
        except Exception as e:
            logging.error('error:', e)
            send_message(
                space_name = space_name,
                message = 'I am sorry, I could not process your request. Please try again.'
            )
            return

    # check if the event was a message
    elif event_type == 'MESSAGE':
        message = 'You said: `' + event['message']['argumentText'] + '`\n'
        message += 'Your email address is ' + sender_email + '.\n'
        message += 'Try using the /weeklySummary command!'

        send_message(
            space_name = space_name,
            message = message
        )
        return



if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        style='{',
        format='{levelname:.1}{asctime} {filename}:{lineno}] {message}'
    )

    run_app()