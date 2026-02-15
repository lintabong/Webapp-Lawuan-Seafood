
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app.helpers.auth import login_required
from app.repositories.orders_repo import list_order_by_date
from app.services.orders_service import (
    list_orders_service,
    create_order_service,
    update_order_service,
    update_order_status_service
)

orders_api_bp = Blueprint('orders_api', __name__)

@orders_api_bp.route('/orders')
@login_required
def orders():
    return jsonify(list_orders_service(request.args))

@orders_api_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    return jsonify(create_order_service(
        request.get_json(),
        session.get('user_id')
    ))

@orders_api_bp.route('/orders/<int:order_id>', methods=['PUT'])
@login_required
def update_order(order_id):
    return jsonify(update_order_service(order_id, request.get_json()))

@orders_api_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_status(order_id):
    return jsonify(update_order_status_service(
        order_id,
        request.get_json().get('status')
    ))

@orders_api_bp.route('/delivery-orders')
@login_required
def api_delivery_orders():
    try:
        access_token = session.get('access_token')
        if not access_token:
            return jsonify({'error': 'Unauthorized'}), 401

        date = request.args.get('date')
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')

        orders = list_order_by_date(date)

        return jsonify(orders)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# from flask import (
#     Blueprint, request, 
#     jsonify, session
# )
# from app.lib.supabase_client import supabase
# from app.helpers.auth import login_required
# from app import log

# logger = log.get_logger()


# orders_api_bp = Blueprint('orders_api', __name__)

# @orders_api_bp.route('/orders')
# @login_required
# def api_orders():
#     try:
#         supabase.postgrest.auth(session['access_token'])

#         status = request.args.get('status')
#         search = request.args.get('search')
#         page = int(request.args.get('page', 1))
#         per_page = int(request.args.get('per_page', 25))

#         if page < 1:
#             page = 1
#         if per_page < 1 or per_page > 100:
#             per_page = 25

#         offset = (page - 1) * per_page

#         query = supabase.table('orders') \
#             .select('''
#                 id,
#                 order_date,
#                 status,
#                 total_amount,
#                 delivery_price,
#                 delivery_type,
#                 customers!inner(id, name, phone, address),
#                 order_items(
#                     id,
#                     quantity,
#                     sell_price,
#                     products(name, unit),
#                     is_prepared
#                 )''', count='exact') \
#             .order('order_date', desc=True)

#         if status and status != 'all':
#             query = query.eq('status', status)

#         if search:
#             query = query.ilike('customers.name', f'%{search}%')

#         query = query.range(offset, offset + per_page - 1)

#         response = query.execute()
#         orders = response.data
#         total = response.count

#         return jsonify({
#             'orders': orders,
#             'total': total,
#             'page': page,
#             'per_page': per_page,
#             'total_pages': (total + per_page - 1) // per_page
#         })

#     except Exception as e:
#         logger.error(str(e))
#         return jsonify({'error': str(e)}), 500
    
# @orders_api_bp.route('/order-items/<int:item_id>/prepared', methods=['PUT'])
# @login_required
# def update_item_prepared(item_id):
#     try:
#         supabase.postgrest.auth(session['access_token'])
        
#         data = request.get_json()
#         is_prepared = data.get('is_prepared', False)
        
#         response = supabase.table('order_items') \
#             .update({'is_prepared': is_prepared}) \
#             .eq('id', item_id) \
#             .execute()
        
#         return jsonify({'success': True, 'data': response.data})
    
#     except Exception as e:
#         logger.error(str(e))
#         return jsonify({'error': str(e)}), 500


# @orders_api_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
# @login_required
# def update_order_status(order_id):
#     try:
#         supabase.postgrest.auth(session['access_token'])

#         data = request.get_json()
#         new_status = data.get('status')

#         valid_statuses = ['pending', 'paid', 'delivered', 'cancelled']
#         if new_status not in valid_statuses:
#             return jsonify({'error': 'Invalid status'}), 400

#         current_order = supabase.table('orders') \
#             .select('id, status, total_amount, delivery_price') \
#             .eq('id', order_id) \
#             .single() \
#             .execute() \
#             .data

#         if not current_order:
#             return jsonify({'error': 'Order not found'}), 404

#         old_status = current_order['status']
#         total_amount = float(current_order['total_amount'])
#         delivery_price = float(current_order['delivery_price'])
#         grand_total = total_amount + delivery_price

#         response = supabase.table('orders') \
#             .update({'status': new_status}) \
#             .eq('id', order_id) \
#             .execute()

