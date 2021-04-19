from fastapi.testclient import TestClient
from pydantic import BaseModel
from datetime import datetime, timedelta

from main import app

client = TestClient(app)


class RegisterUser(BaseModel):
    name: str = ''
    surname: str = ''


def test_read_main():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello world!'}


def test_read_method():
    response = client.get('/method')
    assert response.status_code == 200
    assert response.json() == {'method': 'GET'}

    response = client.post('/method')
    assert response.status_code == 201
    assert response.json() == {'method': 'POST'}

    response = client.delete('/method')
    assert response.status_code == 200
    assert response.json() == {'method': 'DELETE'}

    response = client.put('/method')
    assert response.status_code == 200
    assert response.json() == {'method': 'PUT'}

    response = client.options('/method')
    assert response.status_code == 200
    assert response.json() == {'method': 'OPTIONS'}


def test_hash():
    response = client.get(
        '/auth?password=kasia&password_hash=77b95508b962ee4320bc31da18776d220b7a42ef0cce3e02a404b049b3d2ac9ddad1d09b4a2928f6dd0942d42e0b87d2bebeb7a78a821e1b57cef29e5b910580')
    assert response.status_code == 204

    response = client.get(
        '/auth?password=kasia&password_hash=nu4u3xi7rgcn3gximh23i2crh4bxbdv3u2x')
    assert response.status_code == 401

    response = client.get(
        '/auth?password=kasia')
    assert response.status_code == 401


# def test_register():
#     response = client.post(
#         '/register', RegisterUser(name='ola', surname='buk'))
#     assert response.status_code == 201
#     assert response.json() == {
#         'id': 1,
#         'name': 'ola',
#         'surname': 'buk',
#         'register_date': datetime.today().strftime('%Y-%m-%d'),
#         'vaccination_date': (datetime.today() + timedelta(days=6)).strftime('%Y-%m-%d')
#     }

#     response = client.post(
#         '/register', RegisterUser(name='arek', surname='marek'))
#     assert response.status_code == 201
#     assert response.json() == {
#         'id': 2,
#         'name': 'arek',
#         'surname': 'marek',
#         'register_date': datetime.today().strftime('%Y-%m-%d'),
#         'vaccination_date': (datetime.today() + timedelta(days=9)).strftime('%Y-%m-%d')
#     }
