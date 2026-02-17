
from flask import session
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase


def create_ledger(cash_id, amount, balance_after, direction, transaction_id):
    auth()
    res = supabase.table('cash_ledgers').insert({
        'cash_id': cash_id,
        'transaction_id': transaction_id,
        'direction': direction,
        'amount': amount,
        'balance_after': balance_after
    }).execute()

    return res.data[0] if res.data else None

def get_ledger_by_id(ledger_id: int):
    auth()
    return (supabase.table('cash_ledgers')
        .select('*')
        .eq('id', ledger_id)
        .single()
        .execute().data)

def get_ledgers_by_cash_account(
            cash_account_id: int,
            limit: int = 50,
            offset: int = 0
        ):
    auth()
    return supabase.table('cash_ledgers') \
        .select('*') \
        .eq('cash_account_id', cash_account_id) \
        .order('created_at', desc=True) \
        .range(offset, offset + limit - 1) \
        .execute().data

def get_ledgers_by_transaction(transaction_id: int):
    auth()
    return supabase.table('cash_ledgers') \
        .select('*') \
        .eq('transaction_id', transaction_id) \
        .order('created_at', desc=True) \
        .execute().data

def get_last_ledger_balance(cash_account_id: int):
    auth()
    res = supabase.table('cash_ledgers') \
        .select('balance_after') \
        .eq('cash_account_id', cash_account_id) \
        .order('created_at', desc=True) \
        .limit(1) \
        .execute()

    if not res.data:
        return 0

    return float(res.data[0]['balance_after'])

def update_ledger(ledger_id: int, data: dict):
    auth()
    res = supabase.table('cash_ledgers') \
        .update(data) \
        .eq('id', ledger_id) \
        .execute()

    return res.data[0] if res.data else None

def delete_ledger(ledger_id: int):
    auth()
    res = supabase.table('cash_ledgers') \
        .delete() \
        .eq('id', ledger_id) \
        .execute()

    return res.data
