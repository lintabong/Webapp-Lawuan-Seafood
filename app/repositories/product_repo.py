
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase
from app.models.product import Product

def list_product(is_active=True):
    auth() 

    response = (supabase.table('products')
        .select('id, name, stock, unit, buy_price, sell_price')
        .eq('is_active', is_active)
        .order('name')
        .execute())  
 
    return [Product.from_dict(row) for row in response.data]
