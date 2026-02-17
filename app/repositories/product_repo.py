
from typing import List, Optional
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase
from app.models.product import Product


def list_product(is_active='true', search=None):
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

def insert_product(
    name: str,
    buy_price: float,
    sell_price: float,
    category_id: Optional[int] = None,
    unit: str = 'kg',
    stock: float = 0,
    is_active: bool = True,
):
    auth()

    res = supabase.table('products').insert({
        'name': name,
        'category_id': category_id,
        'unit': unit,
        'buy_price': buy_price,
        'sell_price': sell_price,
        'stock': stock,
        'is_active': is_active
    }).execute()

    return res.data[0] if res.data else None


def insert_products(products: List[dict]):
    auth()
    res = supabase.table('products').insert(products).execute()
    return res.data

def get_product_by_id(product_id: int):
    auth()

    res = supabase.table('products') \
        .select('*') \
        .eq('id', product_id) \
        .single() \
        .execute()

    return res.data

def update_product(product_id: int, data: dict):
    auth()

    supabase.table('products') \
        .update(data) \
        .eq('id', product_id) \
        .execute()


def update_stock(product_id: int, quantity_change: float):
    auth()

    product = get_product_by_id(product_id)
    if not product:
        raise ValueError('Product not found')

    new_stock = float(product['stock']) + float(quantity_change)

    supabase.table('products') \
        .update({'stock': new_stock}) \
        .eq('id', product_id) \
        .execute()

    return new_stock

def set_stock(product_id: int, new_stock: float):
    auth()

    supabase.table('products') \
        .update({'stock': new_stock}) \
        .eq('id', product_id) \
        .execute()

    return new_stock

def toggle_active(product_id: int, is_active: bool):
    auth()

    supabase.table('products') \
        .update({'is_active': is_active}) \
        .eq('id', product_id) \
        .execute()

def delete_product(product_id: int):
    auth()

    supabase.table('products') \
        .delete() \
        .eq('id', product_id) \
        .execute()
