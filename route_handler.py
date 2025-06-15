from flask import redirect, url_for, request, render_template, jsonify, session
from functools import wraps
import database
from utilites.auth import AuthValidation
from cache import CacheHandler

def start_route_handler(app):
    cache = CacheHandler(5, 60)
    cache.start()
    
    def limit_account_handler_required(f):
        @wraps(f)
        def limit_account_handler(*args, **kwargs):
            ip = request.remote_addr
            cache.create_account_limit_handler(ip)
            status = cache.check_create_account_validation(ip)
            if status:
                return f(*args, **kwargs)
            return jsonify({'status': False, 'msg': 'voce esta no limite de contas criadas para um usuario'}), 400
        return limit_account_handler
    
    def blacklist_handler_required(f):
        @wraps(f)
        def blacklist_handler(*args, **kwargs):
            ip = request.remote_addr
            cache.set_login_rate_limit(ip)
            black_list_status = cache.is_black_listed(ip)
            if not black_list_status: 
                return f(*args, **kwargs)
            else:
                return jsonify({'status': False, 'msg': 'voce esta na blacklist para evitar bruteforce'}), 400
        return blacklist_handler
    
    def auth_handler_required(f):
        @wraps(f)
        def auth_handler(*args, **kwargs):
            auth = AuthValidation()
            return f(auth, *args, **kwargs)
        return auth_handler 
    
    def route_login_required(f):
        @wraps(f)
        def route_login_required_wrapper(*args, **kwargs):
            user_id = session.get('user_id')
            if user_id:
                status, data = database.run_db_operation(database.get_user_from_token, token=user_id)
                if status and data is not None:
                    return f(*args, **kwargs)
                return redirect(url_for('login_page'))
            else:
                return redirect(url_for('login_page'))
        return route_login_required_wrapper
        
    def route_unloged_required(f):
        @wraps(f)
        def route_unloged_required_wrapper(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return f(*args, **kwargs)
            else:
                return redirect(url_for('home'))
        return route_unloged_required_wrapper
    
    @app.route('/')
    @route_login_required
    def root():
        return redirect(url_for('home'))

    @app.route('/home')
    @route_login_required
    def home():
        return render_perfil()
    
    @app.route('/login_page')
    @route_unloged_required
    def login_page():
        return render_template('login.html')
        
    @app.route('/login', methods=['POST'])
    @route_unloged_required
    @blacklist_handler_required
    @auth_handler_required
    def login(auth):
        data = request.get_json()
        username = data.get('usuario')
        password = data.get('senha')
        response, status_code = auth.login_handler(username, password)
        if auth.session.get('user_id'):
            session['user_id'] = auth.session.get('user_id')
        return jsonify(response), status_code

    @app.route('/signup')
    @route_unloged_required
    def signup():
        return render_template("signup.html")
        
    @app.route('/register', methods=["POST"])
    @route_unloged_required
    @limit_account_handler_required
    @auth_handler_required
    def register(auth):
        data = request.get_json()
        username = data['usuario']
        password = data['senha']
        response, status_code = auth.register_handler(username, password)
        if auth.session.get('user_id'):
            session['user_id'] = auth.session.get('user_id')
        return jsonify(response), status_code

    @app.route('/request_logout')
    @route_login_required
    def request_logout():
        session.clear()
        return redirect(url_for('login_page'))

def render_perfil():
    return render_template('perfil.html')