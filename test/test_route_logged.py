import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from flask import Flask
import pytest
from server import app
import random
from functools import wraps
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def logged_client(client):
    response = client.post('/login', json={
        "usuario": "keven123",
        "senha": "keven123"
    })
    assert response.status_code == 200
    yield client

def test_index_route_logged(logged_client):
    response = logged_client.get('/home')
    assert response.status_code == 200
    
def test_login_route_logged(logged_client):
    response = logged_client.get('/login_page')
    assert response.status_code == 302    
    
def test_signup_route_logged(logged_client):
    response = logged_client.get('/signup')
    assert response.status_code == 302
    
def test_wrong_login_logged(logged_client):
    response = logged_client.post('/login', json={
        "usuario": "sqaijhflkjsa",
        "senha": "jaklsjflkas"
    })
    assert response.status_code == 302
def test_wrong_login_type_logged(logged_client):
    response = logged_client.post('/login', json={
        "usuario": 1234513,
        "senha": None
    })
    assert response.status_code == 302
    
def test_right_login_logged(logged_client):
    response = logged_client.post('/login', json={
        "usuario": "keven123",
        "senha": "keven123"
    })
    assert response.status_code == 302
    
def test_wrong_signup_logged(logged_client):
    response = logged_client.post('/register', json={'usuario': "keven123", 'senha': "keven123"})
    assert response.status_code == 302
    
def test_wrong_type_signup_logged(logged_client):
    response = logged_client.post('/register', json={'usuario': 213124, 'senha': None})
    assert response.status_code == 302

def test_already_signuped_register_logged(logged_client):
    response = logged_client.post('/register', json={'usuario': "keven123", 'senha': "keven123"})
    assert response.status_code == 302

def test_righ_signup_logged(logged_client):
    response = logged_client.post('/register', json={'usuario': f"{random.randint(1000000000, 9000000000)}", 'senha': f"{random.randint(1000000000, 9000000000)}"})
    assert response.status_code == 302
