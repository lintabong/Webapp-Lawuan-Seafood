
from flask import Blueprint, request, jsonify

from app import log
from app.helpers.auth import login_required
from app.repositories.order_items_repo import update_item_is_prepared

order_item_api_bp = Blueprint('order_item_api', __name__)

logger = log.get_logger('API_ORDER_ITEM')


@order_item_api_bp.route('/order-items/<int:item_id>/prepared', methods=['PUT'])
@login_required
def update_item_prepared(item_id):
    try:
        data = request.get_json()

        response = update_item_is_prepared(
            item_id, 
            data.get('is_prepared', False)
        )

        return jsonify({'success': True, 'data': response})

    except Exception as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 500
