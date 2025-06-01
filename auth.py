import database
def check_token(session):
    user_id = session.get('user_id')
    status, msg = database.run_db_operation(database.check_token_existence, token = user_id)
    return status, msg