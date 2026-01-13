/**
 * SQL Knowledge Base for PesacodeDB
 * Provides context and examples for the AI assistant
 */

export const SQL_KNOWLEDGE_BASE = `
# PesacodeDB - Relational Database Management System

## Overview
PesacodeDB is a custom-built RDBMS that supports standard SQL operations including:
- Data Definition Language (DDL): CREATE, DROP, ALTER
- Data Manipulation Language (DML): INSERT, UPDATE, DELETE
- Data Query Language (DQL): SELECT with WHERE, JOIN, ORDER BY, GROUP BY
- Constraints: PRIMARY KEY, UNIQUE, NOT NULL, CHECK, FOREIGN KEY
- Indexes for performance optimization

## Supported Data Types
- INT: Integer numbers
- FLOAT: Decimal numbers
- STRING: Text data
- BOOL: Boolean values (TRUE/FALSE)
- DATE: Date values (YYYY-MM-DD format)

## Common SQL Patterns

### Creating Tables
\`\`\`sql
CREATE TABLE table_name (
  column1 datatype constraint,
  column2 datatype constraint,
  ...
)
\`\`\`

### Inserting Data
\`\`\`sql
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...)
-- or
INSERT INTO table_name VALUES (value1, value2, ...)
\`\`\`

### Querying Data
\`\`\`sql
SELECT column1, column2 FROM table_name WHERE condition
SELECT * FROM table_name WHERE column1 = value
SELECT * FROM table_name ORDER BY column1 ASC
\`\`\`

### Joins
\`\`\`sql
SELECT * FROM table1 
INNER JOIN table2 ON table1.id = table2.foreign_id
\`\`\`

### Updating Data
\`\`\`sql
UPDATE table_name SET column1 = value WHERE condition
\`\`\`

### Deleting Data
\`\`\`sql
DELETE FROM table_name WHERE condition
\`\`\`

## Best Practices
1. Always use WHERE clause with UPDATE and DELETE to avoid affecting all rows
2. Use meaningful table and column names
3. Define PRIMARY KEY for all tables
4. Use UNIQUE constraint for columns that should have unique values
5. Create indexes on columns frequently used in WHERE clauses
6. Use INNER JOIN when you only want matching rows from both tables
7. Always specify column names in INSERT statements for clarity
`;

export const QUICK_SQL_QUESTIONS = [
  "How do I create a table with a primary key?",
  "Show me how to insert data into a table",
  "How can I select all records from a table?",
  "How do I join two tables together?",
  "How do I update a specific record?",
  "How can I delete records with a condition?",
  "What's the syntax for creating an index?",
  "How do I add a foreign key constraint?",
  "Show me how to filter results with WHERE",
  "How do I sort query results?",
];

export const SQL_QUERY_TEMPLATES = [
  {
    title: "Create Table",
    category: "DDL",
    template: "CREATE TABLE [table_name] ([column_name] [data_type] [constraints], ...)",
    example: "CREATE TABLE users (id INT PRIMARY KEY, email STRING UNIQUE, name STRING NOT NULL)",
    description: "Define a new table structure with columns and constraints"
  },
  {
    title: "Insert Single Row",
    category: "DML",
    template: "INSERT INTO [table_name] ([columns]) VALUES ([values])",
    example: "INSERT INTO users (id, email, name) VALUES (1, 'alice@example.com', 'Alice')",
    description: "Add a new record to a table"
  },
  {
    title: "Insert Multiple Rows",
    category: "DML",
    template: "INSERT INTO [table_name] VALUES ([row1]), ([row2]), ...",
    example: "INSERT INTO users VALUES (1, 'alice@example.com', 'Alice'), (2, 'bob@example.com', 'Bob')",
    description: "Add multiple records at once"
  },
  {
    title: "Select All",
    category: "DQL",
    template: "SELECT * FROM [table_name]",
    example: "SELECT * FROM users",
    description: "Retrieve all columns and rows from a table"
  },
  {
    title: "Select Specific Columns",
    category: "DQL",
    template: "SELECT [column1], [column2] FROM [table_name]",
    example: "SELECT name, email FROM users",
    description: "Retrieve only specified columns"
  },
  {
    title: "Select With Filter",
    category: "DQL",
    template: "SELECT * FROM [table_name] WHERE [condition]",
    example: "SELECT * FROM users WHERE is_active = TRUE",
    description: "Retrieve rows matching a condition"
  },
  {
    title: "Select With Multiple Conditions",
    category: "DQL",
    template: "SELECT * FROM [table_name] WHERE [condition1] AND [condition2]",
    example: "SELECT * FROM orders WHERE status = 'pending' AND amount > 100",
    description: "Filter using multiple conditions"
  },
  {
    title: "Inner Join",
    category: "DQL",
    template: "SELECT * FROM [table1] INNER JOIN [table2] ON [table1.column] = [table2.column]",
    example: "SELECT users.name, orders.amount FROM users INNER JOIN orders ON users.id = orders.user_id",
    description: "Combine rows from two tables based on a related column"
  },
  {
    title: "Select With Sorting",
    category: "DQL",
    template: "SELECT * FROM [table_name] ORDER BY [column] [ASC|DESC]",
    example: "SELECT * FROM products ORDER BY price DESC",
    description: "Retrieve rows sorted by a column"
  },
  {
    title: "Update Records",
    category: "DML",
    template: "UPDATE [table_name] SET [column] = [value] WHERE [condition]",
    example: "UPDATE users SET is_active = FALSE WHERE id = 1",
    description: "Modify existing records"
  },
  {
    title: "Update Multiple Columns",
    category: "DML",
    template: "UPDATE [table_name] SET [col1] = [val1], [col2] = [val2] WHERE [condition]",
    example: "UPDATE users SET name = 'Alice Smith', email = 'alice.smith@example.com' WHERE id = 1",
    description: "Update multiple columns at once"
  },
  {
    title: "Delete Records",
    category: "DML",
    template: "DELETE FROM [table_name] WHERE [condition]",
    example: "DELETE FROM users WHERE is_active = FALSE",
    description: "Remove rows matching a condition"
  },
  {
    title: "Drop Table",
    category: "DDL",
    template: "DROP TABLE [table_name]",
    example: "DROP TABLE old_users",
    description: "Permanently remove a table"
  },
  {
    title: "Create Index",
    category: "DDL",
    template: "CREATE INDEX [index_name] ON [table_name]([column])",
    example: "CREATE INDEX idx_user_email ON users(email)",
    description: "Create an index for faster queries"
  },
];

