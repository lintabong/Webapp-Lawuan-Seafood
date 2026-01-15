
from flask import Blueprint, render_template
from app.models.product import Product

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
def list():
    """List all products"""
    products = Product.get_all()
    return render_template('products/products.html', products=products)
