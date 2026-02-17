
from app import exceptions
from app.repositories import (
    orders_repo,
    order_items_repo
)
from app.services import cashflow_service
from app.constants import VALID_STATUSES

def list_orders_service(params):
    page = max(int(params.get('page', 1)), 1)
    per_page = min(max(int(params.get('per_page', 25)), 1), 100)
    offset = (page - 1) * per_page

    response = orders_repo.list_orders(params, offset, per_page)

    return {
        'orders': response.data,
        'total': response.count,
        'page': page,
        'per_page': per_page,
        'total_pages': (response.count + per_page - 1) // per_page
    }

def create_order_service(data, user_id):
    if not data.get('customer_id'):
        raise exceptions.ValidationError('Customer required')

    items = data.get('items', [])
    if not items:
        raise exceptions.ValidationError('At least one item required')

    total = sum(i['quantity'] * i['sell_price'] for i in items)
    delivery = data.get('delivery_price', 0)

    order = orders_repo.insert_order({
        'customer_id': data['customer_id'],
        'order_date': data.get('order_date'),
        'status': data.get('status', 'pending'),
        'total_amount': total,
        'delivery_price': delivery,
        'delivery_type': data.get('delivery_type', 'pickup'),
        'created_by': user_id
    })

    order_items_repo.insert_items([
        {
            'order_id': order['id'],
            **i
        } for i in items
    ])

    cash_balance = None
    if order['status'] in ['paid', 'delivered']:
        cash_balance = cashflow_service.create_cashflow(order['id'], total, delivery)

    return {
        'success': True,
        'order_id': order['id'],
        'cash_balance': cash_balance
    }

def update_order_service(order_id, data):
    order = orders_repo.get_order_by_id(order_id)
    if not order:
        return 'Order not found', 404

    if order['status'] != 'pending':
        return 'Only pending orders editable', 400

    subtotal = sum(i['quantity'] * i['sell_price'] for i in data['items'])
    delivery = data.get('delivery_price', 0)

    orders_repo.update_order(order_id, {
        'order_date': data['order_date'],
        'customer_id': data['customer_id'],
        'delivery_type': data['delivery_type'],
        'delivery_price': delivery,
        'status': data.get('status', order['status']),
        'total_amount': subtotal
    })

    for item_id in data.get('items_to_delete', []):
        order_items_repo.delete_item(item_id, order_id)

    for item in data['items']:
        if item.get('id'):
            order_items_repo.update_item(item['id'], item)
        else:
            order_items_repo.insert_items([{**item, 'order_id': order_id}])

    return {'success': True, 'order_id': order_id}

def update_order_status_service(order_id, new_status):
    if new_status not in VALID_STATUSES:
        return {'error': 'Invalid status'}, 400

    order = orders_repo.get_order_by_id(order_id)
    if not order:
        return {'error': 'Order not found'}, 404

    old = order['status']
    orders_repo.update_order(order_id, {'status': new_status})

    total = float(order['total_amount'])
    delivery = float(order['delivery_price'])

    if old in ['pending', 'cancelled'] and new_status in ['paid', 'delivered']:
        balance = cashflow_service.create_cashflow(order_id, total, delivery)
        action = 'created'
    elif old in ['paid', 'delivered'] and new_status == 'cancelled':
        balance = cashflow_service.rollback_cashflow(order_id, total, delivery)
        action = 'deleted'
    else:
        balance = None
        action = None

    return {
        'success': True,
        'old_status': old,
        'new_status': new_status,
        'cashflow_action': action,
        'cash_balance': balance
    }
