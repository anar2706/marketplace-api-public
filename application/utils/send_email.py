import os
import boto3
from models import EmailTemplates


def send_email(to_email,email_type):
    email_record = EmailTemplates.select().where(EmailTemplates.type==email_type).dicts()[0]

    client = boto3.client('ses',aws_access_key_id=os.environ['SES_ACCESS'], 
        aws_secret_access_key=os.environ['SES_SECRET'],
        region_name=os.environ['SES_REGION'])

    response = client.send_email(
        Destination={
            'ToAddresses': [to_email],
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': "UTF-8",
                    'Data': email_record['html'],
                },
                'Text': {
                    'Charset': "UTF-8",
                    'Data': email_record['plain'],
                },
            },
            'Subject': {
                'Charset': "UTF-8",
                'Data': email_record['subject'],
            },
        },
        Source=os.environ['SES_MAIL_FROM']
    )

    print(f"Email sent! {response['MessageId']}")