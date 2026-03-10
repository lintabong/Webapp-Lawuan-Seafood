
from app import exceptions
from app import log
from app.repositories import orders_repo
from app.constants import (
    VALID_STATUSES, 
    INSERT_CASHFLOW_STATUSES, 
    IDLE_CASHFLOW_STATUSES
)
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase
from app.helpers import date_utils

logger = log.get_logger('ORDERS_SERVICE')


def list_orders_service(
        filter_name='',
        filter_status=None,        # None | 'pending' | 'paid' | etc | ['pending','paid']
        delivery_type=None,        # None | 'delivery' | 'pickup'
        date=None,                 # 'YYYY-MM-DD'
        require_coords=False,      # for routing/maps
        page=1,
        per_page=25,
        order_desc=True
    ):
    response = orders_repo.list_orders(
        filter_name=filter_name,
        filter_status=filter_status,
        delivery_type=delivery_type,
        date=date,
        require_coords=require_coords,
        offset=(page - 1) * per_page,
        limit=per_page,
        order_desc=order_desc
    )

    return {
        'orders': response['data'],
        'total': response['count'],
        'page': page,
        'per_page': per_page,
        'total_pages': (response['count'] + per_page - 1) // per_page
    }

def create_order_service(
        user_id:str, 
        customer_id:int, 
        items=[], 
        delivery_price=0, 
        delivery_type='delivery', 
        status='pending', 
        order_date=date_utils.create_now_gmt()
    ):
    if not customer_id:
        raise exceptions.ValidationError('Customer required')

    if not items:
        raise exceptions.ValidationError('At least one item required')

    auth()
    payload = {
        'p_customer_id': customer_id,
        'p_created_by': user_id,
        'p_order_date': order_date.isoformat(),
        'p_status': status,
        'p_delivery_price': delivery_price,
        'p_delivery_type': delivery_type,
        'p_items': items
    }
    result = supabase.rpc('create_order_full', payload).execute().data[0]

    return {
        'success': True,
        'order_id': result['order_id'],
        'transaction_id': result['transaction_id'],
        'cash_balance': result['current_balance']
    }

def update_order_service(
        user_id: str,
        order_id=1,
        customer_id=1,
        delivery_type='delivery',
        delivery_price=0,
        items=[],
        items_to_delete=[],
        status='pending',
        order_date=date_utils.create_now_gmt()
    ):
    order = orders_repo.get_order_by_id(order_id)
    if not order:
        raise exceptions.ValidationError('Order not found')

    auth()

    if order['status'] in ['paid','delivered', 'picked up'] and status == 'cancelled':
        result = supabase.rpc('cancel_order_with_reversal', {
            'p_order_id':order['id'],
            'p_cash_id': 1,
            'p_voided_by': user_id
        }).execute().data[0]

        return {
            'success': True,
            'order_id': result['order_id'],
            'cash_balance': result['current_balance']
        }

    result = supabase.rpc('update_order_full', {
        'p_order_id': order_id,
        'p_customer_id': customer_id,
        'p_created_by': user_id,
        'p_order_date': order_date.isoformat(),
        'p_status': status,
        'p_delivery_price': delivery_price,
        'p_delivery_type': delivery_type,
        'p_items': items,
        'p_items_to_delete': items_to_delete
    }).execute().data[0]

    return {
        'success': True,
        'order_id': result['out_order_id'],
        'transaction_id': result['out_transaction_id'],
        'cash_balance': result['out_current_balance']
    }

def update_order_status_service(user_id, order_id, new_status):
    if new_status not in VALID_STATUSES:
        raise exceptions.ValidationError('Invalid status')

    order = orders_repo.get_order_by_id(order_id)
    if not order:
        raise exceptions.ValidationError('Order not found')

    old_status = order['status']
    orders_repo.update_order(order_id, {'status': new_status})

    balance = None
    action = None

    if old_status in IDLE_CASHFLOW_STATUSES and new_status in INSERT_CASHFLOW_STATUSES:
        auth()
        result = supabase.rpc('apply_cash_inflow', {
            'p_created_by': user_id,
            'p_order_id': order_id,
            'p_total': float(order['total_amount']),
            'p_delivery': float(order['delivery_price']),
            'p_transaction_date': order['order_date'],
        }).execute().data[0]
        balance = result['current_balance']
        action = 'created'

    return {
        'success': True,
        'old_status': old_status,
        'new_status': new_status,
        'cashflow_action': action,
        'cash_balance': balance
    }
