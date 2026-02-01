from flask import (
    Blueprint,
    render_template,
    jsonify,
    session,
    request
)
from app.lib.supabase_client import supabase
from app.helpers.auth import login_required

cashflow_bp = Blueprint('cashflow', __name__)


@cashflow_bp.route('/cashflow/create')
@login_required
def cashflow_create():
    access_token = session.get('access_token')
    supabase.postgrest.auth(access_token)

    categories = (
        supabase.table('cashflow_categories')
        .select('id, name, type')
        .order('name')
        .execute()
        .data
    )

    products = (
        supabase.table('products')
        .select('id, name, unit, buy_price, stock')
        .eq('is_active', True)
        .order('name')
        .execute()
        .data
    )

    return render_template(
        'cashflow_create.html',
        categories=categories,
        products=products
    )

@cashflow_bp.route('/cashflow/transactions')
@login_required
def cashflow_transactions():
    access_token = session.get('access_token')
    supabase.postgrest.auth(access_token)

    # Get filter and pagination params
    category_filter = request.args.get('category', 'all')
    page = int(request.args.get('page', 1))
    per_page = 20

    # Get all categories for filter dropdown
    categories = (
        supabase.table('cashflow_categories')
        .select('id, name')
        .order('name')
        .execute()
        .data
    )

    # Build query
    query = supabase.table('cashflow_transactions').select('*, cashflow_categories(name, type)', count='exact')

    # Apply category filter
    if category_filter != 'all':
        # Find category ID by name
        category_id = next((c['id'] for c in categories if c['name'] == category_filter), None)
        if category_id:
            query = query.eq('category_id', category_id)

    # Get total count and paginated data
    offset = (page - 1) * per_page
    result = (
        query
        .order('transaction_date', desc=True)
        .range(offset, offset + per_page - 1)
        .execute()
    )

    transactions = result.data
    total_count = result.count
    total_pages = (total_count + per_page - 1) // per_page

    # Enrich transactions with reference details
    for trx in transactions:
        trx['reference_details'] = None
        
        if trx['reference_type'] == 'product':
            # Get product purchase items
            purchase_items = (
                supabase.table('product_purchase_items')
                .select('*, products(name, unit)')
                .eq('transaction_id', trx['id'])
                .execute()
                .data
            )
            
            if purchase_items:
                trx['reference_details'] = {
                    'type': 'product',
                    'purchase_items': purchase_items
                }
        
        elif trx['reference_type'] == 'order' and trx['reference_id']:
            # Get order details
            order = (
                supabase.table('orders')
                .select('*, customers(name), order_items(*, products(name))')
                .eq('id', trx['reference_id'])
                .single()
                .execute()
                .data
            )
            
            # Calculate items summary
            items_summary = []
            for item in order['order_items']:
                items_summary.append({
                    'product_name': item['products']['name'],
                    'quantity': item['quantity'],
                    'sell_price': item['sell_price'],
                    'subtotal': item['quantity'] * item['sell_price']
                })
            
            trx['reference_details'] = {
                'type': 'order',
                'customer_name': order['customers']['name'],
                'order_items': items_summary,
                'total_items': len(items_summary)
            }

    return render_template(
        'cashflow_transactions.html',
        transactions=transactions,
        categories=categories,
        current_category=category_filter,
        page=page,
        total_pages=total_pages,
        total_count=total_count
    )

# @cashflow_bp.route('/api/cashflow', methods=['POST'])
# @login_required
# def api_cashflow_create():
#     data = request.json
#     access_token = session.get('access_token')
#     supabase.postgrest.auth(access_token)

#     user_id = session.get('user_id')

#     category_id = int(data['category_id'])
#     amount = float(data['amount'])
#     description = data.get('description')
#     product_id = data.get('product_id')
#     qty = float(data.get('quantity', 0))
#     buy_price = float(data.get('buy_price', 0))

#     # 1️⃣ Get category type (income / expense)
#     category = (
#         supabase.table('cashflow_categories')
#         .select('type')
#         .eq('id', category_id)
#         .single()
#         .execute()
#         .data
#     )

#     trx_type = category['type']  # income / expense

#     # 2️⃣ Insert cashflow transaction
#     trx = (
#         supabase.table('cashflow_transactions')
#         .insert({
#             'category_id': category_id,
#             'amount': amount,
#             'description': description,
#             'reference_type': 'product' if product_id else 'general',
#             'reference_id': product_id,
#             'created_by': user_id
#         })
#         .execute()
#     )

#     transaction_id = trx.data[0]['id']  # 🆕 Get the transaction ID

#     # 3️⃣ Update CASH account (id = 1)
#     cash = (
#         supabase.table('cash_accounts')
#         .select('balance')
#         .eq('id', 1)
#         .single()
#         .execute()
#         .data
#     )

#     old_balance = float(cash['balance'])

#     new_balance = (
#         old_balance + amount
#         if trx_type == 'income'
#         else old_balance - amount
#     )

#     supabase.table('cash_accounts').update({
#         'balance': round(new_balance, 2)
#     }).eq('id', 1).execute()

#     # 4️⃣ If product purchase → insert purchase item & update inventory
#     if product_id:
#         # 🆕 Insert into product_purchase_items
#         supabase.table('product_purchase_items').insert({
#             'transaction_id': transaction_id,
#             'product_id': product_id,
#             'quantity': qty,
#             'buy_price': buy_price,
#             'subtotal': round(qty * buy_price, 2)
#         }).execute()
        
#         # Update product inventory
#         product = (
#             supabase.table('products')
#             .select('stock, buy_price')
#             .eq('id', product_id)
#             .single()
#             .execute()
#             .data
#         )

#         old_stock = float(product['stock'])
#         old_price = float(product['buy_price'])

#         new_stock = old_stock + qty

#         # weighted average price
#         new_price = (
#             (old_stock * old_price + qty * buy_price) / new_stock
#             if new_stock > 0 else buy_price
#         )

#         supabase.table('products').update({
#             'stock': new_stock,
#             'buy_price': round(new_price, 2)
#         }).eq('id', product_id).execute()

#     return jsonify({
#         'success': True,
#         'cash_balance': round(new_balance, 2)
#     })

@cashflow_bp.route('/api/cashflow', methods=['POST'])
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
