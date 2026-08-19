from backend.database.db_manager import DatabaseConnection
from backend.exceptions import DatabaseException
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class AssignmentRepository:

    def __init__(self):

        self.db = DatabaseConnection()

    def get_all(self):

        query = """
            SELECT
                AssignmentID,
                EmployeeID,
                ProjectID,
                RoleInProject,
                AllocationPercentage,
                StartDate,
                EndDate
            FROM Assignments
            ORDER BY AssignmentID
        """

        cursor = None

        try:

            cursor = self.db.get_cursor("oltp")

            cursor.execute(query)

            return cursor.fetchall()

        except Exception as e:

            logger.exception(
                "Failed to fetch assignments."
            )

            raise DatabaseException(
                f"Failed to fetch assignments: {e}"
            )

        finally:

            if cursor:

                cursor.close()
    def get_by_id(
        self,
        assignment_id
    ):

        query = """
            SELECT
                AssignmentID,
                EmployeeID,
                ProjectID,
                RoleInProject,
                AllocationPercentage,
                StartDate,
                EndDate
            FROM Assignments
            WHERE AssignmentID = %s
        """

        cursor = None

        try:

            cursor = self.db.get_cursor("oltp")

            cursor.execute(
                query,
                (assignment_id,)
            )

            return cursor.fetchone()

        except Exception as e:

            logger.exception(
                "Failed to fetch assignment."
            )

            raise DatabaseException(
                f"Failed to fetch assignment: {e}"
            )

        finally:

            if cursor:

                cursor.close()


    def get_employee_allocation(
        self,
        employee_id
    ):

        query = """
            SELECT
                COALESCE(
                    SUM(AllocationPercentage),
                    0
                ) AS TotalAllocation
            FROM Assignments
            WHERE EmployeeID = %s
              AND (
                    EndDate IS NULL
                    OR EndDate >= CURDATE()
                  )
        """

        cursor = None

        try:

            cursor = self.db.get_cursor("oltp")

            cursor.execute(
                query,
                (employee_id,)
            )

            return cursor.fetchone()

        except Exception as e:

            logger.exception(
                "Failed to calculate employee allocation."
            )

            raise DatabaseException(
                f"Failed to calculate allocation: {e}"
            )

        finally:

            if cursor:

                cursor.close()

    def create(
        self,
        assignment
    ):

        query = """
            INSERT INTO Assignments
            (
                EmployeeID,
                ProjectID,
                RoleInProject,
                AllocationPercentage,
                StartDate,
                EndDate
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        values = (
            assignment.employee_id,
            assignment.project_id,
            assignment.role_in_project,
            assignment.allocation_percentage,
            assignment.start_date,
            assignment.end_date
        )

        cursor = None

        try:

            connection = self.db.connect("oltp")

            cursor = connection.cursor()

            cursor.execute(
                query,
                values
            )

            self.db.commit("oltp")

            return cursor.lastrowid

        except Exception as e:

            self.db.rollback("oltp")

            logger.exception(
                "Failed to create assignment."
            )

            raise DatabaseException(
                f"Failed to create assignment: {e}"
            )

        finally:

            if cursor:

                cursor.close()

   

    def update(
        self,
        assignment_id,
        assignment
    ):

        query = """
            UPDATE Assignments
            SET
                EmployeeID = %s,
                ProjectID = %s,
                RoleInProject = %s,
                AllocationPercentage = %s,
                StartDate = %s,
                EndDate = %s
            WHERE AssignmentID = %s
        """

        values = (
            assignment.employee_id,
            assignment.project_id,
            assignment.role_in_project,
            assignment.allocation_percentage,
            assignment.start_date,
            assignment.end_date,
            assignment_id
        )

        cursor = None

        try:

            connection = self.db.connect("oltp")

            cursor = connection.cursor()

            cursor.execute(
                query,
                values
            )

            self.db.commit("oltp")

            return cursor.rowcount

        except Exception as e:

            self.db.rollback("oltp")

            logger.exception(
                "Failed to update assignment."
            )

            raise DatabaseException(
                f"Failed to update assignment: {e}"
            )

        finally:

            if cursor:

                cursor.close()

    
    