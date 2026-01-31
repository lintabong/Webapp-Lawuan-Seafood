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
    product_id = data.get('product_id')
    qty = float(data.get('quantity', 0))
    buy_price = float(data.get('buy_price', 0))

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
            'reference_type': 'product' if product_id else 'general',
            'reference_id': product_id,
            'created_by': user_id
        })
        .execute()
    )

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

    # 4️⃣ If product purchase → update inventory
    if product_id:
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
