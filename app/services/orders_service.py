

from datetime import datetime
from app import exceptions
from app import log
from app.repositories import (
    orders_repo,
    order_items_repo,
    transactions_repo,
    cash_repo,
    cash_ledger_repo,
)
from app.constants import VALID_STATUSES

logger = log.get_logger('ORDERS_SERVICE')


def _apply_cash_inflow(created_by, order_id, total, delivery, transaction_date):
    total_change = 0
    main_transaction_id = None

    if total > 0:
        main_transaction_id = transactions_repo.insert_transaction(
            category_id=1,
            transaction_type='sale',
            amount=total,
            desc=f'Order #{order_id}',
            reference_id=order_id,
            created_by=created_by,
            transaction_date=transaction_date
        )
        total_change += total

    if delivery > 0:
        transactions_repo.insert_transaction(
            category_id=2,
            transaction_type='sale',
            amount=delivery,
            desc=f'Delivery Fee for Order #{order_id}',
            reference_id=order_id,
            created_by=created_by,
            transaction_date=transaction_date
        )
        total_change += delivery

    balance = int(cash_repo.update_cash_balance(amount=int(total_change)))

    cash_ledger_repo.create_ledger(
        cash_id=1,
        amount=int(total_change),
        balance_after=balance,
        direction='in',
        transaction_id=main_transaction_id
    )

    return balance

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

def create_order_service(
        user_id, 
        customer_id, 
        items, 
        delivery_price, 
        delivery_type, 
        status, 
        order_date
    ):
    if not customer_id:
        raise exceptions.ValidationError('Customer required')

    if not items:
        raise exceptions.ValidationError('At least one item required')

    total = sum(i['quantity'] * i['sell_price'] for i in items)

    order = orders_repo.insert_order({
        'customer_id': customer_id,
        'order_date': order_date,
        'status': status,
        'total_amount': total,
        'delivery_price': delivery_price,
        'delivery_type': delivery_type,
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
        cash_balance = _apply_cash_inflow(
            created_by=user_id,
            order_id=order['id'],
            total=total,
            delivery=delivery_price,
            transaction_date=order_date
        )

    return {
        'success': True,
        'order_id': order['id'],
        'cash_balance': cash_balance
    }

def update_order_service(order_id, data):
    order = orders_repo.get_order_by_id(order_id)
    if not order:
        raise exceptions.ValidationError('Order not found')

    if order['status'] != 'pending':
        raise exceptions.ValidationError('Only pending orders editable')

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

def update_order_status_service(user_id, order_id, new_status):
    if new_status not in VALID_STATUSES:
        raise exceptions.ValidationError('Invalid status')

    order = orders_repo.get_order_by_id(order_id)
    if not order:
        raise exceptions.ValidationError('Order not found')

    old_status = order['status']
    orders_repo.update_order(order_id, {'status': new_status})

    total = float(order['total_amount'])
    delivery = float(order['delivery_price'])
    transaction_date = datetime.fromisoformat(order['order_date'])

    balance = None
    action = None

    if old_status in ['pending', 'cancelled'] and new_status in ['paid', 'delivered']:
        balance = _apply_cash_inflow(
            created_by=user_id,
            order_id=order_id,
            total=total,
            delivery=delivery,
            transaction_date=transaction_date
        )
        action = 'created'

    return {
        'success': True,
        'old_status': old_status,
        'new_status': new_status,
        'cashflow_action': action,
        'cash_balance': balance
    }
