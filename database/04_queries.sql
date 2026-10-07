-- Campus Career & Internship Management System
-- Phase 2: DML queries

USE campus_career_db;

-- SECTION 1: BASIC SELECT QUERIES

-- Query 1: Display all students.
SELECT *
FROM STUDENT;

-- Query 2: Display students with CGPA greater than or equal to 8.0.
SELECT *
FROM STUDENT
WHERE CGPA >= 8.00;

-- Query 3: Display students belonging to Computer Science and Engineering.
SELECT s.*
FROM STUDENT AS s
INNER JOIN DEPARTMENT AS d ON s.Department_ID = d.Department_ID
WHERE d.Department_Name = 'Computer Science and Engineering';

-- Query 4: Display all open jobs.
SELECT *
FROM JOB
WHERE Status = 'Open';

-- Query 5: Display jobs with minimum CGPA less than or equal to 8.0.
SELECT *
FROM JOB
WHERE Minimum_CGPA <= 8.00;

-- Query 6: Display all companies.
SELECT *
FROM COMPANY;

-- Query 7: Display all available skills.
SELECT *
FROM SKILL;

-- SECTION 2: ORDER BY AND FILTERING

-- Query 8: Students ordered by CGPA descending.
SELECT Student_ID, Name, CGPA
FROM STUDENT
ORDER BY CGPA DESC;

-- Query 9: Jobs ordered by salary descending.
SELECT Job_ID, Job_Title, Salary
FROM JOB
ORDER BY Salary DESC;

-- Query 10: Jobs located in Bengaluru.
SELECT *
FROM JOB
WHERE Location = 'Bengaluru';

-- Query 11: Applications with status Selected.
SELECT *
FROM APPLICATION
WHERE Status = 'Selected';

-- Query 12: Applications with status Shortlisted.
SELECT *
FROM APPLICATION
WHERE Status = 'Shortlisted';

-- Query 13: Students whose names start with A.
SELECT *
FROM STUDENT
WHERE Name LIKE 'A%';

-- Query 14: Jobs with salary between 25000 and 35000.
SELECT *
FROM JOB
WHERE Salary BETWEEN 25000.00 AND 35000.00;

-- SECTION 3: JOIN QUERIES

-- Query 15: Student name and department name.
SELECT s.Name AS Student_Name, d.Department_Name
FROM STUDENT AS s
INNER JOIN DEPARTMENT AS d ON s.Department_ID = d.Department_ID;

-- Query 16: Job title, company name, and recruiter name.
SELECT j.Job_Title, c.Company_Name, r.Recruiter_Name
FROM JOB AS j
INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
INNER JOIN RECRUITER AS r ON j.Recruiter_ID = r.Recruiter_ID;

-- Query 17: Student name, job title, and application status.
SELECT s.Name AS Student_Name, j.Job_Title, a.Status AS Application_Status
FROM APPLICATION AS a
INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID;

-- Query 18: Student name, skill name, and proficiency.
SELECT s.Name AS Student_Name, sk.Skill_Name, ss.Proficiency
FROM STUDENT_SKILL AS ss
INNER JOIN STUDENT AS s ON ss.Student_ID = s.Student_ID
INNER JOIN SKILL AS sk ON ss.Skill_ID = sk.Skill_ID;

-- Query 19: Job title and required skill.
SELECT j.Job_Title, sk.Skill_Name AS Required_Skill
FROM JOB_SKILL AS js
INNER JOIN JOB AS j ON js.Job_ID = j.Job_ID
INNER JOIN SKILL AS sk ON js.Skill_ID = sk.Skill_ID;

-- Query 20: Student name, certification name, and issuing organization.
SELECT s.Name AS Student_Name, c.Certification_Name, c.Issuing_Organization
FROM CERTIFICATION AS c
INNER JOIN STUDENT AS s ON c.Student_ID = s.Student_ID;

-- Query 21: Student name, job title, interview date, and interview status.
SELECT s.Name AS Student_Name, j.Job_Title,
       i.Interview_Date, i.Interview_Status
