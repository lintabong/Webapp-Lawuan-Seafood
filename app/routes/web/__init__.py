
from flask import Blueprint

web_bp = Blueprint('web', __name__)

from .customer import customer_bp
from .product import products_bp
from .dashboard import dashboard_bp
from .main import main_bp
from .order import orders_bp
from .cashflow import cashflow_bp

web_bp.register_blueprint(customer_bp, url_prefix='/')
web_bp.register_blueprint(products_bp, url_prefix='/')
web_bp.register_blueprint(dashboard_bp, url_prefix='/')
web_bp.register_blueprint(main_bp, url_prefix='/')
web_bp.register_blueprint(orders_bp, url_prefix='/')
web_bp.register_blueprint(cashflow_bp, url_prefix='/')
