from mysql.connector import IntegrityError

from utils.db import create_db_connection
from utils.utilities import decrypt_password, generate_id


def create_password(user_id, name, url, username, password):
    conn = create_db_connection()
    cursor = conn.cursor()
    password_id = generate_id()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO passwords (id, name, username, password, url, user_id) VALUES (%s,%s,%s,%s,%s,%s)", (password_id, name, username, password, url, user_id))
        conn.commit()
        return password_id
    except Exception as e:
        if e == IntegrityError:
            raise("PasswordAlreadyExists")
        else:
            raise


def user_password_list(user_id, master_key):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM passwords WHERE user_id = %s", (user_id,))
    passwords = cursor.fetchall()
    transformed_result = []
    for i in passwords:
        transformed_result.append({
            "id": i[0],
            "name": i[1],
            "username": i[2],
            "password": decrypt_password(i[3], master_key),
            "url": i[4],
            "created_at": i[5]
        })
    return transformed_result


def get_password(password_id, user_id):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM passwords WHERE id = %s AND user_id = %s", (password_id, user_id))
    password = cursor.fetchone()
    if password:
        return {
            "id": password[0],
            "name": password[1],
            "username": password[2],
            "password": password[3],
            "url": password[4],
            "created_at": password[5],
            "user_id": password[6]
        }
    else:
        raise Exception("PasswordDoesNotExist")

def get_all_passwords(user_id):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM passwords WHERE user_id = %s", (user_id,))
    passwords = cursor.fetchall()
    transformed_result = []
    for i in passwords:
        transformed_result.append({
            "id": i[0],
            "name": i[1],
            "username": i[2],
            "url": i[4],
            "created_at": i[5],
            "user_id": i[6]
        })
    return transformed_result

def delete_password(password_id,user_id):
    conn = create_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM passwords WHERE id = %s AND user_id = %s", (password_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        raise (e)

def update_password(password_id, name, username, password, url):
    conn = create_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE passwords SET name = %s, username = %s, password = %s, url = %s WHERE id = %s", (name, username, password, url, password_id))
        conn.commit()
        return True
    except Exception as e:
        raise (e)


    