from backend.repositories.employee_repository import EmployeeRepository
from backend.repositories.etl_repository import ETLRepository

from backend.exceptions import (
    DatabaseException,
    NotFoundException,
    BadRequestException
)

from backend.utils.logger import get_logger


logger = get_logger(__name__)


class EmployeeService:
    """
    Business logic layer for Employee operations.

    Architecture:

        Streamlit
            ↓
        EmployeeService
            ↓
        EmployeeRepository
            ↓
        OLTP

        EmployeeService
            ↓
        ETLRepository
            ↓
        OLAP

    SCD Type 2 is handled by the service layer.

    Tracked SCD attributes:
        - DepartmentID
        - JobRole
        - JobLevel
        - MonthlyIncome
        - PercentSalaryHike
        - OverTime
        - BusinessTravel
        - Education
        - EducationField
        - IsActive

    When any tracked attribute changes:

        OLD Dim_Employee version
                ↓
             expired
                ↓
        NEW Dim_Employee version
                ↓
             IsCurrent = 1
    """

    def __init__(self):

        self.repository = EmployeeRepository()
        self.etl_repository = ETLRepository()

        logger.info(
            "EmployeeService initialized."
        )

  

    def get_all_employees(self):

        try:

            return self.repository.get_all()

        except DatabaseException:

            logger.exception(
                "Failed to get all employees."
            )

            raise

        except Exception as e:

            logger.exception(
                "Unexpected error while getting employees."
            )

            raise DatabaseException(
                f"Unable to get employees: {e}"
            )

   

    def get_employee(
        self,
        employee_id
    ):

        if employee_id is None:

            raise BadRequestException(
                "Employee ID is required."
            )

        try:

            employee_id = int(employee_id)

        except (ValueError, TypeError):

            raise BadRequestException(
                "Employee ID must be a valid integer."
            )

        try:

            employee = self.repository.get_by_id(
                employee_id
            )

            if not employee:

                raise NotFoundException(
                    f"Employee {employee_id} not found."
                )

            return employee

        except NotFoundException:

            raise

        except DatabaseException:

            logger.exception(
                "Database error while getting employee %s.",
                employee_id
            )

            raise

        except Exception as e:

            logger.exception(
                "Unexpected error while getting employee %s.",
                employee_id
            )

            raise DatabaseException(
                f"Unable to get employee: {e}"
            )



    def create_employee(
        self,
        employee
    ):

        if employee is None:

            raise BadRequestException(
                "Employee data is required."
            )

        try:

          

            employee.employee_id = None

            generated_id = self.repository.create(
                employee
            )

            logger.info(
                "Employee %s created in OLTP.",
                generated_id
            )

            

            created_employee = (
                self.repository.get_by_id(
                    generated_id
                )
            )

            if not created_employee:

                raise DatabaseException(
                    "Employee was created in OLTP but "
                    "could not be retrieved."
                )


            employee_sk = (
                self.etl_repository
                .insert_employee_dimension(
                    created_employee
                )
            )

            logger.info(
                "Initial Dim_Employee version created. "
                "EmployeeID=%s EmployeeSK=%s",
                generated_id,
                employee_sk
            )

            return generated_id

        except DatabaseException:

            logger.exception(
                "Database error while creating employee."
            )

            raise

        except Exception as e:

            logger.exception(
                "Unexpected error while creating employee."
            )

            raise DatabaseException(
                f"Unable to create employee: {e}"
            )

   

    def update_employee(
        self,
        employee_id,
        data
    ):

      

        if employee_id is None:

            raise BadRequestException(
                "Employee ID is required."
            )

        if not data:

            raise BadRequestException(
                "Update data is required."
            )


        try:

            employee_id = int(employee_id)

        except (ValueError, TypeError):

            raise BadRequestException(
                "Employee ID must be a valid integer."
            )

    

        required_fields = [

            "first_name",
            "last_name",
            "age",
            "gender",
            "marital_status",
            "department_id",
            "job_role",
            "job_level",
            "monthly_income",
            "daily_rate",
            "hourly_rate",
            "monthly_rate",
            "percent_salary_hike",
            "stock_option_level",
            "over_time",
            "business_travel",
            "distance_from_home",
            "education",
            "education_field",
            "environment_satisfaction",
            "job_involvement",
            "job_satisfaction",
            "relationship_satisfaction",
            "work_life_balance",
            "total_working_years",
            "training_times_last_year",
            "years_at_company",
            "years_in_current_role",
            "years_since_last_promotion",
            "years_with_curr_manager",
            "is_active",
            "hire_date",
            "termination_date"
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in data
        ]

        if missing_fields:

            raise BadRequestException(
                "Missing update fields: "
                + ", ".join(missing_fields)
            )

        

        if not str(
            data["first_name"]
        ).strip():

            raise BadRequestException(
                "First name is required."
            )

        if not str(
            data["last_name"]
        ).strip():

            raise BadRequestException(
                "Last name is required."
            )

        if not str(
            data["job_role"]
        ).strip():

            raise BadRequestException(
                "Job role is required."
            )


        try:

            department_id = int(
                data["department_id"]
            )

            if department_id <= 0:

                raise ValueError

        except (ValueError, TypeError):

            raise BadRequestException(
                "Department ID must be a valid positive integer."
            )

       

        try:

            job_level = int(
                data["job_level"]
            )

            if job_level < 1:

                raise ValueError

        except (ValueError, TypeError):

            raise BadRequestException(
                "Job level must be a positive integer."
            )


        try:

            monthly_income = float(
                data["monthly_income"]
            )

            if monthly_income < 0:

                raise ValueError

        except (ValueError, TypeError):

            raise BadRequestException(
                "Monthly income must be a valid non-negative number."
            )

      

        try:

            percent_salary_hike = float(
                data["percent_salary_hike"]
            )

            if percent_salary_hike < 0:

                raise ValueError

        except (ValueError, TypeError):

            raise BadRequestException(
                "Percent salary hike must be a valid "
                "non-negative number."
            )

       

        is_active = bool(
            data["is_active"]
        )

        hire_date = data["hire_date"]

        termination_date = data[
            "termination_date"
        ]

        if hire_date is None:

            raise BadRequestException(
                "Hire date is required."
            )

        

        if (
            not is_active
            and termination_date is None
        ):

            raise BadRequestException(
                "Inactive employee must have a termination date."
            )

    
        if (
            termination_date is not None
            and termination_date < hire_date
        ):

            raise BadRequestException(
                "Termination date cannot be before hire date."
            )


        if is_active:

            data["termination_date"] = None

      

        try:

            existing_employee = (
                self.repository.get_by_id(
                    employee_id
                )
            )

            if not existing_employee:

                raise NotFoundException(
                    f"Employee {employee_id} not found."
                )

           

            old_department_id = existing_employee.get(
                "DepartmentID"
            )

            old_job_role = existing_employee.get(
                "JobRole"
            )

            old_job_level = existing_employee.get(
                "JobLevel"
            )

            old_monthly_income = existing_employee.get(
                "MonthlyIncome"
            )

            old_percent_salary_hike = existing_employee.get(
                "PercentSalaryHike"
            )

            old_over_time = existing_employee.get(
                "OverTime"
            )

            old_business_travel = existing_employee.get(
                "BusinessTravel"
            )

            old_education = existing_employee.get(
                "Education"
            )

            old_education_field = existing_employee.get(
                "EducationField"
            )

            old_is_active = existing_employee.get(
                "IsActive"
            )

            

            new_department_id = department_id

            new_job_role = str(
                data["job_role"]
            ).strip()

            new_job_level = job_level

            new_monthly_income = monthly_income

            new_percent_salary_hike = percent_salary_hike

            new_over_time = data[
                "over_time"
            ]

            new_business_travel = data[
                "business_travel"
            ]

            new_education = data[
                "education"
            ]

            new_education_field = data[
                "education_field"
            ]

            new_is_active = is_active

           

            def normalize_overtime(value):

                if isinstance(value, bool):

                    return value

                if value is None:

                    return False

                value = str(value).strip().lower()

                return value in (
                    "yes",
                    "true",
                    "1"
                )

            old_over_time_normalized = (
                normalize_overtime(
                    old_over_time
                )
            )

            new_over_time_normalized = (
                normalize_overtime(
                    new_over_time
                )
            )

           
            scd_changed = (

                old_department_id
                != new_department_id

                or str(
                    old_job_role or ""
                ).strip()
                != new_job_role

                or int(
                    old_job_level or 0
                )
                != new_job_level

                or float(
                    old_monthly_income or 0
                )
                != new_monthly_income

                or float(
                    old_percent_salary_hike or 0
                )
                != new_percent_salary_hike

                or old_over_time_normalized
                != new_over_time_normalized

                or str(
                    old_business_travel or ""
                ).strip().lower()
                != str(
                    new_business_travel or ""
                ).strip().lower()

                or str(
                    old_education or ""
                ).strip()
                != str(
                    new_education or ""
                ).strip()

                or str(
                    old_education_field or ""
                ).strip().lower()
                != str(
                    new_education_field or ""
                ).strip().lower()

                or bool(
                    old_is_active
                )
                != new_is_active
            )

            logger.info(
                "Employee %s SCD change detected: %s",
                employee_id,
                scd_changed
            )

      

            result = self.repository.update(
                employee_id,
                data
            )

            logger.info(
                "Employee %s successfully updated in OLTP.",
                employee_id
            )

          

            if scd_changed:

                logger.info(
                    "Applying SCD Type 2 for employee %s.",
                    employee_id
                )


                updated_employee = (
                    self.repository.get_by_id(
                        employee_id
                    )
                )

                if not updated_employee:

                    raise DatabaseException(
                        "Employee updated in OLTP but "
                        "could not be retrieved."
                    )

               

                new_employee_sk = (
                    self.etl_repository
                    .apply_employee_scd_type2(
                        updated_employee
                    )
                )

                logger.info(
                    "SCD Type 2 completed successfully. "
                    "EmployeeID=%s NewEmployeeSK=%s",
                    employee_id,
                    new_employee_sk
                )

            else:

                logger.info(
                    "No SCD Type 2 change required for employee %s.",
                    employee_id
                )

            return result

        except NotFoundException:

            raise

        except DatabaseException:

            logger.exception(
                "Database error while updating employee %s.",
                employee_id
            )

            raise

        except Exception as e:

            logger.exception(
                "Unexpected error while updating employee %s.",
                employee_id
            )

            raise DatabaseException(
                f"Unable to update employee: {e}"
            )

    