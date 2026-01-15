
from app.services.database import get_db_connection
from mysql.connector import Error

class Product:
    @staticmethod
    def get_all(active_only=True):
        """Fetch all products"""
        connection = get_db_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT id, name, unit, buy_price, sell_price, stock 
                FROM products 
            """
            if active_only:
                query += "WHERE isActive = 1 "
            query += "ORDER BY name"
            
            cursor.execute(query)
            products = cursor.fetchall()
            return products
        except Error as e:
            print(f"Error fetching products: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_by_id(product_id):
        """Get product by ID"""
        connection = get_db_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM products WHERE id = %s"
            cursor.execute(query, (product_id,))
            product = cursor.fetchone()
            return product
        except Error as e:
            print(f"Error fetching product: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def update_stock(product_id, quantity):
        """Update product stock"""
        connection = get_db_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            query = "UPDATE products SET stock = stock - %s WHERE id = %s"
            cursor.execute(query, (quantity, product_id))
            connection.commit()
            return True
        except Error as e:
            connection.rollback()
            print(f"Error updating stock: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
