
from flask import Blueprint, jsonify
from app.helpers.auth import login_required
from app.services.product_service import (
    list_active_product
)

products_api_bp = Blueprint('products_api', __name__)

@products_api_bp.route('/products/active')
@login_required
def api_active_products():
    try:
        products = list_active_product()
        return jsonify(products)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
