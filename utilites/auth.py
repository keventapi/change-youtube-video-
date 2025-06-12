import database
from flask import jsonify
import logging

class AuthValidation:
    def __init__(self, session):
        self.session = session
        
    def check_token(self):
        try:
            user_id = self.session.get('user_id')
            if user_id:
                if isinstance(user_id, str):
                    status, msg = database.run_db_operation(database.check_token_existence, token = user_id)
                    return status, msg
            return False, "problema na checagem do token"
        except Exception as e:
            logging.error(f"erro na função check_token, idenficiador do erro: {e}")
            return False, "erro no sistema, por favor tente novamente mais tarde"

    def validate_password(self, password):
        if password:
            if len(password) > 6:
                return True, "o password é valido"
        return False, "o password não atende os requesitos"

    def validate_username_creation(self, username):
        try:
            if username:
                if len(username) > 5:
                    status, msg = database.run_db_operation(database.check_username_existence, username=username)
                    if not status:
                        return True, msg
                    return False, msg
                return False, "usuario tem que ter pelo menos 5 caracteres"
        except Exception as e:
            logging.error(f'erro na função validate_username_creation, identificador do erro: {e}')
            return False, "erro no sistema, por favor tente novamente mais tarde"
    
    def create_credential_msg_error(self, username_status, password_status):
        msg = ''
        if not password_status:
            msg += "o password não atende os requesitos e "
        if not username_status:
            msg += "username não atende os requesitos"
        return msg
    
    def credentials_handler(self, username, password):
        password_status, password_msg = self.validate_password(password)
        username_status, username_msg = self.validate_username_creation(username)
        if not password_status or not username_status:
            msg = self.create_credential_msg_error(username_status, password_status)
            return False, msg
        else:
            return True, "crecenciais validas"
        
    def check_credential_validation(self, username, password):
        if username and password:
            if isinstance(username, str) and isinstance(password, str):
                status, msg = self.credentials_handler(username, password)
                if status:
                    return True, msg
                return False, msg
        return False, "credenciais invalidas, elas não estão no formato esperado"

    def login_handler(self, username, password):
        try:
            username = username.lower()
            valid, msg = self.check_credential_validation(username, password)
            if not valid:
                return jsonify({"status": False, "msg": msg, "token": False}), 400
            status, data = database.run_db_operation(database.get_user, username=username, password=password)
            if status:
                token = data.get('token')
                if token:
                    self.session['user_id'] = token
                    return jsonify({"status": True, "msg": "login efetuado", "token": data['token']}), 200
            return jsonify({"status": False, "msg": "erro ao efetuar login, usuario ou senha invalidos", "token": False}), 400
        except Exception as e:
            logging.error(f'erro no login_handler, especificação do erro: {e}')
            return jsonify({"status": False, "msg": "erro ao efetuar login, sistema com erro", "token": False}), 400
            

    def register_handler(self, username, password):
        try:
            username = username.lower()
            valid, msg = self.check_credential_validation(username, password)
            if not valid:
                return jsonify({"status": False, "msg": msg, "token": False}), 400
            status, msg = database.run_db_operation(database.add_user, username=username, password=password)
            if status == True:
                login_response = self.login_handler(username, password)
                if login_response[1] == 200:
                    login_data = login_response[0].get_json()
                    return jsonify(login_data), 201
                else:
                    return jsonify({"status": False, "msg": "erro ao efetuar login automatico, mas criação de usuario foi feita"}), 201
            return jsonify({"status": False, "msg": "usuario ja existe"}), 400
        except Exception as e:
            logging.error(f'erro no login_handler, especificação do erro: {e}')
            return jsonify({"status": False, "msg": "erro ao efetuar login, sistema com erro", "token": False}), 400
