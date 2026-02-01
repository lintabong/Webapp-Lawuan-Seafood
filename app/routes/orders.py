
from flask import (
    Blueprint, render_template, 
    request, jsonify, session
)
from app.lib.supabase_client import supabase
from app.helpers.auth import login_required

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/my-orders')
@login_required
def orders():
    return render_template('orders.html')

@orders_bp.route('/api/orders')
@login_required
def api_orders():
    try:
        supabase.postgrest.auth(session['access_token'])

        status = request.args.get('status')
        search = request.args.get('search')

        query = supabase.table('orders') \
            .select('''
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
                    products(name, unit)
                )''') \
            .order('order_date', desc=True)

        if status and status != 'all':
            query = query.eq('status', status)
        
        if search:
            query = query.ilike('customers.name', f'%{search}%')

        orders = query.execute().data

        return jsonify(orders)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route('/api/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    try:
        supabase.postgrest.auth(session['access_token'])

        data = request.get_json()
        new_status = data.get('status')

        if new_status not in ['pending', 'paid', 'delivered', 'cancelled']:
            return jsonify({'error': 'Invalid status'}), 400

        result = supabase.table('orders') \
            .update({'status': new_status}) \
            .eq('id', order_id) \
            .execute()

        return jsonify({'success': True, 'data': result.data})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/create')
@login_required
def create_order():
    return render_template("create_order.html")

@orders_bp.route('/api/customers')
@login_required
def api_customers():
    try:
        supabase.postgrest.auth(session["access_token"])

        customers = supabase.table('customers') \
            .select('*') \
            .order('name') \
            .execute().data

        return jsonify(customers)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route('/api/products/active')
@login_required
def api_active_products():
    try:
        supabase.postgrest.auth(session['access_token'])

        products = supabase.table('products') \
            .select('*') \
            .eq('is_active', True) \
            .order('name') \
            .execute().data

        return jsonify(products)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/api/orders', methods=['POST'])
@login_required
def create_order_api():
    try:
        supabase.postgrest.auth(session['access_token'])

        data = request.get_json()

        # Validate
        if not data.get('customer_id'):
            return jsonify({'error': 'Customer is required'}), 400
        
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'error': 'At least one item is required'}), 400
        
        # Calculate total
        total_amount = sum(
            item['quantity'] * item['sell_price'] 
            for item in data['items']
        )

        delivery_price = data.get('delivery_price', 0)

        order_data = {
            "customer_id": data['customer_id'],
            "order_date": data.get('order_date'),
            "status": data.get('status', 'pending'),
            "total_amount": total_amount,
            "delivery_price": delivery_price,
            "delivery_type": data.get('delivery_type', 'pickup'),
            "created_by": session.get('user_id')
        }

        order_result = supabase.table("orders") \
            .insert(order_data) \
            .execute()

        order_id = order_result.data[0]['id']

        items_data = [
            {
                "order_id": order_id,
                "product_id": item['product_id'],
                "quantity": item['quantity'],
                "buy_price": item['buy_price'],
                "sell_price": item['sell_price']
            }
            for item in data['items']
        ]
        
        supabase.table("order_items") \
            .insert(items_data) \
            .execute()
        
        # 🆕 Get category IDs for Product Sales and Delivery Fees
        categories = supabase.table('cashflow_categories') \
            .select('id, name') \
            .in_('name', ['Product Sales', 'Delivery Fees']) \
            .execute() \
            .data
        
        category_map = {cat['name']: cat['id'] for cat in categories}
        
        # 🆕 Create cashflow transaction for Product Sales
        if total_amount > 0:
            supabase.table('cashflow_transactions').insert({
                'category_id': category_map['Product Sales'],
                'amount': total_amount,
                'description': f'Order #{order_id}',
                'reference_type': 'order',
                'reference_id': order_id,
                'created_by': session.get('user_id')
            }).execute()
        
        # 🆕 Create cashflow transaction for Delivery Fees (if any)
        if delivery_price > 0:
            supabase.table('cashflow_transactions').insert({
                'category_id': category_map['Delivery Fees'],
                'amount': delivery_price,
                'description': f'Delivery for Order #{order_id}',
                'reference_type': 'order',
                'reference_id': order_id,
                'created_by': session.get('user_id')
            }).execute()
        
        # 🆕 Update cash account (id = 1)
        cash = supabase.table('cash_accounts') \
            .select('balance') \
            .eq('id', 1) \
            .single() \
            .execute() \
            .data
        
        old_balance = float(cash['balance'])
        grand_total = total_amount + delivery_price
        new_balance = old_balance + grand_total
        
        supabase.table('cash_accounts').update({
            'balance': round(new_balance, 2)
        }).eq('id', 1).execute()
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': 'Order created successfully',
            'cash_balance': round(new_balance, 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
