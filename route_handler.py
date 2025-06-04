from flask import redirect, url_for, request, render_template, jsonify, session
import database
import auth

def start_route_handler(app):
    @app.route('/')
    def home():
        auth_status, auth_msg = auth.check_token(session)
        if auth_status:
            return render_perfil()
        return render_template('login.html')

    @app.route('/login_page')
    def login_page():
        if not session.get('user_id'):
            return render_template('login.html')
        else:
            return render_perfil()
        
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('usuario')
        password = data.get('senha')
        return login_handler(username, password)

    @app.route('/signup')
    def signup():
        if not session.get('user_id'):
            return render_template("signup.html")
        else:
            return render_perfil()
        
    @app.route('/register', methods=["POST"])
    def register():
        data = request.get_json()
        username = data['usuario']
        password = data['senha']
        return register_handler(username, password)

    @app.route('/request_logout')
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
