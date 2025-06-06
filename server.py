from flask import Flask, redirect, url_for, request, render_template, jsonify, send_from_directory, session
from flask_socketio import SocketIO, emit, join_room
import event_handler
import route_handler

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet", manage_session=True)
app.secret_key = "secret_key"

route_handler.start_route_handler(app)

event_handler.start_event_handler(socketio)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)
