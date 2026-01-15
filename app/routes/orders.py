
import os
from datetime import date
from flask import Blueprint, render_template, flash, redirect, url_for

from app.models.order import Order
from app.models.customer import Customer
from app.models.product import Product

orders_bp = Blueprint('orders', __name__)

DEPOT = {
    'lat': float(os.getenv('DEPOT_LAT', -7.7956)),
    'lng': float(os.getenv('DEPOT_LON', 110.3695)),
    'name': 'Lawuan Seafood Depot'
}

@orders_bp.route('/')
def list():
    orders = Order.get_all()
    return render_template(
        'orders/orders.html', 
        orders=orders
    )

@orders_bp.route('/create')
def create():
    customers = Customer.get_all()
    products = Product.get_all()
    return render_template(
        'orders/create_order.html', 
        customers=customers, 
        products=products
    )

@orders_bp.route('/')
def view(order_id):
    order = Order.get_by_id(order_id)
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('orders.list'))
    
    return render_template(
        'orders/view_order.html', 
        order=order
    )

@orders_bp.route('/route')
def route():
    today = date.today().isoformat()
    return render_template(
        'orders/order_route.html', 
        route_date=today, 
        depot=DEPOT
    )
