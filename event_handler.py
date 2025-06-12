from flask_socketio import emit, join_room, leave_room
from flask import request
import database
from functools import wraps
import json
import html
import cache
from utilites import data_sanitization

ws_cache = {}
def start_event_handler(socketio):
    def socket_login_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = ws_cache.get(request.sid)
            if not user_id or not isinstance(user_id, str):
                socketio.emit('auth_error', {'msg': 'autenticação falhou'}, to=request.sid)
                return None
            return f(user_id=user_id, *args, **kwargs)
        return wrapper
    
    def black_list(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            sid = request.sid
            cache.set_login_rate_limit(sid, 5, 60)
            black_list_status = cache.is_black_listed(sid, 5)
            if not black_list_status: 
                return f(*args, **kwargs)
            else:
                socketio.emit('error', {"status": False,"msg": "Limite de tentativas atingido. Tente novamente mais tarde."}, to=sid)
                return
        return wrapper
    
    @socketio.on("connect")
    def handle_connect():
        print(f'usuario {request.sid} conectado ao servidor')

    @socketio.on('disconnect')
    def handle_disconnect():
        user_id = ws_cache.pop(request.sid, None)
        if user_id:
            leave_room(user_id)


    @socketio.on('login_websocket')
    @black_list
    def handle_login_websocket(msg):
        user_id = msg.get('token')
        if user_id is None or not isinstance(user_id, str):
            return socketio.emit('error', {'status': False, "msg": "voce esta sem token de autenticação, logue ou crie uma conta"}, to=request.sid)
        token_status, token_msg = database.run_db_operation(database.check_token_existence, token=user_id)
        if token_status:
            ws_cache[request.sid] = user_id
            join_room(user_id)
            return socketio.emit('success', {'status': True, "msg": "sucesso ao efetuar login pelo token no websocket"}, to=request.sid)
        else:
            return socketio.emit('error', {'status': False, "msg": "voce esta com um token invalido ou sessão expirada, relogue para criar uma nova sessão"}, to=request.sid)

    @socketio.on('post_recommendations')
    @socket_login_required
    def post_recommendations(msg, user_id): # seria bom um debounce ou no minimo delay
        ytrecommendations_array = msg.get('recommendations')
        if ytrecommendations_array is None:
            return socketio.emit('error', {'status': False, "msg": "a lista de recomendações feita pela extensão veio com valor None sendo o esperado lista"}, to=user_id)
        ytrecommendations = create_dict(ytrecommendations_array)
        if ytrecommendations:
            recommendations_status, recommendations_msg = database.run_db_operation(database.update_recommendations, token=user_id, recommendations=json.dumps(ytrecommendations))
            socketio.emit('new_recommendations', {"recommendations": ytrecommendations}, to=user_id)
           
    @socketio.on('get_recommendations')
    @socket_login_required
    def get_recommendations(user_id): # seria bom um debounce ou no minimo delay
        status, data = database.run_db_operation(database.get_user_from_token, token=user_id)
        recommendations = data.get('recommendations')
        if status and recommendations:
            recommendations_json = json.loads(recommendations)
            socketio.emit('new_recommendations', {"status": True, "recommendations": recommendations_json}, to=user_id)
        else:
            socketio.emit('error', {'status': False, "msg": "erro ao pegar recomendações, token esta invalido ou não tem nenhuma recomendação"}, to=user_id)

    @socketio.on('next')
    @socket_login_required
    def handle_next(user_id): #web_client //// seria bom um debounce ou no minimo delay
        socketio.emit("send_next", to=user_id)

    @socketio.on('pause')
    @socket_login_required
    def handle_pause(user_id): #web_client ///// seria bom um debounce ou no minimo delay
        socketio.emit('emit_pause', to=user_id)

    @socketio.on('get_video_from_client')
    @socket_login_required
    def get_video(message, user_id):
        try:
            url = message.get('url')
            if is_an_allowed_url(url):
                socketio.emit('change_video', {"url": url}, to=user_id)
        except Exception as e:
            socketio.emit('error', {'status': False, "msg": "o video que voce tentou enviar esta em um formato invalido"}) #adicionar logging
            
    @socketio.on('new_volume')
    @socket_login_required
    def new_volume(msg, user_id):    
        volume = msg.get('volume')
        volume_handler(volume, "change_volume", user_id)
                       
    @socketio.on('recive_volume')
    @socket_login_required
    def recive_volume(msg, user_id):   
        volume = msg.get('volume')
        volume_handler(volume, "sync_volume", user_id)
        

    @socketio.on('emit_volume_to_client')
    @socket_login_required
    def emit_volume_to_client(user_id):
        socketio.emit('get_volume', to=user_id)

    def volume_handler(volume, socket_event, user_id):
        if volume is not None:
            try:
                volume = int(volume)
                if 0 <= volume <= 100:
                    volume_status, volume_msg = database.run_db_operation(database.update_volume, volume=volume, token=user_id)
                    if volume_status:
                        socketio.emit(f'{socket_event}', {"status": True, "volume": volume}, to=user_id)
                    else:
                        socketio.emit("error", {"status": False, "msg": "o erro foi desencadeado pela expiração da sessão ou alteração do seu token, por favor, reconecte com sua conta"}, to=user_id)
                else:
                    socketio.emit('error', {"status": False, "msg": "erro ao registrar volume, entrada invalida, ele não estava no range permitido (0 a 100)"}, to=user_id)
            except Exception as e:
                print('erro no recive_volume, identificado do erro: ', e) #futuro log
                socketio.emit('error', {"status": False, "msg": "erro ao registrar volume, entrada invalida, tenha certeza de não tentar enviar dados invalidos ao servidor"}, to=user_id)


               
def is_an_allowed_url(url):
    if url is None:
        return False
    allowed = ("https://i.ytimg.com/", "https://img.youtube.com/", "https://www.youtube.com/", "https://youtu.be/")
    if isinstance(url, str):
        return url.startswith(allowed)
    return False

def sanitize_title(title):
    return html.escape(title) if isinstance(title, str) else None

def build_recommendation_entry(entry):
    title = sanitize_title(entry.get('titulo'))
    thumb = entry.get('thumb')
    url = entry.get('link')
    if title and is_an_allowed_url(url) and is_an_allowed_url(thumb):
        return title, {'url': url, 'thumb': thumb}
    return None, None

def create_dict(ytrecommendations_array):
    if isinstance(ytrecommendations_array, list) and len(ytrecommendations_array) > 0:
        try:
            limit = 20
            ytrecommendations = {}
            for i in ytrecommendations_array:
                if limit == 0:
                    break
                title, data = build_recommendation_entry(i)
                if title and data:
                    ytrecommendations[title] = data
                limit -= 1
            return ytrecommendations
        except Exception as e:
            print('erro na criação do dicionario de recomendação, indicador do erro: ', e)
            return {}
    else:
        return {}
