import database
def check_token(session):
    user_id = session.get('user_id')
    status, msg = database.run_db_operation(database.check_token_existence, token = user_id)
    return status, msg

def validate_password(password):
    if len(password) > 6:
        return True, "o password é valido"
    return False, "o password não atende os requesitos"

def validate_username_creation(username):
    if len(username) > 5:
        status, msg = database.run_db_operation(database.check_username_existence, username=username)
        if status == True:
            return False, "usuario ja existe"
        if status == False:
            return True, "usuario novo"
    return False, "usuario tem que ter pelo menos 5 caracteres"