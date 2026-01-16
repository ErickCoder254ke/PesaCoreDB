-- ============================================================================
-- M-Pesa Expense Tracker - MySQL Database Schema
-- ============================================================================
-- Version: 2.0.0
-- Database: MySQL 8.0+
-- Description: Complete schema with tables, relationships, indexes, and seed data
-- ============================================================================

-- Set character encoding
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS mpesa_tracker
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mpesa_tracker;

-- ============================================================================
-- TABLE: USERS
-- ============================================================================
-- Stores user accounts with email/password authentication

CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    preferences JSON DEFAULT NULL,
    CONSTRAINT chk_email_format CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_password_length CHECK (LENGTH(password_hash) >= 60)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- ============================================================================
-- TABLE: CATEGORIES
-- ============================================================================
-- Expense and income categories with auto-categorization keywords

CREATE TABLE IF NOT EXISTS categories (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) DEFAULT NULL,
    name VARCHAR(100) NOT NULL,
    icon VARCHAR(50) NOT NULL,
    color VARCHAR(7) NOT NULL,
    keywords JSON NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_categories_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_color_format CHECK (color REGEXP '^#[0-9A-Fa-f]{6}$')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for categories table
CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE INDEX idx_categories_is_default ON categories(is_default);
CREATE INDEX idx_categories_user_name ON categories(user_id, name);

-- ============================================================================
-- TABLE: TRANSACTIONS
-- ============================================================================
-- All financial transactions (manual entries and SMS imports)

