
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
