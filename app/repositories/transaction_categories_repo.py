
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase
from app.models.transaction_category import TransactionCategory

def list_transaction_categories():
    auth()

    response = (
        supabase.table('transaction_categories')
        .select('id, name, type')
        .order('name')
        .execute()
    )

    return [TransactionCategory.from_dict(row) for row in response.data]

def get_all_map():
    auth()
    res = supabase.table('transaction_categories') \
        .select('id, name, type') \
        .execute()

    return {c['id']: c for c in (res.data or [])}

def get_category_name(category_id):
    auth()

    category = (
        supabase.table('transaction_categories')
        .select('id, name, type')
        .eq('id', category_id)
        .single()
        .execute()
        .data
    )

    return category