#         should_create_cashflow = (
#             old_status in ['pending', 'cancelled'] and 
#             new_status in ['paid', 'delivered']
#         )
        
#         should_delete_cashflow = (
#             old_status in ['paid', 'delivered'] and 
#             new_status == 'cancelled'
#         )
        
#         cash_balance = None
#         action_taken = None

#         if should_create_cashflow:
#             categories = supabase.table('cashflow_categories') \
#                 .select('id, name') \
#                 .in_('name', ['Product Sales', 'Delivery Fees']) \
#                 .execute() \
#                 .data
            
#             category_map = {cat['name']: cat['id'] for cat in categories}
            
#             # Create cashflow transaction for Product Sales
#             if total_amount > 0:
#                 supabase.table('cashflow_transactions').insert({
#                     'category_id': category_map['Product Sales'],
#                     'amount': total_amount,
#                     'description': f'Order #{order_id}',
#                     'reference_type': 'order',
#                     'reference_id': order_id,
#                     'created_by': session.get('user_id')
#                 }).execute()
            
#             # Create cashflow transaction for Delivery Fees (if any)
#             if delivery_price > 0:
#                 supabase.table('cashflow_transactions').insert({
#                     'category_id': category_map['Delivery Fees'],
#                     'amount': delivery_price,
#                     'description': f'Delivery for Order #{order_id}',
#                     'reference_type': 'order',
#                     'reference_id': order_id,
#                     'created_by': session.get('user_id')
#                 }).execute()
            
#             # Update cash account - ADD money
#             cash = supabase.table('cash_accounts') \
#                 .select('balance') \
#                 .eq('id', 1) \
#                 .single() \
#                 .execute() \
#                 .data
            
#             old_balance = float(cash['balance'])
#             new_balance = old_balance + grand_total
            
#             supabase.table('cash_accounts').update({
#                 'balance': round(new_balance, 2)
#             }).eq('id', 1).execute()
            
#             cash_balance = round(new_balance, 2)
#             action_taken = 'created'

#         elif should_delete_cashflow:
#             supabase.table('cashflow_transactions') \
#                 .delete() \
#                 .eq('reference_type', 'order') \
#                 .eq('reference_id', order_id) \
#                 .execute()

#             cash = supabase.table('cash_accounts') \
#                 .select('balance') \
#                 .eq('id', 1) \
#                 .single() \
#                 .execute() \
#                 .data
            
#             old_balance = float(cash['balance'])
#             new_balance = old_balance - grand_total
            
#             supabase.table('cash_accounts').update({
#                 'balance': round(new_balance, 2)
#             }).eq('id', 1).execute()
            
#             cash_balance = round(new_balance, 2)
#             action_taken = 'deleted'

#         return jsonify({
#             'success': True,
#             'order': response.data[0],
#             'cashflow_action': action_taken,
#             'cash_balance': cash_balance,
#             'old_status': old_status,
#             'new_status': new_status
#         })

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @orders_api_bp.route('/products/active')
# @login_required
# def api_active_products():
#     try:
#         supabase.postgrest.auth(session['access_token'])

#         products = supabase.table('products') \
#             .select('*') \
#             .eq('is_active', True) \
#             .order('name') \
#             .execute().data

#         return jsonify(products)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @orders_api_bp.route('/orders', methods=['POST'])
# @login_required
# def create_order_api():
#     try:
#         supabase.postgrest.auth(session['access_token'])

#         data = request.get_json()

#         # Validate
#         if not data.get('customer_id'):
#             return jsonify({'error': 'Customer is required'}), 400
        
#         if not data.get('items') or len(data['items']) == 0:
#             return jsonify({'error': 'At least one item is required'}), 400
        
#         # Calculate total
#         total_amount = sum(
#             item['quantity'] * item['sell_price'] 
#             for item in data['items']
#         )

#         delivery_price = data.get('delivery_price', 0)

#         order_data = {
#             "customer_id": data['customer_id'],
#             "order_date": data.get('order_date'),
#             "status": data.get('status', 'pending'),
#             "total_amount": total_amount,
#             "delivery_price": delivery_price,
#             "delivery_type": data.get('delivery_type', 'pickup'),
#             "created_by": session.get('user_id')
#         }

#         order_result = supabase.table("orders") \
#             .insert(order_data) \
#             .execute()

#         order_id = order_result.data[0]['id']

