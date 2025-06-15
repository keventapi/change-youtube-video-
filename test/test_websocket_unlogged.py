import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from flask import Flask
import pytest
from server import app, create_app_flask, create_app_socket, socketio
import database
from flask_socketio import SocketIOTestClient

def test_right_login_websocket():
    app = create_app_flask()
    socket = create_app_socket(app)
    
    client = socket.test_client(app)
    client.emit('login_websocket', {'token': '67b78b0a-913d-4f29-a604-523d18d4821b'})
    received = client.get_received()
    assert any(msg['name'] == 'sucess' for msg in received)
    
def test_wrong_login_websocket():
    app = create_app_flask()
    socket = create_app_socket(app)
    
    client = socket.test_client(app)
    client.emit('login_websocket', {'token': '67b78b0a--4f29-a604-523d18d4821b'})
    received = client.get_received()
    assert any(msg['name'] == 'error' for msg in received)
    
def test_invalide_type_none_login_websocket():
    app = create_app_flask()
    socket = create_app_socket(app)
    
    client = socket.test_client(app)
    client.emit('login_websocket', {'token': None})
    received = client.get_received()
    assert any(msg['name'] == 'error' for msg in received)

def test_invalide_type_int_login_websocket():
    app = create_app_flask()
    socket = create_app_socket(app)
    
    client = socket.test_client(app)
    client.emit('login_websocket', {'token': 1231254124})
    received = client.get_received()
    assert any(msg['name'] == 'error' for msg in received)
    
def test_invalide_type_int_login_websocket():
    app = create_app_flask()
    socket = create_app_socket(app)
    
    client = socket.test_client(app)
    client.emit('login_websocket', {'token': 1231254124})
    received = client.get_received()
    assert any(msg['name'] == 'error' for msg in received)
    
