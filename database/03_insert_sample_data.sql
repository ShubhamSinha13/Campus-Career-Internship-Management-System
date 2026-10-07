-- Campus Career & Internship Management System
-- Phase 2: Fictional sample data / DML

USE campus_career_db;

INSERT INTO DEPARTMENT (Department_ID, Department_Name) VALUES
(1, 'Computer Science and Engineering'),
(2, 'Information Technology'),
(3, 'Electronics and Communication Engineering'),
(4, 'Business Administration');

INSERT INTO STUDENT (Student_ID, Name, Email, Phone, DOB, CGPA, Graduation_Year, Department_ID) VALUES
(1, 'Aarav Mehta', 'aarav.mehta@example.com', '9000000001', '2003-04-12', 8.70, 2026, 1),
(2, 'Diya Nair', 'diya.nair@example.com', '9000000002', '2003-08-21', 9.10, 2026, 1),
(3, 'Kabir Shah', 'kabir.shah@example.com', '9000000003', '2002-12-05', 7.80, 2026, 2),
(4, 'Meera Iyer', 'meera.iyer@example.com', '9000000004', '2003-02-17', 8.40, 2026, 3),
(5, 'Rohan Gupta', 'rohan.gupta@example.com', '9000000005', '2003-06-30', 7.20, 2026, 2),
(6, 'Sara Khan', 'sara.khan@example.com', '9000000006', '2003-10-11', 8.90, 2026, 4),
(7, 'Vikram Rao', 'vikram.rao@example.com', '9000000007', '2002-03-26', 6.90, 2026, 3),
(8, 'Ananya Bose', 'ananya.bose@example.com', '9000000008', '2003-11-09', 9.30, 2026, 1);

INSERT INTO SKILL (Skill_ID, Skill_Name) VALUES
(1, 'Python'),
(2, 'Java'),
(3, 'SQL'),
(4, 'Data Analysis'),
(5, 'HTML and CSS'),
(6, 'JavaScript'),
(7, 'Communication'),
(8, 'Digital Marketing'),
(9, 'C++'),
(10, 'Cloud Fundamentals');

INSERT INTO STUDENT_SKILL (Student_ID, Skill_ID, Proficiency) VALUES
(1, 1, 'Advanced'), (1, 3, 'Advanced'),
(2, 1, 'Intermediate'), (2, 4, 'Advanced'),
(3, 2, 'Advanced'), (3, 3, 'Intermediate'),
(4, 5, 'Advanced'), (4, 6, 'Intermediate'),
(5, 9, 'Advanced'), (5, 3, 'Intermediate'),
(6, 7, 'Advanced'), (6, 8, 'Advanced'),
(7, 9, 'Advanced'), (7, 2, 'Intermediate');

INSERT INTO CERTIFICATION (Certification_ID, Student_ID, Certification_Name, Issuing_Organization, Issue_Date, Expiry_Date) VALUES
(1, 1, 'Python Programming Fundamentals', 'OpenLearn Institute', '2024-02-10', NULL),
(2, 2, 'Data Analytics Certificate', 'SkillPath Academy', '2024-05-18', '2027-05-18'),
(3, 3, 'Java Application Development', 'CodeBridge Academy', '2023-11-12', NULL),
(4, 4, 'Responsive Web Design', 'WebCraft Institute', '2024-01-25', NULL),
(5, 6, 'Digital Marketing Essentials', 'MarketWise Academy', '2024-07-06', '2026-07-06'),
(6, 8, 'Cloud Foundations', 'CloudStart Institute', '2024-08-22', NULL);

INSERT INTO COMPANY (Company_ID, Company_Name, Industry, Location, Website, Email, Phone) VALUES
(1, 'Nexora Technologies', 'Software Services', 'Bengaluru', 'https://www.nexora.example', 'careers@nexora.example', '9100000001'),
(2, 'BrightPath Analytics', 'Data Analytics', 'Pune', 'https://www.brightpath.example', 'careers@brightpath.example', '9100000002'),
(3, 'GreenGrid Systems', 'Cloud Infrastructure', 'Hyderabad', 'https://www.greengrid.example', 'careers@greengrid.example', '9100000003'),
(4, 'MarketNest Media', 'Digital Marketing', 'Mumbai', 'https://www.marketnest.example', 'careers@marketnest.example', '9100000004');

