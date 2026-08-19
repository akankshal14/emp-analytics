from backend.repositories.etl_repository import ETLRepository

from backend.exceptions import (
    DatabaseException,
    NotFoundException,
    BadRequestException
)

from backend.utils.logger import get_logger


logger = get_logger(__name__)


class ETLService:
    """
    Service layer for ETL-related operations.

    NOTE:

    These methods are for manual/batch ETL operations.

    Employee SCD Type 2 updates do NOT need to call
    run_master_etl().

    EmployeeService handles SCD Type 2 directly when
    an employee is changed from the application.
    """

    def __init__(self):

        self.repository = ETLRepository()

        logger.info(
            "ETLService initialized."
        )

    # ============================================================
    # RUN DIMENSION ETL
    # ============================================================

    def run_dimensions(self):

        try:

            result = (
                self.repository
                .run_dimensions()
            )

            logger.info(
                "Dimension ETL completed successfully."
            )

            return result

        except DatabaseException:

            logger.exception(
                "Database error while running dimension ETL."
            )

            raise

        except Exception as e:

            logger.exception(
                "Unexpected error while running dimension ETL."
            )

            raise DatabaseException(
                f"Unable to run dimension ETL: {e}"
            )

    # ============================================================
    # RUN FACT ETL
    # ============================================================

    def run_fact(self):

        try:

            result = (
                self.repository
                .run_fact()
            )

            logger.info(
                "Fact ETL completed successfully."
            )

            return result

        except DatabaseException:

            logger.exception(
                "Database error while running fact ETL."
            )

            raise

        except Exception as e:

            logger.exception(
                "Unexpected error while running fact ETL."
            )

            raise DatabaseException(
                f"Unable to run fact ETL: {e}"
            )

    # ============================================================
    # RUN MASTER ETL
    # ============================================================

    def run_master_etl(self):

        try:

            logger.info(
                "Executing master ETL pipeline."
            )

            result = (
                self.repository
                .run_master_etl()
            )

            logger.info(
                "Master ETL completed successfully."
            )

            return result

        except DatabaseException:

            logger.exception(
                "Database error while running master ETL."
            )

            raise

        except Exception as e:

            logger.exception(
                "Unexpected error while running master ETL."
            )

            raise DatabaseException(
                f"Unable to run master ETL: {e}"
            )

    # ============================================================
    # GET ETL LOGS
    # ============================================================

    def get_execution_logs(self):

        try:

            return (
                self.repository
                .get_execution_logs()
            )

        except DatabaseException:

            logger.exception(
                "Database error while getting ETL logs."
            )

            raise

        except Exception as e:

            logger.exception(
                "Unexpected error while getting ETL logs."
            )

            raise DatabaseException(
                f"Unable to get ETL execution logs: {e}"
            )

    # ============================================================
    # GET CURRENT EMPLOYEE DIMENSIONS
    # ============================================================

    def get_current_employee_dimensions(self):

        try:

            return (
                self.repository
                .get_current_employee_dimensions()
            )

        except DatabaseException:

            logger.exception(
                "Database error while getting "
                "current employee dimensions."
            )

            raise

        except Exception as e:

            logger.exception(
                "Unexpected error while getting "
                "current employee dimensions."
            )

            raise DatabaseException(
                f"Unable to get current employee dimensions: {e}"
            )

    # ============================================================
    # GET EMPLOYEE SCD HISTORY
    # ============================================================

    def get_employee_history(
        self,
        employee_id
    ):

        if employee_id is None:

            raise BadRequestException(
                "Employee ID is required."
            )

        try:

            employee_id = int(
                employee_id
            )

        except (ValueError, TypeError):

            raise BadRequestException(
                "Employee ID must be a valid integer."
            )

        try:

            history = (
                self.repository
                .get_employee_history(
                    employee_id
                )
            )

            if not history:

                raise NotFoundException(
                    f"No SCD history found for employee "
                    f"{employee_id}."
                )

            return history

        except NotFoundException:

            raise

        except DatabaseException:

            logger.exception(
                "Database error while getting SCD history "
                "for employee %s.",
                employee_id
            )

            raise

        except Exception as e:

            logger.exception(
                "Unexpected error while getting SCD history "
                "for employee %s.",
                employee_id
            )

            raise DatabaseException(
                f"Unable to get employee SCD history: {e}"
            )