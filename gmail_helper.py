from __future__ import print_function

import os.path
import base64
import html.parser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))


def __create_message_html(sender, to, subject, msg_html, msg_plain=""):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    if msg_plain == "":
        msg_plain = html.parser.unescape(msg_html)
    msg.attach(MIMEText(msg_plain, 'plain'))
    msg.attach(MIMEText(msg_html, 'html'))

    b64_encoded_message = base64.urlsafe_b64encode(msg.as_bytes())
    if isinstance(b64_encoded_message, bytes):
        b64_encoded_message = b64_encoded_message.decode('utf-8')

    return {'raw': b64_encoded_message}


def __send_message_internal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"


def __get_credentials():
    """
    Shows basic usage of the Gmail API.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = SCRIPT_PATH + '/gmail_credentials/token.json'
    client_secret = SCRIPT_PATH + '/gmail_credentials/credentials.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds


def send_message(sender, receiver, subject, message_html, message=""):
    creds = __get_credentials()
    service = build('gmail', 'v1', credentials=creds)
    message = __create_message_html(sender, receiver, subject, message_html, message)
    __send_message_internal(service, "me", message)

