import os
from functools import wraps

import jwt
import mysql.connector as mysql
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request, send_from_directory
from flask_cors import CORS

import data_utils

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
app = Flask(__name__)
CORS(app)

connPool = mysql.pooling.MySQLConnectionPool(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    ssl_ca="/etc/ssl/cert.pem",
    pool_name="myPool",
    port=4000,
    pool_size=20,
)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization')
            token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Token is missing.'}), 401
        try:
            decoded_token = jwt.decode(
                token, JWT_SECRET, algorithms=['HS256'])
            g.decoded_token = decoded_token
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token.'}), 401
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    return jsonify({
        "response": "Hello World"
    })


@app.route('/assets/<path:path>')
def send_files(path):
    return send_from_directory('assets', path)


@app.route("/password/export_all", methods=["GET"])
@token_required
def export_all_passwords():
    master_key = request.args.get("master_key")
    if master_key is None:
        return jsonify({
            "status": "error",
            "response": "Please provide master key"
        }), 400
    user_id = g.decoded_token["id"]
    conn = connPool.get_connection()
    response = data_utils.export_all_passwords(master_key, user_id, conn)
    return jsonify(response)


@app.route("/user/create", methods=["POST"])
def create_user():
    data = request.get_json()
    required_keys = ["username", "password", "email"]
    if not all(key in data for key in required_keys):
        return jsonify({
            "status": "error",
            "response": "Please provide all the required fields"
        }), 400

    data = {
        "username": data["username"],
        "password": data["password"],
        "email": data["email"]
    }
    conn = connPool.get_connection()
    response = data_utils.create_user(data, conn)
    return jsonify(response)


@app.route("/user/create_master_key", methods=["POST"])
@token_required
def master_key():
    data = request.get_json()
    required_keys = ["master_key"]
    if not all(key in data for key in required_keys):
        return jsonify({
            "status": "error",
            "response": "Please provide all the required fields"
        }), 400
    conn = connPool.get_connection()
    response = data_utils.update_master_key(
        data["master_key"], g.decoded_token["id"], conn)
    return jsonify(response)


@app.route("/user/login", methods=["POST"])
def login_user():
    data = request.get_json()
    required_keys = ["email", "password", "master_key"]
    if not all(key in data for key in required_keys):
        return jsonify({
            "status": "error",
            "response": "Please provide all the required fields"
        }), 400

    data = {
        "email": data["email"],
        "password": data["password"],
        "master_key": data["master_key"]
    }
    conn = connPool.get_connection()
    response = data_utils.login_user(data, conn)
    return jsonify(response)


@app.route("/password/create", methods=["POST"])
@token_required
def create_password():
    data = request.get_json()
    required_keys = ["name", "username", "password", "url"]
    if not all(key in data for key in required_keys):
        return jsonify({
            "status": "error",
            "response": "Please provide all the required fields"
        }), 400
    data = {
        "name": data["name"],
        "username": data["username"],
        "password": data["password"],
        "url": data["url"],
        "user_id": g.decoded_token["id"]
    }
    conn = connPool.get_connection()
    response = data_utils.create_password(data, conn)
    return jsonify(response)


@app.route("/password/all", methods=["GET"])
@token_required
def get_all_passwords():
    conn = connPool.get_connection()
    response = data_utils.get_all_passwords(g.decoded_token["id"], conn)
    return jsonify(response)


@app.route("/password/delete/<pass_id>", methods=["GET"])
@token_required
def delete_password(pass_id):
    if not pass_id:
        return jsonify({
            "status": "error",
            "response": "Please provide the password id"
        }), 400
    conn = connPool.get_connection()
    response = data_utils.delete_password(pass_id, g.decoded_token["id"], conn)
    return jsonify(response)


@app.route("/password/get/<pass_id>", methods=["GET"])
@token_required
def get_password(pass_id):
    if not pass_id:
        return jsonify({
            "status": "error",
            "response": "Please provide the password id"
        }), 400
    conn = connPool.get_connection()
    response = data_utils.get_password(pass_id, g.decoded_token["id"], conn)
    return jsonify(response)


@app.route("/password/update", methods=["POST"])
@token_required
def update_password():
    data = request.get_json()
    required_keys = ["id", "name", "username", "password", "url"]
    if not all(key in data for key in required_keys):
        return jsonify({
            "status": "error",
            "response": "Please provide all the required fields"
        }), 400
    data = {
        "id": data["id"],
        "name": data["name"],
        "username": data["username"],
        "password": data["password"],
        "url": data["url"],
        "user_id": g.decoded_token["id"]
    }
    conn = connPool.get_connection()
    response = data_utils.update_password(data, conn)
    return jsonify(response)


if __name__ == '__main__':
    app.run(port=8000)
