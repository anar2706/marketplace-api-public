import os
import time
import httpx
from functools import wraps

def timefn(fn):
    @wraps(fn)
    def measure_time(*args, **kwargs):
        t1 = time.time()
        result = fn(*args, **kwargs)
        t2 = time.time()
        print(f"@timefn: {fn.__name__} took {t2 - t1} seconds")
        return result
    return measure_time


async def send_contact_message(arguments):
    slack_url = os.environ['CONTACT_SLACK_URL']
    text = ""

    for key,value in arguments.items():
        text += f"{key}: {value}\n"

    async with httpx.AsyncClient() as client:
        await client.post(slack_url,json={
            "attachments": [
                {
                    
                    "text": f'```{text}```',
                    "title": "Chatbot API",
                    "mrkdwn_in": ["text"],
                }
            ],
            "text": ""
        })
