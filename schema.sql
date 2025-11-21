CREATE DATABASE if not exists ItsAllGoodMan;

USE ItsAllGoodMan;

CREATE table Employee (
    employee_id int,
    first_name varchar(15) NOT NULL,
    last_name varchar(10) not null,
    role varchar(20),
    salary int,
    trust_level int,
    PRIMARY KEY (employee_id),
    constraint check_role CHECK (role in ('lawyer', 'paralegal', 'receptionist', 'investigator')),
    constraint trust_level_range check (trust_level between 1 and 10)
);

create table Lawyer (
    lawyer_id int not null,
    bar_number int,
    primary key (bar_number),
    foreign key (lawyer_id) references Employee(employee_id) on update cascade on delete cascade
);

create table Specialization_table (
    specialization varchar(20),
    lawyer int,
    primary key (specialization, lawyer),
    foreign key (lawyer) references Lawyer(bar_number) on update cascade on delete cascade
);

create table Client (
    client_id int,
    first_name varchar(15) not null,
    last_name varchar(10) not null,
    phone BIGINT,
    email varchar(30),
    address varchar(100),
    type varchar(25),
    date_joined date not null,
    account_no int,
    lawyer_assigned int,
    primary key (client_id),
    foreign key (lawyer_assigned) references Lawyer(bar_number),
    constraint check_phone check (phone  between 1000000000 and 9999999999),
    constraint check_email check (email regexp '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'),
    constraint type_vals check (type in ('individual', 'business', 'cartel-affiliated'))
);

create table Cases (
    case_title varchar(20),
    client_id int,
    description varchar(100),
    status varchar(10),
    primary key (case_title),
    foreign key (client_id) REFERENCES Client(client_id) on update cascade on delete set null,
    constraint status_vals check (status in ('open', 'closed'))
);

create table Trial (
    trial_date date,
    case_title varchar(20),
    primary key (trial_date, case_title),
    foreign key (case_title) references Cases(case_title)
);

create table Document (
    document_id int,
    title varchar(20),
    type varchar(10),
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes INT,
    mime_type VARCHAR(50),
    create_date date,
    primary key (document_id)
);

create table Documents_required (
    document_id int,
    trial_date date,
    case_title varchar(20),
    PRIMARY KEY (document_id, trial_date, case_title),
    foreign key (document_id) references Document(document_id) on update cascade on delete cascade,
    foreign key (trial_date, case_title) references Trial(trial_date, case_title) on update cascade on delete cascade
);

create table Casefile (
    trial_date date,
    document_id int,
    case_title VARCHAR(20),
    client_id int,
    primary key (trial_date, document_id, case_title, client_id),
    foreign key (trial_date, case_title) references Trial(trial_date, case_title) on update cascade on delete cascade,
    foreign key (case_title) references Cases(case_title) on update cascade on delete cascade,
    foreign key (document_id) REFERENCES Document(document_id) on update cascade on delete cascade,
    foreign key (client_id) REFERENCES Client(client_id) on update cascade on delete cascade
);

create table Transaction (
    transaction_id int,
    source_account int,
    destination_account int,
    amount int,
    date date,
    primary key (transaction_id)
);

create table Fee_payment (
    transaction_id int,
    client_id int,
    case_title varchar(20),
    primary key (transaction_id),
    Foreign Key (transaction_id) REFERENCES Transaction(transaction_id) on update cascade on delete cascade,
    Foreign Key (client_id) REFERENCES Client(client_id) on update cascade on delete set null,
    Foreign Key (case_title) REFERENCES Cases(case_title) on update cascade on delete set null
);

create table Associate (
    associate_id int,
    name varchar(20),
    status varchar(10),
    loyalty_score int,
    account_no int,
    alias int,
    primary key (associate_id),
    Foreign Key (alias) REFERENCES Client(client_id) on update cascade on delete set null,
    constraint loyalty_score_range check (loyalty_score between 1 and 10),
    constraint check_status check (status in ('active', 'dead', 'missing'))
);

create table CriminalAssociate (
    associate_id int,
    codename varchar(10),
    primary KEY (associate_id),
    Foreign Key (associate_id) REFERENCES Associate(associate_id) on update cascade on delete cascade
);

create table Skills(
    skill_name varchar(50),
    associate_id int,
    primary key (skill_name, associate_id),
    Foreign Key (associate_id) REFERENCES CriminalAssociate(associate_id) on update cascade on delete cascade
);

create table CartelAssociate (
    associate_id int,
    affiliation varchar(10),
    primary key (associate_id),
    Foreign Key (associate_id) REFERENCES Associate(associate_id) on update cascade on delete cascade
);

create table Associated_business (
    business_name varchar(20),
    location varchar(20),
    account_no int,
    handler_id int,
    PRIMARY KEY (business_name, location),
    Foreign Key (handler_id) REFERENCES CriminalAssociate(associate_id) on update cascade on delete set null
);

create table Associated_business_type (
    business_name varchar(20),
    business_type varchar(20),
    primary key (business_name),
    Foreign Key (business_name) REFERENCES Associated_business(business_name) on update cascade on delete cascade
);

create table Hitlist (
    Target_id int,
    codename varchar(10),
    status varchar(20),
    justification varchar(100),
    threat_level varchar(20),
    assigned_associate int,
    primary key (Target_id),
    Foreign Key (assigned_associate) REFERENCES CriminalAssociate(associate_id) on update cascade on delete set null,
    constraint status_vals check (status in ('Listed', 'Under Surveillance', 'Action Pending', 'Neutralized', 'De-escalated')),
    constraint threat_level_vals check (threat_level in ('Low', 'Moderate', 'High', 'Critical')),
);

create table Operation (
    operation_id int,
    name varchar(10),
    
)