
from flask import Blueprint, jsonify, request
from app import log
from app.helpers.auth import login_required
from app.repositories.product_repo import list_product

products_api_bp = Blueprint('products_api', __name__)

logger = log.get_logger('API_PRODUCT')


@products_api_bp.route('/products')
@login_required
def api_products():
    try:
        products = list_product(
            request.args.get('is_active'),
            request.args.get('search')
        )
        
        return jsonify(products)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @products_api_bp.route("/api/products/<int:product_id>", methods=['PUT'])
# @login_required
# def update_product(product_id):
#     """API endpoint to update product"""
#     try:
#         supabase.postgrest.auth(session["access_token"])
        
#         data = request.get_json()
        
#         # Validate required fields
#         if not data.get('name'):
#             return jsonify({"error": "Product name is required"}), 400
        
#         if data.get('buy_price') is not None and float(data['buy_price']) < 0:
#             return jsonify({"error": "Buy price must be positive"}), 400
            
#         if data.get('sell_price') is not None and float(data['sell_price']) < 0:
#             return jsonify({"error": "Sell price must be positive"}), 400
        
#         # Update product
#         result = supabase.table("products") \
#             .update(data) \
#             .eq("id", product_id) \
#             .execute()
        
#         return jsonify({"success": True, "data": result.data})
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @products_api_bp.route("/api/products", methods=['POST'])
# @login_required
# def create_product():
#     try:
#         supabase.postgrest.auth(session["access_token"])
        
#         data = request.get_json()
        
#         # Validate required fields
#         if not data.get('name'):
#             return jsonify({"error": "Product name is required"}), 400
        
#         # Insert product
#         result = supabase.table("products") \
#             .insert(data) \
#             .execute()
        
#         return jsonify({"success": True, "data": result.data})
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @products_api_bp.route("/api/products/<int:product_id>/toggle", methods=['PUT'])
# @login_required
# def toggle_product_status(product_id):
#     try:
#         supabase.postgrest.auth(session["access_token"])
        
#         data = request.get_json()
#         is_active = data.get('is_active', True)
        
#         result = supabase.table("products") \
#             .update({"is_active": is_active}) \
#             .eq("id", product_id) \
#             .execute()
        
#         return jsonify({"success": True, "data": result.data})
        
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
