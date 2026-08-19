import sys
from pathlib import Path
from datetime import date

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from backend.services.employee_service import EmployeeService
from backend.models.employee import Employee

st.set_page_config(
    page_title="Employees",
    page_icon="👨‍💼",
    layout="wide"
)

employee_service = EmployeeService()

EMPLOYEE_COLUMNS = [
    "EmployeeID",
    "FirstName",
    "LastName",
    "Age",
    "Gender",
    "MaritalStatus",
    "DepartmentID",
    "JobRole",
    "JobLevel",
    "MonthlyIncome",
    "DailyRate",
    "HourlyRate",
    "MonthlyRate",
    "PercentSalaryHike",
    "StockOptionLevel",
    "OverTime",
    "BusinessTravel",
    "DistanceFromHome",
    "Education",
    "EducationField",
    "EnvironmentSatisfaction",
    "JobInvolvement",
    "JobSatisfaction",
    "RelationshipSatisfaction",
    "WorkLifeBalance",
    "TotalWorkingYears",
    "TrainingTimesLastYear",
    "YearsAtCompany",
    "YearsInCurrentRole",
    "YearsSinceLastPromotion",
    "YearsWithCurrManager",
    "IsActive",
    "HireDate",
    "TerminationDate"
]


def employees_to_dataframe(employees):

    if employees is None:
        return pd.DataFrame()

    if isinstance(employees, dict):
        employees = [employees]

    elif not isinstance(employees, (list, tuple)):
        employees = [employees]

    if len(employees) == 0:
        return pd.DataFrame()

    first_employee = employees[0]

    if isinstance(first_employee, dict):
        return pd.DataFrame(employees)

    if hasattr(first_employee, "_asdict"):
        return pd.DataFrame(
            [
                employee._asdict()
                for employee in employees
            ]
        )

    if hasattr(first_employee, "__dict__"):

        rows = []

        for employee in employees:

            row = {}

            for key, value in vars(employee).items():

                if not key.startswith("_"):
                    row[key] = value

            rows.append(row)

        return pd.DataFrame(rows)

    rows = []

    for employee in employees:

        try:
            rows.append(list(employee))

        except TypeError:
            rows.append([employee])

    if (
        len(rows) > 0
        and len(rows[0]) == len(EMPLOYEE_COLUMNS)
    ):

        return pd.DataFrame(
            rows,
            columns=EMPLOYEE_COLUMNS
        )

    return pd.DataFrame(rows)


def single_employee_to_dataframe(employee):

    if employee is None:
        return pd.DataFrame()

    return employees_to_dataframe([employee])


def get_employee_value(
    employee,
    key,
    default=None
):

    if employee is None:
        return default

    if isinstance(employee, dict):

        if key in employee:
            return employee[key]

        key_lower = key.lower()

        for existing_key, value in employee.items():

            if str(existing_key).lower() == key_lower:
                return value

        return default

    if hasattr(employee, "_asdict"):

        data = employee._asdict()

        if key in data:
            return data[key]

        key_lower = key.lower()

        for existing_key, value in data.items():

            if str(existing_key).lower() == key_lower:
                return value

        return default

    if hasattr(employee, key):
        return getattr(employee, key)

    snake_key = ""

    for index, character in enumerate(key):

        if character.isupper() and index > 0:
            snake_key += "_"

        snake_key += character.lower()

    if hasattr(employee, snake_key):
        return getattr(employee, snake_key)

    if isinstance(employee, (tuple, list)):

        try:

            index = EMPLOYEE_COLUMNS.index(key)

            return employee[index]

        except (
            ValueError,
            IndexError
        ):

            return default

    return default


def to_bool(value, default=False):

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    return str(value).lower() in (
        "1",
        "true",
        "yes",
        "y"
    )


def to_date(value):

    if value is None:
        return None

    if isinstance(value, date):
        return value

    if hasattr(value, "date"):

        try:
            return value.date()

        except Exception:
            pass

    try:
        return pd.to_datetime(value).date()

    except Exception:
        return None


