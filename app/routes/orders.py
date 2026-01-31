
from flask import (
    Blueprint, render_template, 
    request, jsonify, session
)
from app.lib.supabase_client import supabase
from app.helpers.auth import login_required

orders_bp = Blueprint('orders', __name__)


@orders_bp.route("/my-orders")
@login_required
def orders():
    return render_template("orders.html")

@orders_bp.route("/api/orders")
@login_required
def api_orders():
    """API endpoint for orders list"""
    try:
        supabase.postgrest.auth(session["access_token"])
        
        # Get filter parameters
        status = request.args.get('status')
        search = request.args.get('search')
        
        # Base query with joins - now including order_items and products
        query = supabase.table("orders") \
            .select("""
                id,
                order_date,
                status,
                total_amount,
                delivery_price,
                delivery_type,
                customers!inner(id, name, phone, address),
                order_items(
                    id,
                    quantity,
                    sell_price,
                    products(name, unit)
                )
            """) \
            .order("order_date", desc=True)
        
        # Apply filters
        if status and status != 'all':
            query = query.eq("status", status)
        
        if search:
            query = query.ilike("customers.name", f"%{search}%")
        
        orders = query.execute().data
        
        return jsonify(orders)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route("/api/orders/<int:order_id>/status", methods=['PUT'])
@login_required
def update_order_status(order_id):
    """API endpoint to update order status"""
    try:
        supabase.postgrest.auth(session["access_token"])
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['pending', 'paid', 'delivered', 'cancelled']:
            return jsonify({"error": "Invalid status"}), 400
        
        result = supabase.table("orders") \
            .update({"status": new_status}) \
            .eq("id", order_id) \
            .execute()
        
        return jsonify({"success": True, "data": result.data})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route("/orders/create")
@login_required
def create_order():
    """Render the create order page"""
    return render_template("create_order.html")

@orders_bp.route("/api/customers")
@login_required
def api_customers():
    """API endpoint for customers list"""
    try:
        supabase.postgrest.auth(session["access_token"])
        
        customers = supabase.table("customers") \
            .select("*") \
            .order("name") \
            .execute().data
        
        return jsonify(customers)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route("/api/products/active")
@login_required
def api_active_products():
    """API endpoint for active products"""
    try:
        supabase.postgrest.auth(session["access_token"])
        
        products = supabase.table("products") \
            .select("*") \
            .eq("is_active", True) \
            .order("name") \
            .execute().data
        
        return jsonify(products)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route("/api/orders", methods=['POST'])
@login_required
def create_order_api():
    """API endpoint to create new order"""
    try:
        supabase.postgrest.auth(session["access_token"])
        
        data = request.get_json()
        
        # Validate
        if not data.get('customer_id'):
            return jsonify({"error": "Customer is required"}), 400
        
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({"error": "At least one item is required"}), 400
        
        # Calculate total
        total_amount = sum(
            item['quantity'] * item['sell_price'] 
            for item in data['items']
        )
        
        # Create order
        order_data = {
            "customer_id": data['customer_id'],
            "order_date": data.get('order_date'),
            "status": data.get('status', 'pending'),
            "total_amount": total_amount,
            "delivery_price": data.get('delivery_price', 0),
            "delivery_type": data.get('delivery_type', 'pickup'),
            "created_by": session.get('user_id')
        }
        
        order_result = supabase.table("orders") \
            .insert(order_data) \
            .execute()
        
        order_id = order_result.data[0]['id']
        
        # Create order items
        items_data = [
            {
                "order_id": order_id,
                "product_id": item['product_id'],
                "quantity": item['quantity'],
                "buy_price": item['buy_price'],
                "sell_price": item['sell_price']
            }
            for item in data['items']
        ]
        
        supabase.table("order_items") \
            .insert(items_data) \
            .execute()
        
        return jsonify({
            "success": True,
            "order_id": order_id,
            "message": "Order created successfully"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