FROM INTERVIEW AS i
INNER JOIN APPLICATION AS a ON i.Application_ID = a.Application_ID
INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID;

-- Query 22: Student name, job title, offer salary, and offer status.
SELECT s.Name AS Student_Name, j.Job_Title, o.Salary, o.Offer_Status
FROM OFFER AS o
INNER JOIN APPLICATION AS a ON o.Application_ID = a.Application_ID
INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID;

-- SECTION 4: AGGREGATE FUNCTIONS

-- Query 23: Number of students in each department.
SELECT d.Department_ID, d.Department_Name,
       COUNT(s.Student_ID) AS Student_Count
FROM DEPARTMENT AS d
LEFT JOIN STUDENT AS s ON d.Department_ID = s.Department_ID
GROUP BY d.Department_ID, d.Department_Name;

-- Query 24: Number of jobs posted by each company.
SELECT c.Company_ID, c.Company_Name,
       COUNT(j.Job_ID) AS Job_Count
FROM COMPANY AS c
LEFT JOIN JOB AS j ON c.Company_ID = j.Company_ID
GROUP BY c.Company_ID, c.Company_Name;

-- Query 25: Number of applications for each job.
SELECT j.Job_ID, j.Job_Title,
       COUNT(a.Application_ID) AS Application_Count
FROM JOB AS j
LEFT JOIN APPLICATION AS a ON j.Job_ID = a.Job_ID
GROUP BY j.Job_ID, j.Job_Title;

-- Query 26: Average student CGPA.
SELECT AVG(CGPA) AS Average_Student_CGPA
FROM STUDENT;

-- Query 27: Highest student CGPA.
SELECT MAX(CGPA) AS Highest_Student_CGPA
FROM STUDENT;

-- Query 28: Lowest student CGPA.
SELECT MIN(CGPA) AS Lowest_Student_CGPA
FROM STUDENT;

-- Query 29: Average job salary.
SELECT AVG(Salary) AS Average_Job_Salary
FROM JOB;

-- Query 30: Number of applications by status.
SELECT Status, COUNT(*) AS Application_Count
FROM APPLICATION
GROUP BY Status;

-- SECTION 5: GROUP BY AND HAVING

-- Query 31: Departments having more than one student.
SELECT d.Department_Name, COUNT(s.Student_ID) AS Student_Count
FROM DEPARTMENT AS d
INNER JOIN STUDENT AS s ON d.Department_ID = s.Department_ID
GROUP BY d.Department_ID, d.Department_Name
HAVING COUNT(s.Student_ID) > 1;

-- Query 32: Jobs having more than one application.
SELECT j.Job_Title, COUNT(a.Application_ID) AS Application_Count
FROM JOB AS j
INNER JOIN APPLICATION AS a ON j.Job_ID = a.Job_ID
GROUP BY j.Job_ID, j.Job_Title
HAVING COUNT(a.Application_ID) > 1;

-- Query 33: Companies having more than one job.
SELECT c.Company_Name, COUNT(j.Job_ID) AS Job_Count
FROM COMPANY AS c
INNER JOIN JOB AS j ON c.Company_ID = j.Company_ID
GROUP BY c.Company_ID, c.Company_Name
HAVING COUNT(j.Job_ID) > 1;

-- Query 34: Application statuses having more than one application.
SELECT Status, COUNT(*) AS Application_Count
FROM APPLICATION
GROUP BY Status
HAVING COUNT(*) > 1;

-- SECTION 6: SUBQUERIES

-- Query 35: Students whose CGPA is above the average CGPA.
SELECT Student_ID, Name, CGPA
FROM STUDENT
WHERE CGPA > (SELECT AVG(CGPA) FROM STUDENT);

-- Query 36: Jobs whose salary is above the average job salary.
SELECT Job_ID, Job_Title, Salary
FROM JOB
WHERE Salary > (SELECT AVG(Salary) FROM JOB);

