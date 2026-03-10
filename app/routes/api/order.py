
from flask import Blueprint, request, jsonify, session

from app import log, exceptions
from app.helpers.auth import login_required
from app.helpers import date_utils
from app.repositories.orders_repo import get_order_by_id
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
    data = request.args

    page = max(int(data.get('page', 1)), 1)
    per_page = min(max(int(data.get('per_page', 25)), 1), 100)
    filter_status = data.get('status', None)
    filter_name = data.get('search', '')

    orders = list_orders_service(
        page=page,
        per_page=per_page,
        filter_name=filter_name,
        filter_status=filter_status
    )

    return jsonify(orders)


@orders_api_bp.route('/delivery-orders')
@login_required
def delivery_orders():
    try:
        date = request.args.get('date')
        if not date:
            date = date_utils.create_now_gmt().strftime('%Y-%m-%d')

        response = list_orders_service(
            filter_status=['pending', 'paid', 'delivered'],
            date=date, 
            page=1, 
            per_page=1000
        )

        orders = []

        for o in response['orders']:
            customer = o['customers']

            if customer['latitude'] is None or customer['longitude'] is None:
                continue

            orders.append({
                'order_id': o['id'],
                'status': o['status'],
                'customer_name': customer['name'],
                'customer_phone': customer['phone'],
                'address': customer['address'],
                'latitude': float(customer['latitude']),
                'longitude': float(customer['longitude']),
                'delivery_price': float(o['delivery_price'] or 0),
                'total_amount': float(o['total_amount'] or 0),
                'products': [
                    {
                        'item_id': item['id'],
                        'name': item['products']['name'],
                        'unit': item['products']['unit'],
                        'quantity': float(item['quantity']),
                        'sell_price': float(item['sell_price']),
                        'is_prepared': item['is_prepared']
                    }
                    for item in o['order_items']
                ]
            })

        return jsonify(orders)

    except Exception as error:
        logger.error(f'{str(error)}')
        return jsonify({'error': str(error)}), 500


@orders_api_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    try:
        data = request.get_json()

        delivery_price = data.get('delivery_price', 0)
        customer_id = data['customer_id']
        delivery_type = data.get('delivery_type', 'pickup')
        status = data.get('status', 'pending')
        items = data.get('items', [])

        order_date = date_utils.convert_local_to_gmt(data.get('order_date'))

        result = create_order_service(
            user_id=session['user']['id'], 
            customer_id=customer_id, 
            items=items, 
            delivery_price=delivery_price, 
            delivery_type=delivery_type, 
            status=status, 
            order_date=order_date
        )
        return jsonify(result), 201

    except exceptions.ValidationError as e:
        return jsonify({'error': str(e)}), 400

    except exceptions.ServiceError as e:
        return jsonify({'error': str(e)}), 500

    except Exception as e:
        return jsonify({'error': 'Unexpected error'}), 500


@orders_api_bp.route('/orders/<int:order_id>', methods=['PUT'])
@login_required
def update_order(order_id):
    try:
        data = request.get_json()

        required_fields = ['delivery_type', 'items', 'status']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({
                'success': False,
                'message': f"Missing fields: {', '.join(missing)}"
            }), 400

        customer_id = data.get('customer_id')
        delivery_type = data['delivery_type']
        delivery_price = float(data.get('delivery_price', 0))
        items = data['items']
        items_to_delete = data.get('items_to_delete', [])
        status = data['status']

        order_date = None
        if data.get('order_date'):
            order_date = date_utils.convert_local_to_gmt(data['order_date'])

        result = update_order_service(
            user_id=session['user']['id'],
            order_id=order_id,
            customer_id=customer_id,
            delivery_type=delivery_type,
            delivery_price=delivery_price,
            items=items,
            items_to_delete=items_to_delete,
            status=status,
            order_date=order_date
        )
        return jsonify({'success': True, 'data': result}), 200

    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': 'Internal server error'}), 500


@orders_api_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_status(order_id):
    return jsonify(
        update_order_status_service(
            session['user']['id'],
            order_id,
            request.get_json().get('status')
        )
    )


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
                'product_variant_id': item['product_variants']['id'],
                'product_variant_name': item['product_variants']['name'],
                'product_variant_buy_price': item['product_variants']['buy_price'],
                'product_variant_sell_price': item['product_variants']['sell_price'],
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
