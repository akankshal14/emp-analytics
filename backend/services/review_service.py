# from backend.exceptions import (
#     ValidationException,
#     NotFoundException
# )

# from backend.repositories.review_repository import (
#     ReviewRepository
# )

# from backend.repositories.employee_repository import (
#     EmployeeRepository
# )

# from backend.utils.logger import get_logger
# from backend.utils.validators import (
#     validate_required,
#     validate_rating
# )


# logger = get_logger(__name__)


# class ReviewService:

#     def __init__(self):

#         self.repository = ReviewRepository()

#         self.employee_repository = (
#             EmployeeRepository()
#         )

#     def get_all_reviews(self):

#         try:

#             return self.repository.get_all()

#         except Exception:

#             logger.exception(
#                 "Failed to get reviews."
#             )

#             raise

#     def get_review(
#         self,
#         review_id
#     ):

#         try:

#             review = (
#                 self.repository
#                 .get_by_id(review_id)
#             )

#             if not review:

#                 raise NotFoundException(
#                     "Review not found."
#                 )

#             return review

#         except Exception:

#             logger.exception(
#                 "Failed to get review."
#             )

#             raise

#     def get_employee_reviews(
#         self,
#         employee_id
#     ):

#         try:

#             employee = (
#                 self.employee_repository
#                 .get_by_id(employee_id)
#             )

#             if not employee:

#                 raise NotFoundException(
#                     "Employee not found."
#                 )

#             return (
#                 self.repository
#                 .get_by_employee_id(
#                     employee_id
#                 )
#             )

#         except Exception:

#             logger.exception(
#                 "Failed to get employee reviews."
#             )

#             raise

#     def create_review(
#         self,
#         review
#     ):

#         try:

#             employee = (
#                 self.employee_repository
#                 .get_by_id(
#                     review.employee_id
#                 )
#             )

#             if not employee:

#                 raise NotFoundException(
#                     "Employee does not exist."
#                 )

#             validate_required(
#                 review.review_date,
#                 "Review date"
#             )

#             validate_rating(
#                 review.performance_rating
#             )

#             return self.repository.create(
#                 review
#             )

#         except Exception:

#             logger.exception(
#                 "Failed to create review."
#             )

#             raise

#     def update_review(
#         self,
#         review_id,
#         review
#     ):

#         try:

#             existing = (
#                 self.repository
#                 .get_by_id(review_id)
#             )

#             if not existing:

#                 raise NotFoundException(
#                     "Review not found."
#                 )

#             validate_rating(
#                 review.performance_rating
#             )

#             return self.repository.update(
#                 review_id,
#                 review
#             )

#         except Exception:

#             logger.exception(
#                 "Failed to update review."
#             )

#             raise

#     def delete_review(
#         self,
#         review_id
#     ):

#         try:

#             existing = (
#                 self.repository
#                 .get_by_id(review_id)
#             )

#             if not existing:

#                 raise NotFoundException(
#                     "Review not found."
#                 )

#             return self.repository.delete(
#                 review_id
#             )

#         except Exception:

#             logger.exception(
#                 "Failed to delete review."
#             )

#             raise






# from backend.exceptions import (
#     NotFoundException
# )

# from backend.repositories.review_repository import (
#     ReviewRepository
# )

# from backend.repositories.employee_repository import (
#     EmployeeRepository
# )

# from backend.utils.logger import get_logger

# from backend.utils.validators import (
#     validate_required,
#     validate_rating
# )


# logger = get_logger(__name__)


# class ReviewService:

#     def __init__(self):

#         self.repository = ReviewRepository()

#         self.employee_repository = (
#             EmployeeRepository()
#         )

#     # =========================================================
#     # GET ALL
#     # =========================================================

#     def get_all_reviews(self):

#         try:

#             return self.repository.get_all()

#         except Exception:

#             logger.exception(
#                 "Failed to get reviews."
#             )

#             raise

#     # =========================================================
#     # GET BY ID
#     # =========================================================

