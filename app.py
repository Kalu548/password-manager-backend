import csv
import os
from functools import wraps

import jwt
from flask import Flask, g, jsonify, request, send_from_directory
from flask_cors import CORS

from utils import password, user, utilities

app = Flask(__name__)
CORS(app)



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
                token, utilities.JWT_SECRET, algorithms=['HS256'])
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


@app.route("/user/signup", methods=["POST"])
def user_signup():
    data = request.get_json()
    required_keys = ["username", "password", "email"]
    if not all(key in data for key in required_keys):
        return jsonify({
            "status": "error",
            "response": "Please provide all the required fields"
        }), 400
    try:
        master_key = utilities.generate_master_key()
        hashed_master_key = utilities.generate_password_hash(master_key)
        password_hash = utilities.generate_password_hash(data["password"])
        user_id = user.create_user(data["email"], data["username"], password_hash, hashed_master_key)
        token = utilities.create_jwt(data["username"], user_id, data["email"])
        return jsonify({
            "status": "success",
            "message": "User created successfully",
            "data": {
                "token": token,
                "master_key": master_key
            }
        })
    except Exception as e:
        if str(e) == "UserAlreadyExists":
            return jsonify({
                "status": "error",
                "response": "Username or email already exists",
            }), 400
        else:
            return jsonify({
                "status": "error",
                "response": str(e)
            }), 500


@app.route("/user/login", methods=["POST"])
def user_login():
    data = request.get_json()
    required_keys = ["email", "password", "master_key"]
    if not all(key in data for key in required_keys):
        return jsonify({
            "status": "error",
            "response": "Please provide all the required fields"
        }), 400
    try:
        user_info = user.get_user_from_email(data["email"])
        if not utilities.check_password_hash(data["password"], user_info["password"]):
            return jsonify({
                "status": "error",
                "response": "Incorrect password"
            }), 400
        if not utilities.check_password_hash(data["master_key"], user_info["master_key"]):
            return jsonify({
                "status": "error",
                "response": "Incorrect master key"
            }), 400
        token = utilities.create_jwt(user_info["username"], user_info["id"], user_info["email"])
        return jsonify({
            "status": "success",
            "message": "User logged in successfully",
            "data": {
                "token": token
            }
        })
    except Exception as e:
        if str(e) == "UserDoesNotExist":
            return jsonify({
                "status": "error",
                "response": "User does not exist"
            }), 400
        else:
            return jsonify({
                "status": "error",
                "response": str(e)
            }), 500

@app.route("/password/create", methods=["POST"])
@token_required
def create_password():
    data = request.get_json()
    required_keys = ["name", "username", "password", "url", "master_key"]
    if not all(key in data for key in required_keys):
        return jsonify({
            "status": "error",
            "response": "Please provide all the required fields"
        }), 400
    try:
        hash_password = utilities.encrypt_password(data["password"], data["master_key"])
        password_id = password.create_password(g.decoded_token["id"], data["name"], data["url"], data["username"], hash_password)
        return jsonify({
            "status": "success",
            "message": "Password created successfully",
            "data": {
                "id": password_id
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "response": str(e)
        }), 500


@app.route("/password/all", methods=["GET"])
@token_required
def get_all_passwords():
    try:
        passwords = password.get_all_passwords(g.decoded_token["id"])
        return jsonify({
            "status": "success",
            "message": "Passwords fetched successfully",
            "data": passwords
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "response": str(e)
        }), 500

@app.route("/password/delete/<pass_id>", methods=["GET"])
@token_required
def delete_password(pass_id):
    if not pass_id:
        return jsonify({
            "status": "error",
            "response": "Please provide the password id"
        }), 400
    try:
        if password.delete_password(pass_id, g.decoded_token["id"]):
            return jsonify({
                "status": "success",
                "message": "Password deleted successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "response": "Password does not exist"
            }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "response": str(e)
        }), 500

@app.route("/password/get/<pass_id>", methods=["GET"])
@token_required
def get_password(pass_id):
    if not pass_id:
        return jsonify({
            "status": "error",
            "response": "Please provide the password id"
        }), 400
    if not request.args.get("key"):
        return jsonify({
            "status": "error",
            "response": "Please provide the master key"
        }), 400
    try:
        master_key = request.args.get("key")
        password_data = password.get_password(pass_id, g.decoded_token["id"])
        password_data["password"] = utilities.decrypt_password(password_data["password"], master_key)
        return jsonify({
            "status": "success",
            "message": "Password fetched successfully",
            "data": password_data
        })
    except Exception as e:
        if str(e) == "PasswordDoesNotExist":
            return jsonify({
                "status": "error",
                "response": "Password does not exist"
            }), 400
        else:
            return jsonify({
                "status": "error",
                "response": str(e)
            }), 500
        

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
    if not request.args.get("key"):
        return jsonify({
            "status": "error",
            "response": "Please provide the master key"
        }), 400
    try:
        master_key = request.args.get("key")
        hash_password = utilities.encrypt_password(data["password"], master_key)
        if password.update_password(data["id"], data["name"], data["username"], hash_password, data["url"]):
            return jsonify({
                "status": "success",
                "message": "Password updated successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "response": "Password does not exist"
            }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "response": str(e)
        })

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
    passwords = password.user_password_list(user_id, master_key)
    filename = f"assets/download/passwords_{user_id}.csv"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode="w") as file:
        writer = csv.writer(file)
        writer.writerow(["Id", "Name", "Username", "Password", "Url", "Created At"])
        writer.writerows(passwords)
    return {
        "status": "success",
        "message": "Passwords exported successfully",
        "data": {
            "download_url": filename
        }
    }





if __name__ == '__main__':
    app.run(port=8000)