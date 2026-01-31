-- Users table
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(20) DEFAULT 'staff' CHECK (role IN ('admin', 'staff', 'driver', 'customers')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Products table
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  category_id BIGINT DEFAULT NULL,
  unit VARCHAR(20) DEFAULT 'kg',
  buy_price DECIMAL(10,2) NOT NULL,
  sell_price DECIMAL(10,2) NOT NULL,
  stock DECIMAL(10,2) DEFAULT 0.00,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Customers table
CREATE TABLE customers (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(30),
  address TEXT,
  latitude DECIMAL(10,6),
  longitude DECIMAL(10,6),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Orders table
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  order_date TIMESTAMPTZ DEFAULT NOW(),
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'delivered', 'cancelled')),
  created_by BIGINT,
  total_amount DECIMAL(12,2),
  delivery_price DECIMAL(10,2) DEFAULT 0.00,
  delivery_type VARCHAR(20) DEFAULT 'pickup' CHECK (delivery_type IN ('pickup', 'delivery')),
  FOREIGN KEY (customer_id) REFERENCES customers(id),
  FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Order items table
CREATE TABLE order_items (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity DECIMAL(10,2) NOT NULL,
  buy_price DECIMAL(10,2) NOT NULL,
  sell_price DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Delivery routes table
CREATE TABLE delivery_routes (
  id BIGSERIAL PRIMARY KEY,
  route_date DATE NOT NULL,
  driver_id BIGINT DEFAULT NULL,
  order_id BIGINT DEFAULT NULL,
  delivery_price DECIMAL(10,2) DEFAULT 0.00,
  start_lat DECIMAL(10,6) DEFAULT NULL,
  start_lng DECIMAL(10,6) DEFAULT NULL,
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  FOREIGN KEY (driver_id) REFERENCES users(id),
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
);

-- Create indexes for better performance
CREATE INDEX idx_delivery_routes_driver ON delivery_routes(driver_id);
CREATE INDEX idx_delivery_routes_order ON delivery_routes(order_id);
CREATE INDEX idx_delivery_routes_date ON delivery_routes(route_date);

-- Create trigger for updated_at on delivery_routes
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_delivery_routes_updated_at
BEFORE UPDATE ON delivery_routes
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE cashflow_categories (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Main cashflow transactions table
CREATE TABLE cashflow_transactions (
  id BIGSERIAL PRIMARY KEY,
  transaction_date TIMESTAMPTZ DEFAULT NOW(),
  category_id BIGINT NOT NULL,
  amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
  description TEXT,
  payment_method VARCHAR(30) DEFAULT 'cash',
  reference_type VARCHAR(50),
  reference_id BIGINT,
  created_by BIGINT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  FOREIGN KEY (category_id) REFERENCES cashflow_categories(id),
  FOREIGN KEY (created_by) REFERENCES users(id)
);

