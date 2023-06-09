import os
import requests
from dotenv import load_dotenv

def load_environment():
    load_dotenv(f".env.{os.environ['ENVIRONMENT']}")


def send_log_slack_message(text):
    slack_url = os.environ['SLACK_URL']

    requests.post(slack_url,json={
        "attachments": [
            {
                
                "text": f'```{text}```',
                "title": "Chatbot API",
                "mrkdwn_in": ["text"],
            }
        ],
        "text": ""
    })