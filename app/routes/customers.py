
from flask import (
    Blueprint, render_template, request, flash, redirect, url_for
)
from app.models.customer import Customer
from app.constants import DEPOT

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/')
def list():
    customers = Customer.get_all()
    return render_template(
        'customers/customers.html', 
        customers=customers, 
        depot=DEPOT
    )

@customers_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        latlng = request.form.get('latlng')

        latitude = None
        longitude = None

        if latlng:
            try:
                lat_str, lng_str = latlng.split(',')
                latitude = float(lat_str.strip())
                longitude = float(lng_str.strip())
            except ValueError:
                flash('Invalid latitude, longitude format', 'danger')
                return redirect(url_for('customers.create'))

        try:
            Customer.create(name, phone, address, latitude, longitude)
            flash('Customer created successfully', 'success')
            return redirect(url_for('customers.list'))
        except Exception as e:
            flash(f'Error saving customer: {e}', 'danger')

    return render_template('customers/create_customer.html')