-- Query 37: Students who have applied for at least one job.
SELECT Student_ID, Name
FROM STUDENT
WHERE Student_ID IN (
    SELECT Student_ID
    FROM APPLICATION
);

-- Query 38: Students who have not applied for any job.
SELECT Student_ID, Name
FROM STUDENT
WHERE Student_ID NOT IN (
    SELECT Student_ID
    FROM APPLICATION
);

-- Query 39: Student(s) with the highest CGPA.
SELECT Student_ID, Name, CGPA
FROM STUDENT
WHERE CGPA = (SELECT MAX(CGPA) FROM STUDENT);

-- SECTION 7: BUSINESS LOGIC / ELIGIBILITY QUERY

-- Query 40: Check whether a student meets a selected job's minimum CGPA.
-- Change Student_ID and Job_ID values to test another combination.
SELECT s.Name AS Student_Name, s.CGPA,
       j.Job_Title, j.Minimum_CGPA,
       CASE
           WHEN s.CGPA >= j.Minimum_CGPA THEN 'Eligible'
           ELSE 'Not Eligible'
       END AS CGPA_Eligibility
FROM STUDENT AS s
CROSS JOIN JOB AS j
WHERE s.Student_ID = 2
  AND j.Job_ID = 1;

-- Query 41: Students who possess every required skill for Job_ID 1.
SELECT s.Student_ID, s.Name
FROM STUDENT AS s
WHERE NOT EXISTS (
    SELECT 1
    FROM JOB_SKILL AS required_skill
    WHERE required_skill.Job_ID = 1
      AND NOT EXISTS (
          SELECT 1
          FROM STUDENT_SKILL AS student_skill
          WHERE student_skill.Student_ID = s.Student_ID
            AND student_skill.Skill_ID = required_skill.Skill_ID
      )
);

-- Query 42: Eligibility report based on CGPA for every student and open job.
SELECT s.Name AS Student_Name, s.CGPA,
       j.Job_Title, j.Minimum_CGPA,
       CASE
           WHEN s.CGPA >= j.Minimum_CGPA THEN 'Eligible'
           ELSE 'Not Eligible'
       END AS Eligibility_Status
FROM STUDENT AS s
CROSS JOIN JOB AS j
WHERE j.Status = 'Open'
ORDER BY s.Student_ID, j.Job_ID;

-- SECTION 8: APPLICATION TRACKING

-- Query 43: Students and their application status.
SELECT s.Name AS Student_Name, j.Job_Title, a.Status AS Application_Status
FROM APPLICATION AS a
INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID;

-- Query 44: All shortlisted students.
SELECT s.Name AS Student_Name, j.Job_Title, a.Status
FROM APPLICATION AS a
INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID
WHERE a.Status = 'Shortlisted';

-- Query 45: All selected students.
SELECT s.Name AS Student_Name, j.Job_Title, a.Status
FROM APPLICATION AS a
INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID
WHERE a.Status = 'Selected';

-- Query 46: All rejected applications.
SELECT s.Name AS Student_Name, j.Job_Title, a.Status
FROM APPLICATION AS a
INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID
WHERE a.Status = 'Rejected';

-- Query 47: Students who received offers.
SELECT s.Name AS Student_Name, j.Job_Title,
       o.Salary, o.Offer_Status
FROM OFFER AS o
INNER JOIN APPLICATION AS a ON o.Application_ID = a.Application_ID
INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID;

-- Query 48: Students whose applications have interviews scheduled.
SELECT s.Name AS Student_Name, j.Job_Title,
       i.Interview_Date, i.Interview_Status
FROM INTERVIEW AS i
INNER JOIN APPLICATION AS a ON i.Application_ID = a.Application_ID
INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID
WHERE i.Interview_Status = 'Scheduled';

-- Query 49: Complete application tracking report.
SELECT s.Name AS Student_Name, j.Job_Title, c.Company_Name,
       a.Status AS Application_Status,
       i.Interview_Status, o.Offer_Status
