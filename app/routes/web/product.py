
from flask import Blueprint, render_template
from app import log
from app.helpers.auth import login_required

logger = log.get_logger('WEB_PRODUCT')

products_bp = Blueprint('products', __name__)


@products_bp.route('/my-products')
@login_required
def products():
    return render_template('product/list_product.html')
