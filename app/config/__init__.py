import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_DB = os.getenv('MYSQL_DB', 'seafood_db')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASS = os.getenv('MYSQL_PASS', '')
    
    DEPOT_LAT = float(os.getenv('DEPOT_LAT', -7.7956))
    DEPOT_LNG = float(os.getenv('DEPOT_LAN', 110.3695))
    DEPOT_NAME = 'Lawuan Seafood Depot'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    MYSQL_DB = 'seafood_db_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}