CREATE TABLE IF NOT EXISTS transactions (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    type VARCHAR(20) NOT NULL,
    category_id CHAR(36) NOT NULL,
    description TEXT NOT NULL,
    date TIMESTAMP NOT NULL,
    source VARCHAR(20) NOT NULL DEFAULT 'manual',
    mpesa_details JSON DEFAULT NULL,
    sms_metadata JSON DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transaction_group_id CHAR(36) DEFAULT NULL,
    transaction_role VARCHAR(20) NOT NULL DEFAULT 'primary',
    parent_transaction_id CHAR(36) DEFAULT NULL,
    CONSTRAINT fk_transactions_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_transactions_category FOREIGN KEY (category_id) 
        REFERENCES categories(id) ON DELETE RESTRICT,
    CONSTRAINT fk_transactions_parent FOREIGN KEY (parent_transaction_id) 
        REFERENCES transactions(id) ON DELETE SET NULL,
    CONSTRAINT chk_amount_positive CHECK (amount >= 0),
    CONSTRAINT chk_type_valid CHECK (type IN ('expense', 'income')),
    CONSTRAINT chk_source_valid CHECK (source IN ('manual', 'sms', 'api')),
    CONSTRAINT chk_role_valid CHECK (transaction_role IN ('primary', 'fee', 'fuliza_deduction', 'access_fee'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for transactions table (critical for performance)
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
CREATE INDEX idx_transactions_date_desc ON transactions(date DESC);
CREATE INDEX idx_transactions_user_date ON transactions(user_id, date DESC);
CREATE INDEX idx_transactions_user_category_date ON transactions(user_id, category_id, date);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_transactions_group_id ON transactions(transaction_group_id);
CREATE INDEX idx_transactions_parent_id ON transactions(parent_transaction_id);
-- Full-text search on description
CREATE FULLTEXT INDEX idx_transactions_description_fts ON transactions(description);

-- ============================================================================
-- TABLE: BUDGETS
-- ============================================================================
-- Monthly budget allocations per category

CREATE TABLE IF NOT EXISTS budgets (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    category_id CHAR(36) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    period VARCHAR(20) NOT NULL DEFAULT 'monthly',
    month INT NOT NULL,
    year INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_budgets_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_budgets_category FOREIGN KEY (category_id) 
        REFERENCES categories(id) ON DELETE CASCADE,
    CONSTRAINT chk_amount_positive CHECK (amount > 0),
    CONSTRAINT chk_period_valid CHECK (period IN ('monthly', 'weekly', 'yearly')),
    CONSTRAINT chk_month_valid CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT chk_year_valid CHECK (year >= 2020),
    CONSTRAINT unique_budget_period UNIQUE (user_id, category_id, year, month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for budgets table
CREATE INDEX idx_budgets_user_id ON budgets(user_id);
CREATE INDEX idx_budgets_category_id ON budgets(category_id);
CREATE INDEX idx_budgets_user_period ON budgets(user_id, year, month);

-- ============================================================================
-- TABLE: SMS_IMPORT_LOGS
-- ============================================================================
-- Track SMS import sessions with statistics

CREATE TABLE IF NOT EXISTS sms_import_logs (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    import_session_id CHAR(36) NOT NULL UNIQUE,
    total_messages INT NOT NULL,
    successful_imports INT NOT NULL,
    duplicates_found INT NOT NULL,
    parsing_errors INT NOT NULL,
    transactions_created JSON NOT NULL,
    errors JSON NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sms_logs_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_stats_non_negative CHECK (
        total_messages >= 0 AND
        successful_imports >= 0 AND
        duplicates_found >= 0 AND
        parsing_errors >= 0
    )
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for sms_import_logs table
CREATE INDEX idx_sms_logs_user_id ON sms_import_logs(user_id);
CREATE INDEX idx_sms_logs_session_id ON sms_import_logs(import_session_id);
CREATE INDEX idx_sms_logs_created_at ON sms_import_logs(created_at DESC);

-- ============================================================================
-- TABLE: DUPLICATE_LOGS
-- ============================================================================
-- Track detected duplicate transactions for audit purposes

CREATE TABLE IF NOT EXISTS duplicate_logs (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    original_transaction_id CHAR(36) NOT NULL,
    duplicate_transaction_id CHAR(36) NOT NULL,
    message_hash VARCHAR(64) DEFAULT NULL,
    mpesa_transaction_id VARCHAR(50) DEFAULT NULL,
    reason TEXT NOT NULL,
    duplicate_reasons JSON NOT NULL,
    duplicate_confidence DECIMAL(3,2) NOT NULL,
    similarity_score DECIMAL(3,2) NOT NULL,
    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    action_taken VARCHAR(20) NOT NULL,
    CONSTRAINT fk_duplicate_logs_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_duplicate_logs_original FOREIGN KEY (original_transaction_id) 
        REFERENCES transactions(id) ON DELETE CASCADE,
    CONSTRAINT chk_action_valid CHECK (action_taken IN ('rejected', 'merged', 'flagged')),
    CONSTRAINT chk_confidence_range CHECK (duplicate_confidence BETWEEN 0.0 AND 1.0),
    CONSTRAINT chk_similarity_range CHECK (similarity_score BETWEEN 0.0 AND 1.0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for duplicate_logs table
CREATE INDEX idx_duplicate_logs_user_id ON duplicate_logs(user_id);
CREATE INDEX idx_duplicate_logs_original_tx ON duplicate_logs(original_transaction_id);
CREATE INDEX idx_duplicate_logs_message_hash ON duplicate_logs(message_hash);
CREATE INDEX idx_duplicate_logs_mpesa_id ON duplicate_logs(mpesa_transaction_id);
CREATE INDEX idx_duplicate_logs_detected_at ON duplicate_logs(detected_at DESC);

-- ============================================================================
-- TABLE: STATUS_CHECKS
-- ============================================================================
-- Health checks and system status tracking

CREATE TABLE IF NOT EXISTS status_checks (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    status VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details JSON DEFAULT NULL,
    CONSTRAINT chk_status_valid CHECK (status IN ('healthy', 'degraded', 'down', 'unknown'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for status_checks table
CREATE INDEX idx_status_checks_timestamp ON status_checks(timestamp DESC);
CREATE INDEX idx_status_checks_status ON status_checks(status);

-- ============================================================================
-- SEED DATA: DEFAULT CATEGORIES
-- ============================================================================
-- Insert 12 default categories with Kenyan-specific keywords

INSERT INTO categories (id, user_id, name, icon, color, keywords, is_default)
VALUES
    ('cat-food-dining', NULL, 'Food & Dining', 'restaurant', '#FF6B6B', 
     '["food", "restaurant", "dining", "lunch", "dinner", "breakfast", "cafe", "hotel", "nyama", "choma", "kfc", "pizza", "java"]', TRUE),
    
    ('cat-transport', NULL, 'Transport', 'car', '#4ECDC4',
     '["taxi", "bus", "matatu", "uber", "bolt", "fuel", "parking", "transport", "travel", "petrol", "diesel", "little", "total", "shell"]', TRUE),
    
    ('cat-shopping', NULL, 'Shopping', 'shopping-bag', '#95E1D3',
     '["shop", "store", "mall", "clothing", "electronics", "supermarket", "carrefour", "naivas", "quickmart", "tuskys", "chandarana"]', TRUE),
    
    ('cat-bills-utilities', NULL, 'Bills & Utilities', 'receipt', '#F38181',
     '["bill", "electricity", "water", "internet", "phone", "utility", "kplc", "nairobi water", "zuku", "safaricom", "airtel", "telkom", "rent", "dstv", "gotv", "startimes"]', TRUE),
    
    ('cat-entertainment', NULL, 'Entertainment', 'film', '#AA96DA',
     '["movie", "cinema", "game", "entertainment", "music", "showmax", "netflix", "spotify", "club", "concert", "theater"]', TRUE),
    
    ('cat-health-fitness', NULL, 'Health & Fitness', 'medical', '#FCBAD3',
     '["hospital", "pharmacy", "doctor", "medicine", "gym", "health", "clinic", "lab", "dentist", "fitness", "wellness"]', TRUE),
    
    ('cat-education', NULL, 'Education', 'book', '#A8D8EA',
     '["school", "books", "tuition", "education", "course", "university", "college", "training", "fees", "stationary"]', TRUE),
    
    ('cat-airtime-data', NULL, 'Airtime & Data', 'call', '#FFFFD2',
     '["airtime", "data", "bundles", "safaricom", "airtel", "telkom", "faiba", "wifi"]', TRUE),
    
    ('cat-money-transfer', NULL, 'Money Transfer', 'swap-horizontal', '#FEC8D8',
     '["transfer", "send money", "mpesa", "paybill", "till", "buy goods", "agent"]', TRUE),
    
    ('cat-savings-investment', NULL, 'Savings & Investments', 'wallet', '#957DAD',
     '["savings", "investment", "deposit", "savings account", "mshwari", "kcb mpesa", "fuliza", "okoa", "equity", "co-op"]', TRUE),
    
    ('cat-income', NULL, 'Income', 'cash', '#90EE90',
     '["salary", "income", "payment", "received", "deposit", "earnings", "wage", "bonus", "commission"]', TRUE),
    
    ('cat-other', NULL, 'Other', 'ellipsis-horizontal', '#D4A5A5',
     '[]', TRUE)
ON DUPLICATE KEY UPDATE id=id;

-- ============================================================================
-- SEED DATA: DEFAULT ADMIN USER
-- ============================================================================
-- Password: admin123 (bcrypt hash with cost factor 12)
-- ⚠️ CHANGE THIS PASSWORD AFTER FIRST LOGIN!

INSERT INTO users (id, email, password_hash, name, preferences)
VALUES (
    'admin-default-user',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7eBhXEPFXu',
    'Admin User',
    JSON_OBJECT(
        'theme', 'light',
        'currency', 'KES',
        'notifications', TRUE,
        'language', 'en'
    )
)
ON DUPLICATE KEY UPDATE id=id;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger to auto-lowercase emails on insert
DELIMITER //
CREATE TRIGGER before_user_insert
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    SET NEW.email = LOWER(NEW.email);
END;//

-- Trigger to auto-lowercase emails on update
CREATE TRIGGER before_user_update
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    SET NEW.email = LOWER(NEW.email);
END;//

DELIMITER ;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these queries to verify the schema was created successfully

-- Check all tables exist
SELECT 
    COUNT(*) AS table_count,
    CASE 
        WHEN COUNT(*) = 7 THEN 'Schema verification: All 7 tables exist ✓'
        ELSE 'ERROR: Not all tables were created'
    END AS status
FROM information_schema.tables
WHERE table_schema = DATABASE()
AND table_name IN ('users', 'categories', 'transactions', 'budgets', 
                   'sms_import_logs', 'duplicate_logs', 'status_checks');

-- Check categories were seeded
SELECT 
    COUNT(*) AS category_count,
    CASE 
        WHEN COUNT(*) = 12 THEN 'Seed data verification: 12 default categories exist ✓'
        ELSE 'ERROR: Default categories were not seeded correctly'
    END AS status
FROM categories 
WHERE is_default = TRUE;

-- Check admin user was created
SELECT 
    COUNT(*) AS user_count,
    CASE 
        WHEN COUNT(*) = 1 THEN 'Seed data verification: Default admin user exists ✓'
        ELSE 'ERROR: Default admin user was not created'
    END AS status
FROM users 
WHERE email = 'admin@example.com';

-- Show table sizes
SELECT 
    table_name,
    table_rows AS row_count,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = DATABASE()
ORDER BY table_name;

-- ============================================================================
-- SCHEMA CREATION COMPLETE
-- ============================================================================
-- Version: 2.0.0
-- Database: mpesa_tracker
-- Tables Created: 7
-- Default Categories: 12
-- Default Users: 1 (admin@example.com / admin123)
-- 
-- Next Steps:
-- 1. Change the default admin password
-- 2. Create application-specific database user with limited permissions
-- 3. Set up regular backups
-- 4. Monitor query performance and add indexes as needed
-- 5. Configure MySQL for optimal performance (innodb_buffer_pool_size, etc.)
-- ============================================================================
