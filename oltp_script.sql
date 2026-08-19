CREATE DATABASE IF NOT EXISTS MINI_PROJECT;
USE MINI_PROJECT;

-- 1. Departments Lookup Table
CREATE TABLE IF NOT EXISTS Departments (
    DepartmentID INT PRIMARY KEY AUTO_INCREMENT,
    DepartmentName VARCHAR(100) UNIQUE NOT NULL
);

-- 2. Projects Master Table
CREATE TABLE IF NOT EXISTS Projects (
    ProjectID INT PRIMARY KEY AUTO_INCREMENT,
    ProjectName VARCHAR(150) NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NULL,
    Status VARCHAR(50) NOT NULL DEFAULT 'Active'
);

-- 3. Employees Table
CREATE TABLE IF NOT EXISTS Employees (
    EmployeeID INT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Age INT,
    Gender VARCHAR(20),
    MaritalStatus VARCHAR(20),
    DepartmentID INT,
    JobRole VARCHAR(100),
    JobLevel INT,
    MonthlyIncome DECIMAL(10,2),
    DailyRate DECIMAL(10,2),
    HourlyRate DECIMAL(10,2),
    MonthlyRate DECIMAL(10,2),
    PercentSalaryHike INT,
    StockOptionLevel INT,
    OverTime BOOLEAN,
    BusinessTravel VARCHAR(50),
    DistanceFromHome INT,
    Education INT,
    EducationField VARCHAR(100),
    EnvironmentSatisfaction INT,
    JobInvolvement INT,
    JobSatisfaction INT,
    RelationshipSatisfaction INT,
    WorkLifeBalance INT,
    TotalWorkingYears INT,
    TrainingTimesLastYear INT,
    YearsAtCompany INT,
    YearsInCurrentRole INT,
    YearsSinceLastPromotion INT,
    YearsWithCurrManager INT,
    IsActive BOOLEAN NOT NULL,
    HireDate DATE NOT NULL,
    TerminationDate DATE NULL,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);

-- 4. Assignments Junction Table
CREATE TABLE IF NOT EXISTS Assignments (
    AssignmentID INT PRIMARY KEY AUTO_INCREMENT,
    EmployeeID INT NOT NULL,
    ProjectID INT NOT NULL,
    RoleInProject VARCHAR(100),
    AllocationPercentage DECIMAL(5,2),
    StartDate DATE NOT NULL,
    EndDate DATE DEFAULT NULL,
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
    FOREIGN KEY (ProjectID) REFERENCES Projects(ProjectID)
);

-- 5. PerformanceReviews Transaction Table
CREATE TABLE IF NOT EXISTS PerformanceReviews (
    ReviewID INT PRIMARY KEY AUTO_INCREMENT,
    EmployeeID INT NOT NULL,
    ReviewDate DATE NOT NULL,
    PerformanceRating INT NOT NULL,
    ReviewerID INT NULL,
    Comments TEXT NULL,
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
    FOREIGN KEY (ReviewerID) REFERENCES Employees(EmployeeID)
);


CREATE TABLE IF NOT EXISTS stg_employees (
    EmployeeID INT PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    Age INT,
    Gender VARCHAR(20),
    MaritalStatus VARCHAR(20),
    DepartmentName VARCHAR(100),
    JobRole VARCHAR(100),
    JobLevel INT,
    MonthlyIncome DECIMAL(10,2),
    DailyRate DECIMAL(10,2),
    HourlyRate DECIMAL(10,2),
    MonthlyRate DECIMAL(10,2),
    PercentSalaryHike INT,
    StockOptionLevel INT,
    OverTime INT,
    BusinessTravel VARCHAR(50),
    DistanceFromHome INT,
    Education INT,
    EducationField VARCHAR(100),
    EnvironmentSatisfaction INT,
    JobInvolvement INT,
    JobSatisfaction INT,
    RelationshipSatisfaction INT,
    WorkLifeBalance INT,
    TotalWorkingYears INT,
    TrainingTimesLastYear INT,
    YearsAtCompany INT,
    YearsInCurrentRole INT,
    YearsSinceLastPromotion INT,
    YearsWithCurrManager INT,
    IsActive INT,
    HireDate DATE,
    TerminationDate DATE DEFAULT NULL,
    LatestPerformanceRating INT,
    AssignedProjectName VARCHAR(150),
    ProjectAllocationPercentage DECIMAL(5,2),
    ActiveProjectCount INT
);

