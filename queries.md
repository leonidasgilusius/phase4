# SQL Queries Reference

This document contains all SQL queries used in the application, organized by functionality.

## Table of Contents
1. [Employee Management](#employee-management)
2. [Client Management](#client-management)
3. [Case Management](#case-management)
4. [Trial Management](#trial-management)
5. [Financial Transactions](#financial-transactions)
6. [Document Management](#document-management)
7. [Associate Management](#associate-management)
8. [List Operations](#list-operations)
9. [Dashboard Queries](#dashboard-queries)

## Employee Management

### Create Employee
```sql
-- Get next available employee ID
SELECT COALESCE(MAX(employee_id),0)+1 AS next_id FROM Employee

-- Check if ID exists
SELECT 1 FROM Employee WHERE employee_id=%s

-- Insert new employee
INSERT INTO Employee (employee_id, first_name, last_name, role, salary, trust_level) 
VALUES (%s,%s,%s,%s,%s,%s)
```

### Upgrade Employee to Lawyer
```sql
-- Check if employee exists
SELECT 1 FROM Employee WHERE employee_id=%s

-- Check if already a lawyer
SELECT 1 FROM Lawyer WHERE lawyer_id=%s

-- Insert into Lawyer table
INSERT INTO Lawyer (lawyer_id, bar_number) VALUES (%s,%s)
```

### Add Specializations
```sql
-- Insert specializations
INSERT INTO Specialization_table (specialization, lawyer) VALUES (%s,%s)
```

## Client Management

### Create Client
```sql
-- Get next client ID
SELECT COALESCE(MAX(client_id),0)+1 AS next_id FROM Client

-- Insert new client
INSERT INTO Client (client_id, first_name, last_name, phone, email, address, type, date_joined, account_no, lawyer_assigned)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
```

### Reassign Client's Lawyer
```sql
-- Verify lawyer exists
SELECT 1 FROM Lawyer WHERE bar_number=%s

-- Update client's lawyer
UPDATE Client SET lawyer_assigned=%s WHERE client_id=%s
```

## Case Management

### Create Case
```sql
INSERT INTO Cases (case_title, client_id, description, status) 
VALUES (%s,%s,%s,%s)
```

### Update Case Status
```sql
UPDATE Cases SET status=%s WHERE case_title=%s
```

### Get Case Summary
```sql
-- Get case details with client and lawyer info
SELECT ca.case_title, ca.description, ca.status, 
       c.client_id, c.first_name AS client_first, c.last_name AS client_last, 
       c.lawyer_assigned, le.first_name AS lawyer_first, le.last_name AS lawyer_last 
FROM Cases ca 
LEFT JOIN Client c ON c.client_id = ca.client_id 
LEFT JOIN Lawyer l ON l.bar_number = c.lawyer_assigned 
LEFT JOIN Employee le ON le.employee_id = l.lawyer_id 
WHERE ca.case_title = %s

-- Get latest trial date
SELECT MAX(trial_date) AS latest_trial FROM Trial WHERE case_title = %s

-- Get total payments
SELECT COALESCE(SUM(t.amount),0) AS total_paid
FROM Fee_payment f 
JOIN `Transaction` t ON t.transaction_id = f.transaction_id
WHERE f.case_title = %s

-- Count missing documents
SELECT COUNT(*) AS missing
FROM Documents_required dr
LEFT JOIN Casefile cf ON cf.document_id = dr.document_id 
    AND cf.trial_date = dr.trial_date 
    AND cf.case_title = dr.case_title
WHERE dr.case_title = %s AND cf.document_id IS NULL
```

## Trial Management

### Schedule Trial
```sql
INSERT INTO Trial (trial_date, case_title) VALUES (%s,%s)
```

### Add Required Document
```sql
INSERT INTO Documents_required (document_id, trial_date, case_title) 
VALUES (%s,%s,%s)
```

### Get Upcoming Trials with Missing Documents
```sql
SELECT tr.trial_date, tr.case_title,
       SUM(CASE WHEN cf.document_id IS NULL THEN 1 ELSE 0 END) AS missing_docs
FROM Trial tr
LEFT JOIN Documents_required dr ON dr.trial_date = tr.trial_date AND dr.case_title = tr.case_title
LEFT JOIN Casefile cf ON cf.trial_date = dr.trial_date 
    AND cf.case_title = dr.case_title 
    AND cf.document_id = dr.document_id
WHERE tr.trial_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
GROUP BY tr.trial_date, tr.case_title
HAVING missing_docs > 0
ORDER BY tr.trial_date ASC
```

## Financial Transactions

### Record Fee Payment
```sql
-- Verify case belongs to client
SELECT 1 FROM Cases WHERE case_title=%s AND client_id=%s

-- Insert transaction
INSERT INTO `Transaction` (transaction_id, source_account, destination_account, amount, date) 
VALUES (%s,%s,%s,%s,%s)

-- Record fee payment
INSERT INTO Fee_payment (transaction_id, client_id, case_title) 
VALUES (%s,%s,%s)
```

### Record Business Fee
```sql
-- Verify business exists
SELECT 1 FROM Associated_business WHERE business_name=%s AND location=%s

-- Insert transaction
INSERT INTO `Transaction` (transaction_id, source_account, destination_account, amount, date) 
VALUES (%s,%s,%s,%s,%s)

-- Record business fee
INSERT INTO Business_fee (transaction_id, business_name, location) 
VALUES (%s,%s,%s)
```

### Payments Ledger
```sql
SELECT t.transaction_id, t.amount, t.date, f.client_id, f.case_title 
FROM Fee_payment f 
JOIN `Transaction` t ON t.transaction_id = f.transaction_id 
WHERE 1=1
[+ client_id filter]
[+ case_title filter]
[+ date range filters]
ORDER BY t.date DESC, t.transaction_id DESC
```

## Document Management

### Create Document
```sql
-- Get next document ID
SELECT COALESCE(MAX(document_id),0)+1 AS next_id FROM Document

-- Insert document
INSERT INTO Document (document_id, title, type, file_path, file_size_bytes, mime_type, create_date) 
VALUES (%s,%s,%s,%s,%s,%s,%s)
```

### Attach Document to Casefile
```sql
INSERT INTO Casefile (trial_date, document_id, case_title, client_id) 
VALUES (%s,%s,%s,%s)
```

### Remove Document from Casefile
```sql
DELETE FROM Casefile 
WHERE trial_date=%s AND document_id=%s AND case_title=%s AND client_id=%s
```

## Associate Management

### Create Associate
```sql
-- Get next associate ID
SELECT COALESCE(MAX(associate_id),0)+1 AS next_id FROM Associate

-- Insert associate
INSERT INTO Associate (associate_id, name, status, loyalty_score, account_no, alias) 
VALUES (%s,%s,%s,%s,%s,%s)
```

### Mark Criminal Associate
```sql
INSERT INTO CriminalAssociate (associate_id, codename) 
VALUES (%s,%s)
```

### Add Skill to Associate
```sql
INSERT INTO Skills (skill_name, associate_id) 
VALUES (%s,%s)
```

### Find Associates
```sql
SELECT a.associate_id, a.name, a.status, a.loyalty_score, a.account_no, a.alias,
       CONCAT(c.first_name, ' ', c.last_name) AS alias_name 
FROM Associate a 
LEFT JOIN Client c ON c.client_id = a.alias 
[+ status filter]
[+ loyalty score filters]
ORDER BY a.loyalty_score DESC, a.name
```

### Find Criminal Associates by Skills
```sql
SELECT a.associate_id, a.name, a.status, a.loyalty_score, 
       GROUP_CONCAT(DISTINCT s.skill_name) AS skills 
FROM CriminalAssociate ca 
JOIN Associate a ON a.associate_id = ca.associate_id 
JOIN Skills s ON s.associate_id = ca.associate_id 
WHERE s.skill_name IN ([skill_list])
GROUP BY a.associate_id, a.name, a.status, a.loyalty_score 
[HAVING COUNT(DISTINCT s.skill_name) = [number of skills] | HAVING COUNT(DISTINCT s.skill_name) >= 1]
```

## List Operations

### List Lawyers
```sql
SELECT l.bar_number, e.first_name, e.last_name 
FROM Lawyer l 
JOIN Employee e ON e.employee_id = l.lawyer_id 
ORDER BY e.first_name, e.last_name
```

### List Clients (Basic)
```sql
SELECT client_id, first_name, last_name 
FROM Client 
ORDER BY first_name, last_name 
LIMIT %s
```

### List Cases (Basic)
```sql
SELECT case_title 
FROM Cases 
ORDER BY case_title 
LIMIT %s
```

### List Cases for Client
```sql
SELECT case_title 
FROM Cases 
WHERE client_id = %s 
ORDER BY case_title 
LIMIT %s
```

### List Document Types
```sql
SELECT DISTINCT type 
FROM Document 
WHERE type IS NOT NULL 
ORDER BY type
```

### List MIME Types
```sql
SELECT DISTINCT mime_type 
FROM Document 
WHERE mime_type IS NOT NULL 
ORDER BY mime_type
```

### List Required Documents for Trial
```sql
SELECT dr.document_id, d.title, d.type, d.mime_type, d.create_date 
FROM Documents_required dr 
JOIN Document d ON d.document_id = dr.document_id 
WHERE dr.case_title = %s AND dr.trial_date = %s
```

### List Casefile Documents
```sql
SELECT cf.document_id, d.title, d.type, d.mime_type, d.create_date 
FROM Casefile cf 
JOIN Document d ON d.document_id = cf.document_id 
WHERE cf.case_title = %s AND cf.trial_date = %s AND cf.client_id = %s
```

## Dashboard Queries

### Get KPIs
```sql
-- Open cases count
SELECT COUNT(*) AS open_cases FROM Cases WHERE status = 'open'

-- Upcoming trials
SELECT COUNT(*) AS upcoming_trials 
FROM Trial 
WHERE trial_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)

-- Monthly fees
SELECT COALESCE(SUM(t.amount),0) AS total_mtd
FROM `Transaction` t
JOIN Fee_payment f ON f.transaction_id = t.transaction_id
WHERE t.date BETWEEN DATE_FORMAT(CURDATE(), '%%Y-%%m-01') AND CURDATE()

-- Top specializations
SELECT s.specialization, COUNT(ca.case_title) AS open_count
FROM Specialization_table s
JOIN Lawyer l ON s.lawyer = l.bar_number
LEFT JOIN Client c ON c.lawyer_assigned = l.bar_number
LEFT JOIN Cases ca ON ca.client_id = c.client_id AND ca.status = 'open'
GROUP BY s.specialization
ORDER BY open_count DESC
LIMIT 5
```
