
from app import log
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase

logger = log.get_logger('ORDERS_REPO')


def list_orders(
        filter_name='',
        filter_status=None,   # None | 'pending' | 'paid' | etc | ['pending','paid']
        delivery_type=None,   # None | 'delivery' | 'pickup'
        date=None,            # 'YYYY-MM-DD'
        require_coords=False, # for routing/maps
        offset=0,
        limit=25,
        order_desc=True
    ):
    auth()
    query = supabase.table('orders').select(
        '''
        id,
        order_date,
        status,
        total_amount,
        delivery_price,
        delivery_type,
        customers!inner(
            name,
            phone,
            address,
            latitude,
            longitude
        ),
        order_items(
            id,
            product_id,
            product_variant_id,
            product_variants(id, name, unit, buy_price, sell_price),
            quantity,
            sell_price,
            products(name, unit),
            is_prepared
        )
        ''',
        count='exact'
    )

    query = query.order('order_date', desc=order_desc)

    if filter_status:
        if isinstance(filter_status, list):
            query = query.in_('status', filter_status)
        else:
            query = query.eq('status', filter_status)

    if delivery_type:
        query = query.eq('delivery_type', delivery_type)

    if filter_name:
        query = query.ilike('customers.name', f"%{filter_name}%")

    if date:
        query = query.gte('order_date', f'{date}T00:00:00')
        query = query.lte('order_date', f'{date}T23:59:59')

    if require_coords:
        query = query.not_.is_('customers.latitude', None)
        query = query.not_.is_('customers.longitude', None)

    response = query.range(offset, offset + limit - 1).execute()

    return {
        'data': response.data or [],
        'count': response.count
    }

def get_orders_by_ids(order_ids):
    if not order_ids:
        return {}

    auth()
    res = supabase.table('orders') \
        .select('''
            id,
            customers(name),
            order_items(
                quantity,
                buy_price,
                sell_price,
                products(name, unit)
            )
        ''') \
        .in_('id', order_ids) \
        .execute()

    return {o['id']: o for o in (res.data or [])}

def get_order_by_id(order_id):
    auth()

    response = supabase.table('orders') \
        .select('''
            id,
            order_date,
            status,
            total_amount,
            delivery_price,
            delivery_type,
            customer_id,
            customers!inner(id, name, phone),
            order_items(
                id,
                product_id,
                product_variant_id,
                product_variants(id, name, buy_price, sell_price),
                quantity,
                buy_price,
                sell_price,
                products(id, name, unit)
            )
        ''') \
        .eq('id', order_id) \
        .single() \
        .execute()
    
    return response.data

def insert_order(data):
    auth()
    response = supabase.table('orders').insert(data).execute()

    if response.data:
        return response.data[0]

    raise Exception(f'Insert failed: {str(response)}')

def update_order(order_id, data):
    auth()
    response = (
        supabase.table('orders')
        .update(data)
        .eq('id', order_id)
        .execute()
    )

    if response.data:
        return response.data[0]

    raise Exception(f"Update failed: {response}")

