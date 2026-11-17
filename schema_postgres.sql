-- PostgreSQL schema for Render deployment.
CREATE TABLE IF NOT EXISTS contacts (
    id BIGSERIAL PRIMARY KEY, full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL, phone VARCHAR(50), company VARCHAR(150),
    job_title VARCHAR(100), address TEXT, notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_contact_name ON contacts (full_name);
CREATE INDEX IF NOT EXISTS idx_contact_email ON contacts (email);
CREATE INDEX IF NOT EXISTS idx_contact_phone ON contacts (phone);

CREATE TABLE IF NOT EXISTS leads (
    id BIGSERIAL PRIMARY KEY, full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150), phone VARCHAR(50), company VARCHAR(150),
    source VARCHAR(100), status VARCHAR(20) NOT NULL DEFAULT 'New'
        CHECK (status IN ('New', 'Contacted', 'Qualified', 'Converted', 'Lost')),
    notes TEXT, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_lead_status ON leads (status);
CREATE INDEX IF NOT EXISTS idx_lead_name ON leads (full_name);
CREATE INDEX IF NOT EXISTS idx_lead_email ON leads (email);
CREATE INDEX IF NOT EXISTS idx_lead_company ON leads (company);

CREATE TABLE IF NOT EXISTS customers (
    id BIGSERIAL PRIMARY KEY, full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL, phone VARCHAR(50), company VARCHAR(150),
    address TEXT, notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_customer_name ON customers (full_name);
CREATE INDEX IF NOT EXISTS idx_customer_email ON customers (email);
CREATE INDEX IF NOT EXISTS idx_customer_company ON customers (company);
CREATE INDEX IF NOT EXISTS idx_customer_phone ON customers (phone);