#     def get_review(
#         self,
#         review_id
#     ):

#         try:

#             review_id = int(review_id)

#             review = (
#                 self.repository
#                 .get_by_id(review_id)
#             )

#             if not review:

#                 raise NotFoundException(
#                     f"Review {review_id} not found."
#                 )

#             return review

#         except Exception:

#             logger.exception(
#                 "Failed to get review."
#             )

#             raise

#     # =========================================================
#     # GET REVIEWS BY EMPLOYEE
#     # =========================================================

#     def get_employee_reviews(
#         self,
#         employee_id
#     ):

#         try:

#             employee_id = int(employee_id)

#             employee = (
#                 self.employee_repository
#                 .get_by_id(employee_id)
#             )

#             if not employee:

#                 raise NotFoundException(
#                     f"Employee {employee_id} not found."
#                 )

#             return (
#                 self.repository
#                 .get_by_employee_id(
#                     employee_id
#                 )
#             )

#         except Exception:

#             logger.exception(
#                 "Failed to get employee reviews."
#             )

#             raise

#     # =========================================================
#     # CREATE
#     # =========================================================

#     def create_review(
#         self,
#         review
#     ):

#         try:

#             validate_required(
#                 review.review_date,
#                 "Review date"
#             )

#             validate_rating(
#                 review.performance_rating
#             )

#             # ---------------------------------------------
#             # Validate Employee
#             # ---------------------------------------------

#             employee = (
#                 self.employee_repository
#                 .get_by_id(
#                     int(review.employee_id)
#                 )
#             )

#             if not employee:

#                 raise NotFoundException(
#                     f"Employee {review.employee_id} "
#                     "does not exist."
#                 )

#             # ---------------------------------------------
#             # Validate Reviewer
#             # ---------------------------------------------

#             reviewer = (
#                 self.employee_repository
#                 .get_by_id(
#                     int(review.reviewer_id)
#                 )
#             )

#             if not reviewer:

#                 raise NotFoundException(
#                     f"Reviewer {review.reviewer_id} "
#                     "does not exist."
#                 )

#             return self.repository.create(
#                 review
#             )

#         except Exception:

#             logger.exception(
#                 "Failed to create review."
#             )

#             raise

#     # =========================================================
#     # UPDATE
#     # =========================================================

#     def update_review(
#         self,
#         review_id,
#         review
#     ):

#         try:

#             review_id = int(review_id)

#             # ---------------------------------------------
#             # Check existing review
#             # ---------------------------------------------

#             existing = (
#                 self.repository
#                 .get_by_id(review_id)
#             )

#             if not existing:

#                 raise NotFoundException(
#                     f"Review {review_id} not found."
#                 )

#             # ---------------------------------------------
#             # Validation
#             # ---------------------------------------------

#             validate_required(
#                 review.review_date,
#                 "Review date"
#             )

#             validate_rating(
#                 review.performance_rating
#             )

#             # ---------------------------------------------
#             # Check employee
#             # ---------------------------------------------

#             employee = (
#                 self.employee_repository
#                 .get_by_id(
#                     int(review.employee_id)
#                 )
#             )

#             if not employee:

#                 raise NotFoundException(
#                     f"Employee {review.employee_id} "
#                     "does not exist."
#                 )

#             # ---------------------------------------------
#             # Check reviewer
#             # ---------------------------------------------

#             reviewer = (
#                 self.employee_repository
#                 .get_by_id(
#                     int(review.reviewer_id)
#                 )
#             )

#             if not reviewer:

#                 raise NotFoundException(
#                     f"Reviewer {review.reviewer_id} "
#                     "does not exist."
#                 )

#             return self.repository.update(
#                 review_id,
#                 review
#             )

#         except Exception:

#             logger.exception(
#                 "Failed to update review."
#             )

#             raise

#     # =========================================================
#     # DELETE
#     # =========================================================

#     def delete_review(
#         self,
#         review_id
#     ):

#         try:

#             review_id = int(review_id)

#             existing = (
#                 self.repository
#                 .get_by_id(review_id)
#             )

