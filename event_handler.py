from flask_socketio import emit, join_room
import database
import json

ws_cache = {}
def start_event_handler(socketio, request):
    def login_required(f):
        def wrapper(*args, **kwargs):
            user_id = ws_cache.get(request.sid)
            if not user_id:
                socketio.emit('auth_error', {'msg': 'autenticação falhou'})
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
            status, msg = database.run_db_operation(database.check_token_existence, token=user_id)
            if status:
                ws_cache[request.sid] = user_id
                print(ws_cache)
                join_room(user_id)
            else:
                print('token inject') #emit de erro de auth (meelhoria futura)
            
    @socketio.on('post_recommendations')
    @login_required
    def post_recommendations(msg):
        ytrecommendations = {}
        ytrecommendations_array = msg.get('recommendations')
        ytrecommendations = create_dict(ytrecommendations_array)

        if ytrecommendations:
            user_id = ws_cache.get(request.sid)
            msg = database.run_db_operation(database.update_recommendations, token=user_id, recommendations=json.dumps(ytrecommendations))
        socketio.emit('new_recommendations', {"recommendations": ytrecommendations}, to=user_id)

    @socketio.on('get_recommendations')
    @login_required
    def get_recommendations():
        user_id = ws_cache.get(request.sid)
        status, data = database.run_db_operation(database.get_user_from_token, token=user_id)
        if status:
            recommendations = data.get('recommendations')
            if recommendations:
                recommendations_json = json.loads(recommendations)
                socketio.emit('new_recommendations', {"recommendations": recommendations_json}, to=user_id)

            
    @socketio.on('next')
    @login_required
    def handle_next(): #web_client
        user_id = ws_cache.get(request.sid)
        socketio.emit("send_next", to=user_id)

    @socketio.on('pause')
    @login_required
    def handle_pause(): #web_client
        user_id = ws_cache.get(request.sid)
        socketio.emit('emit_pause', to=user_id)

    @socketio.on('get_video_from_client')
    @login_required
    def get_video(message): #web_client
        user_id = ws_cache.get(request.sid)
        socketio.emit('change_video', {"url": message['url']}, to=user_id)

    @socketio.on('new_volume')
    @login_required
    def new_volume(message): #web_client
        volume = message.get('volume')
        if volume:
            try:
                volume = int(volume)
                user_id = ws_cache.get(request.sid)
                msg = database.run_db_operation(database.update_volume, volume=volume, token=user_id)
                socketio.emit('change_volume', {"volume": volume}, to=user_id)
            except Exception as e:
                print('error no evento new_volume, tipo do erro: ', e)
        
    @socketio.on('emit_volume_to_client')
    @login_required
    def emit_volume_to_client(): #web client
        user_id = ws_cache.get(request.sid)
        socketio.emit('get_volume', to=user_id)

    @socketio.on('recive_volume')
    @login_required
    def recive_volume(msg):
        user_id = ws_cache.get(request.sid)      
        volume = msg.get('volume')
        if volume:
            try:
                volume = int(volume)
                msg = database.run_db_operation(database.update_volume, volume=volume, token=user_id)
                socketio.emit('sync_volume', {"volume": str(volume)}, to=user_id)
            except Exception as e:
                print('erro no recive_volume, identificado do erro: ', e)

                
def create_dict(ytrecommendations_array):
    if isinstance(ytrecommendations_array, list) and len(ytrecommendations_array) > 0:
        try:
            ytrecommendations = {}
            for i in ytrecommendations_array:
                ytrecommendations[i["titulo"]] = {'url': i['link'], 'thumb': i['thumb']}
            return ytrecommendations
        except Exception as e:
            print('erro na criação do dicionario de recomendação, indicador do erro: ', e)
    else:
        return None
