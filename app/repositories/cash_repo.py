
from flask import session
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase

def get_cash_balance():
    auth()
    cash = supabase.table('cash_accounts') \
        .select('balance') \
        .eq('id', 1) \
        .single() \
        .execute().data
    return float(cash['balance'])

def update_cash_balance(amount):
    old = get_cash_balance()
    new = round(old + amount, 2)
    supabase.table('cash_accounts') \
        .update({'balance': new}) \
        .eq('id', 1) \
        .execute()
    return new

def insert_cashflow(category_id, amount, desc, order_id):
    auth()
    supabase.table('cashflow_transactions').insert({
        'category_id': category_id,
        'amount': amount,
        'description': desc,
        'reference_type': 'order',
        'reference_id': order_id,
        'created_by': session.get('user_id')
    }).execute()

def delete_cashflow(order_id):
    auth()
    supabase.table('cashflow_transactions') \
        .delete() \
        .eq('reference_type', 'order') \
        .eq('reference_id', order_id) \
        .execute()
