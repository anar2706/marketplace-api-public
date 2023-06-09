import os
import random
import requests
from fastapi.testclient import TestClient


Response = requests.models.Response


def test_signup(client: TestClient,cache,red):
    password = 'test1234'
    email = f"user{random.randint(1,10000)}@testgrow.co"
    
    red.set('test:email',email)
    cache.password = password
    cache.email = email

    data = {
        "email":email,
        "password":password,
        "country":"UK",
        "company_name":"Test Company",
        "type":"buyer"
    }
    
    response : Response = client.post('/v1/auth/signup',json=data)
    assert response.status_code == 200
    assert response.json() == {'status':'ok'}
    


def test_login(client: TestClient,cache,red):
    data = {
        "email":cache.email,
        "password":cache.password
    }
    
    response : Response = client.post('/v1/auth/login',json=data)
    assert response.status_code == 200
    assert response.json().get('access_token')

    red.set('test:access_token',response.json()['access_token'])
    red.set('test:refresh_token',response.json()['refresh_token'])
   

def test_refresh_token(client: TestClient,red):
    refresh_token = red.get('test:refresh_token').decode()
    response : Response = client.post('/v1/auth/refresh',headers={
            'Authorization': f'Bearer {refresh_token}'
        }
    )

    assert response.status_code == 200
    assert response.json().get('access_token')
    
    red.set('test:access_token',response.json()['access_token'])
    red.set('test:refresh_token',response.json()['refresh_token'])
   


def test_reset_password(client: TestClient,red):
    email = red.get('test:email').decode()
    response : Response = client.post('/v1/auth/reset-password',json={
            'email':email
        }
    )

    assert response.status_code == 200
    assert response.json() == {'status':'ok'}

def test_login_attempt(client: TestClient,red,cache):
    os.environ['LOGIN_ATTEMPT_LIMIT'] = '2'
    response : Response = client.post('/v1/auth/login',json={
            "email":cache.email,
            "password":"wrong_password"
        }
    )

    assert response.status_code == 401
    assert response.json()['message'] == 'Incorrect Password'

    response : Response = client.post('/v1/auth/login',json={
            "email":cache.email,
            "password":"wrong_password"
        }
    )

    assert response.status_code == 401
    assert response.json()['message'] == 'Incorrect Password'

    response : Response = client.post('/v1/auth/login',json={
            "email":cache.email,
            "password":"wrong_password"
        }
    )

    assert response.status_code == 401
    assert response.json()['message'] == 'You have reached max login limits'