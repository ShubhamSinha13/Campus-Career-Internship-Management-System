-- Phase 2 authentication account table
-- Run after the approved Phase 1 schema and sample-data scripts.

USE campus_career_db;

CREATE TABLE USER_ACCOUNT (
    User_ID INT AUTO_INCREMENT,
    Email VARCHAR(150) NOT NULL,
    Password_Hash VARCHAR(255) NOT NULL,
    Role ENUM('ADMIN', 'STUDENT', 'COMPANY') NOT NULL,
    Student_ID INT NULL,
    Company_ID INT NULL,
    CONSTRAINT pk_user_account PRIMARY KEY (User_ID),
    CONSTRAINT uq_user_account_email UNIQUE (Email),
    CONSTRAINT uq_user_account_student UNIQUE (Student_ID),
    CONSTRAINT uq_user_account_company UNIQUE (Company_ID),
    CONSTRAINT fk_user_account_student FOREIGN KEY (Student_ID)
        REFERENCES STUDENT (Student_ID)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_user_account_company FOREIGN KEY (Company_ID)
        REFERENCES COMPANY (Company_ID)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE = InnoDB;
