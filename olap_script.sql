CREATE TABLE IF NOT EXISTS Dim_Employee (
    EmployeeSK INT PRIMARY KEY AUTO_INCREMENT,
    EmployeeID INT NOT NULL,
    Age INT,
    Gender VARCHAR(20),
    MaritalStatus VARCHAR(20),
    JobRole VARCHAR(100),
    JobLevel INT,
    MonthlyIncome DECIMAL(10,2),
    PercentSalaryHike INT,
    OverTime VARCHAR(10),
    BusinessTravel VARCHAR(50),
    Education INT,
    EducationField VARCHAR(100),
    Attrition VARCHAR(5),
    IsActive BOOLEAN,
    EffectiveDate DATE NOT NULL,
    ExpirationDate DATE NULL,
    IsCurrent BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS Dim_Department (
    DepartmentSK INT PRIMARY KEY AUTO_INCREMENT,
    DepartmentID INT NOT NULL,
    DepartmentName VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS Dim_Project (
    ProjectSK INT PRIMARY KEY AUTO_INCREMENT,
    ProjectID INT NOT NULL,
    ProjectName VARCHAR(150) NOT NULL,
    Status VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS Dim_Date (
    DateKey INT PRIMARY KEY,
    FullDate DATE NOT NULL,
    Year INT NOT NULL,
    Quarter INT NOT NULL,
    Month INT NOT NULL,
    MonthName VARCHAR(20) NOT NULL,
    DayOfWeek VARCHAR(20) NOT NULL,
    IsWeekend BOOLEAN NOT NULL
);

-- DROP TABLE FACT_PERFORMANCEREVIEWS;
-- DROP TABLE DIM_DATE;
-- DROP TABLE DIM_PROJECT;
-- DROP TABLE DIM_DEPARTMENT;
-- DROP TABLE DIM_EMPLOYEE;
CREATE TABLE IF NOT EXISTS Fact_PerformanceReviews (
    PerformanceReviewSK BIGINT PRIMARY KEY AUTO_INCREMENT,
    EmployeeSK INT NOT NULL,
    DepartmentSK INT NOT NULL,
    ProjectSK INT NOT NULL,
    ReviewDateKey INT NOT NULL,
    ReviewID INT NOT NULL,
    PerformanceRating INT,
    EnvironmentSatisfaction INT,
    JobInvolvement INT,
    JobSatisfaction INT,
    RelationshipSatisfaction INT,
    WorkLifeBalance INT,
    TrainingTimesLastYear INT,
    YearsAtCompany INT,
    YearsInCurrentRole INT,
    YearsSinceLastPromotion INT,
    AllocatedHours DECIMAL(8,2),
    ActiveProjectCount INT,
    FOREIGN KEY (EmployeeSK) REFERENCES Dim_Employee(EmployeeSK),
    FOREIGN KEY (DepartmentSK) REFERENCES Dim_Department(DepartmentSK),
    FOREIGN KEY (ProjectSK) REFERENCES Dim_Project(ProjectSK),
    FOREIGN KEY (ReviewDateKey) REFERENCES Dim_Date(DateKey)
);

-- Audit log table for ETL execution metrics
CREATE TABLE IF NOT EXISTS ETL_Execution_Log (
    LogID INT PRIMARY KEY AUTO_INCREMENT,
    ProcedureName VARCHAR(100) NOT NULL,
    TargetTable VARCHAR(100) NOT NULL,
    RowsProcessed INT DEFAULT 0,
    Status VARCHAR(20) NOT NULL,
    ErrorMessage TEXT NULL,
    ExecutionTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


DELIMITER //

CREATE PROCEDURE sp_load_dimensions()
BEGIN
    DECLARE rows_affected INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        INSERT INTO ETL_Execution_Log (ProcedureName, TargetTable, Status, ErrorMessage)
        VALUES ('sp_load_dimensions', 'Dimensions', 'FAILED', 'Error executing dimension population pipeline.');
        RESIGNAL;
    END;

    START TRANSACTION;

    -- A. Dim_Department
    INSERT IGNORE INTO Dim_Department (DepartmentID, DepartmentName)
    SELECT DepartmentID, DepartmentName FROM Departments;

    -- B. Dim_Project (Includes Fallback record)
    INSERT IGNORE INTO Dim_Project (ProjectSK, ProjectID, ProjectName, Status)
    VALUES (1, 0, 'Unassigned Project', 'N/A');

    INSERT IGNORE INTO Dim_Project (ProjectID, ProjectName, Status)
    SELECT ProjectID, ProjectName, Status FROM Projects;

    -- C. Dim_Date (Generates 2010 to 2030)
    SET SESSION cte_max_recursion_depth = 10000;

    INSERT IGNORE INTO Dim_Date (DateKey, FullDate, Year, Quarter, Month, MonthName, DayOfWeek, IsWeekend)
    WITH RECURSIVE seq AS (
        SELECT CAST('2010-01-01' AS DATE) AS d
        UNION ALL
        SELECT d + INTERVAL 1 DAY 
        FROM seq 
        WHERE d < '2030-12-31'
    )
    SELECT 
        CAST(DATE_FORMAT(d, '%Y%m%d') AS UNSIGNED) AS DateKey,
        d AS FullDate,
        YEAR(d) AS Year,
        QUARTER(d) AS Quarter,
        MONTH(d) AS Month,
        MONTHNAME(d) AS MonthName,
        DAYNAME(d) AS DayOfWeek,
        IF(WEEKDAY(d) IN (5, 6), 1, 0) AS IsWeekend
    FROM seq;

    -- D. Dim_Employee SCD Type 2: Expire existing records when attributes change
    UPDATE Dim_Employee de
    JOIN Employees e ON de.EmployeeID = e.EmployeeID
    SET de.ExpirationDate = CURRENT_DATE(),
        de.IsCurrent = 0
    WHERE de.IsCurrent = 1 
      AND (
          de.JobRole <> e.JobRole OR 
          de.MonthlyIncome <> e.MonthlyIncome OR 
          de.JobLevel <> e.JobLevel OR
          de.IsActive <> e.IsActive
      );

    -- E. Dim_Employee SCD Type 2: Insert NEW versions for updated or missing employees
    INSERT INTO Dim_Employee (
        EmployeeID, Age, Gender, MaritalStatus, JobRole, JobLevel, MonthlyIncome,
        PercentSalaryHike, OverTime, BusinessTravel, Education, EducationField,
        Attrition, IsActive, EffectiveDate, ExpirationDate, IsCurrent
    )
    SELECT 
        e.EmployeeID, e.Age, e.Gender, e.MaritalStatus, e.JobRole, e.JobLevel, e.MonthlyIncome,
        e.PercentSalaryHike, IF(e.OverTime = 1, 'Yes', 'No'), e.BusinessTravel, e.Education, e.EducationField,
        IF(e.IsActive = 1, 'No', 'Yes'), e.IsActive,
        CURRENT_DATE() AS EffectiveDate, NULL AS ExpirationDate, 1 AS IsCurrent
    FROM Employees e
    LEFT JOIN Dim_Employee de ON e.EmployeeID = de.EmployeeID AND de.IsCurrent = 1
    WHERE de.EmployeeSK IS NULL;

    SET rows_affected = ROW_COUNT();

    INSERT INTO ETL_Execution_Log (ProcedureName, TargetTable, RowsProcessed, Status)
    VALUES ('sp_load_dimensions', 'Dim_Employee & Dimensions', rows_affected, 'SUCCESS');

    COMMIT;
END //

DELIMITER ;


DELIMITER //

CREATE PROCEDURE sp_load_fact_performance()
BEGIN
    DECLARE rows_affected INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        INSERT INTO ETL_Execution_Log (ProcedureName, TargetTable, Status, ErrorMessage)
        VALUES ('sp_load_fact_performance', 'Fact_PerformanceReviews', 'FAILED', 'Error inserting into Fact table.');
        RESIGNAL;
    END;

    START TRANSACTION;

    -- CTE 1: Aggregate multiple project allocations per employee
    -- CTE 2: Deduplicate multiple evaluation records using ROW_NUMBER()
    INSERT INTO Fact_PerformanceReviews (
        EmployeeSK, DepartmentSK, ProjectSK, ReviewDateKey, ReviewID,
        PerformanceRating, EnvironmentSatisfaction, JobInvolvement, JobSatisfaction,
        RelationshipSatisfaction, WorkLifeBalance, TrainingTimesLastYear,
        YearsAtCompany, YearsInCurrentRole, YearsSinceLastPromotion, AllocatedHours, ActiveProjectCount
    )
    WITH EmployeeAssignmentsAgg AS (
        SELECT 
            EmployeeID,
            MAX(ProjectID) AS PrimaryProjectID,
            SUM(AllocationPercentage) AS TotalAllocationPercentage,
            COUNT(DISTINCT ProjectID) AS TotalProjects
        FROM Assignments
        GROUP BY EmployeeID
    ),
    DeduplicatedReviews AS (
        SELECT 
            pr.*,
            ROW_NUMBER() OVER (
                PARTITION BY pr.EmployeeID, pr.ReviewDate 
                ORDER BY pr.ReviewID DESC
            ) AS RowSeq
        FROM PerformanceReviews pr
    )
    SELECT 
        dim_e.EmployeeSK,
        dim_d.DepartmentSK,
        COALESCE(dim_p.ProjectSK, 1) AS ProjectSK,
        COALESCE(dim_date.DateKey, 20240101) AS ReviewDateKey,
        dr.ReviewID,
        dr.PerformanceRating,
        emp.EnvironmentSatisfaction,
        emp.JobInvolvement,
        emp.JobSatisfaction,
        emp.RelationshipSatisfaction,
        emp.WorkLifeBalance,
        emp.TrainingTimesLastYear,
        emp.YearsAtCompany,
        emp.YearsInCurrentRole,
        emp.YearsSinceLastPromotion,
        ROUND((COALESCE(agg.TotalAllocationPercentage, 100.0) / 100.0) * 40.0, 2) AS AllocatedHours,
        COALESCE(agg.TotalProjects, 1) AS ActiveProjectCount
    FROM DeduplicatedReviews dr
    JOIN Employees emp 
        ON dr.EmployeeID = emp.EmployeeID
    JOIN Dim_Employee dim_e 
        ON emp.EmployeeID = dim_e.EmployeeID 
       AND dim_e.IsCurrent = 1
    JOIN Dim_Department dim_d 
        ON emp.DepartmentID = dim_d.DepartmentID
    LEFT JOIN EmployeeAssignmentsAgg agg 
        ON emp.EmployeeID = agg.EmployeeID
    LEFT JOIN Dim_Project dim_p 
        ON agg.PrimaryProjectID = dim_p.ProjectID
    LEFT JOIN Dim_Date dim_date 
        ON CAST(DATE_FORMAT(dr.ReviewDate, '%Y%m%d') AS UNSIGNED) = dim_date.DateKey
    WHERE dr.RowSeq = 1
      AND NOT EXISTS (
          SELECT 1 FROM Fact_PerformanceReviews f WHERE f.ReviewID = dr.ReviewID
      );

    SET rows_affected = ROW_COUNT();

    INSERT INTO ETL_Execution_Log (ProcedureName, TargetTable, RowsProcessed, Status)
    VALUES ('sp_load_fact_performance', 'Fact_PerformanceReviews', rows_affected, 'SUCCESS');

    COMMIT;
END //

DELIMITER ;


DROP PROCEDURE IF EXISTS sp_run_master_etl;

DELIMITER //

CREATE PROCEDURE sp_run_master_etl()
BEGIN
    CALL sp_load_dimensions();
    CALL sp_load_fact_performance();
END //

DELIMITER ;



-- Execute master ETL procedure
CALL sp_run_master_etl();

-- View execution log report
SELECT * FROM ETL_Execution_Log ORDER BY ExecutionTime DESC;

-- Audit record counts across OLTP and OLAP layers
SELECT 
    (SELECT COUNT(*) FROM mini_project.PerformanceReviews) AS OLTP_Review_Count,
    (SELECT COUNT(*) FROM mini_project.Fact_PerformanceReviews) AS OLAP_Fact_Count,
    (SELECT COUNT(*) FROM mini_project.Dim_Employee WHERE IsCurrent = 1) AS Active_Dim_Employees,
    (SELECT COUNT(*) FROM mini_project.Dim_Employee) AS Total_Dim_Employee_Versions;
  