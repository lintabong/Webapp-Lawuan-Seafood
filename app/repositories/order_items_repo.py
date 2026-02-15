
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase

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
