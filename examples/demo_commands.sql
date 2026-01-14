-- ============================================================================
-- RDBMS v2.0 - Comprehensive SQL Demo Script
-- ============================================================================
-- This script demonstrates all supported SQL commands in the RDBMS engine
-- ============================================================================

-- ----------------------------------------------------------------------------
-- DATABASE MANAGEMENT
-- ----------------------------------------------------------------------------

-- Create databases
CREATE DATABASE university;
CREATE DATABASE company;

-- Show all databases
SHOW DATABASES;

-- Select a database to work with
USE university;

-- ----------------------------------------------------------------------------
-- TABLE MANAGEMENT
-- ----------------------------------------------------------------------------

-- Create a students table
CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name STRING,
    age INT,
    email STRING UNIQUE,
    enrolled BOOL
);

-- Create a courses table
CREATE TABLE courses (
    course_id INT PRIMARY KEY,
    title STRING,
    credits INT,
    active BOOL
);

-- Create an enrollments table with foreign keys
CREATE TABLE enrollments (
    enrollment_id INT PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    course_id INT REFERENCES courses(course_id),
    grade STRING
);

-- Show all tables
SHOW TABLES;

-- Describe table structure
DESCRIBE students;
DESCRIBE courses;
DESCRIBE enrollments;

-- ----------------------------------------------------------------------------
-- DATA INSERTION
-- ----------------------------------------------------------------------------

-- Insert students
INSERT INTO students VALUES (1, 'Alice Johnson', 20, 'alice@university.edu', TRUE);
INSERT INTO students VALUES (2, 'Bob Smith', 22, 'bob@university.edu', TRUE);
INSERT INTO students VALUES (3, 'Charlie Davis', 19, 'charlie@university.edu', FALSE);
INSERT INTO students VALUES (4, 'Diana Prince', 21, 'diana@university.edu', TRUE);

-- Insert with column specification
INSERT INTO students (student_id, name, age, email, enrolled) 
VALUES (5, 'Eve Wilson', 23, 'eve@university.edu', TRUE);

-- Insert courses
INSERT INTO courses VALUES (101, 'Introduction to Computer Science', 4, TRUE);
INSERT INTO courses VALUES (102, 'Data Structures', 4, TRUE);
INSERT INTO courses VALUES (103, 'Database Systems', 3, TRUE);
INSERT INTO courses VALUES (104, 'Web Development', 3, TRUE);

-- Insert enrollments
INSERT INTO enrollments VALUES (1, 1, 101, 'A');
INSERT INTO enrollments VALUES (2, 1, 102, 'B');
INSERT INTO enrollments VALUES (3, 2, 101, 'B');
INSERT INTO enrollments VALUES (4, 2, 103, 'A');
INSERT INTO enrollments VALUES (5, 4, 102, 'A');
INSERT INTO enrollments VALUES (6, 4, 103, 'A');
INSERT INTO enrollments VALUES (7, 5, 104, 'B');

-- ----------------------------------------------------------------------------
-- DATA RETRIEVAL (SELECT)
-- ----------------------------------------------------------------------------

-- Select all students
SELECT * FROM students;

-- Select specific columns
SELECT student_id, name, email FROM students;

-- Select with WHERE clause
SELECT * FROM students WHERE enrolled = TRUE;
SELECT * FROM students WHERE age = 20;
SELECT * FROM courses WHERE credits = 4;

-- Select all courses
SELECT * FROM courses;

-- Select all enrollments
SELECT * FROM enrollments;

-- ----------------------------------------------------------------------------
-- JOINS
-- ----------------------------------------------------------------------------

-- Inner join: Get student enrollments with student names
SELECT students.name, enrollments.grade 
FROM students 
INNER JOIN enrollments ON students.student_id = enrollments.student_id;

-- Inner join: Get enrollments with course titles
SELECT courses.title, enrollments.grade 
FROM enrollments 
INNER JOIN courses ON enrollments.course_id = courses.course_id;

-- ----------------------------------------------------------------------------
-- DATA UPDATE
-- ----------------------------------------------------------------------------

-- Update a student's enrollment status
UPDATE students SET enrolled = FALSE WHERE student_id = 3;

-- Update a student's age
UPDATE students SET age = 21 WHERE student_id = 1;

-- Update a course status
UPDATE courses SET active = FALSE WHERE course_id = 104;

-- Verify updates
SELECT * FROM students WHERE student_id = 1;
SELECT * FROM courses WHERE course_id = 104;

-- ----------------------------------------------------------------------------
-- DATA DELETION
-- ----------------------------------------------------------------------------

-- Delete a specific enrollment
DELETE FROM enrollments WHERE enrollment_id = 7;

-- Delete students who are not enrolled
DELETE FROM students WHERE enrolled = FALSE;

-- Verify deletions
SELECT * FROM students;
SELECT * FROM enrollments;

-- ----------------------------------------------------------------------------
-- CONSTRAINT TESTING
-- ----------------------------------------------------------------------------

-- Try to insert duplicate primary key (should fail)
-- INSERT INTO students VALUES (1, 'Test User', 25, 'test@university.edu', TRUE);

-- Try to insert duplicate unique value (should fail)
-- INSERT INTO students VALUES (10, 'Another User', 25, 'alice@university.edu', TRUE);

-- ----------------------------------------------------------------------------
-- DROP OPERATIONS
-- ----------------------------------------------------------------------------

-- Drop a table
DROP TABLE enrollments;

-- Verify table was dropped
SHOW TABLES;

-- Switch to another database
USE company;

-- Create tables in company database
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    name STRING,
    department STRING,
    salary INT,
    active BOOL
);

CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name STRING,
    budget INT
);

-- Insert sample data
INSERT INTO employees VALUES (1, 'John Doe', 'Engineering', 95000, TRUE);
INSERT INTO employees VALUES (2, 'Jane Smith', 'Marketing', 75000, TRUE);
INSERT INTO employees VALUES (3, 'Mike Johnson', 'Engineering', 88000, TRUE);

INSERT INTO departments VALUES (1, 'Engineering', 500000);
INSERT INTO departments VALUES (2, 'Marketing', 300000);
INSERT INTO departments VALUES (3, 'Sales', 400000);

-- Show tables
SHOW TABLES;

-- Select data
SELECT * FROM employees;
SELECT * FROM departments;

-- Switch back to university database
USE university;

-- Show remaining tables
SHOW TABLES;

-- Drop the university database (be careful!)
-- DROP DATABASE university;

-- Show all databases
SHOW DATABASES;

-- ============================================================================
-- END OF DEMO SCRIPT
-- ============================================================================
-- 
-- Key Features Demonstrated:
-- 1. Database Management: CREATE, DROP, USE, SHOW DATABASES
-- 2. Table Management: CREATE TABLE, DROP TABLE, SHOW TABLES, DESCRIBE
-- 3. Data Manipulation: INSERT, SELECT, UPDATE, DELETE
-- 4. Constraints: PRIMARY KEY, UNIQUE, FOREIGN KEY
-- 5. Data Types: INT, STRING, BOOL
-- 6. WHERE Clauses: Filtering with conditions
-- 7. INNER JOIN: Combining data from multiple tables
-- 8. Index Usage: Automatic optimization with indexes on PK and UNIQUE columns
-- ============================================================================
