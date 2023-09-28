from api.utils.db import create_db_connection

conn = create_db_connection()

cursor = conn.cursor()

user_table = """
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    created_at DATE NOT NULL DEFAULT CURRENT_DATE,
    master_key TEXT
);
"""

password_table = """
CREATE TABLE IF NOT EXISTS passwords (
    id VARCHAR(255) PRIMARY KEY NOT NULL,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(50) NOT NULL,
    password TEXT NOT NULL,
    url VARCHAR(255) NOT NULL,
    created_at DATE NOT NULL DEFAULT CURRENT_DATE,
    user_id VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

cursor.execute(user_table)
print("User table created")
cursor.execute(password_table)
print("Password table created")
