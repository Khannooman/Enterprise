CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phone_number VARCHAR(20),
    company_name VARCHAR(100) NOT NULL,
    addressline1 VARCHAR(100) NOT NULL,
    addressline2 VARCHAR(100),
    landmark VARCHAR(100),
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,     
    pincode VARCHAR(10) NOT NULL,
    country VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    contact_info VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE products (
    product_id VARCHAR(50),
    user_id VARCHAR(50),
    product VARCHAR(100) NOT NULL,
    weight VARCHAR(50),
    batch_number VARCHAR(50),
    expiry_date DATE,
    quantity INTEGER NOT NULL CHECK (stock >= 0),
    mrp DECIMAL(10, 2) NOT NULL,
    distributer_landing DECIMAL(10, 2),
    selling_price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (product_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE orders (
    order_id VARCHAR(50),
    product_id VARCHAR(50),
    user_id VARCHAR(50),
    customer_id VARCHAR(50),
    created_by_name VARCHAR(50),
    invoice_id VARCHAR(50),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    rate DECIMAL(10, 2) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id, user_id) REFERENCES products(product_id, user_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE CASCADE
);

CREATE TABLE invoices (
    invoice_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50),
    invoice_number VARCHAR(50) NOT NULL UNIQUE,
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    created_by_name VARCHAR(50),
    amount_paid DECIMAL(10, 2) DEFAULT 0.0,
    payment_status VARCHAR DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
);

CREATE TABLE payments(
    payment_id VARCHAR(50) PRIMARY KEY,
    invoice_id UUID NOT NULL,
    user_id UUID NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(50),  -- e.g., 'cash', 'credit_card', 'bank_transfer'
    note TEXT,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)

