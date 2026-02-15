
import os
from flask import Flask
from dotenv import load_dotenv

from app.logger import AppLogger

log = AppLogger()


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY', "dev-secret")

    from app.routes.delivery import delivery_bp
    app.register_blueprint(delivery_bp)

    from app.routes.cashflow import cashflow_bp
    app.register_blueprint(cashflow_bp)

    from app.routes.web import web_bp
    app.register_blueprint(web_bp, url_prefix='/')

    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
