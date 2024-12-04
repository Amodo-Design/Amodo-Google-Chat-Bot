import json
import time
import logging
from google.apps import chat_v1 as google_chat
from google.cloud import pubsub_v1
from google.oauth2.service_account import Credentials

from pprint import pprint

from config import SUBSCRIPTION_PATH

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
            reply(event)
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


def reply(event):
    """
    appropriately respond to an event
    """
    response = None
    # get details about event
    space_name = event['space']['name']
    event_type = event['type']

    # check if the event removed us from the space
    if event['type'] == 'REMOVED_FROM_SPACE':
        logging.info('app removed rom space %s', space_name)
        return
    # check if the event was adding us to the space
    elif event_type == 'ADDED_TO_SPACE':
        response = google_chat.CreateMessageRequest(
            parent = space_name,
            message = {
            'text': 'Thank you for adding me! Remember that I can only see direct messages.'
            }
        )
    # check if the event was a message
    elif event_type in ['ADDED_TO_SPACE', 'MESSAGE']:
        response = google_chat.CreateMessageRequest(
            parent = space_name,
            message = {
            'text': 'You said: `' + event['message']['text'] + '`'
            }
        )

    if response is not None:
        chat.create_message(response)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        style='{',
        format='{levelname:.1}{asctime} {filename}:{lineno}] {message}'
    )

    run_app()