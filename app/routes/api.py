
from datetime import date
from flask import Blueprint, jsonify, request

from app.models.customer import Customer
from app.models.product import Product
from app.models.order import Order

api_bp = Blueprint('api', __name__)

@api_bp.route('/customers')
def customers():
    customers = Customer.get_with_coordinates()
    return jsonify(customers)

@api_bp.route('/products')
def products():
    products = Product.get_all()
    return jsonify(products)

@api_bp.route('/order-route')
def order_route():
    route_date = request.args.get('date')
    if not route_date:
        route_date = date.today().isoformat()
    
    orders = Order.get_with_coordinates(route_date)
    return jsonify(orders)

@api_bp.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        if not data.get('customer_id'):
            return jsonify({'success': False, 
                          'message': 'Customer is required'}), 400
        
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'success': False, 
                          'message': 'At least one item is required'}), 400
        
        order_id = Order.create(
            customer_id=data['customer_id'],
            items=data['items'],
            delivery_price=data.get('delivery_price', 0),
            delivery_type=data.get('delivery_type', 'pickup'),
            status=data.get('status', 'pending'),
            created_by=data.get('created_by', 1)
        )
        
        return jsonify({
            'success': True, 
            'message': 'Order created successfully',
            'order_id': order_id
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/orders/', methods=['GET'])
def get_order(order_id):
    order = Order.get_by_id(order_id)
    if not order:
        return jsonify({'success': False, 
                       'message': 'Order not found'}), 404
    
    return jsonify({'success': True, 'order': order}), 200

@api_bp.route('/orders/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['pending', 'paid', 'delivered', 'cancelled']:
            return jsonify(
                {
                    'success': False, 
                    'message': 'Invalid status'
                }), 400
        
        success = Order.update_status(order_id, new_status)
        
        if not success:
            return jsonify(
                {
                    'success': False, 
                    'message': 'Order not found'
                }), 404
        
        return jsonify(
            {
                'success': True, 
                'message': 'Order status updated'
            }), 200
        
    except Exception as e:
        return jsonify(
            {
                'success': False, 
                'message': str(e)
            }), 500
