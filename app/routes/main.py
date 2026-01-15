
from flask import Blueprint, render_template
from app.models.customer import Customer
from app.models.product import Product

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard page"""
    customers = Customer.get_with_coordinates()
    products = Product.get_all()
    
    total_customers = len(customers)
    total_products = len(products)
    
    return render_template(
        'index.html',
        total_customers=total_customers,
        total_products=total_products
    )