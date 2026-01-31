
from flask import Blueprint, render_template, request, jsonify, session
from app.lib.supabase_client import supabase
from app.helpers.auth import login_required

products_bp = Blueprint('products', __name__)

@products_bp.route("/my-products")
@login_required
def products():
    """Render the products page (HTML only)"""
    return render_template("products.html")

@products_bp.route("/api/products")
@login_required
def api_products():
    """API endpoint for products list"""
    try:
        supabase.postgrest.auth(session["access_token"])
        
        # Get filter parameters
        is_active = request.args.get('is_active')
        search = request.args.get('search')
        
        # Base query
        query = supabase.table("products") \
            .select("*") \
            .order("name")
        
        # Apply filters
        if is_active and is_active != 'all':
            query = query.eq("is_active", is_active == 'true')
        
        if search:
            query = query.ilike("name", f"%{search}%")
        
        products = query.execute().data
        
        return jsonify(products)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route("/api/products/<int:product_id>", methods=['PUT'])
@login_required
def update_product(product_id):
    """API endpoint to update product"""
    try:
        supabase.postgrest.auth(session["access_token"])
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Product name is required"}), 400
        
        if data.get('buy_price') is not None and float(data['buy_price']) < 0:
            return jsonify({"error": "Buy price must be positive"}), 400
            
        if data.get('sell_price') is not None and float(data['sell_price']) < 0:
            return jsonify({"error": "Sell price must be positive"}), 400
        
        # Update product
        result = supabase.table("products") \
            .update(data) \
            .eq("id", product_id) \
            .execute()
        
        return jsonify({"success": True, "data": result.data})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route("/api/products", methods=['POST'])
@login_required
def create_product():
    """API endpoint to create new product"""
    try:
        supabase.postgrest.auth(session["access_token"])
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Product name is required"}), 400
        
        # Insert product
        result = supabase.table("products") \
            .insert(data) \
            .execute()
        
        return jsonify({"success": True, "data": result.data})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route("/api/products/<int:product_id>/toggle", methods=['PUT'])
@login_required
def toggle_product_status(product_id):
    """API endpoint to toggle product active status"""
    try:
        supabase.postgrest.auth(session["access_token"])
        
        data = request.get_json()
        is_active = data.get('is_active', True)
        
        result = supabase.table("products") \
            .update({"is_active": is_active}) \
            .eq("id", product_id) \
            .execute()
        
        return jsonify({"success": True, "data": result.data})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
