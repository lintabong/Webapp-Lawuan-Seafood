
from flask import Blueprint

api_bp = Blueprint('api', __name__)

from .customer import customer_api_bp
from .dashboard import dashboard_api_bp
from .order import orders_api_bp
from .product import products_api_bp
from .cashflow import cashflow_api_bp

api_bp.register_blueprint(customer_api_bp, url_prefix='/')
api_bp.register_blueprint(dashboard_api_bp, url_prefix='/')
api_bp.register_blueprint(orders_api_bp, url_prefix='/')
api_bp.register_blueprint(products_api_bp, url_prerfix='/')
api_bp.register_blueprint(cashflow_api_bp, url_prefix='/')
