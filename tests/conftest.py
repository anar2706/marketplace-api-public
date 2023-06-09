from pytest import fixture
from pytest import fixture
from application.app import create_app
from fastapi.testclient import TestClient
from application.helpers.connections import Redis_Con_Sync


@fixture(scope='session')
def red():
    red = Redis_Con_Sync().red
    return red


@fixture(scope="session")
def client(red):
    app = create_app()
    client = TestClient(app)
    yield client
