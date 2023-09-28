from mysql.connector import IntegrityError

from utils.db import create_db_connection
from utils.utilities import generate_id


def create_user(email, username, password, master_key):
    conn = create_db_connection()
    cursor = conn.cursor()
    user_id = generate_id()
    try:
        cursor.execute("INSERT INTO users (id, username, email, password, master_key) VALUES (%s,%s,%s,%s,%s)", (user_id, username, email, password, master_key))
        conn.commit()
        return user_id
    except IntegrityError:
            raise Exception("UserAlreadyExists")
    except:
        raise

def get_user(user_id):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "password": user[3],
            "created_at": user[4],
            "master_key": user[5]
        }
    else:
        raise Exception("UserDoesNotExist")
    
def get_user_from_email(email):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if user:
        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "password": user[3],
            "created_at": user[4],
            "master_key": user[5]
        }
    else:
        raise Exception("UserDoesNotExist")
        
def update_user(user_id, username, email, password, master_key):
    conn = create_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET username = %s, email = %s, password = %s, master_key = %s WHERE id = %s", (username, email, password, master_key, user_id))
        conn.commit()
        return True
    except Exception as e:
        raise Exception(e)

def delete_user(user_id):
    conn = create_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        raise (e)
    