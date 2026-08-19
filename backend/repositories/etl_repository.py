from backend.database.db_manager import DatabaseConnection
from backend.exceptions import DatabaseException
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class ETLRepository:
    """
    Repository responsible for OLAP / ETL database operations.

    Responsibilities:
        - SCD Type 2 operations
        - Dimension ETL
        - Fact ETL
        - ETL execution logs
        - Employee history queries
    """

    def __init__(self):

        self.db = DatabaseConnection()

        logger.info(
            "ETLRepository initialized."
        )



    def get_current_employee_dimension(
        self,
        employee_id
    ):

        query = """
            SELECT
                EmployeeSK,
                EmployeeID,
                DepartmentID,
                Age,
                Gender,
                MaritalStatus,
                JobRole,
                JobLevel,
                MonthlyIncome,
                PercentSalaryHike,
                OverTime,
                BusinessTravel,
                Education,
                EducationField,
                Attrition,
                IsActive,
                EffectiveDate,
                ExpirationDate,
                IsCurrent
            FROM Dim_Employee
            WHERE EmployeeID = %s
              AND IsCurrent = 1
            LIMIT 1
        """

        cursor = None

        try:

            logger.info(
                "Fetching current Dim_Employee record "
                "for EmployeeID=%s.",
                employee_id
            )

            cursor = self.db.get_cursor("olap")

            cursor.execute(
                query,
                (employee_id,)
            )

            return cursor.fetchone()

        except Exception as e:

            logger.exception(
                "Failed to get current dimension "
                "for employee %s.",
                employee_id
            )

            raise DatabaseException(
                f"Failed to get current employee dimension: {e}"
            )

        finally:

            if cursor:
                cursor.close()



    def expire_employee_dimension(
        self,
        employee_id
    ):
        """
        Expire the current Dim_Employee record.

        NOTE:
        This method is kept as a standalone repository operation.

        For a complete SCD Type 2 update, prefer:
            apply_employee_scd_type2()
        """

        query = """
            UPDATE Dim_Employee
            SET
                ExpirationDate = CURRENT_DATE() - INTERVAL 1 DAY,
                IsCurrent = 0
            WHERE EmployeeID = %s
              AND IsCurrent = 1
        """

        cursor = None

        try:

            logger.info(
                "Expiring current Dim_Employee record "
                "for EmployeeID=%s.",
                employee_id
            )

            connection = self.db.connect("olap")

            cursor = connection.cursor()

            cursor.execute(
                query,
                (employee_id,)
            )

            rows_updated = cursor.rowcount

            self.db.commit("olap")

            logger.info(
                "Expired %s Dim_Employee record(s) "
                "for EmployeeID=%s.",
                rows_updated,
                employee_id
            )

            return rows_updated

        except Exception as e:

            self.db.rollback("olap")

            logger.exception(
                "Failed to expire Dim_Employee record "
                "for EmployeeID=%s.",
                employee_id
            )

            raise DatabaseException(
                f"Failed to expire employee dimension: {e}"
            )

        finally:

            if cursor:
                cursor.close()

    
    def insert_employee_dimension(
        self,
        employee
    ):
        """
        Insert a new current Dim_Employee version.

        Used for:
            - Initial employee creation
            - Explicit insertion of a dimension version

        SCD update itself should normally use:
            apply_employee_scd_type2()
        """

        query = """
            INSERT INTO Dim_Employee
            (
                EmployeeID,
                DepartmentID,
                Age,
                Gender,
                MaritalStatus,
                JobRole,
                JobLevel,
                MonthlyIncome,
                PercentSalaryHike,
                OverTime,
                BusinessTravel,
                Education,
                EducationField,
                Attrition,
                IsActive,
                EffectiveDate,
                ExpirationDate,
                IsCurrent
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                CURRENT_DATE(),
                NULL,
                1
            )
        """

        values = (
            employee["EmployeeID"],
            employee["DepartmentID"],
            employee["Age"],
            employee["Gender"],
            employee["MaritalStatus"],
            employee["JobRole"],
            employee["JobLevel"],
            employee["MonthlyIncome"],
            employee["PercentSalaryHike"],
            employee["OverTime"],
            employee["BusinessTravel"],
            employee["Education"],
            employee["EducationField"],
            "No" if employee["IsActive"] else "Yes",
            employee["IsActive"]
        )

        cursor = None

        try:

            logger.info(
                "Inserting Dim_Employee version "
                "for EmployeeID=%s.",
                employee["EmployeeID"]
            )

            connection = self.db.connect("olap")

            cursor = connection.cursor()

            cursor.execute(
                query,
                values
            )

            employee_sk = cursor.lastrowid

            self.db.commit("olap")

            logger.info(
                "Inserted Dim_Employee version. "
                "EmployeeID=%s, EmployeeSK=%s.",
                employee["EmployeeID"],
                employee_sk
            )

            return employee_sk

        except Exception as e:

            self.db.rollback("olap")

            logger.exception(
                "Failed to insert dimension version "
                "for EmployeeID=%s.",
                employee["EmployeeID"]
            )

            raise DatabaseException(
                f"Failed to insert employee dimension: {e}"
            )

        finally:

            if cursor:
                cursor.close()

    

    def apply_employee_scd_type2(
        self,
        employee
    ):
        

        connection = None
        cursor = None

        employee_id = employee["EmployeeID"]

        expire_query = """
            UPDATE Dim_Employee
            SET
                ExpirationDate = CURRENT_DATE() - INTERVAL 1 DAY,
                IsCurrent = 0
            WHERE EmployeeID = %s
              AND IsCurrent = 1
        """

        insert_query = """
            INSERT INTO Dim_Employee
            (
                EmployeeID,
                DepartmentID,
                Age,
                Gender,
                MaritalStatus,
                JobRole,
                JobLevel,
                MonthlyIncome,
                PercentSalaryHike,
                OverTime,
                BusinessTravel,
                Education,
                EducationField,
                Attrition,
                IsActive,
                EffectiveDate,
                ExpirationDate,
                IsCurrent
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                CURRENT_DATE(),
                NULL,
                1
            )
        """

        values = (
            employee["EmployeeID"],
            employee["DepartmentID"],
            employee["Age"],
            employee["Gender"],
            employee["MaritalStatus"],
            employee["JobRole"],
            employee["JobLevel"],
            employee["MonthlyIncome"],
            employee["PercentSalaryHike"],
            employee["OverTime"],
            employee["BusinessTravel"],
            employee["Education"],
            employee["EducationField"],
            "No" if employee["IsActive"] else "Yes",
            employee["IsActive"]
        )

        try:

            logger.info(
                "Starting SCD Type 2 for EmployeeID=%s.",
                employee_id
            )

            connection = self.db.connect("olap")

            cursor = connection.cursor()

          

            cursor.execute(
                expire_query,
                (employee_id,)
            )

            expired_rows = cursor.rowcount

            logger.info(
                "Expired %s current dimension row(s) "
                "for EmployeeID=%s.",
                expired_rows,
                employee_id
            )

            if expired_rows == 0:

                raise DatabaseException(
                    "No current Dim_Employee record exists for "
                    f"EmployeeID {employee_id}."
                )

          

            cursor.execute(
                insert_query,
                values
            )

            new_employee_sk = cursor.lastrowid

            logger.info(
                "Inserted new SCD Type 2 version. "
                "EmployeeID=%s, EmployeeSK=%s.",
                employee_id,
                new_employee_sk
            )

            

            connection.commit()

            logger.info(
                "SCD Type 2 completed successfully. "
                "EmployeeID=%s, EmployeeSK=%s.",
                employee_id,
                new_employee_sk
            )

            return new_employee_sk

        except DatabaseException:

            if connection:

                connection.rollback()

            logger.exception(
                "SCD Type 2 failed for EmployeeID=%s.",
                employee_id
            )

            raise

        except Exception as e:

            if connection:

                connection.rollback()

            logger.exception(
                "SCD Type 2 failed for EmployeeID=%s.",
                employee_id
            )

            raise DatabaseException(
                f"SCD Type 2 failed: {e}"
            )

        finally:

            if cursor:

                cursor.close()

   

    def get_employee_history(
        self,
        employee_id
    ):

        query = """
            SELECT
                EmployeeSK,
                EmployeeID,
                DepartmentID,
                Age,
                Gender,
                MaritalStatus,
                JobRole,
                JobLevel,
                MonthlyIncome,
                PercentSalaryHike,
                OverTime,
                BusinessTravel,
                Education,
                EducationField,
                Attrition,
                IsActive,
                EffectiveDate,
                ExpirationDate,
                IsCurrent
            FROM Dim_Employee
            WHERE EmployeeID = %s
            ORDER BY
                EffectiveDate ASC,
                EmployeeSK ASC
        """

        cursor = None

        try:

            logger.info(
                "Fetching SCD history "
                "for EmployeeID=%s.",
                employee_id
            )

            cursor = self.db.get_cursor("olap")

            cursor.execute(
                query,
                (employee_id,)
            )

            return cursor.fetchall()

        except Exception as e:

            logger.exception(
                "Failed to get SCD history "
                "for EmployeeID=%s.",
                employee_id
            )

            raise DatabaseException(
                f"Failed to get employee history: {e}"
            )

        finally:

            if cursor:

                cursor.close()

    

    def get_current_employee_dimensions(self):

        query = """
            SELECT
                EmployeeSK,
                EmployeeID,
                DepartmentID,
                Age,
                Gender,
                MaritalStatus,
                JobRole,
                JobLevel,
                MonthlyIncome,
                PercentSalaryHike,
                OverTime,
                BusinessTravel,
                Education,
                EducationField,
                Attrition,
                IsActive,
                EffectiveDate,
                ExpirationDate,
                IsCurrent
            FROM Dim_Employee
            WHERE IsCurrent = 1
            ORDER BY EmployeeID
        """

        cursor = None

        try:

            logger.info(
                "Fetching current employee dimensions."
            )

            cursor = self.db.get_cursor("olap")

            cursor.execute(query)

            return cursor.fetchall()

        except Exception as e:

            logger.exception(
                "Failed to get current employee dimensions."
            )

            raise DatabaseException(
                f"Failed to get current employee dimensions: {e}"
            )

        finally:

            if cursor:

                cursor.close()

  

    def run_dimensions(self):

        query = """
            CALL sp_load_dimensions()
        """

        cursor = None

        try:

            logger.info(
                "Starting dimension ETL."
            )

            connection = self.db.connect("oltp")

            cursor = connection.cursor()

            cursor.execute(query)

            while cursor.nextset():

                pass

            connection.commit()

            logger.info(
                "Dimension ETL completed successfully."
            )

            return True

        except Exception as e:

            self.db.rollback("oltp")

            logger.exception(
                "Dimension ETL failed."
            )

            raise DatabaseException(
                f"Dimension ETL failed: {e}"
            )

        finally:

            if cursor:

                cursor.close()

    

    def run_fact(self):

        query = """
            CALL sp_load_fact_performance()
        """

        cursor = None

        try:

            logger.info(
                "Starting fact ETL."
            )

            connection = self.db.connect("oltp")

            cursor = connection.cursor()

            cursor.execute(query)

            while cursor.nextset():

                pass

            connection.commit()

            logger.info(
                "Fact ETL completed successfully."
            )

            return True

        except Exception as e:

            self.db.rollback("oltp")

            logger.exception(
                "Fact ETL failed."
            )

            raise DatabaseException(
                f"Fact ETL failed: {e}"
            )

        finally:

            if cursor:

                cursor.close()

   

    def run_master_etl(self):

        query = """
            CALL sp_run_master_etl()
        """

        cursor = None

        try:

            logger.info(
                "Starting master ETL."
            )

            connection = self.db.connect("oltp")

            cursor = connection.cursor()

            cursor.execute(query)

            while cursor.nextset():

                pass

            connection.commit()

            logger.info(
                "Master ETL completed successfully."
            )

            return True

        except Exception as e:

            self.db.rollback("oltp")

            logger.exception(
                "Master ETL failed."
            )

            raise DatabaseException(
                f"Master ETL failed: {e}"
            )

        finally:

            if cursor:

                cursor.close()

 

    def get_execution_logs(self):

        query = """
            SELECT
                LogID,
                ProcedureName,
                TargetTable,
                RowsProcessed,
                Status,
                ErrorMessage,
                ExecutionTime
            FROM ETL_Execution_Log
            ORDER BY ExecutionTime DESC
        """

        cursor = None

        try:

            logger.info(
                "Fetching ETL execution logs."
            )

            cursor = self.db.get_cursor("olap")

            cursor.execute(query)

            return cursor.fetchall()

        except Exception as e:

            logger.exception(
                "Failed to get ETL execution logs."
            )

            raise DatabaseException(
                f"Failed to get ETL logs: {e}"
            )

        finally:

            if cursor:

                cursor.close()