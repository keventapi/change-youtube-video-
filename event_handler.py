from flask_socketio import emit, join_room
from flask import request
import database
from functools import wraps
import json
import html

ws_cache = {}
def start_event_handler(socketio):
    def socket_login_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = ws_cache.get(request.sid)
            if not user_id:
                socketio.emit('auth_error', {'msg': 'autenticação falhou'}, to=request.sid)
                return
            return f(*args, **kwargs)
        return wrapper
    
    @socketio.on("connect")
    def handle_connect():
        print(f'usuario {request.sid} conectado ao servidor')

    @socketio.on('disconnect')
    def handle_disconnect():
        if request.sid in ws_cache:
            ws_cache.pop(request.sid)

    @socketio.on('login_websocket')
    def handle_login_websocket(msg):
        user_id = msg.get('token')
        if user_id:
            token_status, token_msg = database.run_db_operation(database.check_token_existence, token=user_id)
            if token_status:
                ws_cache[request.sid] = user_id
                print(ws_cache)
                join_room(user_id)
            else:
                socketio.emit('error', {'status': False, "msg": "voce esta com um token invalido, relogue para criar uma nova sessão"})
            
    @socketio.on('post_recommendations')
    @socket_login_required
    def post_recommendations(msg):
        ytrecommendations = {}
        ytrecommendations_array = msg.get('recommendations')
        ytrecommendations = create_dict(ytrecommendations_array)

        if ytrecommendations:
            user_id = ws_cache.get(request.sid)
            recommendations_status, recommendations_msg = database.run_db_operation(database.update_recommendations, token=user_id, recommendations=json.dumps(ytrecommendations))
        socketio.emit('new_recommendations', {"recommendations": ytrecommendations}, to=user_id)

    @socketio.on('get_recommendations')
    @socket_login_required
    def get_recommendations():
        user_id = ws_cache.get(request.sid)
        status, data = database.run_db_operation(database.get_user_from_token, token=user_id)
        if status:
            recommendations = data.get('recommendations')
            if recommendations:
                recommendations_json = json.loads(recommendations)
                socketio.emit('new_recommendations', {"recommendations": recommendations_json}, to=user_id)

    @socketio.on('next')
    @socket_login_required
    def handle_next(): #web_client
        user_id = ws_cache.get(request.sid)
        socketio.emit("send_next", to=user_id)

    @socketio.on('pause')
    @socket_login_required
    def handle_pause(): #web_client
        user_id = ws_cache.get(request.sid)
        socketio.emit('emit_pause', to=user_id)

    @socketio.on('get_video_from_client')
    @socket_login_required
    def get_video(message):
        user_id = ws_cache.get(request.sid)
        try:
            url = message.get('url')
            if url is not None:
                if is_an_allowed_url(url):
                    socketio.emit('change_video', {"url": url}, to=user_id)
        except Exception as e:
            socketio.emit('error', {'status': False, "msg": "o video que voce tentou enviar esta em um formato invalido"}
                          )
    @socketio.on('new_volume')
    @socket_login_required
    def new_volume(msg):
        user_id = ws_cache.get(request.sid)      
        volume = msg.get('volume')
        if volume is not None:
            try:
                volume = int(volume)
                if 0 <= volume <= 100:
                    volume_status, volume_msg = database.run_db_operation(database.update_volume, volume=volume, token=user_id)
                    if volume_status:
                        socketio.emit('change_volume', {"status": True, "volume": volume}, to=user_id)
                    else:
                        socketio.emit("error", {"status": False, "msg": "o erro foi desencadeado pela expiração da sessão ou alteração do seu token, por favor, reconecte com sua conta"}, to=user_id)
                else:
                    socketio.emit('error', {"status": False, "msg": "erro ao registrar volume, entrada invalida, ele não estava no range permitido (0 a 100)"}, to=user_id)
            except Exception as e:
                print('erro no new_volume, identificado do erro: ', e)
                socketio.emit('error', {"status": False, "msg": "erro ao registrar volume, entrada invalida, tenha certeza de não tentar enviar dados invalidos ao servidor"}, to=user_id)
                
    @socketio.on('emit_volume_to_client')
    @socket_login_required
    def emit_volume_to_client(): #web client
        user_id = ws_cache.get(request.sid)
        socketio.emit('get_volume', to=user_id)

    @socketio.on('recive_volume')
    @socket_login_required
    def recive_volume(msg):
        user_id = ws_cache.get(request.sid)      
        volume = msg.get('volume')
        if volume is not None:
            try:
                volume = int(volume)
                if 0 <= volume <= 100:
                    volume_status, volume_msg = database.run_db_operation(database.update_volume, volume=volume, token=user_id)
                    if volume_status:
                        socketio.emit('sync_volume', {"status": True, "volume": volume}, to=user_id)
                    else:
                        socketio.emit("error", {"status": False, "msg": "o erro foi desencadeado pela expiração da sessão ou alteração do seu token, por favor, reconecte com sua conta"}, to=user_id)
                else:
                    socketio.emit('error', {"status": False, "msg": "erro ao registrar volume, entrada invalida, ele não estava no range permitido (0 a 100)"}, to=user_id)
            except Exception as e:
                print('erro no recive_volume, identificado do erro: ', e)
                socketio.emit('error', {"status": False, "msg": "erro ao registrar volume, entrada invalida, tenha certeza de não tentar enviar dados invalidos ao servidor"}, to=user_id)

                
def is_an_allowed_url(url):
    allowed = ("https://i.ytimg.com", "https://img.youtube.com", "https://www.youtube.com", "https://youtu.be/")
    return isinstance(url, str) and url.startswith(allowed)

def sanitize_title(title):
    return html.escape(title) if isinstance(title, str) else None

def build_recommendation_entry(entry):
    title = sanitize_title(entry.get('title'))
    thumb = entry.get('thumb')
    url = entry.get('link')
    if title and is_an_allowed_url(url) and is_an_allowed_url(thumb):
        return title, {'url': url, 'thumb': thumb}
    return None, None

def create_dict(ytrecommendations_array):
    if isinstance(ytrecommendations_array, list) and len(ytrecommendations_array) > 0:
        try:
            ytrecommendations = {}
            for i in ytrecommendations_array:
                title, data = build_recommendation_entry(i)
                if title and data:
                    ytrecommendations[title] = data
            return ytrecommendations
        except Exception as e:
            print('erro na criação do dicionario de recomendação, indicador do erro: ', e)
            return None
    else:
        return None