#         items_data = [
#             {
#                 "order_id": order_id,
#                 "product_id": item['product_id'],
#                 "quantity": item['quantity'],
#                 "buy_price": item['buy_price'],
#                 "sell_price": item['sell_price']
#             }
#             for item in data['items']
#         ]
        
#         supabase.table("order_items") \
#             .insert(items_data) \
#             .execute()

#         status = data.get('status', 'pending')
#         cash_balance = None

#         if status in ['paid', 'delivered']:
#             categories = supabase.table('cashflow_categories') \
#                 .select('id, name') \
#                 .in_('name', ['Product Sales', 'Delivery Fees']) \
#                 .execute() \
#                 .data

#             category_map = {cat['name']: cat['id'] for cat in categories}

#             if total_amount > 0:
#                 supabase.table('cashflow_transactions').insert({
#                     'category_id': category_map['Product Sales'],
#                     'amount': total_amount,
#                     'description': f'Order #{order_id}',
#                     'reference_type': 'order',
#                     'reference_id': order_id,
#                     'created_by': session.get('user_id')
#                 }).execute()

#             if delivery_price > 0:
#                 supabase.table('cashflow_transactions').insert({
#                     'category_id': category_map['Delivery Fees'],
#                     'amount': delivery_price,
#                     'description': f'Delivery for Order #{order_id}',
#                     'reference_type': 'order',
#                     'reference_id': order_id,
#                     'created_by': session.get('user_id')
#                 }).execute()

#             cash = supabase.table('cash_accounts') \
#                 .select('balance') \
#                 .eq('id', 1) \
#                 .single() \
#                 .execute() \
#                 .data

#             old_balance = float(cash['balance'])
#             grand_total = total_amount + delivery_price
#             new_balance = old_balance + grand_total

#             supabase.table('cash_accounts').update({
#                 'balance': round(new_balance, 2)
#             }).eq('id', 1).execute()

#             cash_balance = round(new_balance, 2)

#         return jsonify({
#             'success': True,
#             'order_id': order_id,
#             'message': 'Order created successfully',
#             'cash_balance': cash_balance
#         })

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @orders_api_bp.route('/orders/<int:order_id>', methods=['GET', 'PUT'])
# @login_required
# def get_order(order_id):
#     if request.method == 'GET':
#         try:
#             supabase.postgrest.auth(session['access_token'])

#             response = supabase.table('orders') \
#                 .select('''
#                     id,
#                     order_date,
#                     status,
#                     total_amount,
#                     delivery_price,
#                     delivery_type,
#                     customer_id,
#                     customers!inner(id, name, phone),
#                     order_items(
#                         id,
#                         product_id,
#                         quantity,
#                         buy_price,
#                         sell_price,
#                         products(id, name, unit)
#                     )
#                 ''') \
#                 .eq('id', order_id) \
#                 .single() \
#                 .execute()

#             if not response.data:
#                 return jsonify({'error': 'Order not found'}), 404

#             order_data = response.data

#             formatted_order = {
#                 'id': order_data['id'],
#                 'customer_id': order_data['customer_id'],
#                 'order_date': order_data['order_date'],
#                 'status': order_data['status'],
#                 'delivery_type': order_data['delivery_type'],
#                 'delivery_price': float(order_data['delivery_price']) if order_data['delivery_price'] else 0,
#                 'total_amount': float(order_data['total_amount']) if order_data['total_amount'] else 0,
#                 'customer_name': order_data['customers']['name'],
#                 'items': []
#             }

#             for item in order_data.get('order_items', []):
#                 formatted_order['items'].append({
#                     'id': item['id'],
#                     'product_id': item['product_id'],
#                     'quantity': float(item['quantity']),
#                     'buy_price': float(item['buy_price']),
#                     'sell_price': float(item['sell_price']),
#                     'product_name': item['products']['name'],
#                     'unit': item['products']['unit']
#                 })

#             return jsonify(formatted_order)

#         except Exception as e:
#             print(f"Error getting order: {str(e)}")
#             return jsonify({'error': str(e)}), 500
    
#     try:
#         data = request.get_json()
#         supabase.postgrest.auth(session['access_token'])
#         print(data)

#         order_check = supabase.table('orders') \
#             .select('status') \
#             .eq('id', order_id) \
#             .single() \
#             .execute()
        
#         if not order_check.data:
#             return jsonify({'error': 'Order not found'}), 404

#         current_status = order_check.data['status']
#         new_status = data.get('status', current_status)

#         if current_status != 'pending':
#             return jsonify({
#                 'error': 'Only pending orders can be edited',
#                 'current_status': current_status
#             }), 400

