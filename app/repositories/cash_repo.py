
from flask import session
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase

def get_cash_balance(id=1):
    auth()
    cash = supabase.table('cash') \
        .select('balance') \
        .eq('id', id) \
        .single() \
        .execute().data
    return float(cash['balance'])

def update_cash_balance(id=1, amount=0):
    old = get_cash_balance()
    new = round(old + amount, 2)
    supabase.table('cash') \
        .update({'balance': new}) \
        .eq('id', id) \
        .execute()
    return new

# def insert_cashflow(category_id, amount, desc, order_id):
#     auth()
#     supabase.table('cashflow_transactions').insert({
#         'category_id': category_id,
#         'amount': amount,
#         'description': desc,
#         'reference_type': 'order',
#         'reference_id': order_id,
#         'created_by': session['user']['id']
#     }).execute()

# def delete_cashflow(order_id):
#     auth()
#     supabase.table('cashflow_transactions') \
#         .delete() \
#         .eq('reference_type', 'order') \
#         .eq('reference_id', order_id) \
#         .execute()
