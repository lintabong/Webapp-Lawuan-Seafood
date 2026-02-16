
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase
from app.models.product import Product


def list_product(is_active, search):
    auth()

    query = supabase.table('products') \
        .select('*') \
        .order('name')

    if is_active and is_active != 'all':
        query = query.eq('is_active', is_active == 'true')
    
    if search:
        query = query.ilike('name', f'%{search}%')

    response = query.execute()
    
    return [Product.from_dict(row) for row in response.data]
