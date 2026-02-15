
from flask import Blueprint, render_template
from app.helpers.auth import login_required
from app.repositories import customer_repo

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customer-map')
@login_required
def customers_page():
    return render_template('customer/customers_map.html')

@customer_bp.route('/customer/add')
@login_required
def add_customer_page():
    return render_template('customer/customer_form.html', customer=None)


@customer_bp.route('/customer/edit/<int:customer_id>')
@login_required
def edit_customer_page(customer_id):
    try:
        customer = customer_repo.get_customer_by_id(customer_id)
        if not customer:
            return 'Customer not found', 404
        
        return render_template('customer/customer_form.html', customer=customer)
    
    except Exception as e:
        return f'Error: {str(e)}', 500


@customer_bp.route('/customer/save/<int:customer_id>', methods=['POST'])
@login_required
def save_customer(customer_id):
    # This route is not used anymore since we're using API calls
    # But keeping it here in case you want to use traditional form submission
    return "Please use API endpoints", 400
