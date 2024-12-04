# Amodo Google Chat Bot

This is a project for the Amodo Design Google Chat bot. It was originally set up to send out Amodo Task summaries to users.

⚠️ this project is still in development - currently uses a local version of the time entries database and does not have access to recent time entries

## what the bot can do

Users in the Amodo Design Google Workspace can message the bot on Google Chat and request a weekly summary by using the command:

```
/weeklySummary
```

Users can also use the following argument flags:

- `-e --email` for specifying the email of the user for which the summary should be created - this defaults to the user messaging
- `-w --week` for specifying the week number for which the summary should be created - this defaults to the most recent full week and currently only supports weeks from the same calendar year

## dev set up

Create `credentials.json`. Get these details from an existing developer. The file looks something like this:

```json
{
  "type": "service_account",
  "project_id": "amodo-task-chat-bot",
  "private_key_id": "---",
  "private_key": "---",
  "client_email": "amodo-task-chat-bot@amodo-task-chat-bot.iam.gserviceaccount.com",
  "client_id": "---",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/amodo-task-chat-bot%40amodo-task-chat-bot.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```

## use a virtual environment

It is good practice to use a virtual environment. I use pip and venv for this. Set it up once with:

```
python -m venv dev_environment
```

To activate, run:

```
dev_environment\\Scripts\\activate.bat
```

Install the required modules:

```
pip install -r requirements.txt
```

When you are done, call:

```
deactivate
```

Make sure to keep the requirements.txt file up to date.

```
pip freeze > requirements.txt
```

## run the app

To run the app run:

```
python main.py
```

This starts the app and will keep it running indefinitely. It listens to a Pub/Sub topic and reacts to messages.

## resources

https://developers.google.com/workspace/chat/api/guides/quickstart/python
