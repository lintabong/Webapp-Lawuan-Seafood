from flask import (
    Blueprint,
    render_template,
    jsonify,
    session
)
from app.lib.supabase_client import supabase
from app.helpers.auth import login_required

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customer-map')
@login_required
def customers_page():
    return render_template('customers_map.html')


@customers_bp.route('/api/customers')
@login_required
def api_customers():
    try:
        access_token = session.get('access_token')
        if not access_token:
            return jsonify({'error': 'Unauthorized'}), 401

        supabase.postgrest.auth(access_token)

        response = (
            supabase
            .table('customers')
            .select('''
                id,
                name,
                phone,
                address,
                latitude,
                longitude,
                created_at
            ''')
            .order('name')
            .execute()
        )

        customers = []

        for c in response.data:
            print(c)
            if c['latitude'] is not None and c['longitude'] is not None:
                customers.append({
                    'id': c['id'],
                    'name': c['name'],
                    'phone': c['phone'],
                    'address': c['address'],
                    'latitude': float(c['latitude']),
                    'longitude': float(c['longitude'])
                })

        return jsonify(customers)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
