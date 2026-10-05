# Campus Career & Internship Management System

## Current Status

**Assessment 8 / Phase 1**

This repository currently contains only the database design and DDL work for the DBMS academic project. Later assessments will add sample DML, query collections, Flask, Python, frontend, business logic, and database connectivity.

### Completed in Assessment 8

- Problem identification
- Requirements analysis
- Database design
- ER diagram
- ER-to-relational model
- Normalization: 1NF, 2NF, and 3NF
- DDL / table creation

### Not Implemented Yet

- DML / sample data
- SQL query collection
- Flask backend
- Frontend
- Business logic
- Database connectivity
- Application testing

## Problem Statement

Students often need one organized system to maintain their academic profile, skills, certifications, and internship applications. Companies and recruiters also need a structured way to publish jobs, review applications, conduct interviews, and record offers. This project models these activities in a relational database.

## Objectives

- Store student, department, skill, and certification information.
- Store companies, recruiters, and job opportunities.
- Connect students with skills and jobs through normalized junction tables.
- Track applications, interviews, and offers.
- Demonstrate relational database design, normalization, DDL, keys, and constraints.

## Scope

Assessment 8 is limited to problem identification, requirements, the ER design, the relational model, normalization documentation, and MySQL table creation. Sample DML, SQL queries, Flask, Python, frontend, business logic, connectivity, authentication, dashboards, and testing are intentionally deferred to later project phases. Admin is treated as a system role and is not a database entity. Eligibility is represented using `Minimum_CGPA` and `JOB_SKILL`; no separate eligibility table is used.

## Phase 1 Database Design

- Twelve relational tables representing students, departments, skills, certifications, companies, recruiters, jobs, applications, interviews, and offers.
- Primary keys, foreign keys, composite keys, unique constraints, and referential actions.
- A unique `(Student_ID, Job_ID)` constraint to prevent duplicate applications.
- A unique `Application_ID` in `OFFER` to enforce the `APPLICATION 1 : 0..1 OFFER` relationship.

## Technology Stack

- MySQL
- MySQL Workbench
- Python and Flask planned for a later phase
- HTML, CSS, JavaScript, and Bootstrap planned for a later phase
- `mysql-connector-python` planned for a later phase
- Git and GitHub for version control

## Database Entities

The design contains exactly these 12 tables:

1. `DEPARTMENT(Department_ID, Department_Name)`
2. `STUDENT(Student_ID, Name, Email, Phone, DOB, CGPA, Graduation_Year, Department_ID)`
3. `SKILL(Skill_ID, Skill_Name)`
4. `STUDENT_SKILL(Student_ID, Skill_ID, Proficiency)`
5. `CERTIFICATION(Certification_ID, Student_ID, Certification_Name, Issuing_Organization, Issue_Date, Expiry_Date)`
6. `COMPANY(Company_ID, Company_Name, Industry, Location, Website, Email, Phone)`
7. `RECRUITER(Recruiter_ID, Company_ID, Recruiter_Name, Email, Phone)`
8. `JOB(Job_ID, Company_ID, Recruiter_ID, Job_Title, Job_Type, Description, Location, Minimum_CGPA, Application_Deadline, Salary, Status)`
9. `JOB_SKILL(Job_ID, Skill_ID)`
10. `APPLICATION(Application_ID, Student_ID, Job_ID, Application_Date, Status)`
11. `INTERVIEW(Interview_ID, Application_ID, Interview_Date, Interview_Time, Mode, Interview_Status, Remarks)`
12. `OFFER(Offer_ID, Application_ID, Offer_Date, Job_Title, Salary, Joining_Date, Offer_Status)`

`STUDENT_SKILL` and `JOB_SKILL` use composite primary keys. `APPLICATION` has a unique constraint on `(Student_ID, Job_ID)`, so a student cannot apply to the same job more than once. `OFFER.Application_ID` is unique to enforce the one-to-zero-or-one offer relationship.

## Database Relationships

- `DEPARTMENT` 1 : M `STUDENT`
- `STUDENT` 1 : M `CERTIFICATION`
- `STUDENT` M : N `SKILL`, resolved through `STUDENT_SKILL`
- `COMPANY` 1 : M `RECRUITER`
- `COMPANY` 1 : M `JOB`
- `RECRUITER` 1 : M `JOB`
- `JOB` M : N `SKILL`, resolved through `JOB_SKILL`
- `STUDENT` M : N `JOB`, resolved through `APPLICATION`
- `APPLICATION` 1 : 0..M `INTERVIEW`
- `APPLICATION` 1 : 0..1 `OFFER`

## Normalization Summary

### First Normal Form (1NF)

All attributes contain atomic values. Multivalued student skills and job skills are separated into `STUDENT_SKILL` and `JOB_SKILL` rather than being stored as repeated values in one column.

### Second Normal Form (2NF)

Relations with composite keys have no partial dependencies. The `Proficiency` attribute in `STUDENT_SKILL` depends on the complete `(Student_ID, Skill_ID)` key, while `JOB_SKILL` contains only its complete composite key.

### Third Normal Form (3NF)

Transitive dependencies are removed by separating entities such as `DEPARTMENT`, `COMPANY`, `STUDENT`, `RECRUITER`, and `JOB`. Non-key attributes describe the key of their own relation rather than another non-key attribute.

## Project Structure

```text
Campus-Career-Internship-Management-System/
├── README.md
├── .gitignore
├── database/
│   ├── 01_create_database.sql
│   ├── 02_create_tables.sql
│   ├── 03_insert_sample_data.sql       # Later phase; not in Assessment 8 commit
│   └── 04_queries.sql                  # Later phase; not in Assessment 8 commit
├── diagrams/
│   └── ER_Diagram.drawio
└── docs/
    └── Phase_1/
```

## How to Run the Phase 1 DDL in MySQL Workbench

1. Open MySQL Workbench and connect to your local MySQL server.
2. Open `database/01_create_database.sql` and execute it.
3. Open and execute `database/02_create_tables.sql`.
4. Refresh the Schemas panel and inspect the `campus_career_db` tables, columns, indexes, and foreign keys.

The scripts target MySQL 8.0 or later. No passwords, API keys, or database credentials are stored in this repository.

## Assessment 8 Commit Scope

The Assessment 8 commit contains only the database design and DDL artifacts:

- `README.md`
- `.gitignore`
- `database/01_create_database.sql`
- `database/02_create_tables.sql`
- `diagrams/ER_Diagram.drawio`
- `docs/Phase_1/Phase_1_Database_Design.md`

The existing `database/03_insert_sample_data.sql` and `database/04_queries.sql` files are intentionally excluded from this commit and are not deleted.

## Git Preparation

Review the files before committing. Use an explicit file list so later-phase files are not staged:

```bash
git status
git add README.md .gitignore database/01_create_database.sql database/02_create_tables.sql diagrams/ER_Diagram.drawio docs/Phase_1/Phase_1_Database_Design.md
git commit -m "Complete Assessment 8 Phase 1 database design and DDL"
git remote add origin https://github.com/ShubhamSinha13/Campus-Career-Internship-Management-System.git
git branch -M main
git push -u origin main
```

Do not run the remote or push commands until the GitHub repository exists and is accessible.