#         subtotal = sum(item['quantity'] * item['sell_price'] for item in data['items'])
#         total_amount = subtotal + data.get('delivery_price', 0)

#         supabase.table('orders') \
#             .update({
#                 'order_date': data['order_date'],
#                 'customer_id': data['customer_id'],
#                 'delivery_type': data['delivery_type'],
#                 'delivery_price': data['delivery_price'],
#                 'status': new_status,
#                 'total_amount': total_amount
#             }) \
#             .eq('id', order_id) \
#             .execute()

#         items_to_delete = data.get('items_to_delete', [])
#         if items_to_delete:
#             for item_id in items_to_delete:
#                 supabase.table('order_items') \
#                     .delete() \
#                     .eq('id', item_id) \
#                     .eq('order_id', order_id) \
#                     .execute()

#         for item in data['items']:
#             if 'id' in item and item['id']:
#                 supabase.table('order_items') \
#                     .update({
#                         'product_id': item['product_id'],
#                         'quantity': item['quantity'],
#                         'buy_price': item['buy_price'],
#                         'sell_price': item['sell_price']
#                     }) \
#                     .eq('id', item['id']) \
#                     .eq('order_id', order_id) \
#                     .execute()
#             else:
#                 supabase.table('order_items') \
#                     .insert({
#                         'order_id': order_id,
#                         'product_id': item['product_id'],
#                         'quantity': item['quantity'],
#                         'buy_price': item['buy_price'],
#                         'sell_price': item['sell_price']
#                     }) \
#                     .execute()

#         return jsonify({
#             'success': True,
#             'message': 'Order updated successfully',
#             'order_id': order_id,
#             'total_amount': total_amount
#         })

#     except Exception as e:
#         print(f'Error updating order: {str(e)}')
#         return jsonify({'error': str(e)}), 500



# # @orders_api_bp.route('/orders/<int:order_id>', methods=['PUT'])
# # @login_required
# # def update_order(order_id):
# #     try:
# #         data = request.get_json()
# #         supabase.postgrest.auth(session['access_token'])
# #         print(data)

# #         order_check = supabase.table('orders') \
# #             .select('status') \
# #             .eq('id', order_id) \
# #             .single() \
# #             .execute()
        
# #         if not order_check.data:
# #             return jsonify({'error': 'Order not found'}), 404

# #         current_status = order_check.data['status']
# #         new_status = data.get('status', current_status)

# #         if current_status != 'pending':
# #             return jsonify({
# #                 'error': 'Only pending orders can be edited',
# #                 'current_status': current_status
# #             }), 400

# #         subtotal = sum(item['quantity'] * item['sell_price'] for item in data['items'])
# #         total_amount = subtotal + data.get('delivery_price', 0)

# #         supabase.table('orders') \
# #             .update({
# #                 'order_date': data['order_date'],
# #                 'customer_id': data['customer_id'],
# #                 'delivery_type': data['delivery_type'],
# #                 'delivery_price': data['delivery_price'],
# #                 'status': new_status,
# #                 'total_amount': total_amount
# #             }) \
# #             .eq('id', order_id) \
# #             .execute()

# #         items_to_delete = data.get('items_to_delete', [])
# #         if items_to_delete:
# #             for item_id in items_to_delete:
# #                 supabase.table('order_items') \
# #                     .delete() \
# #                     .eq('id', item_id) \
# #                     .eq('order_id', order_id) \
# #                     .execute()

# #         for item in data['items']:
# #             if 'id' in item and item['id']:
# #                 supabase.table('order_items') \
# #                     .update({
# #                         'product_id': item['product_id'],
# #                         'quantity': item['quantity'],
# #                         'buy_price': item['buy_price'],
# #                         'sell_price': item['sell_price']
# #                     }) \
# #                     .eq('id', item['id']) \
# #                     .eq('order_id', order_id) \
# #                     .execute()
# #             else:
# #                 supabase.table('order_items') \
# #                     .insert({
# #                         'order_id': order_id,
# #                         'product_id': item['product_id'],
# #                         'quantity': item['quantity'],
# #                         'buy_price': item['buy_price'],
# #                         'sell_price': item['sell_price']
# #                     }) \
# #                     .execute()

# #         return jsonify({
# #             'success': True,
# #             'message': 'Order updated successfully',
# #             'order_id': order_id,
# #             'total_amount': total_amount
# #         })

# #     except Exception as e:
# #         print(f'Error updating order: {str(e)}')
# #         return jsonify({'error': str(e)}), 500


