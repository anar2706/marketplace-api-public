import requests
from fastapi.testclient import TestClient


Response = requests.models.Response


def test_get_countries(client: TestClient,cache,red):
    access_token = red.get('test:access_token').decode()
        
    response : Response = client.get('/v1/options/countries',
                headers={'Authorization':f"Bearer {access_token}"})
    
    assert response.status_code == 200
    assert len(response.json()) > 0
    


def test_get_faq(client: TestClient,cache,red):
    access_token = red.get('test:access_token').decode()
        
    response : Response = client.get('/v1/options/faq',
                headers={'Authorization':f"Bearer {access_token}"})
    
    assert response.status_code == 200
    assert len(response.json()) > 0
    