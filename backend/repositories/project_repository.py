from backend.database.db_manager import DatabaseConnection
from backend.exceptions import DatabaseException
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class ProjectRepository:

    def __init__(self):

        self.db = DatabaseConnection()

    def get_all(self):

        query = """
            SELECT
                ProjectID,
                ProjectName,
                StartDate,
                EndDate,
                Status
            FROM Projects
            ORDER BY ProjectID
        """

        cursor = None

        try:

            cursor = self.db.get_cursor("oltp")

            cursor.execute(query)

            return cursor.fetchall()

        except Exception as e:

            logger.exception(
                "Failed to fetch projects."
            )

            raise DatabaseException(
                f"Failed to fetch projects: {e}"
            )

        finally:

            if cursor:
                cursor.close()

    def get_by_id(self, project_id):

        query = """
            SELECT
                ProjectID,
                ProjectName,
                StartDate,
                EndDate,
                Status
            FROM Projects
            WHERE ProjectID = %s
        """

        cursor = None

        try:

            cursor = self.db.get_cursor("oltp")

            cursor.execute(
                query,
                (project_id,)
            )

            return cursor.fetchone()

        except Exception as e:

            logger.exception(
                "Failed to fetch project."
            )

            raise DatabaseException(
                f"Failed to fetch project: {e}"
            )

        finally:

            if cursor:
                cursor.close()

    def create(self, project):

        query = """
            INSERT INTO Projects
            (
                ProjectName,
                StartDate,
                EndDate,
                Status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
        """

        values = (
            project.project_name,
            project.start_date,
            project.end_date,
            project.status
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
                "Failed to create project."
            )

            raise DatabaseException(
                f"Failed to create project: {e}"
            )

        finally:

            if cursor:
                cursor.close()

    def update(self, project_id, data):

        query = """
            UPDATE Projects
            SET
                ProjectName = %s,
                StartDate = %s,
                EndDate = %s,
                Status = %s
            WHERE ProjectID = %s
        """

        values = (
            data["project_name"],
            data["start_date"],
            data["end_date"],
            data["status"],
            project_id
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
                "Failed to update project."
            )

            raise DatabaseException(
                f"Failed to update project: {e}"
            )

        finally:

            if cursor:
                cursor.close()

    def delete(self, project_id):

        query = """
            DELETE FROM Projects
            WHERE ProjectID = %s
        """

        cursor = None

        try:

            connection = self.db.connect("oltp")

            cursor = connection.cursor()

            cursor.execute(
                query,
                (project_id,)
            )

            self.db.commit("oltp")

            return cursor.rowcount

        except Exception as e:

            self.db.rollback("oltp")

            logger.exception(
                "Failed to delete project."
            )

            raise DatabaseException(
                f"Failed to delete project: {e}"
            )

        finally:

            if cursor:
                cursor.close()