#             if not existing:

#                 raise NotFoundException(
#                     f"Review {review_id} not found."
#                 )

#             return self.repository.delete(
#                 review_id
#             )

#         except Exception:

#             logger.exception(
#                 "Failed to delete review."
#             )

#             raise





from backend.exceptions import (
    NotFoundException
)

from backend.repositories.review_repository import (
    ReviewRepository
)

from backend.repositories.employee_repository import (
    EmployeeRepository
)

from backend.utils.logger import get_logger

from backend.utils.validators import (
    validate_required,
    validate_rating
)


logger = get_logger(__name__)


class ReviewService:

    def __init__(self):

        self.repository = ReviewRepository()

        self.employee_repository = (
            EmployeeRepository()
        )

    # =========================================================
    # GET ALL REVIEWS
    # =========================================================

    def get_all_reviews(self):

        try:

            return self.repository.get_all()

        except Exception:

            logger.exception(
                "Failed to get reviews."
            )

            raise

    # =========================================================
    # GET REVIEW BY ID
    # =========================================================

    def get_review(
        self,
        review_id
    ):

        try:

            review_id = int(review_id)

            review = (
                self.repository
                .get_by_id(review_id)
            )

            if not review:

                raise NotFoundException(
                    f"Review {review_id} not found."
                )

            return review

        except Exception:

            logger.exception(
                "Failed to get review."
            )

            raise

    # =========================================================
    # GET EMPLOYEE REVIEWS
    # =========================================================

    def get_employee_reviews(
        self,
        employee_id
    ):

        try:

            employee_id = int(
                employee_id
            )

            employee = (
                self.employee_repository
                .get_by_id(
                    employee_id
                )
            )

            if not employee:

                raise NotFoundException(
                    f"Employee {employee_id} not found."
                )

            return (
                self.repository
                .get_by_employee_id(
                    employee_id
                )
            )

        except Exception:

            logger.exception(
                "Failed to get employee reviews."
            )

            raise

    # =========================================================
    # CREATE REVIEW
    # =========================================================

    def create_review(
        self,
        review
    ):

        try:

            employee_id = int(
                review.employee_id
            )

            employee = (
                self.employee_repository
                .get_by_id(
                    employee_id
                )
            )

            if not employee:

                raise NotFoundException(
                    f"Employee {employee_id} does not exist."
                )

            validate_required(
                review.review_date,
                "Review date"
            )

            validate_rating(
                review.performance_rating
            )

            return (
                self.repository
                .create(review)
            )

        except Exception:

            logger.exception(
                "Failed to create review."
            )

            raise

    # =========================================================
    # UPDATE REVIEW
    # =========================================================

    def update_review(
        self,
        review_id,
        review
    ):

        try:

            review_id = int(
                review_id
            )

            existing = (
                self.repository
                .get_by_id(
                    review_id
                )
            )

            if not existing:

                raise NotFoundException(
                    f"Review {review_id} not found."
                )

            employee_id = int(
                review.employee_id
            )

            employee = (
                self.employee_repository
                .get_by_id(
                    employee_id
                )
            )

            if not employee:

                raise NotFoundException(
                    f"Employee {employee_id} does not exist."
                )

            validate_required(
                review.review_date,
                "Review date"
            )

            validate_rating(
                review.performance_rating
            )

            return (
                self.repository
                .update(
                    review_id,
                    review
                )
            )

        except Exception:

            logger.exception(
                "Failed to update review."
            )

            raise

    # =========================================================
    # DELETE REVIEW
    # =========================================================

    def delete_review(
        self,
        review_id
    ):

        try:

            review_id = int(
                review_id
            )

            existing = (
                self.repository
                .get_by_id(
                    review_id
                )
            )

            if not existing:

                raise NotFoundException(
                    f"Review {review_id} not found."
                )

            return (
                self.repository
                .delete(
                    review_id
                )
            )

        except Exception:

            logger.exception(
                "Failed to delete review."
            )

            raise