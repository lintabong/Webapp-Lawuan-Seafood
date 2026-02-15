
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase

def list_product(is_active=True):
    auth()    
    return supabase.table('products') \
        .select('*') \
        .eq('is_active', is_active) \
        .order('name') \
        .execute().data
