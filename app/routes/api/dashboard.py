
from datetime import datetime, timedelta, timezone
from flask import (
    Blueprint, request, 
    session, jsonify
)
from app import log
from app.lib.supabase_client import supabase
from app.helpers.auth import login_required

dashboard_api_bp = Blueprint('dashboard_api', __name__)

logger = log.get_logger('API_DASHBOARD')


@dashboard_api_bp.route('/kpi')
@login_required
def api_dashboard_kpi():
    try:
        supabase.postgrest.auth(session['access_token'])

        total_customers = (
            supabase.table('customers')
            .select('id', count='exact')
            .execute()
            .count
        )

        cash_response = (
            supabase
            .table('cash_accounts')
            .select('balance')
            .execute()
        )
        current_cash = sum(row['balance'] for row in cash_response.data)

        income_result = supabase.rpc('get_income_comparison').execute()
        income = income_result.data[0] if income_result.data else {}

        products = (
            supabase
            .table('products')
            .select('stock, sell_price')
            .eq('is_active', True)
            .execute()
        )

        inventory_value = sum(
            float(p['stock']) * float(p['sell_price'])
            for p in products.data
        )

        ten_days_ago = (
            datetime.now(timezone.utc) - timedelta(days=10)
        ).isoformat()

        pending_orders = (
            supabase
            .table('orders')
            .select('total_amount')
            .eq('status', 'pending')
            .gte('order_date', ten_days_ago)
            .execute()
        )

        pending_total_amount = sum(
            float(o['total_amount'] or 0)
            for o in pending_orders.data
        )

        return jsonify({
            'total_customers': total_customers,
            'current_cash': str(round(current_cash)),
            'inventory_value': str(inventory_value - (15/100*inventory_value)),
            'pending_total_amount': str(pending_total_amount - (15/100*pending_total_amount)),
            'income': {
                'this_month': income.get('this_month', 0),
                'last_month': income.get('last_month', 0),
                'last_30_days': income.get('last_30_days', 0),
                'days_30_60': income.get('days_30_60', 0)
            }
        })

    except Exception as e:
        logger.error(f'Found error: {str(e)}')
        return jsonify({'error': str(e)}), 500


@dashboard_api_bp.route('/daily_order_summary')
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
        logger.error(f'Found error: {str(e)}')
        return jsonify({'error': str(e)}), 500
