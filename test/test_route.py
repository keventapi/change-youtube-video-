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
    response = client.post('/register', json={'usuario': f"{random.randint(1000000000, 9000000000)}", 'senha': f"{random.randint(1000000000, 9000000000)}"})
    data = response.get_json()
    assert response.status_code == 201
    assert data['status'] == True
    
