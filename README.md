# Amodo Google Chat Bot

This is a project for the Amodo Design Google Chat bot. It was originally set up to send out Amodo Task summaries to users.

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

## run the app

To run the app run:

```
python main.py
```

This starts the app and will keep it running indefinitely. It listens to a Pub/Sub topic and reacts to messages.

## resources

https://developers.google.com/workspace/chat/api/guides/quickstart/python
