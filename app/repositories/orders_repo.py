
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase

def list_orders(filters, offset, limit):
    auth()
    query = supabase.table('orders').select(
        '''
        id,
        order_date,
        status,
        total_amount,
        delivery_price,
        delivery_type,
        customers!inner(id, name, phone, address),
        order_items(
            id,
            quantity,
            sell_price,
            products(name, unit),
            is_prepared
        )
        ''',
        count='exact'
    ).order('order_date', desc=True)

    if filters.get('status') and filters['status'] != 'all':
        query = query.eq('status', filters['status'])

    if filters.get('search'):
        query = query.ilike('customers.name', f"%{filters['search']}%")

    return query.range(offset, offset + limit - 1).execute()

def get_order(order_id):
    auth()
    return supabase.table('orders') \
        .select('*') \
        .eq('id', order_id) \
        .single() \
        .execute().data

def insert_order(data):
    auth()
    return supabase.table('orders').insert(data).execute().data[0]

def update_order(order_id, data):
    auth()
    supabase.table('orders').update(data).eq('id', order_id).execute()
