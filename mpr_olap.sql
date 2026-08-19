CREATE DATABASE IF NOT EXISTS mini_project_olap;
use mini_project_olap;
-- 2. Move your dimension and fact tables into the new OLAP database
RENAME TABLE mini_project.dim_employee TO mini_project_olap.dim_employee;
RENAME TABLE mini_project.dim_department TO mini_project_olap.dim_department;
RENAME TABLE mini_project.dim_project TO mini_project_olap.dim_project;
RENAME TABLE mini_project.dim_date TO mini_project_olap.dim_date;
RENAME TABLE mini_project.fact_performancereviews TO mini_project_olap.fact_performancereviews;

select * from fact_performancereviews;
select * from dim_employee;
select * from dim_date;
select * from dim_project;
select * from dim_department;
show tables;
select count(*) from dim_date;

USE mini_project_olap;

DROP PROCEDURE IF EXISTS sp_load_dimensions;

DELIMITER //

CREATE PROCEDURE sp_load_dimensions()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- A. Dim_Department
    INSERT IGNORE INTO Dim_Department (DepartmentID, DepartmentName)
    SELECT DepartmentID, DepartmentName FROM mini_project.Departments;

    -- B. Dim_Project (Includes Fallback record)
    INSERT IGNORE INTO Dim_Project (ProjectSK, ProjectID, ProjectName, Status)
    VALUES (1, 0, 'Unassigned Project', 'N/A');

    INSERT IGNORE INTO Dim_Project (ProjectID, ProjectName, Status)
    SELECT ProjectID, ProjectName, 'Active' FROM mini_project.Projects;

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
    JOIN mini_project.Employees e ON de.EmployeeID = e.EmployeeID
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
    FROM mini_project.Employees e
    LEFT JOIN Dim_Employee de ON e.EmployeeID = de.EmployeeID AND de.IsCurrent = 1
    WHERE de.EmployeeSK IS NULL;

    COMMIT;
END //

DELIMITER ;


USE mini_project_olap;

DROP PROCEDURE IF EXISTS sp_load_fact_performance;

DELIMITER //

CREATE PROCEDURE sp_load_fact_performance()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

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
        FROM mini_project.Assignments
        GROUP BY EmployeeID
    ),
    DeduplicatedReviews AS (
        SELECT 
            pr.*,
            ROW_NUMBER() OVER (
                PARTITION BY pr.EmployeeID, pr.ReviewDate 
                ORDER BY pr.ReviewID DESC
            ) AS RowSeq
        FROM mini_project.performancereviews pr
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
    JOIN mini_project.Employees emp 
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

    COMMIT;
END //

DELIMITER ;

DELIMITER //

CREATE PROCEDURE sp_run_master_etl()
BEGIN
    CALL sp_load_dimensions();
    CALL sp_load_fact_performance();
END //

DELIMITER ;

CREATE TABLE IF NOT EXISTS ETL_Execution_Log (
    LogID INT PRIMARY KEY AUTO_INCREMENT,
    ProcedureName VARCHAR(100) NOT NULL,
    TargetTable VARCHAR(100) NOT NULL,
    RowsProcessed INT DEFAULT 0,
    Status VARCHAR(20) NOT NULL,
    ErrorMessage TEXT NULL,
    ExecutionTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CALL sp_run_master_etl();

DROP TABLE IF EXISTS mini_project_olap.etl_execution_log;
DROP TABLE IF EXISTS mini_project.etl_execution_log;