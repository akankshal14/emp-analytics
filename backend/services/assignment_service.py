from backend.exceptions import (
    ValidationException,
    NotFoundException,
    BusinessRuleException
)

from backend.repositories.assignment_repository import (
    AssignmentRepository
)

from backend.repositories.employee_repository import (
    EmployeeRepository
)

from backend.repositories.project_repository import (
    ProjectRepository
)

from backend.models.assignment import Assignment

from backend.utils.logger import get_logger

from backend.utils.validators import (
    validate_required,
    validate_percentage
)


logger = get_logger(__name__)


class AssignmentService:

    def __init__(self):

        self.repository = AssignmentRepository()

        self.employee_repository = (
            EmployeeRepository()
        )

        self.project_repository = (
            ProjectRepository()
        )

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all_assignments(self):

        try:

            return self.repository.get_all()

        except Exception:

            logger.exception(
                "Failed to get assignments."
            )

            raise

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_assignment(
        self,
        assignment_id
    ):

        try:

            assignment = (
                self.repository
                .get_by_id(assignment_id)
            )

            if not assignment:

                raise NotFoundException(
                    "Assignment not found."
                )

            return assignment

        except Exception:

            logger.exception(
                "Failed to get assignment."
            )

            raise

    # =====================================================
    # CREATE
    # =====================================================

    def create_assignment(
        self,
        assignment
    ):

        try:

            # -------------------------------------------------
            # Validate employee
            # -------------------------------------------------

            employee = (
                self.employee_repository
                .get_by_id(
                    assignment.employee_id
                )
            )

            if not employee:

                raise NotFoundException(
                    "Employee does not exist."
                )

            # -------------------------------------------------
            # Validate project
            # -------------------------------------------------

            project = (
                self.project_repository
                .get_by_id(
                    assignment.project_id
                )
            )

            if not project:

                raise NotFoundException(
                    "Project does not exist."
                )

            # -------------------------------------------------
            # Validate dates
            # -------------------------------------------------

            validate_required(
                assignment.start_date,
                "Assignment start date"
            )

            if (
                assignment.end_date is not None
                and assignment.end_date < assignment.start_date
            ):

                raise ValidationException(
                    "Assignment end date cannot "
                    "be before start date."
                )

            # -------------------------------------------------
            # Validate allocation
            # -------------------------------------------------

            validate_percentage(
                assignment.allocation_percentage,
                "Allocation percentage"
            )

            if assignment.allocation_percentage <= 0:

                raise ValidationException(
                    "Allocation percentage must "
                    "be greater than 0."
                )

            # -------------------------------------------------
            # Check existing employee allocation
            # -------------------------------------------------

            current = (
                self.repository
                .get_employee_allocation(
                    assignment.employee_id
                )
            )

            current_allocation = (
                current["TotalAllocation"]
                if current
                else 0
            )

            new_total = (
                float(current_allocation)
                + float(
                    assignment.allocation_percentage
                )
            )

            if new_total > 100:

                raise BusinessRuleException(
                    "Employee allocation cannot "
                    "exceed 100%."
                )

            # -------------------------------------------------
            # Create
            # -------------------------------------------------

            return self.repository.create(
                assignment
            )

        except Exception:

            logger.exception(
                "Failed to create assignment."
            )

            raise

    # =====================================================
    # UPDATE
    # =====================================================

    def update_assignment(
        self,
        assignment_id,
        assignment
    ):

        try:

            # -------------------------------------------------
            # Check existing assignment
            # -------------------------------------------------

            existing = (
                self.repository
                .get_by_id(
                    assignment_id
                )
            )

            if not existing:

                raise NotFoundException(
                    "Assignment not found."
                )

            # -------------------------------------------------
            # Validate employee
            # -------------------------------------------------

            employee = (
                self.employee_repository
                .get_by_id(
                    assignment.employee_id
                )
            )

            if not employee:

                raise NotFoundException(
                    "Employee does not exist."
                )

            # -------------------------------------------------
            # Validate project
            # -------------------------------------------------

            project = (
                self.project_repository
                .get_by_id(
                    assignment.project_id
                )
            )

            if not project:

                raise NotFoundException(
                    "Project does not exist."
                )

            # -------------------------------------------------
            # Validate dates
            # -------------------------------------------------

            validate_required(
                assignment.start_date,
                "Assignment start date"
            )

            if (
                assignment.end_date is not None
                and assignment.end_date < assignment.start_date
            ):

                raise ValidationException(
                    "Assignment end date cannot "
                    "be before start date."
                )

            # -------------------------------------------------
            # Validate allocation
            # -------------------------------------------------

            validate_percentage(
                assignment.allocation_percentage,
                "Allocation percentage"
            )

            if assignment.allocation_percentage <= 0:

                raise ValidationException(
                    "Allocation percentage must "
                    "be greater than 0."
                )

            # -------------------------------------------------
            # Check allocation limit
            #
            # Important:
            # Remove the OLD allocation of this assignment
            # before adding the NEW allocation.
            # -------------------------------------------------

            current = (
                self.repository
                .get_employee_allocation(
                    assignment.employee_id
                )
            )

            current_allocation = (
                float(
                    current["TotalAllocation"]
                )
                if current
                else 0
            )

            # Existing assignment's allocation
            old_allocation = float(
                existing["AllocationPercentage"]
            )

            new_total = (
                current_allocation
                - old_allocation
                + float(
                    assignment.allocation_percentage
                )
            )

            if new_total > 100:

                raise BusinessRuleException(
                    "Employee allocation cannot "
                    "exceed 100%."
                )

            # -------------------------------------------------
            # Update repository
            # -------------------------------------------------

            return self.repository.update(
                assignment_id,
                assignment
            )

        except Exception:

            logger.exception(
                "Failed to update assignment."
            )

            raise

    