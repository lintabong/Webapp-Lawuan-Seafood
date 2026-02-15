
from flask import Blueprint, jsonify, request

from app.helpers.auth import login_required
from app.repositories import customer_repo


customer_api_bp = Blueprint('customer_api', __name__)

@customer_api_bp.get('/customers')
@login_required
def get_customers():
    try:
        customers = customer_repo.get_all_customers()
        return jsonify(customers)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customer_api_bp.post('/customers')
@login_required
def create_customer():
    try:
        data = request.get_json()

        new_customer = customer_repo.insert_customer(data)

        return jsonify({
            'message': 'Customer created',
            'data': new_customer
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

from app.repositories.customer_repo import update_customer
from flask import request


@customer_api_bp.put('/customers/<int:customer_id>')
@login_required
def update_customer_api(customer_id):
    try:
        data = request.get_json()

        updated = update_customer(customer_id, data)

        if not updated:
            return jsonify({'error': 'Customer not found'}), 404

        return jsonify({
            'message': 'Customer updated',
            'data': updated
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
