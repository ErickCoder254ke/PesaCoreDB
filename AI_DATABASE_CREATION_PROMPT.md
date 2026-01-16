# AI Database Creation Prompt

Use this prompt to instruct an AI builder to create the M-Pesa Expense Tracker database in a traditional RDBMS.

---

## PROMPT FOR AI BUILDER

Create a complete relational database schema for an M-Pesa Expense Tracker application with the following requirements:

### Database Overview
- **Purpose**: Track financial transactions, categorize expenses, manage budgets, and handle SMS imports from M-Pesa messages
- **Target RDBMS**: PostgreSQL (preferred) or MySQL
- **Schema Version**: 2.0.0
- **Authentication**: Email/password-based user accounts

### Table Requirements

#### 1. USERS TABLE
Create a users table to store user accounts with email/password authentication.

**Columns:**
- `id` (UUID, PRIMARY KEY) - Unique user identifier
- `email` (VARCHAR(255), UNIQUE, NOT NULL) - User email address (stored in lowercase)
- `password_hash` (VARCHAR(255), NOT NULL) - Bcrypt hashed password
- `name` (VARCHAR(255), NOT NULL) - User's full name
- `created_at` (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Account creation timestamp
- `preferences` (JSON/JSONB) - User preferences (theme, currency, notifications, etc.)

**Indexes:**
- Primary key on `id`
- Unique index on `email`
- Index on `created_at` for sorting

**Constraints:**
- Email must be unique
- Email should be validated format
- Password hash must be at least 60 characters (bcrypt)

**Example Data:**
```sql
-- Default admin user (password: admin123)
INSERT INTO users (id, email, password_hash, name, created_at, preferences)
VALUES (
  'admin-uuid-here',
  'admin@example.com',
  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7eBhXEPFXu',
  'Admin User',
  CURRENT_TIMESTAMP,
  '{"theme": "light", "currency": "KES", "notifications": true}'
);
```

---

#### 2. CATEGORIES TABLE
Create a categories table for expense and income categorization with auto-categorization keywords.

**Columns:**
- `id` (UUID, PRIMARY KEY) - Unique category identifier
- `user_id` (UUID, NULLABLE, FOREIGN KEY → users.id) - NULL for default system categories, user-specific otherwise
- `name` (VARCHAR(100), NOT NULL) - Category name (e.g., "Food & Dining")
- `icon` (VARCHAR(50), NOT NULL) - Icon identifier (e.g., "restaurant", "car")
- `color` (VARCHAR(7), NOT NULL) - Hex color code (e.g., "#FF6B6B")
- `keywords` (JSON/JSONB, NOT NULL) - Array of keywords for auto-categorization
- `is_default` (BOOLEAN, NOT NULL, DEFAULT FALSE) - True for system-provided categories

**Indexes:**
- Primary key on `id`
- Index on `user_id` (nullable)
- Index on `is_default`
- Composite index on `(user_id, name)` for user-specific category lookups

**Constraints:**
- Foreign key `user_id` references `users(id)` ON DELETE CASCADE
- Keywords must be a valid JSON array

**Seed Data:**
Create 12 default categories (user_id = NULL, is_default = TRUE) with Kenyan-specific keywords:

1. **Food & Dining** (icon: restaurant, color: #FF6B6B)
   - Keywords: ["food", "restaurant", "dining", "lunch", "dinner", "breakfast", "cafe", "hotel", "nyama", "choma", "kfc", "pizza", "java"]

2. **Transport** (icon: car, color: #4ECDC4)
   - Keywords: ["taxi", "bus", "matatu", "uber", "bolt", "fuel", "parking", "transport", "travel", "petrol", "diesel", "little", "total", "shell"]

3. **Shopping** (icon: shopping-bag, color: #95E1D3)
   - Keywords: ["shop", "store", "mall", "clothing", "electronics", "supermarket", "carrefour", "naivas", "quickmart", "tuskys", "chandarana"]

4. **Bills & Utilities** (icon: receipt, color: #F38181)
   - Keywords: ["bill", "electricity", "water", "internet", "phone", "utility", "kplc", "nairobi water", "zuku", "safaricom", "airtel", "telkom", "rent", "dstv", "gotv", "startimes"]

5. **Entertainment** (icon: film, color: #AA96DA)
   - Keywords: ["movie", "cinema", "game", "entertainment", "music", "showmax", "netflix", "spotify", "club", "concert", "theater"]

6. **Health & Fitness** (icon: medical, color: #FCBAD3)
   - Keywords: ["hospital", "pharmacy", "doctor", "medicine", "gym", "health", "clinic", "lab", "dentist", "fitness", "wellness"]

7. **Education** (icon: book, color: #A8D8EA)
   - Keywords: ["school", "books", "tuition", "education", "course", "university", "college", "training", "fees", "stationary"]

8. **Airtime & Data** (icon: call, color: #FFFFD2)
   - Keywords: ["airtime", "data", "bundles", "safaricom", "airtel", "telkom", "faiba", "wifi"]

9. **Money Transfer** (icon: swap-horizontal, color: #FEC8D8)
   - Keywords: ["transfer", "send money", "mpesa", "paybill", "till", "buy goods", "agent"]

10. **Savings & Investments** (icon: wallet, color: #957DAD)
    - Keywords: ["savings", "investment", "deposit", "savings account", "mshwari", "kcb mpesa", "fuliza", "okoa", "equity", "co-op"]

11. **Income** (icon: cash, color: #90EE90)
    - Keywords: ["salary", "income", "payment", "received", "deposit", "earnings", "wage", "bonus", "commission"]

12. **Other** (icon: ellipsis-horizontal, color: #D4A5A5)
    - Keywords: [] (empty array)

---

#### 3. TRANSACTIONS TABLE
Create a transactions table to store all financial transactions (manual entries and SMS imports).

**Columns:**
- `id` (UUID, PRIMARY KEY) - Unique transaction identifier
- `user_id` (UUID, NOT NULL, FOREIGN KEY → users.id) - Transaction owner
- `amount` (DECIMAL(15,2), NOT NULL) - Transaction amount (positive for all types)
- `type` (VARCHAR(20), NOT NULL) - 'expense' or 'income'
- `category_id` (UUID, NOT NULL, FOREIGN KEY → categories.id) - Transaction category
- `description` (TEXT, NOT NULL) - Transaction description
- `date` (TIMESTAMP, NOT NULL) - Transaction date/time
- `source` (VARCHAR(20), NOT NULL, DEFAULT 'manual') - 'manual', 'sms', or 'api'
- `mpesa_details` (JSON/JSONB, NULLABLE) - M-Pesa specific details (see structure below)
- `sms_metadata` (JSON/JSONB, NULLABLE) - SMS parsing metadata (see structure below)
- `created_at` (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Record creation timestamp
- `transaction_group_id` (UUID, NULLABLE) - Groups related transactions from same SMS
- `transaction_role` (VARCHAR(20), NOT NULL, DEFAULT 'primary') - 'primary', 'fee', 'fuliza_deduction', 'access_fee'
- `parent_transaction_id` (UUID, NULLABLE, FOREIGN KEY → transactions.id) - Links fees to main transaction

**Indexes:**
- Primary key on `id`
- Index on `user_id` (most queries filter by user)
- Index on `category_id` (for category aggregations)
- Index on `date` DESC (for recent transactions)
- Composite index on `(user_id, date DESC)` (common query pattern)
- Composite index on `(user_id, category_id, date)` (analytics)
- Index on `transaction_group_id` (for grouping)
- Index on `parent_transaction_id` (for fee lookups)
- Index on `type` (for expense/income filtering)
- GIN/Full-text index on `description` (for search)

**Constraints:**
- Foreign key `user_id` references `users(id)` ON DELETE CASCADE
- Foreign key `category_id` references `categories(id)` ON DELETE RESTRICT
- Foreign key `parent_transaction_id` references `transactions(id)` ON DELETE SET NULL
- Check constraint: `type IN ('expense', 'income')`
- Check constraint: `source IN ('manual', 'sms', 'api')`
- Check constraint: `transaction_role IN ('primary', 'fee', 'fuliza_deduction', 'access_fee')`
- Check constraint: `amount >= 0`

**JSON Structure for mpesa_details:**
```json
{
  "recipient": "string (optional)",
  "reference": "string (optional)",
  "transaction_id": "string (M-Pesa transaction ID)",
  "phone_number": "string (optional)",
  "balance_after": "number (optional)",
  "message_type": "string (received|sent|withdrawal|airtime|paybill|till|fuliza_loan|fuliza_repayment)",
  "transaction_fee": "number (optional)",
  "access_fee": "number (optional)",
  "fuliza_limit": "number (optional)",
  "fuliza_outstanding": "number (optional)",
  "due_date": "string (optional)"
}
```

**JSON Structure for sms_metadata:**
```json
{
  "original_message_hash": "string (SHA256 hash for duplicate detection)",
  "parsing_confidence": "number (0.0-1.0)",
  "parsed_at": "timestamp",
  "requires_review": "boolean",
  "suggested_category": "string (optional)",
  "total_fees": "number (optional)",
  "fee_breakdown": "object (optional)"
}
```

---

#### 4. BUDGETS TABLE
Create a budgets table to store monthly budget allocations per category.

**Columns:**
- `id` (UUID, PRIMARY KEY) - Unique budget identifier
- `user_id` (UUID, NOT NULL, FOREIGN KEY → users.id) - Budget owner
- `category_id` (UUID, NOT NULL, FOREIGN KEY → categories.id) - Budget category
- `amount` (DECIMAL(15,2), NOT NULL) - Budget amount
- `period` (VARCHAR(20), NOT NULL, DEFAULT 'monthly') - 'monthly', 'weekly', 'yearly'
- `month` (INTEGER, NOT NULL) - Month (1-12)
- `year` (INTEGER, NOT NULL) - Year (e.g., 2025)
- `created_at` (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Creation timestamp

**Indexes:**
- Primary key on `id`
- Index on `user_id`
- Composite index on `(user_id, category_id, year, month)` UNIQUE (prevent duplicates)
- Composite index on `(user_id, year, month)` (for monthly views)

**Constraints:**
- Foreign key `user_id` references `users(id)` ON DELETE CASCADE
- Foreign key `category_id` references `categories(id)` ON DELETE CASCADE
- Check constraint: `period IN ('monthly', 'weekly', 'yearly')`
- Check constraint: `month BETWEEN 1 AND 12`
- Check constraint: `year >= 2020`
- Check constraint: `amount > 0`
- Unique constraint on `(user_id, category_id, year, month)`

---

#### 5. SMS_IMPORT_LOGS TABLE
Create a table to track SMS import sessions with statistics.

**Columns:**
- `id` (UUID, PRIMARY KEY) - Unique log identifier
- `user_id` (UUID, NOT NULL, FOREIGN KEY → users.id) - User who imported SMS
- `import_session_id` (UUID, NOT NULL, UNIQUE) - Unique session identifier
- `total_messages` (INTEGER, NOT NULL) - Total SMS messages processed
- `successful_imports` (INTEGER, NOT NULL) - Successfully parsed messages
- `duplicates_found` (INTEGER, NOT NULL) - Duplicate transactions detected
- `parsing_errors` (INTEGER, NOT NULL) - Messages that failed to parse
- `transactions_created` (JSON/JSONB, NOT NULL) - Array of created transaction IDs
- `errors` (JSON/JSONB, NOT NULL) - Array of error messages
- `created_at` (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Import timestamp

**Indexes:**
- Primary key on `id`
- Unique index on `import_session_id`
- Index on `user_id`
- Index on `created_at` DESC

**Constraints:**
- Foreign key `user_id` references `users(id)` ON DELETE CASCADE
- Check constraint: `total_messages >= 0`
- Check constraint: `successful_imports >= 0`
- Check constraint: `duplicates_found >= 0`
- Check constraint: `parsing_errors >= 0`

---

#### 6. DUPLICATE_LOGS TABLE
Create a table to track detected duplicate transactions for audit purposes.

**Columns:**
- `id` (UUID, PRIMARY KEY) - Unique log identifier
- `user_id` (UUID, NOT NULL, FOREIGN KEY → users.id) - User account
- `original_transaction_id` (UUID, NOT NULL, FOREIGN KEY → transactions.id) - First transaction
- `duplicate_transaction_id` (UUID, NOT NULL) - Attempted duplicate ID
- `message_hash` (VARCHAR(64), NULLABLE) - SHA256 hash of SMS message
- `mpesa_transaction_id` (VARCHAR(50), NULLABLE) - M-Pesa transaction ID
- `reason` (TEXT, NOT NULL) - Why it was marked as duplicate
- `duplicate_reasons` (JSON/JSONB, NOT NULL) - Array of matching criteria
- `duplicate_confidence` (DECIMAL(3,2), NOT NULL) - Confidence score (0.0-1.0)
- `similarity_score` (DECIMAL(3,2), NOT NULL) - Similarity score (0.0-1.0)
- `detected_at` (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Detection timestamp
- `action_taken` (VARCHAR(20), NOT NULL) - 'rejected', 'merged', 'flagged'

**Indexes:**
- Primary key on `id`
- Index on `user_id`
- Index on `original_transaction_id`
- Index on `message_hash` (for lookup)
- Index on `mpesa_transaction_id` (for lookup)
- Index on `detected_at` DESC

**Constraints:**
- Foreign key `user_id` references `users(id)` ON DELETE CASCADE
- Foreign key `original_transaction_id` references `transactions(id)` ON DELETE CASCADE
- Check constraint: `action_taken IN ('rejected', 'merged', 'flagged')`
- Check constraint: `duplicate_confidence BETWEEN 0.0 AND 1.0`
- Check constraint: `similarity_score BETWEEN 0.0 AND 1.0`

---

#### 7. STATUS_CHECKS TABLE
Create a simple table for health checks and system status tracking.

**Columns:**
- `id` (UUID, PRIMARY KEY) - Unique status check identifier
- `status` (VARCHAR(50), NOT NULL) - Status value ('healthy', 'degraded', 'down')
- `timestamp` (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP) - Check timestamp
- `details` (JSON/JSONB, NULLABLE) - Additional status details

**Indexes:**
- Primary key on `id`
- Index on `timestamp` DESC
- Index on `status`

**Constraints:**
- Check constraint: `status IN ('healthy', 'degraded', 'down', 'unknown')`

---

### Database-Level Requirements

#### 1. Use UUID Generation
- For PostgreSQL: Use `gen_random_uuid()` or `uuid-ossp` extension
- For MySQL: Use `UUID()` function
- Application should also be able to generate UUIDs

#### 2. Timestamp Handling
- Use `TIMESTAMP WITH TIME ZONE` (PostgreSQL) or `TIMESTAMP` (MySQL)
- All timestamps should be stored in UTC
- Use `CURRENT_TIMESTAMP` for defaults

#### 3. JSON/JSONB Support
- PostgreSQL: Use `JSONB` for better performance and indexing
- MySQL: Use `JSON` type (MySQL 5.7+)
- Validate JSON structure at application level

#### 4. Character Encoding
- Use UTF-8 encoding for all text fields
- Collation: `utf8mb4_unicode_ci` (MySQL) or `en_US.UTF-8` (PostgreSQL)

#### 5. Decimal Precision
- Use `DECIMAL(15,2)` for all monetary amounts
- Never use FLOAT or DOUBLE for money

---

### Performance Optimizations

#### 1. Partitioning (Optional for large datasets)
```sql
-- Partition transactions by date (yearly or monthly)
-- PostgreSQL example:
CREATE TABLE transactions_2025 PARTITION OF transactions
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

#### 2. Materialized Views (For analytics)
```sql
-- Create materialized view for category spending
CREATE MATERIALIZED VIEW category_spending_summary AS
SELECT 
  user_id,
  category_id,
  DATE_TRUNC('month', date) as month,
  SUM(amount) as total_amount,
  COUNT(*) as transaction_count
FROM transactions
WHERE type = 'expense'
GROUP BY user_id, category_id, DATE_TRUNC('month', date);

-- Refresh periodically
REFRESH MATERIALIZED VIEW category_spending_summary;
```

#### 3. Connection Pooling
- Use connection pooling (e.g., PgBouncer for PostgreSQL)
- Set appropriate pool size based on workload

---

### Security Requirements

#### 1. Row-Level Security (PostgreSQL)
```sql
-- Enable RLS on transactions table
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own transactions
CREATE POLICY user_transactions ON transactions
FOR ALL
USING (user_id = current_setting('app.user_id')::uuid);
```

#### 2. Encryption
- Encrypt passwords using bcrypt (cost factor: 12)
- Consider encrypting sensitive JSON fields at application level
- Use SSL/TLS for database connections

#### 3. Audit Logging
- Consider adding `updated_at` timestamps to all tables
- Implement trigger-based audit logging for sensitive tables

---

### Migration and Backup Strategy

#### 1. Version Control
- Use migration tool (e.g., Flyway, Liquibase, Alembic)
- Version each schema change
- Keep migrations in source control

#### 2. Backup Strategy
- Daily full backups
- Point-in-time recovery enabled
- Test restore procedures regularly

#### 3. Data Retention
- Archive old transactions (> 5 years) to separate table
- Keep audit logs for 1 year minimum

---

### Testing Data

After creating the schema and seed data, generate sample test data:

```sql
-- 1 test user
-- 100 sample transactions across all categories
-- 5 budget entries for current month
-- Mix of expense and income transactions
-- Include some transactions with M-Pesa details
-- Include some grouped transactions (fees)
```

---

### Deliverables

Please provide:

1. **Complete SQL schema file** with:
   - All table definitions
   - All indexes
   - All foreign keys and constraints
   - Seed data for default categories
   - Sample admin user

2. **Separate seed data file** with:
   - Default categories (12 categories)
   - Optional test data

3. **Migration scripts** for:
   - Initial schema creation
   - Rolling back if needed

4. **Database diagram** showing:
   - All tables and relationships
   - Primary and foreign keys
   - Important indexes

5. **Performance tuning recommendations** for:
   - Expected query patterns
   - Index optimization
   - Partitioning strategy (if applicable)

---

### Target Performance

The database should support:
- ✅ 1000+ concurrent users
- ✅ 100,000+ transactions per user
- ✅ Sub-100ms query response times for common queries
- ✅ < 1 second for complex analytics aggregations
- ✅ 1000+ transactions per second write throughput

---

### Additional Notes

- Use snake_case for column names consistently
- Add comments to all tables and complex columns
- Ensure all foreign keys have appropriate ON DELETE actions
- Consider adding `updated_at` triggers for audit trails
- Use appropriate data types for each field
- Validate all constraints at database level where possible

---

**Target Database:** PostgreSQL 14+ (recommended) or MySQL 8.0+
**Schema Version:** 2.0.0
**Last Updated:** January 2026
