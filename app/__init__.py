
import os
from flask import Flask
from app.services.database import init_db
from app.utils.filters import register_filters
from dotenv import load_dotenv

load_dotenv()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

    init_db(app)

    register_filters(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.customers import customers_bp
    from app.routes.products import products_bp
    from app.routes.orders import orders_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app
