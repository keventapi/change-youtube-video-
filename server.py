from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit 
import eventlet

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

@socket.on('connect')
def handle_connect():
    print("Cliente conectado!")
    emit('connect_response', {'message': 'Conexão estabelecida com sucesso!'})

@socket.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado!')

@socket.on('next')
def handle_next():
    global data
    print(data)
    data['function'] = 'next'
    data['executar_algo'] = True
    socket.emit("send_next", data)

@socket.on('pause')
def handle_pause():
    global data
    data['function'] = 'pause'
    data['executar_algo'] = True
    socket.emit('emit_pause', data)

@socket.on('get_video_from_client')
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
    data['volume'] = int(volume)
    socket.emit('change_volume', data)

@socket.on('emit_volume_to_client')
def emit_volume_to_client():
    global data
    socket.emit('get_volume')

@socket.on('recive_volume')
def recive_volume(msg):
    global data
    data['volume'] = int(msg['volume'])
    socket.emit('sync_volume', data)

@socket.on('reset_data')
def reset_data():
    global data
    data['executar_algo'] = False
    data['function'] = ''

@socket.on('post_recommendations')
def post_recommendations(msg):
    global data
    ytrecommendations = {}
    ytrecommendations_array = msg['recommendations']
    
    for i in ytrecommendations_array:
        ytrecommendations[i["titulo"]] = {'url': i['link'], 'thumb': i['thumb']}

    if ytrecommendations:
        data['recommendations'] = ytrecommendations
        print(ytrecommendations)
    socket.emit('new_recommendations', data)

@socket.on('get_recommendations')
def get_recommendations():
    global data
    socket.emit('new_recommendations', data)

if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
