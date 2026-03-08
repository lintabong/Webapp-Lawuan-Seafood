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
  status VARCHAR(20) DEFAULT 'pending' CHECK (
    status IN (
        'pending', 'paid', 'prepared', 'delivered', 'picked up', 'cancelled')),
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
  is_prepared BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(id)
);

-- need to edit
CREATE TABLE transaction_categories (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  type VARCHAR(20) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT transaction_categories_type_check CHECK (
    type IN ('income', 'expense', 'sale', 'purchase', 'transfer', 'adjustment')
  )
);

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


CREATE TABLE transactions (
  id BIGSERIAL PRIMARY KEY,
  type VARCHAR(20) NOT NULL,
  category_id BIGINT,
  reference_type VARCHAR(50),
  reference_id BIGINT,
  amount NUMERIC(12,2) NOT NULL,
  description TEXT,
  created_by UUID,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  transaction_date TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NULL,
  status VARCHAR(20) DEFAULT 'posted' 
  CONSTRAINT transactions_type_check CHECK (
    type IN ('draft', 'partial', 'settled', 'voided', 'reversed')
  ),

  CONSTRAINT transactions_category_fkey
    FOREIGN KEY (category_id) REFERENCES transaction_categories(id),

  CONSTRAINT transactions_created_by_fkey
    FOREIGN KEY (created_by) REFERENCES users(id)
);


CREATE TABLE transaction_items (
  id BIGSERIAL PRIMARY KEY,
  transaction_id BIGINT NOT NULL,
  item_type VARCHAR(20) DEFAULT 'product',
  product_id BIGINT,
  description TEXT,
  quantity NUMERIC(10,2) DEFAULT 1,
  price NUMERIC(12,2),
  subtotal NUMERIC(12,2),
  created_at TIMESTAMPTZ DEFAULT NOW(),

  CONSTRAINT transaction_items_transaction_fkey
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,

  CONSTRAINT transaction_items_product_fkey
    FOREIGN KEY (product_id) REFERENCES products(id),

  CONSTRAINT transaction_items_type_check CHECK (
    item_type IN ('product', 'service', 'expense', 'custom')
  )
);

create table public.cash (
  id bigserial not null,
  name character varying(50) not null,
  balance numeric(14, 2) not null default 0.00,
  is_active boolean null default true,
  created_at timestamp with time zone null default now(),
  constraint cash_pkey primary key (id)
) TABLESPACE pg_default;


CREATE TABLE cash_ledgers (
  id BIGSERIAL PRIMARY KEY,
  cash_id BIGINT NOT NULL,
  transaction_id BIGINT,
  direction VARCHAR(10) CHECK (direction IN ('in', 'out')),
  amount DECIMAL(14,2) NOT NULL,
  balance_after DECIMAL(14,2) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  FOREIGN KEY (cash_id) REFERENCES cash(id),
  FOREIGN KEY (transaction_id) REFERENCES cashflow_transactions(id)
);

ALTER TABLE cash_ledgers
DROP CONSTRAINT cash_ledgers_transaction_id_fkey;

ALTER TABLE cash_ledgers
ADD CONSTRAINT cash_ledgers_transaction_id_fkey
FOREIGN KEY (transaction_id)
REFERENCES transactions(id)
ON DELETE SET NULL;



UPDATE transactions SET reference_type = 'transaction_items';

UPDATE orders
SET status = 'pending'
WHERE order_date >= TIMESTAMPTZ '2026-01-31 17:00:00+00';

alter table public.transactions
add column status varchar(20) not null default 'posted';

alter table public.transactions
add constraint transactions_status_check
check (
  status in ('draft', 'posted', 'partial', 'settled', 'voided', 'reversed')
);



create table public.product_price_tiers (
  id bigserial primary key,
  product_id bigint not null references products(id) on delete cascade,
  min_qty numeric(10,2) not null,   -- minimum weight
  max_qty numeric(10,2) not null,   -- maximum weight
  price numeric(10,2) not null,     -- price per kg
  created_at timestamptz default now()
);