
from typing import List, Optional
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase


def insert_item(
    transaction_id: int,
    item_type: str = 'product',
    product_id: Optional[int] = None,
    description: Optional[str] = None,
    quantity: float = 1,
    price: Optional[float] = None,
    subtotal: Optional[float] = None,
):
    auth()

    if subtotal is None and price is not None:
        subtotal = float(quantity) * float(price)

    res = supabase.table('transaction_items').insert({
        'transaction_id': transaction_id,
        'item_type': item_type,
        'product_id': product_id,
        'description': description,
        'quantity': quantity,
        'price': price,
        'subtotal': subtotal
    }).execute()

    return res.data[0] if res.data else None


def insert_items(items: List[dict]):
    auth()

    for item in items:
        if item.get('subtotal') is None and item.get('price') is not None:
            item['subtotal'] = float(item.get('quantity', 1)) * float(item['price'])

    res = supabase.table('transaction_items').insert(items).execute()
    return res.data

def get_items_by_transaction(transaction_id: int):
    auth()

    res = supabase.table('transaction_items') \
        .select('*') \
        .eq('transaction_id', transaction_id) \
        .execute()

    return res.data


def get_item_by_id(item_id: int):
    auth()

    res = supabase.table('transaction_items') \
        .select('*') \
        .eq('id', item_id) \
        .single() \
        .execute()

    return res.data

def update_item(item_id: int, data: dict):
    auth()

    if 'quantity' in data or 'price' in data:
        qty = float(data.get('quantity', 1))
        price = float(data.get('price', 0))
        data['subtotal'] = qty * price

    supabase.table('transaction_items') \
        .update(data) \
        .eq('id', item_id) \
        .execute()

def delete_item(item_id: int):
    auth()

    supabase.table('transaction_items') \
        .delete() \
        .eq('id', item_id) \
        .execute()

def delete_items_by_transaction(transaction_id: int):
    auth()

    supabase.table('transaction_items') \
        .delete() \
        .eq('transaction_id', transaction_id) \
        .execute()

def get_by_transaction_ids(transaction_ids):
    if not transaction_ids:
        return []

    auth()
    res = supabase.table('transaction_items') \
        .select('*, products(name, unit)') \
        .in_('transaction_id', transaction_ids) \
        .execute()

    return res.data or []
