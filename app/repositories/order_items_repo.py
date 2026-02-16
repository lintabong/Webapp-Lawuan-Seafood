
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase
from app.models.order_items import OrderItem

def insert_items(items):
    auth()
    supabase.table('order_items').insert(items).execute()

def update_item(item_id, data):
    auth()
    supabase.table('order_items').update(data).eq('id', item_id).execute()

def delete_item(item_id, order_id):
    auth()
    supabase.table('order_items') \
        .delete() \
        .eq('id', item_id) \
        .eq('order_id', order_id) \
        .execute()

def update_item_is_prepared(item_id, is_prepared=True):
    auth()

    response = supabase.table('order_items') \
        .update({'is_prepared': is_prepared}) \
        .eq('id', item_id) \
        .execute()

    return response.data
