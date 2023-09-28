import mysql.connector

db_connection = None


def create_db_connection():
    global db_connection
    if db_connection is None:
        db_connection = mysql.connector.connect(
            host="gateway01.eu-central-1.prod.aws.tidbcloud.com",
            user="HAyA9NjBwvvtxbH.root",
            port=4000,
            password="zUUt46RT8kmqtWeF",
            database="password_manager",
        )
    return db_connection

