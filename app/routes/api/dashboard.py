
from datetime import datetime, timedelta
from flask import (
    Blueprint, request, 
    session, jsonify
)
from app import log
from app.lib.supabase_client import supabase
from app.helpers.auth import login_required
from app.repositories.cash_repo import get_cash_balance

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

        current_cash = get_cash_balance()

        income_result = supabase.rpc('get_income_comparison').execute()
        income = income_result.data[0] if income_result.data else {}

        pending_orders = (
            supabase
            .table('orders')
            .select('total_amount, delivery_price')
            .eq('status', 'pending')
            .execute()
        )

        pending_total_amount = sum(
            (float(o['total_amount'] or 0) + float(o['delivery_price'] or 0))
            for o in pending_orders.data
        )

        return jsonify({
            'total_customers': total_customers,
            'current_cash': str(round(current_cash)),
            'pending_total_amount': str(pending_total_amount),
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


@dashboard_api_bp.route('/most_bought_products')
@login_required
def api_most_bought_products():
    try:
        supabase.postgrest.auth(session['access_token'])

        end_date = request.args.get('end_date')
        start_date = request.args.get('start_date')
        limit = int(request.args.get('limit', 10))

        if not end_date:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        # Join order_items → orders (filter by date & non-cancelled) → products
        result = (
            supabase
            .table('order_items')
            .select(
                'quantity, sell_price, buy_price,'
                'orders!inner(order_date, status),'
                'products!inner(id, name, unit)'
            )
            .gte('orders.order_date', str(start_date))
            .lte('orders.order_date', str(end_date) + 'T23:59:59')
            .neq('orders.status', 'cancelled')
            .execute()
        )

        # Aggregate by product
        product_map: dict[int, dict] = {}
        for item in result.data:
            product = item.get('products') or {}
            pid = product.get('id')
            if pid is None:
                continue

            qty = float(item.get('quantity') or 0)
            sell = float(item.get('sell_price') or 0)
            buy = float(item.get('buy_price') or 0)
            revenue = qty * sell
            profit = qty * (sell - buy)

            if pid not in product_map:
                product_map[pid] = {
                    'product_id': pid,
                    'product_name': product.get('name', ''),
                    'unit': product.get('unit', ''),
                    'total_quantity': 0.0,
                    'total_revenue': 0.0,
                    'total_profit': 0.0,
                }

            product_map[pid]['total_quantity'] += qty
            product_map[pid]['total_revenue'] += revenue
            product_map[pid]['total_profit'] += profit

        # Sort by quantity descending, take top N
        sorted_products = sorted(
            product_map.values(),
            key=lambda x: x['total_quantity'],
            reverse=True
        )[:limit]

        # Round floats
        for p in sorted_products:
            p['total_quantity'] = round(p['total_quantity'], 2)
            p['total_revenue'] = round(p['total_revenue'], 2)
            p['total_profit'] = round(p['total_profit'], 2)

        print(sorted_products)
        return jsonify(sorted_products)

    except Exception as e:
        logger.error(f'Found error in most_bought_products: {str(e)}')
        return jsonify({'error': str(e)}), 500


@dashboard_api_bp.route('/cash_ledger_last7days')
@login_required
def api_cash_ledger_last7days():
    try:
        supabase.postgrest.auth(session['access_token'])

        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=6)  # inclusive of today = 7 days

        result = (
            supabase
            .table('cash_ledgers')
            .select('direction, amount, balance_after, created_at')
            .gte('created_at', str(seven_days_ago))
            .lte('created_at', str(today) + 'T23:59:59')
            .order('created_at', desc=False)
            .execute()
        )

        # Build a day-by-day map
        day_map: dict[str, dict] = {}
        # Pre-fill all 7 days so we always have complete series (even empty days)
        for i in range(7):
            day = str(seven_days_ago + timedelta(days=i))
            day_map[day] = {
                'date': day,
                'cash_in': 0.0,
                'cash_out': 0.0,
                'net': 0.0,
                'balance_after': None,   # will hold last balance of that day
            }

        for entry in result.data:
            raw_date = entry.get('created_at', '')[:10]
            if raw_date not in day_map:
                continue

            direction = entry.get('direction')
            amount = float(entry.get('amount') or 0)
            balance = float(entry.get('balance_after') or 0)

            if direction == 'in':
                day_map[raw_date]['cash_in'] += amount
            elif direction == 'out':
                day_map[raw_date]['cash_out'] += amount

            # Keep the LAST balance_after for the day (chronologically ordered)
            day_map[raw_date]['balance_after'] = balance

        # Compute net and round
        for day in day_map.values():
            day['net'] = round(day['cash_in'] - day['cash_out'], 2)
            day['cash_in'] = round(day['cash_in'], 2)
            day['cash_out'] = round(day['cash_out'], 2)
            if day['balance_after'] is not None:
                day['balance_after'] = round(day['balance_after'], 2)

        return jsonify(list(day_map.values()))

    except Exception as e:
        logger.error(f'Found error in cash_ledger_last7days: {str(e)}')
        return jsonify({'error': str(e)}), 500
    