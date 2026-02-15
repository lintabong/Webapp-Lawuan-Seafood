
from datetime import datetime
from flask import (
    Blueprint, 
    render_template, 
    request, 
    jsonify, 
    session
)
from app.lib.supabase_client import supabase
from app.helpers.auth import login_required


delivery_bp = Blueprint('delivery', __name__)

@delivery_bp.route('/delivery-order')
@login_required
def delivery_order():
    return render_template('delivery_order.html')


@delivery_bp.route('/api/delivery-orders')
@login_required
def api_delivery_orders():
    try:
        access_token = session.get('access_token')
        if not access_token:
            return jsonify({'error': 'Unauthorized'}), 401

        supabase.postgrest.auth(access_token)

        date = request.args.get('date')
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

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

        return jsonify(orders)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