st.title("👨‍💼 Employee Management")

st.caption(
    "Create, view, update and delete employee records."
)


st.subheader("Select Action")

operation = st.radio(
    "Employee Operations",
    [
        "Add Employee",
        "Update Employee",
        "Search Employee",
        "View Employees"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

if operation == "View Employees":

    st.header("📋 All Employees")

    try:

        employees = employee_service.get_all_employees()

        if not employees:

            st.info("No employees found.")

        else:

            df = employees_to_dataframe(employees)

            if df.empty:

                st.warning(
                    "Employees were retrieved, "
                    "but no displayable data was returned."
                )

            else:

                st.metric(
                    "Total Employees",
                    len(df)
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

    except Exception as exc:

        st.error(
            f"Unable to load employees: {exc}"
        )


elif operation == "Search Employee":

    st.header("🔍 Find Employee")

    employee_id = st.number_input(
        "Employee ID",
        min_value=1,
        step=1,
        value=1,
        key="view_employee_id"
    )

    if st.button(
        "Search Employee",
        type="primary"
    ):

        try:

            employee = employee_service.get_employee(
                int(employee_id)
            )

            if employee:

                st.success(
                    f"Employee {int(employee_id)} found."
                )

                df = single_employee_to_dataframe(
                    employee
                )

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.warning(
                    f"No employee found with Employee ID "
                    f"{int(employee_id)}."
                )

        except Exception as exc:

            st.error(
                f"Unable to find employee: {exc}"
            )


elif operation == "Add Employee":

    st.header(" Add Employee")

    is_active = st.checkbox(
        "Active Employee",
        value=True,
        key="add_is_active"
    )

    if is_active:

        st.success(
            "Employee is active. Termination Date is not required."
        )

    else:

        st.warning(
            "Employee is inactive. Termination Date is required."
        )

    with st.form("add_employee_form"):

        st.subheader("Basic Information")

        col1, col2, col3 = st.columns(3)

        with col1:

            first_name = st.text_input(
                "First Name"
            )

            last_name = st.text_input(
                "Last Name"
            )

            age = st.number_input(
                "Age",
                min_value=18,
                max_value=100,
                value=25
            )

        with col2:

            gender = st.selectbox(
                "Gender",
                [
                    "Male",
                    "Female",
                    "Other"
                ]
            )

            marital_status = st.selectbox(
                "Marital Status",
                [
                    "Single",
                    "Married",
                    "Divorced"
                ]
            )

            department_id = st.number_input(
                "Department ID",
                min_value=1,
                step=1
            )

            JOB_ROLES = [
            "Data engineer",
            "Healthcare Representative",
            "Human Resources",
            "Laboratory Technician",
            "Manager",
            "Manufacturing Director",
            "Research Director",
            "Research Scientist",
            "Sales Executive",
            "Sales Representative",
            "Senior Manager",
            "Senior Software Engineer",]

            job_role = st.selectbox(
                "Job Role",
                options=JOB_ROLES
            )
        with col3:

            job_level = st.number_input(
                "Job Level",
                min_value=1,
                max_value=5,
                value=1
            )

            monthly_income = st.number_input(
                "Monthly Income",
                min_value=0.0,
                step=100.0
            )

            daily_rate = st.number_input(
                "Daily Rate",
                min_value=0.0,
                step=1.0
            )

            hourly_rate = st.number_input(
                "Hourly Rate",
                min_value=0.0,
                step=1.0
            )

        st.subheader("Employment Information")

        col1, col2, col3 = st.columns(3)

        with col1:

            monthly_rate = st.number_input(
                "Monthly Rate",
                min_value=0.0,
                step=1.0
            )

            percent_salary_hike = st.number_input(
                "Percent Salary Hike",
                min_value=0.0,
                step=1.0
            )

            stock_option_level = st.number_input(
                "Stock Option Level",
                min_value=0,
                step=1
            )

        with col2:

            over_time_choice = st.selectbox(
                "OverTime",
                [
                    "Yes",
                    "No"
                ]
            )

            over_time = (
                1
                if over_time_choice == "Yes"
                else 0
            )

            business_travel = st.selectbox(
                "Business Travel",
                [
                    "Non-Travel",
                    "Travel_Rarely",
                    "Travel_Frequently"
                ]
            )

            distance_from_home = st.number_input(
                "Distance From Home",
                min_value=0,
                step=1
            )

        with col3:

            education = st.number_input(
                "Education",
                min_value=0,
                step=1
            )

            education_field = st.text_input(
                "Education Field"
            )

        st.subheader("Satisfaction & Performance")

        col1, col2, col3 = st.columns(3)

        with col1:

            environment_satisfaction = st.number_input(
                "Environment Satisfaction",
                min_value=0,
                max_value=5,
                value=3
            )

            job_involvement = st.number_input(
                "Job Involvement",
                min_value=0,
                max_value=5,
                value=3
            )

            job_satisfaction = st.number_input(
                "Job Satisfaction",
                min_value=0,
                max_value=5,
                value=3
            )

        with col2:

            relationship_satisfaction = st.number_input(
                "Relationship Satisfaction",
                min_value=0,
                max_value=5,
                value=3
            )

            work_life_balance = st.number_input(
                "Work Life Balance",
                min_value=0,
                max_value=5,
                value=3
            )

        with col3:

            total_working_years = st.number_input(
                "Total Working Years",
                min_value=0,
                step=1
            )

            training_times_last_year = st.number_input(
                "Training Times Last Year",
                min_value=0,
                step=1
            )

        st.subheader("Company History")

        col1, col2, col3 = st.columns(3)

        with col1:

            years_at_company = st.number_input(
                "Years At Company",
                min_value=0,
                step=1
            )

            years_in_current_role = st.number_input(
                "Years In Current Role",
                min_value=0,
                step=1
            )

        with col2:

            years_since_last_promotion = st.number_input(
                "Years Since Last Promotion",
                min_value=0,
                step=1
            )

            years_with_curr_manager = st.number_input(
                "Years With Current Manager",
                min_value=0,
                step=1
            )

        with col3:

            hire_date = st.date_input(
                "Hire Date",
                value=date.today()
            )

            termination_date = None

            if not is_active:

                termination_date = st.date_input(
                    "Termination Date",
                    value=date.today()
                )

        submitted = st.form_submit_button(
            "Create Employee"
        )

    if submitted:

        if not first_name.strip():

            st.error("First name is required.")

        elif not last_name.strip():

            st.error("Last name is required.")

        elif not job_role.strip():

            st.error("Job role is required.")

        elif hire_date > date.today():

            st.error(
                "Hire date cannot be in the future."
            )

        elif (
            not is_active
            and termination_date is None
        ):

            st.error(
                "Inactive employee must have a termination date."
            )

        elif (
            termination_date is not None
            and termination_date < hire_date
        ):

            st.error(
                "Termination date cannot be before "
                "the hire date."
            )

        else:

            try:

                final_termination_date = (
                    None
                    if is_active
                    else termination_date
                )

                employee = Employee(

                    first_name=first_name.strip(),

                    last_name=last_name.strip(),

                    age=int(age),

                    gender=gender,

                    marital_status=marital_status,

                    department_id=int(
                        department_id
                    ),

                    job_role=job_role.strip(),

                    job_level=int(
                        job_level
                    ),

                    monthly_income=float(
                        monthly_income
                    ),

                    daily_rate=float(
                        daily_rate
                    ),

                    hourly_rate=float(
                        hourly_rate
                    ),

                    monthly_rate=float(
                        monthly_rate
                    ),

                    percent_salary_hike=float(
                        percent_salary_hike
                    ),

                    stock_option_level=int(
                        stock_option_level
                    ),

                    over_time=int(
                        over_time
                    ),

                    business_travel=business_travel,

                    distance_from_home=int(
                        distance_from_home
                    ),

                    education=int(
                        education
                    ),

                    education_field=(
                        education_field.strip()
                    ),

                    environment_satisfaction=int(
                        environment_satisfaction
                    ),

                    job_involvement=int(
                        job_involvement
                    ),

                    job_satisfaction=int(
                        job_satisfaction
                    ),

                    relationship_satisfaction=int(
                        relationship_satisfaction
                    ),

                    work_life_balance=int(
                        work_life_balance
                    ),

                    total_working_years=int(
                        total_working_years
                    ),

                    training_times_last_year=int(
                        training_times_last_year
                    ),

                    years_at_company=int(
                        years_at_company
                    ),

                    years_in_current_role=int(
                        years_in_current_role
                    ),

                    years_since_last_promotion=int(
                        years_since_last_promotion
                    ),

                    years_with_curr_manager=int(
                        years_with_curr_manager
                    ),

                    is_active=is_active,

                    hire_date=hire_date,

                    termination_date=final_termination_date
                )

                generated_id = (
                    employee_service
                    .create_employee(employee)
                )

                st.success(
                    "Employee created successfully!"
                )

                st.info(
                    f"Automatically generated Employee ID: "
                    f"{generated_id}"
                )

            except Exception as exc:

                error_message = str(exc).lower()

                if (
                    "1452" in error_message
                    or "foreign key" in error_message
                ):

                    st.error(
                        "The Department ID does not "
                        "exist in the Departments table."
                    )

                else:

                    st.error(
                        f"Unable to create employee: {exc}"
                    )


elif operation == "Update Employee":

    st.header("✏️ Update Employee")

    employee_id = st.number_input(
        "Employee ID",
        min_value=1,
        step=1,
        value=1,
        key="update_employee_id"
    )

    if st.button(
        "Load Employee",
        type="primary"
    ):

        try:

            employee = employee_service.get_employee(
                int(employee_id)
            )

            if employee:

                st.session_state[
                    "employee_to_update"
                ] = employee

                st.session_state[
                    "loaded_employee_id"
                ] = int(employee_id)

                st.success(
                    "Employee loaded successfully."
                )

            else:

                st.warning(
                    f"Employee {employee_id} not found."
                )

        except Exception as exc:

            st.error(
                f"Unable to load employee: {exc}"
            )

    employee = st.session_state.get(
        "employee_to_update"
    )

    loaded_employee_id = st.session_state.get(
        "loaded_employee_id"
    )

    if employee:

        st.subheader(
            f"Updating Employee {loaded_employee_id}"
        )

        current_first_name = get_employee_value(
            employee,
            "FirstName",
            ""
        )

        current_last_name = get_employee_value(
            employee,
            "LastName",
            ""
        )

        current_age = get_employee_value(
            employee,
            "Age",
            25
        )

        current_gender = get_employee_value(
            employee,
            "Gender",
            "Male"
        )

        current_marital_status = get_employee_value(
            employee,
            "MaritalStatus",
            "Single"
        )

        current_department_id = get_employee_value(
            employee,
            "DepartmentID",
            1
        )

        current_job_role = get_employee_value(
            employee,
            "JobRole",
            ""
        )

        current_job_level = get_employee_value(
            employee,
            "JobLevel",
            1
        )

        current_monthly_income = get_employee_value(
            employee,
            "MonthlyIncome",
            0
        )

        current_daily_rate = get_employee_value(
            employee,
            "DailyRate",
            0
        )

        current_hourly_rate = get_employee_value(
            employee,
            "HourlyRate",
            0
        )

        current_monthly_rate = get_employee_value(
            employee,
            "MonthlyRate",
            0
        )

        current_percent_salary_hike = get_employee_value(
            employee,
            "PercentSalaryHike",
            0
        )

        current_stock_option_level = get_employee_value(
            employee,
            "StockOptionLevel",
            0
        )

        current_overtime = get_employee_value(
            employee,
            "OverTime",
            0
        )

        current_business_travel = get_employee_value(
            employee,
            "BusinessTravel",
            "Non-Travel"
        )

        current_distance_from_home = get_employee_value(
            employee,
            "DistanceFromHome",
            0
        )

        current_education = get_employee_value(
            employee,
            "Education",
            0
        )

        current_education_field = get_employee_value(
            employee,
            "EducationField",
            ""
        )

        current_environment_satisfaction = get_employee_value(
            employee,
            "EnvironmentSatisfaction",
            3
        )

        current_job_involvement = get_employee_value(
            employee,
            "JobInvolvement",
            3
        )

        current_job_satisfaction = get_employee_value(
            employee,
            "JobSatisfaction",
            3
        )

        current_relationship_satisfaction = get_employee_value(
            employee,
            "RelationshipSatisfaction",
            3
        )

        current_work_life_balance = get_employee_value(
            employee,
            "WorkLifeBalance",
            3
        )

        current_total_working_years = get_employee_value(
            employee,
            "TotalWorkingYears",
            0
        )

        current_training_times_last_year = get_employee_value(
            employee,
            "TrainingTimesLastYear",
            0
        )

        current_years_at_company = get_employee_value(
            employee,
            "YearsAtCompany",
            0
        )

        current_years_in_current_role = get_employee_value(
            employee,
            "YearsInCurrentRole",
            0
        )

        current_years_since_last_promotion = get_employee_value(
            employee,
            "YearsSinceLastPromotion",
            0
        )

        current_years_with_curr_manager = get_employee_value(
            employee,
            "YearsWithCurrManager",
            0
        )

        current_is_active = get_employee_value(
            employee,
            "IsActive",
            True
        )

        current_hire_date = get_employee_value(
            employee,
            "HireDate",
            date.today()
        )

        current_termination_date = get_employee_value(
            employee,
            "TerminationDate",
            None
        )

        try:
            current_age = int(current_age or 25)
        except (ValueError, TypeError):
            current_age = 25

        try:
            current_department_id = int(
                current_department_id or 1
            )
        except (ValueError, TypeError):
            current_department_id = 1

        try:
            current_job_level = int(
                current_job_level or 1
            )
        except (ValueError, TypeError):
            current_job_level = 1

        try:
            current_monthly_income = float(
                current_monthly_income or 0
            )
        except (ValueError, TypeError):
            current_monthly_income = 0.0

        try:
            current_daily_rate = float(
                current_daily_rate or 0
            )
        except (ValueError, TypeError):
            current_daily_rate = 0.0

        try:
            current_hourly_rate = float(
                current_hourly_rate or 0
            )
        except (ValueError, TypeError):
            current_hourly_rate = 0.0

        try:
            current_monthly_rate = float(
                current_monthly_rate or 0
            )
        except (ValueError, TypeError):
            current_monthly_rate = 0.0

        try:
            current_percent_salary_hike = float(
                current_percent_salary_hike or 0
            )
        except (ValueError, TypeError):
            current_percent_salary_hike = 0.0

        try:
            current_stock_option_level = int(
                current_stock_option_level or 0
            )
        except (ValueError, TypeError):
            current_stock_option_level = 0

        try:
            current_distance_from_home = int(
                current_distance_from_home or 0
            )
        except (ValueError, TypeError):
            current_distance_from_home = 0

        try:
            current_education = int(
                current_education or 0
            )
        except (ValueError, TypeError):
            current_education = 0

        try:
            current_environment_satisfaction = int(
                current_environment_satisfaction or 3
            )
        except (ValueError, TypeError):
            current_environment_satisfaction = 3

        try:
            current_job_involvement = int(
                current_job_involvement or 3
            )
        except (ValueError, TypeError):
            current_job_involvement = 3

        try:
            current_job_satisfaction = int(
                current_job_satisfaction or 3
            )
        except (ValueError, TypeError):
            current_job_satisfaction = 3

        try:
            current_relationship_satisfaction = int(
                current_relationship_satisfaction or 3
            )
        except (ValueError, TypeError):
            current_relationship_satisfaction = 3

        try:
            current_work_life_balance = int(
                current_work_life_balance or 3
            )
        except (ValueError, TypeError):
            current_work_life_balance = 3

        try:
            current_total_working_years = int(
                current_total_working_years or 0
            )
        except (ValueError, TypeError):
            current_total_working_years = 0

        try:
            current_training_times_last_year = int(
                current_training_times_last_year or 0
            )
        except (ValueError, TypeError):
            current_training_times_last_year = 0

        try:
            current_years_at_company = int(
                current_years_at_company or 0
            )
        except (ValueError, TypeError):
            current_years_at_company = 0

        try:
            current_years_in_current_role = int(
                current_years_in_current_role or 0
            )
        except (ValueError, TypeError):
            current_years_in_current_role = 0

        try:
            current_years_since_last_promotion = int(
                current_years_since_last_promotion or 0
            )
        except (ValueError, TypeError):
            current_years_since_last_promotion = 0

        try:
            current_years_with_curr_manager = int(
                current_years_with_curr_manager or 0
            )
        except (ValueError, TypeError):
            current_years_with_curr_manager = 0

        current_is_active = to_bool(
            current_is_active,
            True
        )

        current_hire_date = (
            to_date(current_hire_date)
            or date.today()
        )

        current_termination_date = to_date(
            current_termination_date
        )

        is_active = st.checkbox(
            "Active Employee",
            value=current_is_active,
            key=f"update_is_active_{loaded_employee_id}"
        )

        if is_active:

            st.success(
                "Employee is active. Termination Date is hidden."
            )

        else:

            st.warning(
                "Employee is inactive. Termination Date is required."
            )

        with st.form(
            "update_employee_form"
        ):

            st.subheader("Basic Information")

            col1, col2, col3 = st.columns(3)

            with col1:

                first_name = st.text_input(
                    "First Name",
                    value=str(
                        current_first_name or ""
                    )
                )

                last_name = st.text_input(
                    "Last Name",
                    value=str(
                        current_last_name or ""
                    )
                )

                age = st.number_input(
                    "Age",
                    min_value=18,
                    max_value=100,
                    value=current_age
                )

            with col2:

                gender_options = [
                    "Male",
                    "Female",
                    "Other"
                ]

                gender_index = (
                    gender_options.index(
                        current_gender
                    )
                    if current_gender in gender_options
                    else 0
                )

                gender = st.selectbox(
                    "Gender",
                    gender_options,
                    index=gender_index
                )

                marital_options = [
                    "Single",
                    "Married",
                    "Divorced"
                ]

                marital_index = (
                    marital_options.index(
                        current_marital_status
                    )
                    if current_marital_status
                    in marital_options
                    else 0
                )

                marital_status = st.selectbox(
                    "Marital Status",
                    marital_options,
                    index=marital_index
                )

                department_id = st.number_input(
                    "Department ID",
                    min_value=1,
                    value=current_department_id
                )

                job_role = st.text_input(
                    "Job Role",
                    value=str(
                        current_job_role or ""
                    )
                )

            with col3:

                job_level = st.number_input(
                    "Job Level",
                    min_value=1,
                    max_value=10,
                    value=current_job_level
                )

                monthly_income = st.number_input(
                    "Monthly Income",
                    min_value=0.0,
                    value=current_monthly_income
                )

                daily_rate = st.number_input(
                    "Daily Rate",
                    min_value=0.0,
                    value=current_daily_rate
                )

                hourly_rate = st.number_input(
                    "Hourly Rate",
                    min_value=0.0,
                    value=current_hourly_rate
                )

            st.subheader(
                "Employment Information"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                monthly_rate = st.number_input(
                    "Monthly Rate",
                    min_value=0.0,
                    value=current_monthly_rate
                )

                percent_salary_hike = st.number_input(
                    "Percent Salary Hike",
                    min_value=0.0,
                    value=current_percent_salary_hike
                )

                stock_option_level = st.number_input(
                    "Stock Option Level",
                    min_value=0,
                    value=current_stock_option_level
                )

            with col2:

                overtime_is_yes = (
                    str(current_overtime).lower()
                    in ("1", "yes", "true")
                )

                over_time_choice = st.selectbox(
                    "OverTime",
                    [
                        "Yes",
                        "No"
                    ],
                    index=0 if overtime_is_yes else 1
                )

                over_time = (
                    1
                    if over_time_choice == "Yes"
                    else 0
                )

                travel_options = [
                    "Non-Travel",
                    "Travel_Rarely",
                    "Travel_Frequently"
                ]

                travel_index = (
                    travel_options.index(
                        current_business_travel
                    )
                    if current_business_travel
                    in travel_options
                    else 0
                )

                business_travel = st.selectbox(
                    "Business Travel",
                    travel_options,
                    index=travel_index
                )

                distance_from_home = st.number_input(
                    "Distance From Home",
                    min_value=0,
                    value=current_distance_from_home
                )

            with col3:

                education = st.number_input(
                    "Education",
                    min_value=0,
                    value=current_education
                )

                education_field = st.text_input(
                    "Education Field",
                    value=str(
                        current_education_field or ""
                    )
                )

            st.subheader(
                "Satisfaction & Performance"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                environment_satisfaction = st.number_input(
                    "Environment Satisfaction",
                    min_value=0,
                    max_value=5,
                    value=current_environment_satisfaction
                )

                job_involvement = st.number_input(
                    "Job Involvement",
                    min_value=0,
                    max_value=5,
                    value=current_job_involvement
                )

                job_satisfaction = st.number_input(
                    "Job Satisfaction",
                    min_value=0,
                    max_value=5,
                    value=current_job_satisfaction
                )

            with col2:

                relationship_satisfaction = st.number_input(
                    "Relationship Satisfaction",
                    min_value=0,
                    max_value=5,
                    value=current_relationship_satisfaction
                )

                work_life_balance = st.number_input(
                    "Work Life Balance",
                    min_value=0,
                    max_value=5,
                    value=current_work_life_balance
                )

            with col3:

                total_working_years = st.number_input(
                    "Total Working Years",
                    min_value=0,
                    value=current_total_working_years
                )

                training_times_last_year = st.number_input(
                    "Training Times Last Year",
                    min_value=0,
                    value=current_training_times_last_year
                )

            st.subheader(
                "Company History"
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                years_at_company = st.number_input(
                    "Years At Company",
                    min_value=0,
                    value=current_years_at_company
                )

                years_in_current_role = st.number_input(
                    "Years In Current Role",
                    min_value=0,
                    value=current_years_in_current_role
                )

            with col2:

                years_since_last_promotion = st.number_input(
                    "Years Since Last Promotion",
                    min_value=0,
                    value=current_years_since_last_promotion
                )

                years_with_curr_manager = st.number_input(
                    "Years With Current Manager",
                    min_value=0,
                    value=current_years_with_curr_manager
                )

            with col3:

                hire_date = st.date_input(
                    "Hire Date",
                    value=current_hire_date
                )

                termination_date = None

                if not is_active:

                    termination_date = st.date_input(
                        "Termination Date",
                        value=(
                            current_termination_date
                            or date.today()
                        )
                    )

            submitted = st.form_submit_button(
                "Update Employee"
            )

        if submitted:

            if not first_name.strip():

                st.error(
                    "First name is required."
                )

            elif not last_name.strip():

                st.error(
                    "Last name is required."
                )

            elif not job_role.strip():

                st.error(
                    "Job role is required."
                )

            elif hire_date > date.today():

                st.error(
                    "Hire date cannot be in the future."
                )

            elif (
                not is_active
                and termination_date is None
            ):

                st.error(
                    "Inactive employee must have "
                    "a termination date."
                )

            elif (
                termination_date is not None
                and termination_date < hire_date
            ):

                st.error(
                    "Termination date cannot be "
                    "before the hire date."
                )

            else:

                try:

                    final_termination_date = (
                        None
                        if is_active
                        else termination_date
                    )

                    data = {

                        "first_name":
                            first_name.strip(),

                        "last_name":
                            last_name.strip(),

                        "age":
                            int(age),

                        "gender":
                            gender,

                        "marital_status":
                            marital_status,

                        "department_id":
                            int(department_id),

                        "job_role":
                            job_role.strip(),

                        "job_level":
                            int(job_level),

                        "monthly_income":
                            float(monthly_income),

                        "daily_rate":
                            float(daily_rate),

                        "hourly_rate":
                            float(hourly_rate),

                        "monthly_rate":
                            float(monthly_rate),

                        "percent_salary_hike":
                            float(percent_salary_hike),

                        "stock_option_level":
                            int(stock_option_level),

                        "over_time":
                            int(over_time),

                        "business_travel":
                            business_travel,

                        "distance_from_home":
                            int(distance_from_home),

                        "education":
                            int(education),

                        "education_field":
                            education_field.strip(),

                        "environment_satisfaction":
                            int(environment_satisfaction),

                        "job_involvement":
                            int(job_involvement),

                        "job_satisfaction":
                            int(job_satisfaction),

                        "relationship_satisfaction":
                            int(relationship_satisfaction),

                        "work_life_balance":
                            int(work_life_balance),

                        "total_working_years":
                            int(total_working_years),

                        "training_times_last_year":
                            int(training_times_last_year),

                        "years_at_company":
                            int(years_at_company),

                        "years_in_current_role":
                            int(years_in_current_role),

                        "years_since_last_promotion":
                            int(years_since_last_promotion),

                        "years_with_curr_manager":
                            int(years_with_curr_manager),

                        "is_active":
                            is_active,

                        "hire_date":
                            hire_date,

                        "termination_date":
                            final_termination_date
                    }

                    result = (
                        employee_service
                        .update_employee(
                            int(loaded_employee_id),
                            data
                        )
                    )

                    st.success(
                        "Employee updated successfully."
                    )

                    st.info(
                        f"Rows updated: {result}"
                    )

                    st.session_state.pop(
                        "employee_to_update",
                        None
                    )

                    st.session_state.pop(
                        "loaded_employee_id",
                        None
                    )

                except Exception as exc:

                    error_message = str(
                        exc
                    ).lower()

                    if (
                        "1452" in error_message
                        or "foreign key"
                        in error_message
                    ):

                        st.error(
                            "The Department ID does not "
                            "exist in the Departments table."
                        )

                    else:

                        st.error(
                            f"Unable to update employee: {exc}"
                        )


elif operation == "Delete Employee":

    st.header("🗑️ Delete Employee")

    employee_id = st.number_input(
        "Employee ID",
        min_value=1,
        step=1,
        value=1,
        key="delete_employee_id"
    )

    st.warning(
        "Deleting an employee is permanent."
    )

    confirm = st.checkbox(
        "I confirm that I want to delete this employee."
    )

    if st.button(
        "Delete Employee",
        type="primary"
    ):

        if not confirm:

            st.error(
                "Please confirm deletion first."
            )

        else:

            try:

                result = (
                    employee_service
                    .delete_employee(
                        int(employee_id)
                    )
                )

                if result:

                    st.success(
                        f"Employee {employee_id} "
                        "deleted successfully."
                    )

                else:

                    st.warning(
                        "Employee was not deleted."
                    )

            except Exception as exc:

                error_message = str(
                    exc
                ).lower()

                if (
                    "1451" in error_message
                    or "foreign key constraint"
                    in error_message
                    or "cannot delete or update"
                    in error_message
                ):

                    st.error(
                        "This employee cannot be deleted "
                        "because they are linked to existing "
                        "assignment records."
                    )

                    st.info(
                        "Use Update Employee to mark this "
                        "employee as inactive instead."
                    )

                elif (
                    "not found" in error_message
                    or "does not exist" in error_message
                ):

                    st.warning(
                        f"Employee {employee_id} "
                        "does not exist."
                    )

                else:

                    st.error(
                        f"Unable to delete employee: {exc}"
                    )