FROM APPLICATION AS a
INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID
INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
LEFT JOIN INTERVIEW AS i ON a.Application_ID = i.Application_ID
LEFT JOIN OFFER AS o ON a.Application_ID = o.Application_ID;

-- SECTION 9: UPDATE DML
-- DEMONSTRATION ONLY: Uncomment the UPDATE below when you want to execute it.
-- The sample database remains unchanged while this file is executed normally.

-- Query 50: Demonstrate changing an application status.
SELECT *
FROM APPLICATION
WHERE Application_ID = 2;

-- UPDATE APPLICATION
-- SET Status = 'Shortlisted'
-- WHERE Application_ID = 2;

-- After uncommenting and executing the UPDATE, run the SELECT above again to verify the change.

-- Query 51: Demonstrate changing a student's phone number.
SELECT *
FROM STUDENT
WHERE Student_ID = 2;

-- UPDATE STUDENT
-- SET Phone = '9000000099'
-- WHERE Student_ID = 2;

-- The UPDATE is disabled by default to preserve the sample data.

-- Query 52: Demonstrate changing a job status.
SELECT *
FROM JOB
WHERE Job_ID = 6;

-- UPDATE JOB
-- SET Status = 'Open'
-- WHERE Job_ID = 6;

-- The UPDATE is disabled by default to preserve the sample data.

-- SECTION 10: DELETE DML
-- DEMONSTRATION ONLY: Uncomment the DELETE below when you want to execute it.
-- The DELETE is intentionally disabled to preserve sample data.

-- Query 53: Preview the certification record before deletion.
SELECT *
FROM CERTIFICATION
WHERE Certification_ID = 6;

-- Verify the record above before demonstrating DELETE.

-- Query 54: Demonstrate deleting the specifically verified certification record.
-- DELETE FROM CERTIFICATION
-- WHERE Certification_ID = 6;

-- DELETE is intentionally commented out to preserve the original sample data.
-- Uncomment only when demonstrating DELETE manually in a controlled session.

-- SECTION 11: USEFUL DASHBOARD QUERIES

-- Query 55: Total number of students.
SELECT COUNT(*) AS Total_Students
FROM STUDENT;

-- Query 56: Total number of companies.
SELECT COUNT(*) AS Total_Companies
FROM COMPANY;

-- Query 57: Total number of jobs.
SELECT COUNT(*) AS Total_Jobs
FROM JOB;

-- Query 58: Total number of applications.
SELECT COUNT(*) AS Total_Applications
FROM APPLICATION;

-- Query 59: Total number of selected students.
SELECT COUNT(DISTINCT Student_ID) AS Total_Selected_Students
FROM APPLICATION
WHERE Status = 'Selected';

-- Query 60: Total number of offers.
SELECT COUNT(*) AS Total_Offers
FROM OFFER;

-- Query 61: Number of open jobs.
SELECT COUNT(*) AS Open_Jobs
FROM JOB
WHERE Status = 'Open';

-- Query 62: Number of applications by status.
SELECT Status, COUNT(*) AS Application_Count
FROM APPLICATION
GROUP BY Status;

-- SECTION 12: FINAL DEMONSTRATION QUERY

-- Query 63: Core project workflow report.
SELECT s.Name AS Student_Name,
       d.Department_Name AS Department,
       j.Job_Title,
       c.Company_Name AS Company,
       a.Status AS Application_Status,
       i.Interview_Status,
       o.Offer_Status
FROM APPLICATION AS a
INNER JOIN STUDENT AS s ON a.Student_ID = s.Student_ID
INNER JOIN DEPARTMENT AS d ON s.Department_ID = d.Department_ID
INNER JOIN JOB AS j ON a.Job_ID = j.Job_ID
INNER JOIN COMPANY AS c ON j.Company_ID = c.Company_ID
LEFT JOIN INTERVIEW AS i ON a.Application_ID = i.Application_ID
LEFT JOIN OFFER AS o ON a.Application_ID = o.Application_ID;

-- END OF PHASE 2 DML QUERIES
