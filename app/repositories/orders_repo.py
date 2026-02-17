
from datetime import datetime
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
        customers!inner(
            name,
            phone,
            address,
            latitude,
            longitude
        ),
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

def list_order_by_date(date):
    auth()
    response = (
        supabase
        .table('orders')
        .select('''id,
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
                quantity,
                sell_price,
                products(name, unit),
                is_prepared
            )''')
        .eq('delivery_type', 'delivery')
        .in_('status', ['pending', 'paid', 'delivered']) 
        .gte('order_date', f'{date}T00:00:00')
        .lte('order_date', f'{date}T23:59:59')
        .order('order_date')
        .execute()
    )

    orders = []

    for o in response.data:
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

    return orders

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
    return supabase.table('orders').insert(data).execute().data[0]

def update_order(order_id, data):
    auth()
    supabase.table('orders').update(data).eq('id', order_id).execute()