export const SQL_HELP_TOPICS = {
  "data_types": {
    title: "Data Types",
    content: `
PesacodeDB supports the following data types:

• INT - Integer numbers (e.g., 1, 42, -10)
• FLOAT - Decimal numbers (e.g., 3.14, -2.5)
• STRING - Text data (e.g., 'Hello', 'John Doe')
• BOOL - Boolean values (TRUE or FALSE)
• DATE - Date values in YYYY-MM-DD format (e.g., '2024-01-15')

Example:
CREATE TABLE products (
  id INT,
  name STRING,
  price FLOAT,
  in_stock BOOL,
  created_date DATE
)
    `
  },
  "constraints": {
    title: "Constraints",
    content: `
Constraints enforce rules on data:

• PRIMARY KEY - Uniquely identifies each row, cannot be NULL
• UNIQUE - Ensures all values in column are different
• NOT NULL - Column must have a value
• CHECK - Validates data against a condition
• FOREIGN KEY - Links to another table's primary key

Example:
CREATE TABLE users (
  id INT PRIMARY KEY,
  email STRING UNIQUE NOT NULL,
  age INT CHECK (age >= 18)
)
    `
  },
  "joins": {
    title: "Joins",
    content: `
Joins combine data from multiple tables:

• INNER JOIN - Returns matching rows from both tables
• LEFT JOIN - Returns all from left table, matching from right
• RIGHT JOIN - Returns all from right table, matching from left

Example:
SELECT users.name, orders.total
FROM users
INNER JOIN orders ON users.id = orders.user_id
WHERE orders.status = 'completed'
    `
  },
  "where_clause": {
    title: "WHERE Clause",
    content: `
Filter results with WHERE:

Operators:
• = (equals), != (not equals)
• >, <, >=, <= (comparisons)
• AND, OR (combine conditions)

Examples:
SELECT * FROM users WHERE age >= 18
SELECT * FROM products WHERE price < 100 AND in_stock = TRUE
SELECT * FROM orders WHERE status = 'pending' OR status = 'processing'
    `
  },
  "aggregate": {
    title: "Aggregate Functions",
    content: `
Perform calculations on data:

• COUNT() - Count rows
• SUM() - Sum values
• AVG() - Average value
• MIN() - Minimum value
• MAX() - Maximum value

Example:
SELECT COUNT(*) FROM users
SELECT AVG(price) FROM products
SELECT MAX(amount) FROM orders WHERE status = 'completed'
    `
  }
};

export function buildSchemaContext(tables) {
  if (!tables || tables.length === 0) {
    return "No tables currently exist in the database. You can help the user create their first table.";
  }

  let context = "Current Database Schema:\n\n";
  
  tables.forEach(table => {
    context += `Table: ${table.name}\n`;
    if (table.columns && table.columns.length > 0) {
      context += "Columns:\n";
      table.columns.forEach(col => {
        const constraints = [];
        if (col.is_primary) constraints.push("PRIMARY KEY");
        if (col.is_unique) constraints.push("UNIQUE");
        if (col.not_null) constraints.push("NOT NULL");
        
        const constraintStr = constraints.length > 0 ? ` (${constraints.join(', ')})` : '';
        context += `  - ${col.name}: ${col.type}${constraintStr}\n`;
      });
    }
    context += "\n";
  });

  return context;
}
