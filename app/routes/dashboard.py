
from datetime import datetime, timedelta
from flask import (
    Blueprint, render_template, 
    request, session, jsonify
)
from app.lib.supabase_client import supabase
from app.helpers.auth import login_required


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@dashboard_bp.route('/api/dashboard/kpi')
@login_required
def api_dashboard_kpi():
    try:
        supabase.postgrest.auth(session['access_token'])

        total_customers = supabase.table('customers') \
            .select('id', count='exact') \
            .execute().count

        total_products = supabase.table('products') \
            .select('id', count='exact') \
            .eq('is_active', True) \
            .execute().count

        income_result = supabase.rpc('get_monthly_income').execute()
        income_month = income_result.data if income_result.data else 0

        return jsonify({
            'total_customers': total_customers,
            'total_products': total_products,
            'income_month': income_month
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/dashboard/chart')
@login_required
def api_dashboard_chart():
    try:
        supabase.postgrest.auth(session['access_token'])

        end_date = request.args.get('end_date')
        start_date = request.args.get('start_date')

        if not end_date:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        daily_order_summary = supabase.rpc(
            'get_daily_order_summary',
            {
                'start_date': str(start_date),
                'end_date':  str(end_date)
            }
        ).execute().data

        daily_order_summary = daily_order_summary[::-1]

        return jsonify(daily_order_summary)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
