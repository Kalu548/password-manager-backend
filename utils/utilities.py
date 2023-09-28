import base64
import datetime
import os
import random

import bcrypt
import jwt
from cryptography.fernet import Fernet
from cuid2 import Cuid

JWT_SECRET = os.getenv("JWT_SECRET"),
def generate_id():
    new_id = Cuid(length=12).generate()
    return new_id

def generate_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode("utf-8")

def check_password_hash(password, hash):
    return bcrypt.checkpw(password.encode('utf-8'), hash.encode('utf-8'))


def generate_master_key():
    master_key = Fernet.generate_key()
    return base64.urlsafe_b64encode(master_key).decode()

def encrypt_password(password, master_key):
    cipher = Fernet(base64.urlsafe_b64decode(master_key))
    encrypted_password = cipher.encrypt(password.encode()).decode()
    return encrypted_password

def decrypt_password(password, master_key):
    cipher = Fernet(base64.urlsafe_b64decode(master_key))
    decrypted_password = cipher.decrypt(password.encode()).decode()
    return decrypted_password

def create_jwt(username, user_id, email):
    token = jwt.encode({
        "username": username,
        "id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, JWT_SECRET, algorithm="HS256")
    return token




