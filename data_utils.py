import datetime
import os

import bcrypt
import jwt
from dotenv import load_dotenv
from mysql.connector import IntegrityError
from nanoid import generate

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")


def hashed_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def check_password(password, db_pass):
    return bcrypt.checkpw(password.encode('utf-8'), db_pass.encode('utf-8'))


def generate_token(username, user_id, email):
    token = jwt.encode({
        "username": username,
        "id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET, algorithm="HS256")
    return token


def update_master_key(key, user_id, conn):
    cur = conn.cursor()
    update_query = "UPDATE users SET master_key = %s WHERE id = %s"
    hashed_key = hashed_password(key)
    try:
        cur.execute(update_query, (hashed_key, user_id))
        conn.commit()
        return {
            "status": "success",
            "message": "Master key updated successfully",
            "data": {
                "key": key
            }
        }
    except IntegrityError as _e:
        return {
            "status": "error",
            "message": "Master key already exists",
            "data": str(_e)
        }
    finally:
        cur.close()
        conn.close()


def create_user(data, conn):
    cur = conn.cursor()

    insert_query = "INSERT INTO users(id, username, email, password, avatar_url) VALUES (%s, %s, %s, %s, %s)"
    user_id = generate()
    password = hashed_password(data['password'])
    user_data = (user_id, data['username'], data['email'], password,
                 "")
    try:
        cur.execute(insert_query, user_data)
        conn.commit()
        token = generate_token(data['username'], user_id, data['email'])
        return {
            "status": "success",
            "message": "User created successfully",
            "data": {
                "token": token,
            }
        }

    except IntegrityError as _e:
        return {
            "status": "error",
            "message": "Username or email already exists",
            "data": str(_e)
        }
    finally:
        cur.close()
        conn.close()


def create_password(data, conn):
    cur = conn.cursor()
    insert_query = "INSERT INTO passwords(id, user_id, name, url, username, password) VALUES (%s, %s, %s, %s, %s, %s)"
    password_id = generate()
    password_data = (password_id, data['user_id'], data['name'],
                     data['url'], data['username'], data['password'])
    try:
        cur.execute(insert_query, password_data)
        conn.commit()
        return {
            "status": "success",
            "message": "Password created successfully",
            "data": {
                "id": password_id
            }
        }
    except IntegrityError as _e:
        return {
            "status": "error",
            "message": "Name already exists",
            "data": str(_e)
        }
    finally:
        cur.close()
        conn.close()


def get_all_passwords(user_id, conn):
    cur = conn.cursor()
    select_query = "SELECT id, name, url, created_at FROM passwords WHERE user_id = %s"
    cur.execute(select_query, (user_id,))
    passwords = cur.fetchall()
    cur.close()
    conn.close()
    transformed_result = []
    for i in passwords:
        transformed_result.append({
            "id": i[0],
            "name": i[1],
            "url": i[2],
            "created_at": i[3]
        })
    return {
        "status": "success",
        "message": "Passwords fetched successfully",
        "data": transformed_result
    }


def delete_password(password_id, user_id, conn):
    cur = conn.cursor()
    delete_query = "DELETE FROM passwords WHERE id = %s AND user_id = %s"
    cur.execute(delete_query, (password_id, user_id))
    conn.commit()
    cur.close()
    conn.close()
    return {
        "status": "success",
        "message": "Password deleted successfully",
        "data": None
    }


def update_password(data, conn):
    cur = conn.cursor()
    update_query = "UPDATE passwords SET name = %s, url = %s, username = %s, password = %s WHERE id = %s AND user_id = %s"
    cur.execute(update_query, (data['name'], data['url'],
                data['username'], data['password'], data['id'], data['user_id']))
    conn.commit()
    cur.close()
    conn.close()
    return {
        "status": "success",
        "message": "Password updated successfully",
        "data": None
    }


def get_password(password_id, user_id, conn):
    cur = conn.cursor()
    select_query = "SELECT * FROM passwords WHERE id = %s AND user_id = %s"
    cur.execute(select_query, (password_id, user_id))
    password = cur.fetchone()
    cur.close()
    conn.close()
    if password:
        return {
            "status": "success",
            "message": "Password fetched successfully",
            "data": {
                "id": password[0],
                "name": password[1],
                "username": password[2],
                "password": password[3],
                "url": password[4],
                "created_at": password[5],
            }
        }
    return {
        "status": "error",
        "message": "Password not found",
        "data": None
    }


def login_user(data, conn):
    cur = conn.cursor()

    select_query = "SELECT * FROM users WHERE email = %s"
    cur.execute(select_query, (data['email'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        if check_password(data['password'], user[3]) and check_password(data['master_key'], user[5]):
            token = generate_token(user[1], user[0], user[2])
            return {
                "status": "success",
                "message": "User logged in successfully",
                "data": {
                    "token": token,
                }
            }
        return {
            "status": "error",
            "message": "Invalid password",
            "data": None
        }
    return {
        "status": "error",
        "message": "Invalid email",
        "data": None
    }