INSERT INTO RECRUITER (Recruiter_ID, Company_ID, Recruiter_Name, Email, Phone) VALUES
(1, 1, 'Ishita Verma', 'ishita.verma@nexora.example', '9200000001'),
(2, 1, 'Arjun Pillai', 'arjun.pillai@nexora.example', '9200000002'),
(3, 2, 'Neel Joshi', 'neel.joshi@brightpath.example', '9200000003'),
(4, 3, 'Tara Menon', 'tara.menon@greengrid.example', '9200000004'),
(5, 4, 'Dev Malhotra', 'dev.malhotra@marketnest.example', '9200000005');

INSERT INTO JOB (Job_ID, Company_ID, Recruiter_ID, Job_Title, Job_Type, Description, Location, Minimum_CGPA, Application_Deadline, Salary, Status) VALUES
(1, 1, 1, 'Python Developer Intern', 'Internship', 'Assist with backend development and testing.', 'Bengaluru', 7.50, '2026-10-20', 30000.00, 'Open'),
(2, 1, 2, 'Java Software Intern', 'Internship', 'Develop and test Java service modules.', 'Bengaluru', 7.00, '2026-10-25', 28000.00, 'Open'),
(3, 2, 3, 'Data Analyst Intern', 'Internship', 'Prepare reports and analyze business datasets.', 'Pune', 8.00, '2026-10-18', 32000.00, 'Open'),
(4, 2, 3, 'SQL Reporting Intern', 'Internship', 'Create SQL reports for internal teams.', 'Pune', 7.00, '2026-10-28', 26000.00, 'Open'),
(5, 3, 4, 'Cloud Support Trainee', 'Full-time', 'Support cloud environment monitoring and documentation.', 'Hyderabad', 8.50, '2026-11-05', 45000.00, 'Open'),
(6, 3, 4, 'C++ Systems Intern', 'Internship', 'Assist with systems programming tasks.', 'Hyderabad', 6.50, '2026-03-25', 29000.00, 'Closed'),
(7, 4, 5, 'Digital Marketing Intern', 'Internship', 'Support campaign planning and performance tracking.', 'Mumbai', 7.00, '2026-11-10', 24000.00, 'Open'),
(8, 4, 5, 'Content Strategy Intern', 'Internship', 'Prepare content calendars and audience reports.', 'Mumbai', 8.00, '2026-11-15', 25000.00, 'Open');

INSERT INTO JOB_SKILL (Job_ID, Skill_ID) VALUES
(1, 1), (1, 3),
(2, 2), (2, 3),
(3, 1), (3, 4), (3, 3),
(4, 3),
(5, 10), (5, 3),
(6, 9), (6, 2),
(7, 7), (7, 8),
(8, 7), (8, 5);

INSERT INTO APPLICATION (Application_ID, Student_ID, Job_ID, Application_Date, Status) VALUES
(1, 1, 1, '2026-02-10', 'Selected'),
(2, 1, 3, '2026-02-11', 'Applied'),
(3, 2, 1, '2026-02-12', 'Applied'),
(4, 2, 3, '2026-02-13', 'Shortlisted'),
(5, 3, 2, '2026-02-14', 'Applied'),
(6, 4, 4, '2026-02-15', 'Rejected'),
(7, 5, 6, '2026-02-16', 'Applied'),
(8, 6, 7, '2026-02-17', 'Selected'),
(9, 7, 6, '2026-02-18', 'Shortlisted'),
(10, 8, 5, '2026-02-19', 'Applied');

INSERT INTO INTERVIEW (Interview_ID, Application_ID, Interview_Date, Interview_Time, Mode, Interview_Status, Remarks) VALUES
(1, 1, '2026-02-20', '10:00:00', 'Online', 'Scheduled', 'Technical discussion'),
(2, 1, '2026-02-21', '11:30:00', 'Online', 'Completed', 'Strong programming fundamentals'),
(3, 4, '2026-02-22', '14:00:00', 'In-person', 'Scheduled', 'Bring project portfolio'),
(4, 8, '2026-02-23', '15:30:00', 'Online', 'Completed', 'Marketing case discussion'),
(5, 9, '2026-02-24', '09:30:00', 'In-person', 'Scheduled', 'Systems problem-solving round');

INSERT INTO OFFER (Offer_ID, Application_ID, Offer_Date, Job_Title, Salary, Joining_Date, Offer_Status) VALUES
(1, 1, '2026-03-01', 'Python Developer Intern', 30000.00, '2026-06-01', 'Accepted'),
(2, 8, '2026-03-02', 'Digital Marketing Intern', 24000.00, '2026-06-05', 'Accepted'),
(3, 9, '2026-03-03', 'C++ Systems Intern', 29000.00, '2026-06-10', 'Pending');
