
from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY', "dev-secret")

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.routes.orders import orders_bp
    app.register_blueprint(orders_bp)

    from app.routes.products import products_bp
    app.register_blueprint(products_bp)

    from app.routes.delivery import delivery_bp
    app.register_blueprint(delivery_bp)

    from app.routes.customers import customers_bp
    app.register_blueprint(customers_bp)

    from app.routes.cashflow import cashflow_bp
    app.register_blueprint(cashflow_bp)

    return app
