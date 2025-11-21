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
    phone int,
    email varchar(30),
    address varchar(100),
    type varchar(10),
    date_joined date not null,
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
    
)