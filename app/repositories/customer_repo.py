
from app.repositories.supabase_repo import auth
from app.lib.supabase_client import supabase
from app.models.customer import Customer

def get_all_customers():
    auth()
    response = supabase.table('customers') \
        .select('*') \
        .order('name') \
        .execute()

    return [Customer.from_dict(row) for row in response.data]

def get_customer_by_id(id):
    auth()
    response = supabase.table('customers') \
        .select('*') \
        .eq('id', id) \
        .execute()

    if response:
        return Customer.from_dict(response.data[0])
    return None

def insert_customer(data):
    auth()
    payload = {
        'name': data.get('name'),
        'phone': data.get('phone'),
        'address': data.get('address'),
        'latitude': data.get('latitude'),
        'longitude': data.get('longitude'),
    }

    response = supabase.table('customers').insert(payload).execute()

    if response.data:
        return Customer.from_dict(response.data[0])

    return None

def update_customer(customer_id: int, data: dict):
    auth()
    payload = {
        'name': data.get('name'),
        'phone': data.get('phone'),
        'address': data.get('address'),
        'latitude': data.get('latitude'),
        'longitude': data.get('longitude'),
    }

    payload = {k: v for k, v in payload.items() if v is not None}

    response = (
        supabase.table('customers')
        .update(payload)
        .eq('id', customer_id)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None
