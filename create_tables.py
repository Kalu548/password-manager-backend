import os

import mysql.connector as mysql
from dotenv import load_dotenv

load_dotenv()
conn = mysql.connect(
    port=4000,
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    ssl_ca="/etc/ssl/cert.pem"
)

cursor = conn.cursor()


def create_table():
    user_table = """
    CREATE TABLE IF NOT EXISTS users(
        `id` VARCHAR(255) NOT NULL PRIMARY KEY UNIQUE,
        `username` varchar(100) NOT NULL UNIQUE,
        `email` VARCHAR(255) NOT NULL UNIQUE,
        `password` text NOT NULL,
        `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `master_key` text,
        `avatar_url` text
        );
    """
    password_table = """
    CREATE TABLE IF NOT EXISTS passwords (
        `id` VARCHAR(255) NOT NULL PRIMARY KEY UNIQUE,
        `name` VARCHAR(255)  NOT NULL,
        `username` VARCHAR(255)  NOT NULL,
        `password` text NOT NULL,
        `url` text NOT NULL,
        `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
        `user_id` VARCHAR(255) NOT NULL
        );
    """
    try:
        cursor.execute(user_table)
        print("User table created successfully")
        cursor.execute(password_table)
        print("Password table created successfully")
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)


create_table()
