
from datetime import datetime, timezone, timedelta
from flask import (
    Blueprint,
    jsonify,
    session,
    request
)
from app.helpers.auth import login_required
from app.constants import CASHFLOW_ITEMS_PER_PAGE
from app.services import transactions_service

cashflow_api_bp = Blueprint('cashflow_api', __name__)


@cashflow_api_bp.route('/cashflow/transactions')
@login_required
def api_cashflow_transactions():
    date_filter = request.args.get('date', '')
    category_filter = request.args.get('category', 'all')
    page = int(request.args.get('page', 1))
    per_page = CASHFLOW_ITEMS_PER_PAGE

    try:
        data = transactions_service.get_cashflow_transactions_service(
            date_filter,
            category_filter,
            page,
            per_page
        )

        return jsonify({
            'success': True,
            'transactions': data['transactions'],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_count': data['total_count'],
                'total_pages': data['total_pages']
            },
            'filters': {
                'date': data['date'],
                'category': data['category']
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@cashflow_api_bp.route('/cashflow', methods=['POST'])
@login_required
def api_cashflow_create():
    data = request.json

    date = datetime.strptime(data.get('date') , "%Y-%m-%dT%H:%M")
    local_date = date.replace(tzinfo=timezone(timedelta(hours=7)))

    new_balance = transactions_service.insert_transaction(
        user_id=session['user']['id'],
        category_id=data.get('category_id'), 
        desc=data.get('description', ''), 
        amount=data.get('amount', 0), 
        transaction_date=local_date.astimezone(timezone.utc), 
        products=data.get('products', []) 
    )

    return jsonify({
        'success': True,
        'cash_balance': round(new_balance, 2)
    })
