-- Users table (unified for all user types including customers)
CREATE TABLE users (
  id UUID PRIMARY KEY, -- auth.users.id
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  role VARCHAR(20) DEFAULT 'staff' CHECK (role IN ('admin', 'staff', 'driver', 'customer')),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Customer details table (additional info for customer users)
CREATE TABLE customers (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(30),
  address TEXT,
  latitude DECIMAL(10,6),
  longitude DECIMAL(10,6),
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

-- Orders table (now references users instead of customers)
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  order_date TIMESTAMPTZ DEFAULT NOW(),
  status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'delivered', 'cancelled')),
  created_by UUID,
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
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id)
);


-- Cashflow categories table
CREATE TABLE cashflow_categories (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);


-- Cashflow transactions table
CREATE TABLE cashflow_transactions (
  id BIGSERIAL PRIMARY KEY,
  transaction_date TIMESTAMPTZ DEFAULT NOW(),
  category_id BIGINT NOT NULL,
  amount DECIMAL(12,2) NOT NULL CHECK (amount > 0),
  description TEXT,
  payment_method VARCHAR(30) DEFAULT 'cash',
  reference_type VARCHAR(50),
  reference_id BIGINT,
  created_by UUID,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  FOREIGN KEY (category_id) REFERENCES cashflow_categories(id),
  FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE cash_accounts (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,           -- Cash, BCA, Mandiri, etc
  balance DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO cash_accounts (name, balance)
VALUES ('Cash', 0.00);

-- Create indexes for better performance
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_created_by ON orders(created_by);

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.users (id, email, name, role)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', 'Unknown'),
    'staff'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE PROCEDURE public.handle_new_user();


-- Product purchase items table
CREATE TABLE product_purchase_items (
  id BIGSERIAL PRIMARY KEY,
  transaction_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity DECIMAL(10,2) NOT NULL,
  buy_price DECIMAL(12,2) NOT NULL,
  subtotal DECIMAL(12,2) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  FOREIGN KEY (transaction_id) REFERENCES cashflow_transactions(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE INDEX idx_purchase_items_transaction ON product_purchase_items(transaction_id);
CREATE INDEX idx_purchase_items_product ON product_purchase_items(product_id);

ALTER TABLE cashflow_transactions
ADD COLUMN cash_account_id BIGINT;

ALTER TABLE cashflow_transactions
ADD CONSTRAINT fk_cash_account
FOREIGN KEY (cash_account_id) REFERENCES cash_accounts(id);

CREATE TABLE cash_account_ledgers (
  id BIGSERIAL PRIMARY KEY,
  cash_account_id BIGINT NOT NULL,
  transaction_id BIGINT,
  direction VARCHAR(10) CHECK (direction IN ('in', 'out')),
  amount DECIMAL(14,2) NOT NULL,
  balance_after DECIMAL(14,2) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  FOREIGN KEY (cash_account_id) REFERENCES cash_accounts(id),
  FOREIGN KEY (transaction_id) REFERENCES cashflow_transactions(id)
);
