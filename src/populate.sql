SET FOREIGN_KEY_CHECKS = 0;

INSERT INTO Employee (employee_id, first_name, last_name, role, salary, trust_level) VALUES 
(1, 'Jimmy', 'McGill', 'lawyer', 65000, 10),
(2, 'Kim', 'Wexler', 'lawyer', 145000, 10),
(3, 'Howard', 'Hamlin', 'lawyer', 350000, 8),
(4, 'Chuck', 'McGill', 'lawyer', 400000, 4),
(5, 'Mike', 'Ehrmantraut', 'investigator', 85000, 10),
(6, 'Francesca', 'Liddy', 'receptionist', 50000, 8),
(7, 'Huell', 'Babineaux', 'investigator', 55000, 7),
(8, 'Viola', 'Goto', 'paralegal', 52000, 9),
(9, 'Omar', 'Little', 'paralegal', 52000, 9),
(10, 'Erin', 'Brill', 'lawyer', 90000, 9),
(11, 'Cliff', 'Main', 'lawyer', 320000, 8),
(12, 'Bill', 'Oakley', 'lawyer', 70000, 6);

INSERT INTO Lawyer (lawyer_id, bar_number) VALUES 
(1, 18392),
(2, 12984),
(3, 09283),
(4, 00421),
(10, 22100),
(11, 33400),
(12, 11002);

INSERT INTO Specialization_table (specialization, lawyer) VALUES 
('Elder Law', 18392),
('Criminal Defense', 18392),
('Banking Law', 12984),
('Pro Bono', 12984),
('Corporate Law', 09283),
('Litigation', 09283),
('Intellectual Prop', 00421),
('Environmental Law', 33400),
('Criminal Prosecution', 11002);

INSERT INTO Client (client_id, first_name, last_name, phone, email, address, type, date_joined, account_no, lawyer_assigned) VALUES 
(101, 'Kevin', 'Wachtell', 5055550199, 'kevin@mesaverde.net', '1200 Louisiana Blvd', 'business', '2003-05-15', 9001, 12984),
(102, 'Peter', 'Griffin', 5052427100, 'hehehe@sandpiper.org', 'Sandpiper Crossing', 'individual', '2002-09-10', 7709, 18392),
(103, 'Mexi', 'Gringo', 5055559922, 'mexi@county.gov', '1420 Carlisle Blvd', 'individual', '2002-06-01', 7707, 12984),
(104, 'Richard', 'Schweikart', 5058881111, 'rich@s-c.com', 'Schweikart & Cokely HQ', 'business', '2003-01-20', 9004, 09283),
(105, 'Lydia', 'Rodarte', 5059998111, 'lydia@madrigal.de', 'Madrigal Electromotive', 'business', '2003-11-15', 9005, 09283),
(201, 'Jorge', 'Degruzman', 5058425999, 'temp@hotmail.com', 'Chihuahua, MX', 'cartel-affiliated', '2004-06-20', 7701, 18392),
(202, 'Gustavo', 'Fring', 5052429999, 'owner@lospollos.com', 'Los Pollos Hermanos', 'business', '2001-01-01', 6662, 09283),
(203, 'Biz', 'Natch', 5059991111, 'biznatch@yahoo.com', 'The South Valley', 'cartel-affiliated', '2002-03-15', 7705, 18392),
(204, 'Rag', 'Decorator', 6059291111, 'ash@yahoo.com', 'Viggay Hall Road', 'cartel-affiliated', '2002-07-25', 7704, 18392);

INSERT INTO Associate (associate_id, name, status, loyalty_score, account_no, alias) VALUES 
(1001, 'Lalo Salamanca', 'dead', 9, 7701, 201),
(1002, 'Sanjith Ganapathi', 'active', 8, 7702, NULL),
(1003, 'Sreevijay Sunil', 'missing', 10, 7703, NULL),
(1004, 'Ashlin Sunil', 'active', 7, 7704, 204),
(1005, 'Tuco Salamanca', 'active', 5, 7705, 203),
(1006, 'Mike Ehrmantraut', 'active', 10, 7706, NULL),
(1007, 'Ignacio Varga', 'dead', 9, 7707, 103),
(1009, 'Skinny Pete', 'active', 10, 7709, 102);

INSERT INTO CriminalAssociate (associate_id, codename) VALUES 
(1001, 'Nobody'),
(1002, 'Zero'), 
(1003, 'Ledger'),
(1004, 'Hammer'),
(1005, 'Methhead'),
(1006, 'Grunc'),
(1007, 'Nacho'),
(1009, 'Skinny');

INSERT INTO Skills (skill_name, associate_id) VALUES 
('Cybersecurity', 1002), ('Surveillance', 1002), -- Sanjith
('Forensic Accounting', 1003), ('Laundering', 1003), -- Sreevijay
('Enforcement', 1004), ('Debt Collection', 1004), -- Ashlin
('Stealth', 1005),
('Strategy', 1006);

