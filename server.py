from flask import Flask, request, render_template, jsonify, send_from_directory, session
from flask_socketio import SocketIO, emit, join_room
import eventlet
import json
import database
import auth

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet", manage_session=True)
app.secret_key = "secrete_key"

#client side
@app.route('/')
def home():
    status, msg = auth.check_token(session)
    if status:
        status, msg = database.run_db_operation(database.get_user_from_token, token=session.get('user_id'))
        username, password = status[1], status[2]
        return render_perfil()
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('usuario')
    password = data.get('senha')
    return login_handler(username, password)

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/register', methods=["POST"])
def register():
    data = request.get_json()
    username = data['usuario']
    password = data['senha']
    return register_handler(username, password)

def render_perfil():
    return render_template('perfil.html')

def login_handler(username, password):
    status, msg = database.run_db_operation(database.get_user, username=username, password=password)
    if status is not None:
        session['user_id'] = status[3]
        return jsonify({"status": True, "msg": "login efetuado", "token": status[3]})
    return jsonify({"status": False, "msg": "erro ao efetuar login, usuario ou senha invalidos", "token": False})

def register_handler(username, password):
    status, msg = database.run_db_operation(database.add_user, username=username, password=password)
    if status == True:
            login_response = login_handler(username, password)
            return login_response
    return jsonify({"status": False, "msg": "usuario ja existe"})


#event handler
@socketio.on("connect")
def handle_connect():
    handle_room_client()

@socketio.on('login_websocket')
def handle_login_websocket(msg):
    user_id = msg['token']
    join_room(user_id)
        
@socketio.on('post_recommendations')
def post_recommendations(msg):
    ytrecommendations = {}
    ytrecommendations_array = msg['recommendations']
    ytrecommendations = create_dict(ytrecommendations_array)

    if ytrecommendations:
        user_id = msg['token']
        msg = database.run_db_operation(database.update_recommendations, token=user_id, recommendations=json.dumps(ytrecommendations))
    socketio.emit('new_recommendations', {"recommendations": ytrecommendations}, to=user_id)

@socketio.on('get_recommendations')
def get_recommendations():
    user_id = session.get('user_id')
    status, msg = database.run_db_operation(database.get_user_from_token, token=user_id)
    try:
        recommendations = json.loads(status[6])
        socketio.emit('new_recommendations', {"recommendations": recommendations}, to=user_id)
    except Exception as e:
        print('erro ao adicionar recomendações ao banco de dados, identificador do erro: ', e)
        
@socketio.on('next')
def handle_next(): #web_client
    user_id = session.get('user_id')
    socketio.emit("send_next", to=user_id)

@socketio.on('pause')
def handle_pause(): #web_client
    user_id = session.get('user_id')
    socketio.emit('emit_pause', to=user_id)

@socketio.on('get_video_from_client')
def get_video(message): #web_client
    user_id = session.get('user_id')
    socketio.emit('change_video', {"url": message['url']}, to=user_id)

@socketio.on('new_volume')
def new_volume(message): #web_client
    volume = int(message["volume"])
    user_id = session.get('user_id')
    msg = database.run_db_operation(database.update_volume, volume=volume, token=user_id)
    socketio.emit('change_volume', {"volume": volume}, to=user_id)
    print(msg)
    
@socketio.on('emit_volume_to_client')
def emit_volume_to_client(): #web client
    user_id = session.get('user_id')
    socketio.emit('get_volume', to=user_id)

@socketio.on('recive_volume')
def recive_volume(msg):
    user_id = msg['token']
    volume = int(msg['volume'])
    msg = database.run_db_operation(database.update_volume, volume=volume, token=user_id)
    socketio.emit('sync_volume', {"volume": str(volume)}, to=user_id)
    print(user_id)
    
def create_dict(ytrecommendations_array):
    ytrecommendations = {}
    for i in ytrecommendations_array:
        ytrecommendations[i["titulo"]] = {'url': i['link'], 'thumb': i['thumb']}
    return ytrecommendations

def handle_room_client():
    status, msg = auth.check_token(session)
    if status:
        user_id = session.get('user_id')
        join_room(user_id)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000)
