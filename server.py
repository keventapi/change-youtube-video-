from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit 

app = Flask(__name__)
socket = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

data = {
    'url': None,
    'function': '',
    'executar_algo': False,
    'volume': None,
    'recommendations': {}
}

@app.route('/')
def home():
    global data
    return render_template('home.html', dado=data)

@socket.on('next')
def handle_next(message):
    global data
    data['function'] = 'next'
    data['executar_algo'] = message['should_go_next']
    socket.emit("next", data)

@socket.on('pause')
def handle_pause(message):
    global data
    data['function'] = 'pause'
    data['executar_algo'] = message['should_pause']
    socket.emit('pause', data)

@socket.on('get_video')
def get_video(message):
    global data
    url = message['url']
    data['executar_algo'] = True
    data['function'] = 'change_video'
    data['url'] = url
    socket.emit('change_video', data)

@app.route('/get_data')
def change_video():
    global data
    return jsonify(data)

@socket.on('new_volume')
def new_volume(message):
    global data
    volume = message['volume']
    data['volume'] = int(volume['volume'])
    socket.emit('change_volume', data)

@socket.on('get_volume')
def get_volume(msg):
    global data
    socket.emit('get_volume', data)

@socket.on('reset_data')
def reset_data(msg):
    global data
    data['executar_algo'] = False
    data['function'] = ''

@socket.on('post_recommendations')
def post_recommendations(msg):
    global data
    ytrecommendations = msg['recommendations']
    if ytrecommendations != {}:
        data['recommendations'] = ytrecommendations
        print(ytrecommendations)

@socket.on('send_recommendations')
def send_recommendations():
    global data
    socket.emit('new_recommendations', data)

if __name__ == "__main__":
    socket.run(app, debug=True, host='0.0.0.0', port=5000)