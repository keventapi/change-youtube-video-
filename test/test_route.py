import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from flask import Flask
import pytest
from server import app
import random
from functools import wraps
import database
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route_loggedout(client):
    response = client.get('/')
    assert response.status_code == 302

def test_login_route_loggedout(client):
    response = client.get('/login_page')
    assert response.status_code == 200
    
def test_signup_route_loggedout(client):
    response = client.get('/signup')
    assert response.status_code == 200
    
def test_wrong_login_loggedout(client):
    response = client.post('/login', json={
        "usuario": "sqaijhflkjsa",
        "senha": "jaklsjflkas"
    })
    assert response.status_code == 400
    
def test_wrong_login_type_loggedout(client):
    response = client.post('/login', json={
        "usuario": 1234513,
        "senha": None
    })
    assert response.status_code == 400

def test_right_login_loggedout(client):
    response = client.post('/login', json={
        "usuario": "keven123",
        "senha": "keven123"
    })
    data = response.get_json()
    with client.session_transaction() as sess:
        assert sess['user_id'] == data['token']
    assert response.status_code == 200

def test_wrong_signup_loggedout(client):
    response = client.post('/register', json={'usuario': "keven123", 'senha': "keven123"})
    data = response.get_json()
    assert response.status_code == 400
    assert data['status'] == False

def test_wrong_type_signup_loggedout(client):
    response = client.post('/register', json={'usuario': 213124, 'senha': None})
    data = response.get_json()
    assert response.status_code == 400
    assert data['status'] == False

def test_already_signuped_register_loggedout(client):
    response = client.post('/register', json={'usuario': "keven123", 'senha': "keven123"})
    data = response.get_json()
    assert response.status_code == 400
    assert data['status'] == False

def test_righ_signup_loggedout(client):
    usuario = f"{random.randint(1000000000, 9000000000)}"
    senha = f"{random.randint(1000000000, 9000000000)}"
    response = client.post('/register', json={'usuario': usuario, 'senha': senha})
    data = response.get_json()
    assert response.status_code == 201
    assert data['status'] == True
    
    
    status, data = database.run_db_operation(database.get_user, username=usuario, password=senha)
    assert status == True
    assert data is not None
    
def test_righ_signup_loggedout_uppercase(client):
    usuario, senha = create_random_login()
    response = client.post('/register', json={'usuario': usuario, 'senha': senha})
    data = response.get_json()
    assert response.status_code == 201
    assert data['status'] == True
    
    
    status, data = database.run_db_operation(database.get_user, username=usuario, password=senha)
    assert status == True
    assert data is not None
    
def test_try_logout_loggedout(client):
    response = client.get('/request_logout')
    assert response.status_code == 302
    
def create_random_login():
    characteres = "abcdefghijklmnopqrstuvwxyz"
    username = ''
    password = ''
    for i in range(10):
        username += characteres[random.randint(0, len(characteres)-1)].upper()
        password += characteres[random.randint(0, len(characteres)-1)].upper()
    return username, password