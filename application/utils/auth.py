import os
import json
from fastapi import HTTPException
from application.helpers.connections import Redis_Con

def create_access_token(Authorize,user_data):
    access_token = Authorize.create_access_token(subject=user_data['id'],user_claims={
        'data':{
            'user_id':user_data['id'],
            'type':user_data['type'],
            'company_id':user_data['company_id'],
            'email':user_data['email'],
            'phone':user_data['phone'],
        }
    })

    return access_token

def create_refresh_token(Authorize,user_data):
    access_token = Authorize.create_refresh_token(subject=user_data['id'],user_claims={
         'data':{
            'user_id':user_data['id'],
            'type':user_data['type'],
            'company_id':user_data['company_id'],
            'email':user_data['email'],
            'phone':user_data['phone'],
        }
    })
    return access_token



async def check_login_attempts(email):
    red = Redis_Con().red
    key = f'login:{email}'
    attempts = await red.get(key)
    
    if not attempts:
        return

    attempts = json.loads(attempts)    
    if attempts >= int(os.environ['LOGIN_ATTEMPT_LIMIT']):
       raise HTTPException(401,detail='You have reached max login limits')


async def set_login_attempts(email):
    red = Redis_Con().red
    key = f'login:{email}'
    attempts = await red.get(key)

    if attempts:
        attempts = json.loads(attempts)
    else:
        attempts = 0

    attempts += 1
    await red.set(key,json.dumps(attempts),ex=10)
    


async def check_reset_password_limit(email):
    red = Redis_Con().red
    key = f'reset-password:{email}'
    attempts = await red.get(key)

    if attempts:
        attempts = json.loads(attempts)
    else:
        attempts = 0

    if attempts >= int(os.environ['RESET_ATTEMPT_LIMIT']):
       raise HTTPException(401,detail='You have reached max reset password limits')

    attempts += 1
    await red.set(key,json.dumps(attempts),ex=10)

