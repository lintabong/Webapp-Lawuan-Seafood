
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'database': os.getenv('MYSQL_DB'),
    'user': os.getenv('MYSQL_USER'), 
    'password': os.getenv('MYSQL_PASS')
}

def init_db(app):
    """Initialize database configuration"""
    app.config['DB_CONFIG'] = DB_CONFIG

def get_db_connection():
    """Get MySQL database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None