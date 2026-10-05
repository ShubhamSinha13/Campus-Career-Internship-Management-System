-- Campus Career & Internship Management System
-- Phase 1: Table creation

USE campus_career_db;

CREATE TABLE DEPARTMENT (
    Department_ID INT AUTO_INCREMENT,
    Department_Name VARCHAR(100) NOT NULL,
    CONSTRAINT pk_department PRIMARY KEY (Department_ID),
    CONSTRAINT uq_department_name UNIQUE (Department_Name)
) ENGINE = InnoDB;

CREATE TABLE COMPANY (
    Company_ID INT AUTO_INCREMENT,
    Company_Name VARCHAR(150) NOT NULL,
    Industry VARCHAR(100) NOT NULL,
    Location VARCHAR(150) NOT NULL,
    Website VARCHAR(255),
    Email VARCHAR(150),
    Phone VARCHAR(20),
    CONSTRAINT pk_company PRIMARY KEY (Company_ID),
    CONSTRAINT uq_company_name UNIQUE (Company_Name)
) ENGINE = InnoDB;

CREATE TABLE SKILL (
    Skill_ID INT AUTO_INCREMENT,
    Skill_Name VARCHAR(100) NOT NULL,
    CONSTRAINT pk_skill PRIMARY KEY (Skill_ID),
    CONSTRAINT uq_skill_name UNIQUE (Skill_Name)
) ENGINE = InnoDB;

CREATE TABLE STUDENT (
    Student_ID INT AUTO_INCREMENT,
    Name VARCHAR(120) NOT NULL,
    Email VARCHAR(150) NOT NULL,
    Phone VARCHAR(20),
    DOB DATE NOT NULL,
    CGPA DECIMAL(3,2) NOT NULL,
    Graduation_Year YEAR NOT NULL,
    Department_ID INT NOT NULL,
    CONSTRAINT pk_student PRIMARY KEY (Student_ID),
    CONSTRAINT uq_student_email UNIQUE (Email),
    CONSTRAINT chk_student_cgpa CHECK (CGPA BETWEEN 0.00 AND 10.00),
    CONSTRAINT fk_student_department FOREIGN KEY (Department_ID)
        REFERENCES DEPARTMENT (Department_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE RECRUITER (
    Recruiter_ID INT AUTO_INCREMENT,
    Company_ID INT NOT NULL,
    Recruiter_Name VARCHAR(120) NOT NULL,
    Email VARCHAR(150) NOT NULL,
    Phone VARCHAR(20),
    CONSTRAINT pk_recruiter PRIMARY KEY (Recruiter_ID),
    CONSTRAINT uq_recruiter_email UNIQUE (Email),
    CONSTRAINT fk_recruiter_company FOREIGN KEY (Company_ID)
        REFERENCES COMPANY (Company_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE JOB (
    Job_ID INT AUTO_INCREMENT,
    Company_ID INT NOT NULL,
    Recruiter_ID INT NOT NULL,
    Job_Title VARCHAR(150) NOT NULL,
    Job_Type VARCHAR(50) NOT NULL,
    Description TEXT NOT NULL,
    Location VARCHAR(150) NOT NULL,
    Minimum_CGPA DECIMAL(3,2) NOT NULL,
    Application_Deadline DATE NOT NULL,
    Salary DECIMAL(12,2) NOT NULL,
    Status VARCHAR(30) NOT NULL,
    CONSTRAINT pk_job PRIMARY KEY (Job_ID),
    CONSTRAINT chk_job_minimum_cgpa CHECK (Minimum_CGPA BETWEEN 0.00 AND 10.00),
    CONSTRAINT chk_job_salary CHECK (Salary >= 0.00),
    CONSTRAINT fk_job_company FOREIGN KEY (Company_ID)
        REFERENCES COMPANY (Company_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_job_recruiter FOREIGN KEY (Recruiter_ID)
        REFERENCES RECRUITER (Recruiter_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE STUDENT_SKILL (
    Student_ID INT NOT NULL,
    Skill_ID INT NOT NULL,
    Proficiency VARCHAR(30) NOT NULL,
    CONSTRAINT pk_student_skill PRIMARY KEY (Student_ID, Skill_ID),
    CONSTRAINT fk_student_skill_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT (Student_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_student_skill_skill FOREIGN KEY (Skill_ID)
        REFERENCES SKILL (Skill_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE CERTIFICATION (
    Certification_ID INT AUTO_INCREMENT,
    Student_ID INT NOT NULL,
    Certification_Name VARCHAR(150) NOT NULL,
    Issuing_Organization VARCHAR(150) NOT NULL,
    Issue_Date DATE NOT NULL,
    Expiry_Date DATE,
    CONSTRAINT pk_certification PRIMARY KEY (Certification_ID),
    CONSTRAINT chk_certification_dates CHECK (Expiry_Date IS NULL OR Expiry_Date >= Issue_Date),
    CONSTRAINT fk_certification_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT (Student_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE JOB_SKILL (
    Job_ID INT NOT NULL,
    Skill_ID INT NOT NULL,
    CONSTRAINT pk_job_skill PRIMARY KEY (Job_ID, Skill_ID),
    CONSTRAINT fk_job_skill_job FOREIGN KEY (Job_ID)
        REFERENCES JOB (Job_ID)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_job_skill_skill FOREIGN KEY (Skill_ID)
        REFERENCES SKILL (Skill_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE APPLICATION (
    Application_ID INT AUTO_INCREMENT,
    Student_ID INT NOT NULL,
    Job_ID INT NOT NULL,
    Application_Date DATE NOT NULL,
    Status VARCHAR(30) NOT NULL,
    CONSTRAINT pk_application PRIMARY KEY (Application_ID),
    CONSTRAINT uq_application_student_job UNIQUE (Student_ID, Job_ID),
    CONSTRAINT fk_application_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT (Student_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_application_job FOREIGN KEY (Job_ID)
        REFERENCES JOB (Job_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE INTERVIEW (
    Interview_ID INT AUTO_INCREMENT,
    Application_ID INT NOT NULL,
    Interview_Date DATE NOT NULL,
    Interview_Time TIME NOT NULL,
    Mode VARCHAR(30) NOT NULL,
    Interview_Status VARCHAR(30) NOT NULL,
    Remarks VARCHAR(500),
    CONSTRAINT pk_interview PRIMARY KEY (Interview_ID),
    CONSTRAINT fk_interview_application FOREIGN KEY (Application_ID)
        REFERENCES APPLICATION (Application_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;

CREATE TABLE OFFER (
    Offer_ID INT AUTO_INCREMENT,
    Application_ID INT NOT NULL,
    Offer_Date DATE NOT NULL,
    Job_Title VARCHAR(150) NOT NULL,
    Salary DECIMAL(12,2) NOT NULL,
    Joining_Date DATE NOT NULL,
    Offer_Status VARCHAR(30) NOT NULL,
    CONSTRAINT pk_offer PRIMARY KEY (Offer_ID),
    CONSTRAINT uq_offer_application UNIQUE (Application_ID),
    CONSTRAINT chk_offer_salary CHECK (Salary >= 0.00),
    CONSTRAINT chk_offer_dates CHECK (Joining_Date >= Offer_Date),
    CONSTRAINT fk_offer_application FOREIGN KEY (Application_ID)
        REFERENCES APPLICATION (Application_ID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE = InnoDB;
