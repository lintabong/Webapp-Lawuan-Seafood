

import re
from datetime import datetime, timezone, timedelta
from flask import (
    Blueprint,
    jsonify,
    session,
    request
)
from app.lib.supabase_client import supabase
from app.helpers.auth import login_required
from app.constants import CASHFLOW_ITEMS_PER_PAGE

cashflow_api_bp = Blueprint('cashflow_api', __name__)


@cashflow_api_bp.route('/cashflow/transactions')
@login_required
def api_cashflow_transactions():
    access_token = session.get('access_token')
    supabase.postgrest.auth(access_token)
    
    # Get query parameters
    date_filter = request.args.get('date', '')  # Format: YYYY-MM-DD
    category_filter = request.args.get('category', 'all')
    page = int(request.args.get('page', 1))
    per_page = CASHFLOW_ITEMS_PER_PAGE
    
    try:
        if date_filter:
            day = datetime.strptime(date_filter, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        else:
            day = datetime.now(timezone.utc)
        
        today_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Base query for cashflow transactions
        query = supabase.table('cashflow_transactions')\
            .select('*', count='exact')\
            .gte('transaction_date', today_start.isoformat())\
            .lt('transaction_date', today_end.isoformat())
        
        # Apply category filter
        if category_filter != 'all':
            categories = supabase.table('cashflow_categories')\
                .select('id, name')\
                .execute().data
            category_id = next((c['id'] for c in categories if c['name'] == category_filter), None)
            if category_id:
                query = query.eq('category_id', category_id)
        
        # Execute query with pagination
        offset = (page - 1) * per_page
        result = query.order('transaction_date', desc=True)\
            .range(offset, offset + per_page - 1)\
            .execute()
        
        cashflow_data = result.data or []
        total_count = result.count
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        
        # Get all transaction IDs for fetching related data
        transaction_ids = [cf['id'] for cf in cashflow_data]
        
        # Fetch product purchases for the transactions
        product_purchase_data = []
        if transaction_ids:
            product_purchases = supabase.table('product_purchase_items')\
                .select('id, quantity, buy_price, subtotal, transaction_id, products(name, unit)')\
                .in_('transaction_id', transaction_ids)\
                .execute()
            product_purchase_data = product_purchases.data or []
        
        # Fetch orders for the transactions
        order_ids = [cf['reference_id'] for cf in cashflow_data 
                     if cf.get('reference_type') == 'order' and cf.get('reference_id')]
        order_data = []
        if order_ids:
            orders = supabase.table('orders')\
                .select('''
                    id,
                    order_date,
                    status,
                    total_amount,
                    delivery_price,
                    delivery_type,
                    customers(name),
                    order_items(
                        quantity,
                        buy_price,
                        sell_price,
                        products(name, unit)
                    )
                ''')\
                .in_('id', order_ids)\
                .execute()
            order_data = orders.data or []
        
        # Process and combine data
        combined = []
        for cf in cashflow_data:
            # Get category info
            category_info = supabase.table('cashflow_categories')\
                .select('name, type')\
                .eq('id', cf['category_id'])\
                .single()\
                .execute().data
            
            transaction = {
                'date': cf['transaction_date'],
                'transaction_id': cf['id'],
                'amount': float(cf['amount']),
                'description': cf['description'],
                'reference': cf.get('reference_type'),
                'reference_id': cf.get('reference_id'),
                'category': category_info['name'],
                'category_type': category_info['type'],
                'type': None,
                'items': []
            }
            
            # Handle product purchases
            if transaction['reference'] == 'product':
                transaction['type'] = 'product_purchases'
                for product_purchase in product_purchase_data:
                    if product_purchase['transaction_id'] == transaction['transaction_id']:
                        transaction['items'].append({
                            'name': product_purchase['products']['name'],
                            'unit': product_purchase['products']['unit'],
                            'quantity': float(product_purchase['quantity']),
                            'buy_price': float(product_purchase['buy_price']),
                            'subtotal': float(product_purchase['subtotal'])
                        })
            
            # Handle orders
            elif transaction['reference'] == 'order':
                # Check if it's a delivery fee
                if re.search(r'(?i)delivery', transaction['description'] or ''):
                    transaction['type'] = 'delivery_order'
                else:
                    transaction['type'] = 'order'
                    # Find matching order
                    matching_order = next((o for o in order_data if o['id'] == transaction['reference_id']), None)
                    if matching_order:
                        transaction['customer_name'] = matching_order['customers']['name']
                        for order_item in matching_order['order_items']:
                            transaction['items'].append({
                                'name': order_item['products']['name'],
                                'unit': order_item['products']['unit'],
                                'quantity': float(order_item['quantity']),
                                'buy_price': float(order_item['buy_price']),
                                'sell_price': float(order_item['sell_price']),
                                'subtotal': float(order_item['quantity'] * order_item['sell_price'])
                            })
            else:
                transaction['type'] = 'general'
            
            combined.append(transaction)
        
        # Sort by date (already sorted from query, but ensuring)
        combined.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'transactions': combined,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': total_pages
            },
            'filters': {
                'date': date_filter or day.strftime('%Y-%m-%d'),
                'category': category_filter
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cashflow_api_bp.route('/cashflow', methods=['POST'])
@login_required
def api_cashflow_create():
    data = request.json
    access_token = session.get('access_token')
    supabase.postgrest.auth(access_token)

    user_id = session.get('user_id')

    category_id = int(data['category_id'])
    amount = float(data['amount'])
    description = data.get('description')
    products = data.get('products', [])  # 🆕 Changed to array of products

    # 1️⃣ Get category type (income / expense)
    category = (
        supabase.table('cashflow_categories')
        .select('type')
        .eq('id', category_id)
        .single()
        .execute()
        .data
    )

    trx_type = category['type']  # income / expense

    # 2️⃣ Insert cashflow transaction
    trx = (
        supabase.table('cashflow_transactions')
        .insert({
            'category_id': category_id,
            'amount': amount,
            'description': description,
            'reference_type': 'product' if products else 'general',
            'reference_id': None,  # 🆕 Set to None for multiple products
            'created_by': user_id
        })
        .execute()
    )

    transaction_id = trx.data[0]['id']

    # 3️⃣ Update CASH account (id = 1)
    cash = (
        supabase.table('cash_accounts')
        .select('balance')
        .eq('id', 1)
        .single()
        .execute()
        .data
    )

    old_balance = float(cash['balance'])

    new_balance = (
        old_balance + amount
        if trx_type == 'income'
        else old_balance - amount
    )

    supabase.table('cash_accounts').update({
        'balance': round(new_balance, 2)
    }).eq('id', 1).execute()

    # 4️⃣ If product purchases → insert purchase items & update inventory
    if products:
        for product_item in products:
            product_id = int(product_item['product_id'])
            qty = float(product_item['quantity'])
            buy_price = float(product_item['buy_price'])
            
            # Insert into product_purchase_items
            supabase.table('product_purchase_items').insert({
                'transaction_id': transaction_id,
                'product_id': product_id,
                'quantity': qty,
                'buy_price': buy_price,
                'subtotal': round(qty * buy_price, 2)
            }).execute()
            
            # Update product inventory
            product = (
                supabase.table('products')
                .select('stock, buy_price')
                .eq('id', product_id)
                .single()
                .execute()
                .data
            )

            old_stock = float(product['stock'])
            old_price = float(product['buy_price'])

            new_stock = old_stock + qty

            # weighted average price
            new_price = (
                (old_stock * old_price + qty * buy_price) / new_stock
                if new_stock > 0 else buy_price
            )

            supabase.table('products').update({
                'stock': new_stock,
                'buy_price': round(new_price, 2)
            }).eq('id', product_id).execute()

    return jsonify({
        'success': True,
        'cash_balance': round(new_balance, 2)
    })
