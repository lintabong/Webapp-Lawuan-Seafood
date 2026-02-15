
from flask import Blueprint, render_template
from app.helpers.auth import login_required

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/my-orders')
@login_required
def orders():
    return render_template('order/orders.html')


@orders_bp.route('/orders/create')
@login_required
def create_order():
    return render_template('order/create_order.html')


@orders_bp.route('/orders/edit')
@login_required
def edit_order():
    return render_template('order/edit_order.html')
