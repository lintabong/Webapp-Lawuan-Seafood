
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app import log
from app.helpers.auth import login_required
from app.repositories.orders_repo import (
    list_order_by_date, 
    get_order_by_id
)
from app.repositories.order_items_repo import update_item_is_prepared
from app.services.orders_service import (
    list_orders_service,
    create_order_service,
    update_order_service,
    update_order_status_service
)

orders_api_bp = Blueprint('orders_api', __name__)

logger = log.get_logger('API_ORDER')


@orders_api_bp.route('/orders')
@login_required
def orders():
    return jsonify(list_orders_service(request.args))


@orders_api_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    return jsonify(create_order_service(
        request.get_json(),
        session.get('user_id')
    ))


@orders_api_bp.route('/orders/<int:order_id>', methods=['PUT'])
@login_required
def update_order(order_id):
    return jsonify(update_order_service(order_id, request.get_json()))


@orders_api_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_status(order_id):
    return jsonify(update_order_status_service(
        order_id,
        request.get_json().get('status')
    ))


@orders_api_bp.route('/delivery-orders')
@login_required
def api_delivery_orders():
    try:
        access_token = session.get('access_token')
        if not access_token:
            return jsonify({'error': 'Unauthorized'}), 401

        date = request.args.get('date')
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        orders = list_order_by_date(date)

        return jsonify(orders)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@orders_api_bp.route('/order-items/<int:item_id>/prepared', methods=['PUT'])
@login_required
def update_item_prepared(item_id):
    try:
        data = request.get_json()

        response = update_item_is_prepared(
            item_id, 
            data.get('is_prepared', False)
        )

        return jsonify({'success': True, 'data': response})

    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 500


@orders_api_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def show_order(order_id):
    try:
        order_data = get_order_by_id(order_id)

        formatted_order = {
            'id': order_data['id'],
            'customer_id': order_data['customer_id'],
            'order_date': order_data['order_date'],
            'status': order_data['status'],
            'delivery_type': order_data['delivery_type'],
            'delivery_price': float(order_data['delivery_price']) if order_data['delivery_price'] else 0,
            'total_amount': float(order_data['total_amount']) if order_data['total_amount'] else 0,
            'customer_name': order_data['customers']['name'],
            'items': []
        }

        for item in order_data.get('order_items', []):
            formatted_order['items'].append({
                'id': item['id'],
                'product_id': item['product_id'],
                'quantity': float(item['quantity']),
                'buy_price': float(item['buy_price']),
                'sell_price': float(item['sell_price']),
                'product_name': item['products']['name'],
                'unit': item['products']['unit']
            })

        return jsonify(formatted_order), 200

    except Exception as e:
        logger.error(f'Error getting order: {str(e)}')
        return jsonify({'error': str(e)}), 500
