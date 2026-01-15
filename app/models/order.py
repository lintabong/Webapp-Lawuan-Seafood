
from mysql.connector import Error

from app.services.database import get_db_connection


class Order:
    @staticmethod
    def get_all():
        """Fetch all orders"""
        connection = get_db_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT 
                    o.id,
                    o.order_date,
                    o.status,
                    o.total_amount,
                    o.delivery_price,
                    o.delivery_type,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    u.name as created_by_name
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.id
                LEFT JOIN users u ON o.created_by = u.id
                ORDER BY o.order_date DESC
            """
            cursor.execute(query)
            orders = cursor.fetchall()
            return orders
        except Error as e:
            print(f"Error fetching orders: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_by_id(order_id):
        """Fetch order details including items"""
        connection = get_db_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get order header
            query = """
                SELECT 
                    o.id,
                    o.order_date,
                    o.status,
                    o.total_amount,
                    o.delivery_price,
                    o.delivery_type,
                    o.customer_id,
                    c.name as customer_name,
                    c.phone as customer_phone,
                    c.address as customer_address,
                    u.name as created_by_name
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.id
                LEFT JOIN users u ON o.created_by = u.id
                WHERE o.id = %s
            """
            cursor.execute(query, (order_id,))
            order = cursor.fetchone()
            
            if not order:
                return None
            
            # Get order items
            query = """
                SELECT 
                    oi.id,
                    oi.quantity,
                    oi.buy_price,
                    oi.sell_price,
                    p.name as product_name,
                    p.unit as product_unit,
                    (oi.quantity * oi.sell_price) as subtotal
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """
            cursor.execute(query, (order_id,))
            order['order_items'] = cursor.fetchall()
            
            return order
        except Error as e:
            print(f"Error fetching order details: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_with_coordinates(route_date):
        """Get orders with customer coordinates for a specific date"""
        connection = get_db_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT
                    o.id AS order_id,
                    o.order_date,
                    o.status,
                    o.delivery_type,
                    o.delivery_price,
                    o.total_amount,
                    c.id AS customer_id,
                    c.name AS customer_name,
                    c.phone,
                    c.address,
                    c.latitude,
                    c.longitude,
                    GROUP_CONCAT(
                        CONCAT(
                            p.name, '||',
                            oi.quantity, '||',
                            p.unit, '||',
                            oi.sell_price
                        )
                        SEPARATOR '##'
                    ) AS products
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                JOIN order_items oi ON oi.order_id = o.id
                JOIN products p ON p.id = oi.product_id
                WHERE o.delivery_type = 'delivery' 
                  AND status IN ('pending', 'delivered', 'paid')
                  AND c.latitude IS NOT NULL
                  AND c.longitude IS NOT NULL
                  AND DATE(o.order_date) = %s
                GROUP BY o.id
                ORDER BY o.order_date ASC
            """
            cursor.execute(query, (route_date,))
            rows = cursor.fetchall()

            # Parse product string into list
            for row in rows:
                product_list = []
                if row['products']:
                    items = row['products'].split('##')
                    for item in items:
                        name, qty, unit, price = item.split('||')
                        product_list.append({
                            'name': name,
                            'quantity': float(qty),
                            'unit': unit,
                            'sell_price': price
                        })
                row['products'] = product_list

            return rows
        except Error as e:
            print(f"Error fetching orders: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def create(customer_id, items, delivery_price=0, delivery_type='pickup', 
               status='pending', created_by=1):
        """Create a new order"""
        connection = get_db_connection()
        if not connection:
            raise Exception('Database connection failed')
        
        try:
            cursor = connection.cursor()
            
            # Calculate total amount
            total_amount = sum(float(item['quantity']) * float(item['sell_price']) 
                             for item in items)
            total_amount += float(delivery_price)
            
            # Insert order
            insert_order_query = """
                INSERT INTO orders 
                (customer_id, status, total_amount, delivery_price, delivery_type, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_order_query, (
                customer_id, status, total_amount, delivery_price, 
                delivery_type, created_by
            ))
            order_id = cursor.lastrowid
            
            # Insert order items
            insert_item_query = """
                INSERT INTO order_items 
                (order_id, product_id, quantity, buy_price, sell_price)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            for item in items:
                cursor.execute(insert_item_query, (
                    order_id,
                    item['product_id'],
                    item['quantity'],
                    item['buy_price'],
                    item['sell_price']
                ))
                
                # Update product stock
                update_stock_query = """
                    UPDATE products 
                    SET stock = stock - %s 
                    WHERE id = %s
                """
                cursor.execute(update_stock_query, 
                             (item['quantity'], item['product_id']))
            
            connection.commit()
            return order_id
            
        except Error as e:
            connection.rollback()
            print(f"Error creating order: {e}")
            raise e
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def update_status(order_id, status):
        """Update order status"""
        connection = get_db_connection()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            query = "UPDATE orders SET status = %s WHERE id = %s"
            cursor.execute(query, (status, order_id))
            connection.commit()
            return cursor.rowcount > 0
        except Error as e:
            connection.rollback()
            print(f"Error updating order status: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
