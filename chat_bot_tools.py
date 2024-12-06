from googleapiclient.discovery import build
from google.oauth2 import service_account

import logging

# set up the chat client
SCOPES = [
    'https://www.googleapis.com/auth/chat.bot'
]

credentials = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES)

chat = build('chat', 'v1', credentials=credentials)


def get_spaces():
    '''
    Returns a list of spaces that the bot is a member of.
    '''
    result = chat.spaces().list().execute()
    return result


def send_message(
        message,
        space_name='spaces/AAAAOrgUGRk'
    ):
    '''
    Sends a message to a space.
    Args:
        message (str): The message to send.
        space_name (str): The name of the space to send the message to.
    '''

    result = chat.spaces().messages().create(
        parent  = space_name,
        body    = {'text': message}
    ).execute()

    logging.info('message sent: %s', message)


def send_card(
        space_name = 'spaces/AAAAOrgUGRk',
        title_text = '',
        intro_text = '',
        overview_text = '',
        subsection_texts = [
            ['title', 'content']
        ]
    ):
    '''
    Sends a card to a space.
    Args:
        space_name (str): The name of the space to send the card to.
        title_text (str): The title of the card.
        intro_text (str): The introductory text of the card.
        overview_text (str): The overview text of the card.
        subsection_texts (list): A list of lists, each containing a title and content for a subsection of the card.
    '''

    sections = [{
        "header": "",
        "widgets": [{ "text_paragraph": {
                "text": overview_text
            }}
        ]
    }]

    for subsection_text in subsection_texts:
        sections.append({
            "header": subsection_text[0],
            "collapsible": False,
            "widgets": [{ "text_paragraph": {
                    "text": subsection_text[1]
                }}]
        })

    # https://addons.gsuite.google.com/uikit/builder for building cards

    result = chat.spaces().messages().create(
        parent  = space_name,
        body    = {
            "text": intro_text,
            "cards_v2" : [{ "card": {
                "header": {
                    "title": title_text,
                    "image_url": 'https://cdn.prod.website-files.com/650b1df1d17c457f9b527af0/6527d73438d4e13f4a02488e_Webclip.png'
                },
                "sections": sections
            }}]
        }
    ).execute()

    logging.info('card sent: %s', title_text)
