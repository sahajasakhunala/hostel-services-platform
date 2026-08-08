-- HostelFlow Master Database Verification Script
-- Document ID: HOSTEL-TST-000
-- Target Engine: MySQL 9.7.1+
-- Description: Master test execution runner. Runs all verification suites across structural constraints, triggers, stored procedures, and views.

USE hostelflow_db;

SELECT '========================================================================' AS STATUS;
SELECT 'STARTING HOSTELFLOW COMPLETE DATABASE VERIFICATION SUITE' AS STATUS;
SELECT '========================================================================' AS STATUS;

-- 1. Structural Integrity Verification (BR-02, BR-03, BR-05)
SELECT '--- 1. RUNNING STRUCTURAL INTEGRITY TESTS ---' AS TEST_SUITE;
SOURCE database/tests/integrity_tests.sql;

-- 2. Concurrency-Aware Trigger Verification (Capacity, Payments, Audit Logs)
SELECT '--- 2. RUNNING TRIGGER VERIFICATION TESTS ---' AS TEST_SUITE;
SOURCE database/tests/trigger_tests.sql;

-- 3. Transactional Stored Procedure Verification (Allocations, Transfers, Vacating, Payments)
SELECT '--- 3. RUNNING STORED PROCEDURE VERIFICATION TESTS ---' AS TEST_SUITE;
SOURCE database/tests/procedure_tests.sql;

-- 4. Operational Views Verification
SELECT '--- 4. RUNNING OPERATIONAL VIEW VERIFICATION TESTS ---' AS TEST_SUITE;
SOURCE database/tests/view_tests.sql;

-- 5. Analytical Reports & BI Verification
SELECT '--- 5. RUNNING ANALYTICAL REPORT VERIFICATION TESTS ---' AS TEST_SUITE;
SOURCE database/tests/report_tests.sql;

SELECT '========================================================================' AS STATUS;
SELECT 'HOSTELFLOW DATABASE VERIFICATION COMPLETED SUCCESSFULLY' AS STATUS;
SELECT '========================================================================' AS STATUS;
