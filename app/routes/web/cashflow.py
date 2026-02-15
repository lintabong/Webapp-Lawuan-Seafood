
from flask import (
    Blueprint,
    render_template,
    session,
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
        'cash/cashflow_create.html',
        categories=categories,
        products=products
    )

@cashflow_bp.route('/cashflow/transactions')
@login_required
def cashflow_transactions():
    access_token = session.get('access_token')
    supabase.postgrest.auth(access_token)

    categories = (
        supabase.table('cashflow_categories')
        .select('id, name, type')
        .order('name')
        .execute()
        .data
    )

    return render_template(
        'cash/cashflow_transactions.html',
        categories=categories
    )
