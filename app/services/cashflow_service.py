
from app.repositories.cash_repo import (
    insert_cashflow,
    update_cash_balance,
    delete_cashflow
)
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase

def _get_categories():
    auth()
    data = supabase.table('cashflow_categories') \
        .select('id, name') \
        .in_('name', ['Product Sales', 'Delivery Fees']) \
        .execute().data
    return {c['name']: c['id'] for c in data}

def create_cashflow(order_id, total, delivery):
    categories = _get_categories()

    if total > 0:
        insert_cashflow(
            categories['Product Sales'],
            total,
            f'Order #{order_id}',
            order_id
        )

    if delivery > 0:
        insert_cashflow(
            categories['Delivery Fees'],
            delivery,
            f'Delivery Order #{order_id}',
            order_id
        )

    return update_cash_balance(total + delivery)

def rollback_cashflow(order_id, total, delivery):
    delete_cashflow(order_id)
    return update_cash_balance(-(total + delivery))

