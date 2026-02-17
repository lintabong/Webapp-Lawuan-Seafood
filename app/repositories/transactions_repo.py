
from datetime import datetime, timezone
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase


def insert_transaction(
        category_id, 
        transaction_type, 
        amount=0, 
        desc='', 
        reference_id=None, 
        created_by='',
        transaction_date=None
    ):
    auth()

    reference = None
    if category_id in [1, 2, '1', '2']:
        reference = 'orders'

    if category_id in [4, '4']:
        reference = 'transaction_items'

    if transaction_date is None:
        transaction_date = datetime.now(timezone.utc)

    response = supabase.table('transactions').insert({
        'category_id': category_id,
        'type': transaction_type,
        'amount': amount,
        'description': desc,
        'reference_type': reference,
        'reference_id': reference_id,
        'created_by': created_by,
        'transaction_date': transaction_date.isoformat()
    }).execute()

    if response.data:
        return response.data[0]['id']
    return None

def delete_transaction(order_id):
    auth()
    supabase.table('transactions') \
        .delete() \
        .eq('reference_type', 'order') \
        .eq('reference_id', order_id) \
        .execute()

def get_by_date_range(start, end, category_filter, page, per_page):
    auth()
    query = supabase.table('transactions') \
        .select('*', count='exact') \
        .gte('transaction_date', start) \
        .lt('transaction_date', end)

    if category_filter != 'all':
        query = query.eq('category_id', category_filter)

    offset = (page - 1) * per_page

    return query.order('transaction_date', desc=True) \
        .range(offset, offset + per_page - 1) \
        .execute()
