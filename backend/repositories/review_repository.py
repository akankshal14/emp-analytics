from backend.database.db_manager import DatabaseConnection
from backend.exceptions import DatabaseException
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class ReviewRepository:

    def __init__(self):

        self.db = DatabaseConnection()

        logger.info(
            "ReviewRepository initialized."
        )

    # =========================================================
    # GET ALL REVIEWS
    # =========================================================

    def get_all(self):

        query = """
            SELECT
                ReviewID,
                EmployeeID,
                ReviewDate,
                PerformanceRating,
                ReviewerID,
                Comments
            FROM performancereviews
            ORDER BY ReviewID DESC
        """

        cursor = None

        try:

            cursor = self.db.get_cursor("oltp")

            cursor.execute(query)

            result = cursor.fetchall()

            logger.info(
                "Fetched %d reviews.",
                len(result)
            )

            return result

        except Exception as e:

            logger.exception(
                "Failed to fetch reviews."
            )

            raise DatabaseException(
                f"Failed to fetch reviews: {e}"
            )

        finally:

            if cursor:

                try:
                    cursor.close()

                except Exception:

                    logger.warning(
                        "Failed to close review cursor."
                    )

    # =========================================================
    # GET REVIEW BY ID
    # =========================================================

    def get_by_id(
        self,
        review_id
    ):

        query = """
            SELECT
                ReviewID,
                EmployeeID,
                ReviewDate,
                PerformanceRating,
                ReviewerID,
                Comments
            FROM performancereviews
            WHERE ReviewID = %s
        """

        cursor = None

        try:

            review_id = int(review_id)

            cursor = self.db.get_cursor("oltp")

            cursor.execute(
                query,
                (review_id,)
            )

            result = cursor.fetchone()

            return result

        except (
            TypeError,
            ValueError
        ) as e:

            logger.exception(
                "Invalid review ID: %s",
                review_id
            )

            raise DatabaseException(
                f"Invalid review ID: {e}"
            )

        except Exception as e:

            logger.exception(
                "Failed to fetch review."
            )

            raise DatabaseException(
                f"Failed to fetch review: {e}"
            )

        finally:

            if cursor:

                try:
                    cursor.close()

                except Exception:

                    logger.warning(
                        "Failed to close review cursor."
                    )

    # =========================================================
    # GET REVIEWS BY EMPLOYEE
    # =========================================================

    def get_by_employee_id(
        self,
        employee_id
    ):

        query = """
            SELECT
                ReviewID,
                EmployeeID,
                ReviewDate,
                PerformanceRating,
                ReviewerID,
                Comments
            FROM performancereviews
            WHERE EmployeeID = %s
            ORDER BY ReviewDate DESC
        """

        cursor = None

        try:

            employee_id = int(employee_id)

            cursor = self.db.get_cursor("oltp")

            cursor.execute(
                query,
                (employee_id,)
            )

            result = cursor.fetchall()

            logger.info(
                "Fetched %d reviews for employee %s.",
                len(result),
                employee_id
            )

            return result

        except (
            TypeError,
            ValueError
        ) as e:

            logger.exception(
                "Invalid employee ID: %s",
                employee_id
            )

            raise DatabaseException(
                f"Invalid employee ID: {e}"
            )

        except Exception as e:

            logger.exception(
                "Failed to fetch employee reviews."
            )

            raise DatabaseException(
                f"Failed to fetch employee reviews: {e}"
            )

        finally:

            if cursor:

                try:
                    cursor.close()

                except Exception:

                    logger.warning(
                        "Failed to close review cursor."
                    )

    # =========================================================
    # CREATE
    # =========================================================

    def create(
        self,
        review
    ):

        query = """
            INSERT INTO performancereviews
            (
                EmployeeID,
                ReviewDate,
                PerformanceRating,
                ReviewerID,
                Comments
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """

        values = (
            int(review.employee_id),

            review.review_date,

            int(review.performance_rating),

            (
                None
                if review.reviewer_id is None
                else int(review.reviewer_id)
            ),

            review.comments
        )

        cursor = None

        try:

            connection = self.db.connect(
                "oltp"
            )

            cursor = connection.cursor()

            cursor.execute(
                query,
                values
            )

            self.db.commit(
                "oltp"
            )

            review_id = cursor.lastrowid

            logger.info(
                "Created review with ID: %s",
                review_id
            )

            return review_id

        except Exception as e:

            self.db.rollback(
                "oltp"
            )

            logger.exception(
                "Failed to create review."
            )

            raise DatabaseException(
                f"Failed to create review: {e}"
            )

        finally:

            if cursor:

                try:
                    cursor.close()

                except Exception:

                    logger.warning(
                        "Failed to close review cursor."
                    )

    # =========================================================
    # UPDATE
    # =========================================================

    def update(
        self,
        review_id,
        review
    ):

        query = """
            UPDATE performancereviews
            SET
                EmployeeID = %s,
                ReviewDate = %s,
                PerformanceRating = %s,
                ReviewerID = %s,
                Comments = %s
            WHERE ReviewID = %s
        """

        values = (
            int(review.employee_id),

            review.review_date,

            int(review.performance_rating),

            (
                None
                if review.reviewer_id is None
                else int(review.reviewer_id)
            ),

            review.comments,

            int(review_id)
        )

        cursor = None

        try:

            connection = self.db.connect(
                "oltp"
            )

            cursor = connection.cursor()

            cursor.execute(
                query,
                values
            )

            self.db.commit(
                "oltp"
            )

            affected_rows = cursor.rowcount

            logger.info(
                "Updated review ID: %s. Rows affected: %s",
                review_id,
                affected_rows
            )

            return affected_rows

        except (
            TypeError,
            ValueError
        ) as e:

            self.db.rollback(
                "oltp"
            )

            logger.exception(
                "Invalid review ID during update."
            )

            raise DatabaseException(
                f"Invalid review ID: {e}"
            )

        except Exception as e:

            self.db.rollback(
                "oltp"
            )

            logger.exception(
                "Failed to update review."
            )

            raise DatabaseException(
                f"Failed to update review: {e}"
            )

        finally:

            if cursor:

                try:
                    cursor.close()

                except Exception:

                    logger.warning(
                        "Failed to close review cursor."
                    )

    # =========================================================
    # DELETE
    # =========================================================

    def delete(
        self,
        review_id
    ):

        query = """
            DELETE FROM performancereviews
            WHERE ReviewID = %s
        """

        cursor = None

        try:

            review_id = int(
                review_id
            )

            connection = self.db.connect(
                "oltp"
            )

            cursor = connection.cursor()

            cursor.execute(
                query,
                (review_id,)
            )

            self.db.commit(
                "oltp"
            )

            affected_rows = cursor.rowcount

            logger.info(
                "Deleted review ID: %s. Rows affected: %s",
                review_id,
                affected_rows
            )

            return affected_rows

        except (
            TypeError,
            ValueError
        ) as e:

            self.db.rollback(
                "oltp"
            )

            logger.exception(
                "Invalid review ID during deletion."
            )

            raise DatabaseException(
                f"Invalid review ID: {e}"
            )

        except Exception as e:

            self.db.rollback(
                "oltp"
            )

            logger.exception(
                "Failed to delete review."
            )

            raise DatabaseException(
                f"Failed to delete review: {e}"
            )

        finally:

            if cursor:

                try:
                    cursor.close()

                except Exception:

                    logger.warning(
                        "Failed to close review cursor."
                    )