select * from stg_employees;
INSERT IGNORE INTO Departments (DepartmentName)
SELECT DISTINCT DepartmentName FROM stg_employees;

INSERT IGNORE INTO Projects (ProjectName, StartDate, Status)
SELECT DISTINCT AssignedProjectName, '2024-01-01', 'Active' 
FROM stg_employees;

INSERT IGNORE INTO Employees (
    EmployeeID, FirstName, LastName, Age, Gender, MaritalStatus, DepartmentID,
    JobRole, JobLevel, MonthlyIncome, DailyRate, HourlyRate, MonthlyRate,
    PercentSalaryHike, StockOptionLevel, OverTime, BusinessTravel, DistanceFromHome,
    Education, EducationField, EnvironmentSatisfaction, JobInvolvement, JobSatisfaction,
    RelationshipSatisfaction, WorkLifeBalance, TotalWorkingYears, TrainingTimesLastYear,
    YearsAtCompany, YearsInCurrentRole, YearsSinceLastPromotion, YearsWithCurrManager,
    IsActive, HireDate, TerminationDate
)
SELECT 
    s.EmployeeID, s.FirstName, s.LastName, s.Age, s.Gender, s.MaritalStatus, d.DepartmentID,
    s.JobRole, s.JobLevel, s.MonthlyIncome, s.DailyRate, s.HourlyRate, s.MonthlyRate,
    s.PercentSalaryHike, s.StockOptionLevel, s.OverTime, s.BusinessTravel, s.DistanceFromHome,
    s.Education, s.EducationField, s.EnvironmentSatisfaction, s.JobInvolvement, s.JobSatisfaction,
    s.RelationshipSatisfaction, s.WorkLifeBalance, s.TotalWorkingYears, s.TrainingTimesLastYear,
    s.YearsAtCompany, s.YearsInCurrentRole, s.YearsSinceLastPromotion, s.YearsWithCurrManager,
    s.IsActive, s.HireDate, s.TerminationDate
FROM stg_employees s
JOIN Departments d ON s.DepartmentName = d.DepartmentName;

INSERT IGNORE INTO Assignments (EmployeeID, ProjectID, RoleInProject, AllocationPercentage, StartDate)
SELECT 
    s.EmployeeID, p.ProjectID, CONCAT('Contributor (', s.JobRole, ')'),
    s.ProjectAllocationPercentage, s.HireDate
FROM stg_employees s
JOIN Projects p ON s.AssignedProjectName = p.ProjectName;

INSERT IGNORE INTO PerformanceReviews (EmployeeID, ReviewDate, PerformanceRating, Comments)
SELECT EmployeeID, HireDate, LatestPerformanceRating, 'Initial Evaluation'
FROM stg_employees;


select count(*) from employees;
select count(*) from departments;
select count(*) from assignments;
select count(*) from performancereviews;
select count(*) from projects;

-- Add Attrition column to staging table
ALTER TABLE stg_employees
ADD COLUMN attrition VARCHAR(10);

-- Clear staging table
TRUNCATE TABLE stg_employees;

-- Python connection script runs here to import data into stg_employees


-- Add Attrition column to Employees table
ALTER TABLE Employees
ADD COLUMN attrition VARCHAR(10);

-- Copy Attrition from staging to Employees
UPDATE Employees e
JOIN stg_employees s
    ON e.EmployeeID = s.EmployeeID
SET e.Attrition = s.Attrition;