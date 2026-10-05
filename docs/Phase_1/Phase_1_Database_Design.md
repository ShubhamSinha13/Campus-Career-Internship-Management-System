# Campus Career & Internship Management System

## Assessment 8 / Phase 1: Database Design and DDL

This document records only the Assessment 8 database work. Sample DML, SQL query collections, Flask, Python backend code, frontend code, business logic, connectivity, authentication, dashboards, and testing are deferred to later phases.

## Problem Statement

Students need a structured way to maintain academic details, skills, certifications, and internship applications. Companies and recruiters need a structured way to publish jobs and manage the application, interview, and offer stages. A normalized relational database can organize these records and their relationships.

## Objectives

- Identify the database requirements for the campus career and internship process.
- Model the requirements using an ER/EER diagram.
- Convert the ER design into a relational model.
- Normalize the relations to 1NF, 2NF, and 3NF.
- Create the MySQL database and tables using DDL.

## Functional Requirements

- Store departments and students.
- Store student skills and proficiency levels.
- Store student certifications.
- Store companies, recruiters, and jobs.
- Store job skill requirements.
- Store student job applications.
- Store interviews associated with applications.
- Store at most one offer for an application.
- Prevent a student from applying to the same job more than once.

## Non-Functional Requirements

- Use MySQL and InnoDB tables.
- Maintain referential integrity using primary and foreign keys.
- Use appropriate data types, `NOT NULL`, `UNIQUE`, and `CHECK` constraints.
- Keep the design normalized and suitable for an academic DBMS project.
- Do not store passwords, API keys, or other credentials in the repository.

## Scope

Assessment 8 covers problem identification, requirements, database design, the ER diagram, ER-to-relational mapping, normalization, and DDL/table creation. Admin is a system role, not a database entity. Eligibility is represented by `JOB.Minimum_CGPA` and required skills in `JOB_SKILL`; no separate eligibility table is included.

## Database Design Overview

The design contains exactly 12 tables. Independent entities are represented by their own tables. Many-to-many relationships are resolved with `STUDENT_SKILL`, `JOB_SKILL`, and `APPLICATION`. `INTERVIEW` and `OFFER` depend on `APPLICATION`.

## Entities and Tables

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

## Relationships

- `DEPARTMENT` 1 : M `STUDENT`
- `STUDENT` 1 : M `CERTIFICATION`
- `STUDENT` M : N `SKILL`, resolved using `STUDENT_SKILL`
- `COMPANY` 1 : M `RECRUITER`
- `COMPANY` 1 : M `JOB`
- `RECRUITER` 1 : M `JOB`
- `JOB` M : N `SKILL`, resolved using `JOB_SKILL`
- `STUDENT` M : N `JOB`, resolved using `APPLICATION`
- `APPLICATION` 1 : 0..M `INTERVIEW`
- `APPLICATION` 1 : 0..1 `OFFER`

The approved ER diagram is stored in `diagrams/ER_Diagram.drawio`.

## ER-to-Relational Mapping

- Each strong entity becomes a relation: `DEPARTMENT`, `STUDENT`, `SKILL`, `CERTIFICATION`, `COMPANY`, `RECRUITER`, `JOB`, `APPLICATION`, `INTERVIEW`, and `OFFER`.
- The `STUDENT` to `SKILL` many-to-many relationship becomes `STUDENT_SKILL`.
- The `JOB` to `SKILL` many-to-many relationship becomes `JOB_SKILL`.
- The `STUDENT` to `JOB` many-to-many relationship becomes `APPLICATION`.
- One-to-many relationships are represented by placing the primary key of the one-side relation as a foreign key in the many-side relation.
- The `APPLICATION` to `OFFER` one-to-zero-or-one relationship is enforced by a unique `OFFER.Application_ID`.

## Keys and Constraints

### Primary Keys

