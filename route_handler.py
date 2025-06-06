from flask import redirect, url_for, request, render_template, jsonify, session
from functools import wraps
import database
import auth

def start_route_handler(app):
    def route_login_required(f):
        @wraps(f)
        def route_login_required_wrapper(*args, **kwargs):
            user_id = session.get('user_id')
            if user_id:
                return f(*args, **kwargs)
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
    def login():
        data = request.get_json()
        username = data.get('usuario')
        password = data.get('senha')
        return login_handler(username, password)

    @app.route('/signup')
    def signup():
        return render_template("signup.html")
        
    @app.route('/register', methods=["POST"])
    @route_unloged_required
    def register():
        data = request.get_json()
        username = data['usuario']
        password = data['senha']
        return register_handler(username, password)

    @app.route('/request_logout')
    @route_login_required
    def request_logout():
        session.clear()
        return redirect(url_for('login_page'))

def render_perfil():
    return render_template('perfil.html')

def credentials_handler(username, password):
    password_status, password_msg = auth.validate_password(password)
    username_status, username_msg = auth.validate_username_creation(username)
    msg = ''
    
    if not password_status or not username_status:
        if not password_status:
            msg += password_msg + " and "
        if not username_status:
            msg += username_msg
    else:
        return True, "crecenciais validas"
    return False, msg

def login_handler(username, password):
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"status": False, "msg": "os campos tem que ser string", "token": False})
    username = username.lower()
    status, data = database.run_db_operation(database.get_user, username=username, password=password)
    if status:
        token = data.get('token')
        if token:
            session['user_id'] = token
            return jsonify({"status": True, "msg": "login efetuado", "token": data['token']})
    return jsonify({"status": False, "msg": "erro ao efetuar login, usuario ou senha invalidos", "token": False})

def register_handler(username, password):
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"status": False, "msg": "os campos tem que ser string", "token": False})
    username = username.lower()
    credential_status, credential_msg = credentials_handler(username, password)
    if credential_status == False:
        return jsonify({"status": False, "msg": credential_msg})
        
    status, msg = database.run_db_operation(database.add_user, username=username, password=password)
    if status == True:
            login_response = login_handler(username, password)
            return login_response
    return jsonify({"status": False, "msg": "usuario ja existe"})
