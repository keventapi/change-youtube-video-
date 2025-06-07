import sqlite3
import uuid

def run_db_operation(callback, **kwargs):
    with sqlite3.connect('mydb.db') as connect:
        cursor = connect.cursor()
        username = kwargs.get('username')
        if username:
            kwargs['username'] = username.lower()
        return callback(cursor, connect, **kwargs)

def create_table(cursor, connect):
    table = cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user TEXT NOT NULL,
                        password TEXT NOT NULL,
                        token TEXT NOT NULL,
                        url TEXT,
                        volume INTEGER,
                        recommendations TEXT
    )""")
    connect.commit()
    
def check_username_existence(cursor, connect, username):
    cursor.execute("SELECT 1 FROM users WHERE user = ?", (username,))
    if cursor.fetchone():
        return True, "usuario ja existe"
    return False, "usuario novo"

def add_user(cursor, connect, username, password):
    value, msg = check_username_existence(cursor, connect, username)
    if value == False:
        token = create_token(cursor, connect)
        cursor.execute("INSERT INTO users (user, password, token, url, volume, recommendations) VALUES(?, ?, ?, ?, ?, ?)", (username, password, token, "", 50, '{}'))
        connect.commit()
        return True, "usuario criado com sucesso"
    return False, "nome de usuario ja esta sendo utilizado"

def get_user(cursor, connect, username, password):
    cursor.execute("SELECT * FROM users WHERE user = ? AND password = ?", (username, password,))
    user_data = cursor.fetchone()
    if user_data:
        return True, data_as_dict(user_data)
    else:
        return False, None

def get_user_from_token(cursor, connect, token):
    cursor.execute("SELECT * FROM users WHERE token = ?", (token,))
    user_data = cursor.fetchone()
    if user_data:
        return True, data_as_dict(user_data)
    else:
        return False, None

def check_token_existence(cursor, connect, token):
    cursor.execute("SELECT 1 FROM users WHERE token = ?",(token,))
    if cursor.fetchone():
        return True, "token ja existe"
    return False, "novo token gerado"
    
def create_token(cursor, connect):
    token = str(uuid.uuid4())
    value, msg = check_token_existence(cursor, connect, token)
    if value:
        return create_token(cursor, connect)
    else:
        return token

def delete_account(cursor, connect, username, password):
    cursor.execute("DELETE FROM users WHERE user = ? AND password = ?", (username, password))
    connect.commit()
    return True, "conta removida"

def edit_account(cursor, connect, username, password, new_username):
    cursor.execute("SELECT 1 FROM users WHERE user = ? AND password = ?", (username, password,))
    if cursor.fetchone():
        value, msg = check_username_existence(cursor, connect, new_username)
        if value == False:
            cursor.execute("UPDATE users set user = ? WHERE user = ? AND password = ?", (new_username, username, password))
            connect.commit()
            return True, f"usuario mudado para {new_username}"
        else:
            return False, f"o nome de usauario: {new_username} ja esta sendo usado"
    else:
        return True, "usuario ou senha errado"
     
def update_recommendations(cursor, connect, token, recommendations):
    cursor.execute("SELECT 1 FROM users WHERE token = ?", (token,))
    if cursor.fetchone():
        cursor.execute("UPDATE users set recommendations = ? WHERE token = ?", (recommendations, token,))
        connect.commit()
        return True, f"playlist atualizada com sucesso"
    else:
        return False, "erro ao atualizar a playlist, session token nn existe"

def update_volume(cursor, connect, token, volume):
    cursor.execute("SELECT 1 FROM users WHERE token = ?", (token,))
    if cursor.fetchone():
        cursor.execute("UPDATE users set volume = ? WHERE token = ?", (volume, token,))
        connect.commit()
        return True, "volume atualizado com sucesso"
    return False, "erro ao atualizar volume, token invalido"

def data_as_dict(data):
    return {'id': data[0], 'username': data[1], 'password': data[2], 'token': data[3], 'url': data[4], "volume": data[5], 'recommendations': data[6]}

run_db_operation(create_table)