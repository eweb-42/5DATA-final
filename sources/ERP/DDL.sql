drop table if exists campuses;
drop table if exists professors;
drop table if exists students;
drop table if exists audiences;
drop table if exists lessons;
drop table if exists subjects;
drop table if exists grades;
drop table if exists attendances;
drop table if exists companies;
drop table if exists internships;
drop table if exists events;


create table campuses (
    id serial primary key,
    name varchar(30),
    address varchar(60),
    city varchar(30),
    zip varchar(10),
    region varchar(30),
    country varchar(24)
);

create table professors (
    id serial primary key,
    first_name varchar(30),
    last_name varchar(30),
    email varchar(60),
    gender varchar(12),
    date_of_birth date,
    subject_id varchar(5),
    campus_id int
);

create table students (
    id int primary key,
    first_name varchar(30),
    last_name varchar(30),
    email varchar(60),
    personal_email varchar(60),
    gender varchar(12),
    date_of_birth date,
    join_date date,
    left_date date,
    campus_id int,
    promotion varchar(4)
);

create table audiences(
    id serial primary key,
    first_name varchar(30),
    last_name varchar(30),
    email varchar(60),
    gender varchar(12),
    date_of_birth date,
    event_id int
);

create table lessons (
    id serial primary key,
    date date,
    subject_id varchar(5),
    professor_id int,
    campus_id int
);

create table subjects (
    id varchar(5),
    name varchar(50),
    level varchar(5)
);

create table grades (
    id serial primary key,
    student_id int,
    subject_id varchar(5),
    date date,
    grade float(2)
);

create table attendances (
    id serial primary key,
    lesson_id int,
    student_id int,
    present boolean
);

create table companies (
    id serial primary key,
    name varchar(120),
    phone varchar(14),
    email varchar(30),
    domain varchar(24),
    address varchar(60),
    city varchar(30),
    zip varchar(10),
    country varchar(30)
);

create table apprenticeships (
    id serial primary key,
    student_id int,
    company_id int,
    end_date date
);

create table events (
    id serial primary key,
    type varchar(24),
    date date,
    campus_id int,
    location varchar(24),
    description varchar(120)
);