-- =======================================================
-- 6. CASES (The Legal Work)
-- =======================================================
INSERT INTO Cases (case_title, client_id, description, status) VALUES 
-- Legit Cases
('Mesa Verde Exp', 101, 'Regulatory approval for Tucumcari branch', 'open'),
('Mesa Verde Copyright', 101, 'Trademark infringement lawsuit against logo', 'closed'),
('Sandpiper Crossing', 102, 'Class action lawsuit regarding overcharging', 'open'),
('Kettleman Embezzle', 103, 'Defense against county treasury theft charges', 'closed'),
('Madrigal Audit', 105, 'Internal supply chain audit', 'open'),

-- Criminal Cases
('State v. DeGuzman', 201, 'First-degree murder charge bail hearing', 'open'),
('Tuco Assault', 203, 'Aggravated battery of senior citizen', 'closed'),
('Chicken Safety', 202, 'Health inspection compliance verification', 'closed');

-- =======================================================
-- 7. TRIALS & DOCUMENTS (The Paper Trail)
-- =======================================================
INSERT INTO Trial (trial_date, case_title) VALUES 
('2003-09-05', 'Mesa Verde Exp'),
('2003-11-10', 'Sandpiper Crossing'),
('2002-07-15', 'Kettleman Embezzle'),
('2004-08-15', 'State v. DeGuzman'),
('2002-04-20', 'Tuco Assault');

INSERT INTO Document (document_id, title, type, file_path, file_size_bytes, mime_type, create_date) VALUES 
(501, 'Bank Blueprints', 'blueprint', '/uploads/tucumcari_v2.pdf', 5000000, 'application/pdf', '2003-05-20'),
(502, 'Shredded Inv', 'evidence', '/uploads/restored_invoice.jpg', 204800, 'image/jpeg', '2003-06-01'),
(503, 'Bail Motion', 'legal', '/uploads/lalo_bail.docx', 25000, 'application/word', '2004-08-01'),
(504, 'Lab Schematics', 'secret', '/uploads/superlab_draft.dwg', 10000000, 'application/cad', '2003-01-15'),
(505, 'Kettleman Plea', 'legal', '/uploads/plea_deal_betsy.pdf', 50000, 'application/pdf', '2002-08-01');

INSERT INTO Casefile (trial_date, document_id, case_title, client_id) VALUES 
('2003-09-05', 501, 'Mesa Verde Exp', 101),
('2003-11-10', 502, 'Sandpiper Crossing', 102),
('2004-08-15', 503, 'State v. DeGuzman', 201),
('2002-07-15', 505, 'Kettleman Embezzle', 103);

-- =======================================================
-- 8. OPERATIONS & TASKS (The Shadow Work)
-- =======================================================
INSERT INTO Operation (operation_id, name, description) VALUES 
(1, 'Werner', 'Construction of the underground facility'),
(2, 'Bagman', 'Transport of bail money across border'),
(3, 'Distribution', 'Weekly supply chain management');

INSERT INTO Task (task_id, operation_id, description, status, deadline, assigned_to) VALUES 
-- Specific User Tasks
(1, 3, 'Route logistics for truck A1', 'done', '2003-10-01', 1001), -- Leon
(2, 2, 'Monitor GPS trackers on transport', 'pending', '2004-08-15', 1002), -- Sanjith
(3, 3, 'Launder weekly revenue through shell', 'done', '2003-10-05', 1003), -- Sreevijay
(4, 3, 'Collect payment from street dealers', 'failed', '2003-10-06', 1004); -- Ashlin

-- =======================================================
-- 9. TRANSACTIONS & FEES
-- =======================================================
INSERT INTO Transaction (transaction_id, source_account, destination_account, amount, date) VALUES 
(1001, 9001, 5000, 25000, '2003-06-01'),   -- Mesa Verde Retainer
(1002, 9005, 5000, 50000, '2003-12-01'),   -- Madrigal Fee
(1003, 6661, 9999, 7000000, '2004-08-16'), -- Lalo Bail (Big money)
(1004, 6662, 7701, 5000, '2003-10-02'),    -- Gus pays Leon
(1005, 6662, 7703, 7500, '2003-10-06'),    -- Gus pays Sreevijay
(1006, 6663, 7704, 2000, '2003-10-07');    -- Tuco pays Ashlin

INSERT INTO Fee_payment (transaction_id, client_id, case_title) VALUES 
(1001, 101, 'Mesa Verde Exp'),
(1002, 105, 'Madrigal Audit'),
(1003, 201, 'State v. DeGuzman');

-- =======================================================
-- 10. HITLIST (Just a few)
-- =======================================================
INSERT INTO Hitlist (Target_id, codename, status, justification, threat_level, assigned_associate) VALUES 
(991, 'Werner', 'Neutralized', 'Breach of contract/secrecy', 'Critical', 1006),
(992, 'Hank', 'Under Surveillance', 'DEA investigation overlap', 'High', 1002), -- Sanjith watching Hank
(993, 'Esposito', 'Action Pending', 'Competitor in territory', 'Moderate', 1004); -- Ashlin assigned

SET FOREIGN_KEY_CHECKS = 1;