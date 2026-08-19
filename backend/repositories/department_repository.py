from backend.database.db_manager import (
    DatabaseConnection
)

from backend.exceptions import (
    DatabaseException
)

from backend.utils.logger import (
    get_logger
)


logger = get_logger(__name__)


class DepartmentRepository:

    def __init__(self):

        self.db = DatabaseConnection()


    def get_all(self):

        query = """
            SELECT
                DepartmentID,
                DepartmentName
            FROM MINI_PROJECT.Departments
            ORDER BY DepartmentID
        """

        cursor = None

        try:

            cursor = self.db.get_cursor(
                "oltp"
            )

            cursor.execute(
                query
            )

            return cursor.fetchall()

        except Exception as e:

            logger.exception(
                "Failed to fetch departments."
            )

            raise DatabaseException(
                f"Failed to fetch departments: {e}"
            )

        finally:

            if cursor:

                cursor.close()




    def get_by_id(
        self,
        department_id
    ):

        query = """
            SELECT
                DepartmentID,
                DepartmentName
            FROM MINI_PROJECT.Departments
            WHERE DepartmentID = %s
        """

        cursor = None

        try:

            department_id = int(
                department_id
            )

            cursor = self.db.get_cursor(
                "oltp"
            )

            cursor.execute(
                query,
                (
                    department_id,
                )
            )

            return cursor.fetchone()

        except ValueError:

            raise ValueError(
                "Department ID must be an integer."
            )

        except Exception as e:

            logger.exception(
                "Failed to fetch department."
            )

            raise DatabaseException(
                f"Failed to fetch department: {e}"
            )

        finally:

            if cursor:

                cursor.close()



    def get_by_name(
        self,
        department_name
    ):

        query = """
            SELECT
                DepartmentID,
                DepartmentName
            FROM MINI_PROJECT.Departments
            WHERE DepartmentName = %s
        """

        cursor = None

        try:

            cursor = self.db.get_cursor(
                "oltp"
            )

            cursor.execute(
                query,
                (
                    department_name,
                )
            )

            return cursor.fetchone()

        except Exception as e:

            logger.exception(
                "Failed to find department."
            )

            raise DatabaseException(
                f"Failed to find department: {e}"
            )

        finally:

            if cursor:

                cursor.close()


  

    def extract_department_id(
        self,
        department
    ):

        if department is None:

            return None

    
        if isinstance(
            department,
            (tuple, list)
        ):

            return int(
                department[0]
            )

       

        if isinstance(
            department,
            dict
        ):

            value = (
                department.get(
                    "DepartmentID"
                )
            )

            if value is None:

                value = (
                    department.get(
                        "department_id"
                    )
                )

            if value is not None:

                return int(value)

        return None


  

    def create(
        self,
        department_name
    ):

        query = """
            INSERT INTO MINI_PROJECT.Departments
            (
                DepartmentName
            )
            VALUES
            (
                %s
            )
        """

        cursor = None

        try:

            cursor = self.db.get_cursor(
                "oltp"
            )

            cursor.execute(
                query,
                (
                    department_name,
                )
            )

            self.db.commit(
                "oltp"
            )

            return cursor.lastrowid

        except Exception as e:

            self.db.rollback(
                "oltp"
            )

            logger.exception(
                "Failed to create department."
            )

            

            if getattr(
                e,
                "errno",
                None
            ) == 1062:

                raise DatabaseException(
                    "Department already exists."
                )

            raise DatabaseException(
                f"Failed to create department: {e}"
            )

        finally:

            if cursor:

                cursor.close()




    def update(
        self,
        department_id,
        department_name
    ):

        query = """
            UPDATE MINI_PROJECT.Departments
            SET
                DepartmentName = %s
            WHERE DepartmentID = %s
        """

        cursor = None

        try:

            department_id = int(
                department_id
            )

            cursor = self.db.get_cursor(
                "oltp"
            )

            cursor.execute(
                query,
                (
                    department_name,
                    department_id
                )
            )

            self.db.commit(
                "oltp"
            )

            return cursor.rowcount

        except ValueError:

            raise ValueError(
                "Department ID must be an integer."
            )

        except Exception as e:

            self.db.rollback(
                "oltp"
            )

            logger.exception(
                "Failed to update department."
            )

            if getattr(
                e,
                "errno",
                None
            ) == 1062:

                raise DatabaseException(
                    "Another department with "
                    "this name already exists."
                )

            raise DatabaseException(
                f"Failed to update department: {e}"
            )

        finally:

            if cursor:

                cursor.close()



    