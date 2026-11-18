-- Sidak_CRM schema for BigRock shared hosting
-- Before importing, select the database `upayssmk_sidak_crm` in phpMyAdmin.
-- This file creates the CRM tables only.
-- It does NOT create or switch databases.
-- Target: MySQL 8.0+ / 9.x

-- =======================================================
-- Customer_Management_System Database Schema
-- Target: MySQL 8.0+ / 9.x
-- =======================================================



-- 1. Contacts Table
CREATE TABLE IF NOT EXISTS contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(50),
    company VARCHAR(150),
    job_title VARCHAR(100),
    address TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_contact_name (full_name),
    INDEX idx_contact_email (email),
    INDEX idx_contact_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Leads Table
CREATE TABLE IF NOT EXISTS leads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(50),
    company VARCHAR(150),
    source VARCHAR(100),
    status ENUM('New', 'Contacted', 'Qualified', 'Converted', 'Lost') NOT NULL DEFAULT 'New',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_lead_status (status),
    INDEX idx_lead_name (full_name),
    INDEX idx_lead_email (email),
    INDEX idx_lead_company (company)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(50),
    company VARCHAR(150),
    address TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customer_name (full_name),
    INDEX idx_customer_email (email),
    INDEX idx_customer_company (company),
    INDEX idx_customer_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
