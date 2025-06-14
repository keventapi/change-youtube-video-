from flask_socketio import emit, join_room, leave_room
from flask import request
import database
from functools import wraps
import json
import logging
import traceback
from cache import CacheHandler
from utilites.data_sanitization import RecommendationsSanitizer as recommendations

def start_event_handler(socketio):
    cache = CacheHandler(5, 60)
    cache.start()
    
    def throttle_handler(event_name):
        def throttle(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                sid = request.sid
                if cache.ws_event_throttle(sid, event_name):
                    return f(*args, **kwargs)
                socketio.emit('error', {'status': False, 'msg': f"O evento '{event_name}' está sendo enviado com muita frequência. Aguarde alguns segundos."}, to=sid)
                return None
            return wrapper
        return throttle
    
    
    def socket_login_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                sid = request.sid
                user_id = cache.ws_cache_get_user(sid)
                
                if user_id is None or not isinstance(user_id, str):
                    socketio.emit('auth_error', {'msg': 'autenticação falhou'}, to=sid)
                    return None
                
                return f(user_id=user_id, *args, **kwargs)
            except Exception as e:
                logging.error(f'erro ao checar se o usuario esta logado, identificador do erro: {e} \n{traceback.format_exc()}')
                return None
                
        return wrapper
    
    def black_list(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            sid = request.sid
            cache.set_login_rate_limit(sid)
            black_list_status = cache.is_black_listed(sid)
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
        try:
            user_id = cache.ws_cache_logout(request.sid)
            if user_id:
                leave_room(user_id)
        except Exception as e:
            logging.error(f'erro ao desconectar o usuario do websocket, identificador do erro: {e} \n{traceback.format_exc()}')

    @socketio.on('login_websocket')
    @black_list
    def handle_login_websocket(msg):
        user_id = msg.get('token')
        if user_id is None or not isinstance(user_id, str):
            return socketio.emit('error', {'status': False, "msg": "voce esta sem token de autenticação, logue ou crie uma conta"}, to=request.sid)
        token_status, token_msg = database.run_db_operation(database.check_token_existence, token=user_id)
        if token_status:
            cache.ws_cache_login(request.sid, user_id)
            join_room(user_id)
            return socketio.emit('success', {'status': True, "msg": "sucesso ao efetuar login pelo token no websocket"}, to=request.sid)
        else:
            return socketio.emit('error', {'status': False, "msg": "voce esta com um token invalido ou sessão expirada, relogue para criar uma nova sessão"}, to=request.sid)

    @socketio.on('post_recommendations')
    @throttle_handler('post_recommendations')
    @socket_login_required
    def post_recommendations(msg, user_id): # seria bom um debounce ou no minimo delay
        ytrecommendations_array = msg.get('recommendations')
        if ytrecommendations_array is None:
            return socketio.emit('error', {'status': False, "msg": "a lista de recomendações feita pela extensão veio com valor None sendo o esperado lista"}, to=user_id)
        ytrecommendations = recommendations.create_dict(ytrecommendations_array)
        if ytrecommendations:
            recommendations_status, recommendations_msg = database.run_db_operation(database.update_recommendations, token=user_id, recommendations=json.dumps(ytrecommendations))
            socketio.emit('new_recommendations', {"recommendations": ytrecommendations}, to=user_id)
           
    @socketio.on('get_recommendations')
    @throttle_handler('get_recommendations')
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
    @throttle_handler('next')
    @socket_login_required
    def handle_next(user_id): #web_client //// seria bom um debounce ou no minimo delay
        socketio.emit("send_next", to=user_id)

    @socketio.on('pause')
    @throttle_handler('pause')
    @socket_login_required
    def handle_pause(user_id): #web_client ///// seria bom um debounce ou no minimo delay
        socketio.emit('emit_pause', to=user_id)

    @socketio.on('get_video_from_client')
    @throttle_handler('get_video_from_client')
    @socket_login_required
    def get_video(message, user_id):
        try:
            url = message.get('url')
            if recommendations.is_an_allowed_url(url):
                socketio.emit('change_video', {"url": url}, to=user_id)
        except Exception as e:
            socketio.emit('error', {'status': False, "msg": "o video que voce tentou enviar esta em um formato invalido"}) #adicionar logging
            
    @socketio.on('new_volume')
    @throttle_handler('new_volume')
    @socket_login_required
    def new_volume(msg, user_id):    
        volume = msg.get('volume')
        volume_handler(volume, "change_volume", user_id)
                       
    @socketio.on('recive_volume')
    @throttle_handler('recive_volume')
    @socket_login_required
    def recive_volume(msg, user_id):   
        volume = msg.get('volume')
        volume_handler(volume, "sync_volume", user_id)
        

    @socketio.on('emit_volume_to_client')
    @throttle_handler('emit_volume_to_client')
    @socket_login_required
    def emit_volume_to_client(user_id):
        socketio.emit('get_volume', to=user_id)

    def validate_volume(volume):
        if volume is None:
            return False
        
        if isinstance(volume, int):
            return 0 <= volume <= 100
        
        return False
        

    def volume_handler(volume, socket_event, user_id):
            try:
                if validate_volume(volume):
                    volume_status, volume_msg = database.run_db_operation(database.update_volume, volume=volume, token=user_id)
                    if volume_status:
                        socketio.emit(socket_event, {"status": True, "volume": volume}, to=user_id)
                    else:
                        socketio.emit("error", {"status": False, "msg": volume_msg}, to=user_id)
                else:
                    socketio.emit('error', {"status": False, "msg": "erro ao registrar volume, entrada invalida, ele não estava no range permitido (0 a 100)"}, to=user_id)
            except Exception as e:
                print('erro no recive_volume, identificado do erro: ', e) #futuro log
                socketio.emit('error', {"status": False, "msg": "erro ao registrar volume, falha no sistema"}, to=user_id)


