
from app.services.database import get_db_connection
from mysql.connector import Error

class Customer:
    @staticmethod
    def get_all():
        connection = get_db_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """SELECT id, name, phone, address, latitude, longitude 
                        FROM customers ORDER BY name"""
            cursor.execute(query)
            customers = cursor.fetchall()
            return customers
        except Error as e:
            print(f"Error fetching customers: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_with_coordinates():
        connection = get_db_connection()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT id, name, phone, address, latitude, longitude 
                FROM customers 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                ORDER BY name
            """
            cursor.execute(query)
            customers = cursor.fetchall()
            return customers
        except Error as e:
            print(f"Error fetching customers: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def create(name, phone, address, latitude=None, longitude=None):
        """Create a new customer"""
        connection = get_db_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            query = """
                INSERT INTO customers (name, phone, address, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, phone, address, latitude, longitude))
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            connection.rollback()
            print(f"Error creating customer: {e}")
            raise e
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    @staticmethod
    def get_by_id(customer_id):
        """Get customer by ID"""
        connection = get_db_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM customers WHERE id = %s"
            cursor.execute(query, (customer_id,))
            customer = cursor.fetchone()
            return customer
        except Error as e:
            print(f"Error fetching customer: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()