Each table has its specified primary key. `STUDENT_SKILL` has composite primary key `(Student_ID, Skill_ID)`. `JOB_SKILL` has composite primary key `(Job_ID, Skill_ID)`.

### Foreign Keys

- `STUDENT.Department_ID` references `DEPARTMENT.Department_ID`.
- `STUDENT_SKILL.Student_ID` references `STUDENT.Student_ID`.
- `STUDENT_SKILL.Skill_ID` references `SKILL.Skill_ID`.
- `CERTIFICATION.Student_ID` references `STUDENT.Student_ID`.
- `RECRUITER.Company_ID` references `COMPANY.Company_ID`.
- `JOB.Company_ID` references `COMPANY.Company_ID`.
- `JOB.Recruiter_ID` references `RECRUITER.Recruiter_ID`.
- `JOB_SKILL.Job_ID` references `JOB.Job_ID`.
- `JOB_SKILL.Skill_ID` references `SKILL.Skill_ID`.
- `APPLICATION.Student_ID` references `STUDENT.Student_ID`.
- `APPLICATION.Job_ID` references `JOB.Job_ID`.
- `INTERVIEW.Application_ID` references `APPLICATION.Application_ID`.
- `OFFER.Application_ID` references `APPLICATION.Application_ID`.

### Important Constraints

- `APPLICATION(Student_ID, Job_ID)` is unique.
- `OFFER(Application_ID)` is unique to enforce at most one offer per application.
- Composite primary keys prevent duplicate student-skill and job-skill pairs.
- CGPA values are constrained to the range 0.00 through 10.00.
- Salary values cannot be negative.
- Date checks prevent certification expiry dates before issue dates and joining dates before offer dates.
- Foreign keys use explicit constraint names and `ON UPDATE CASCADE`.

## Normalization

### 1NF

All attributes contain atomic values. Multivalued student skills and job skills are separated using `STUDENT_SKILL` and `JOB_SKILL`.

### 2NF

Relations with composite keys do not contain partial dependencies. `STUDENT_SKILL` and `JOB_SKILL` contain attributes dependent on the complete composite key. `STUDENT_SKILL.Proficiency` depends on `(Student_ID, Skill_ID)`, and `JOB_SKILL` has no non-key attribute.

### 3NF

Transitive dependencies are removed by separating independent entities such as `DEPARTMENT`, `COMPANY`, `STUDENT`, `RECRUITER`, and `JOB`. Non-key attributes describe the key of their own relation rather than another non-key attribute.

## Final Relational Schema

```text
DEPARTMENT(Department_ID PK, Department_Name)
STUDENT(Student_ID PK, Name, Email, Phone, DOB, CGPA, Graduation_Year, Department_ID FK)
SKILL(Skill_ID PK, Skill_Name)
STUDENT_SKILL(Student_ID PK/FK, Skill_ID PK/FK, Proficiency)
CERTIFICATION(Certification_ID PK, Student_ID FK, Certification_Name,
              Issuing_Organization, Issue_Date, Expiry_Date)
COMPANY(Company_ID PK, Company_Name, Industry, Location, Website, Email, Phone)
RECRUITER(Recruiter_ID PK, Company_ID FK, Recruiter_Name, Email, Phone)
JOB(Job_ID PK, Company_ID FK, Recruiter_ID FK, Job_Title, Job_Type,
    Description, Location, Minimum_CGPA, Application_Deadline, Salary, Status)
JOB_SKILL(Job_ID PK/FK, Skill_ID PK/FK)
APPLICATION(Application_ID PK, Student_ID FK, Job_ID FK, Application_Date, Status,
            UNIQUE(Student_ID, Job_ID))
INTERVIEW(Interview_ID PK, Application_ID FK, Interview_Date, Interview_Time,
          Mode, Interview_Status, Remarks)
OFFER(Offer_ID PK, Application_ID FK, Offer_Date, Job_Title, Salary,
      Joining_Date, Offer_Status, UNIQUE(Application_ID))
```