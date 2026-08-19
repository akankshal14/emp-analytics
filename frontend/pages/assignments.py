import sys
from pathlib import Path
from datetime import date

# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# IMPORTS
# =========================================================

import streamlit as st

from utils.helpers import records_to_dataframe

from backend.services.assignment_service import AssignmentService
from backend.models.assignment import Assignment


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Assignments",
    page_icon="🔗",
    layout="wide"
)


# =========================================================
# TITLE
# =========================================================

st.title("🔗 Employee Project Assignments")


# =========================================================
# SERVICE
# =========================================================

service = AssignmentService()


# =========================================================
# SIDEBAR
# =========================================================


st.subheader("Select Action")

operation = st.radio(
    "Employee Operations",
    [
        
        "Assign Employee",
        "Update Assignment",
        "View Assignments"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()


# =========================================================
# VIEW ASSIGNMENTS
# =========================================================

if operation == "View Assignments":

    st.header("📋 Employee Project Assignments")

    try:

        assignments = service.get_all_assignments()

        if not assignments:

            st.info(
                "No assignments found."
            )

        else:

            df = records_to_dataframe(
                assignments
            )

            st.metric(
                "Total Assignments",
                len(df)
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

    except Exception as exc:

        st.error(
            f"Unable to load assignments: {exc}"
        )


# =========================================================
# CREATE ASSIGNMENT
# =========================================================

elif operation == "Assign Employee":

    st.header("➕ Assign Employee to Project")

    with st.form("assignment_form"):

        employee_id = st.number_input(
            "Employee ID",
            min_value=1,
            step=1,
            value=1
        )

        project_id = st.number_input(
            "Project ID",
            min_value=1,
            step=1,
            value=1
        )

        allocation_percentage = st.slider(
            "Allocation Percentage",
            min_value=1,
            max_value=100,
            value=100
        )

        start_date = st.date_input(
            "Assignment Start Date",
            value=date.today()
        )

        end_date = st.date_input(
            "Assignment End Date",
            value=date.today()
        )

        role_in_project = st.text_input(
            "Project Role"
        )

        submitted = st.form_submit_button(
            "Create Assignment",
            use_container_width=True
        )

    if submitted:

        try:

            if end_date < start_date:

                st.error(
                    "End date cannot be before start date."
                )

            else:

                assignment = Assignment(

                    employee_id=int(
                        employee_id
                    ),

                    project_id=int(
                        project_id
                    ),

                    role_in_project=role_in_project,

                    allocation_percentage=int(
                        allocation_percentage
                    ),

                    start_date=start_date,

                    end_date=end_date
                )

                assignment_id = (
                    service.create_assignment(
                        assignment
                    )
                )

                st.success(
                    f"Employee assigned successfully. "
                    f"Assignment ID: {assignment_id}"
                )

        except Exception as exc:

            st.error(
                f"Unable to create assignment: {exc}"
            )


# =========================================================
# UPDATE ASSIGNMENT
# =========================================================

elif operation == "Update Assignment":

    st.header("✏️ Update Assignment")

    assignment_id = st.number_input(
        "Assignment ID",
        min_value=1,
        step=1,
        value=1
    )

    # =====================================================
    # LOAD ASSIGNMENT
    # =====================================================

    if st.button(
        "Load Assignment",
        type="primary"
    ):

        try:

            assignment = service.get_assignment(
                int(assignment_id)
            )

            if assignment:

                st.session_state[
                    "assignment_to_update"
                ] = assignment

                st.session_state[
                    "loaded_assignment_id"
                ] = int(
                    assignment_id
                )

                st.success(
                    f"Assignment {assignment_id} "
                    "loaded successfully."
                )

            else:

                st.warning(
                    "Assignment not found."
                )

        except Exception as exc:

            st.error(
                f"Unable to load assignment: {exc}"
            )


    # =====================================================
    # GET LOADED ASSIGNMENT
    # =====================================================

    assignment = st.session_state.get(
        "assignment_to_update"
    )

    loaded_assignment_id = st.session_state.get(
        "loaded_assignment_id"
    )


    # =====================================================
    # UPDATE FORM
    # =====================================================

    if (
        assignment is not None
        and loaded_assignment_id is not None
    ):

        # -------------------------------------------------
        # HELPER TO READ Assignment OBJECT / DICT
        # -------------------------------------------------

        def get_value(
            name,
            default=None
        ):

            # Assignment object
            if isinstance(
                assignment,
                Assignment
            ):

                return getattr(
                    assignment,
                    name,
                    default
                )


            # Dictionary
            if isinstance(
                assignment,
                dict
            ):

                if name in assignment:

                    return assignment[name]

                mappings = {

                    "assignment_id":
                        "AssignmentID",

                    "employee_id":
                        "EmployeeID",

                    "project_id":
                        "ProjectID",

                    "role_in_project":
                        "RoleInProject",

                    "allocation_percentage":
                        "AllocationPercentage",

                    "start_date":
                        "StartDate",

                    "end_date":
                        "EndDate"
                }

                db_key = mappings.get(
                    name
                )

                if (
                    db_key
                    and db_key in assignment
                ):

                    return assignment[
                        db_key
                    ]

                return default


            # Tuple / List
            if isinstance(
                assignment,
                (tuple, list)
            ):

                index_mapping = {

                    "assignment_id": 0,

                    "employee_id": 1,

                    "project_id": 2,

                    "role_in_project": 3,

                    "allocation_percentage": 4,

                    "start_date": 5,

                    "end_date": 6
                }

                index = index_mapping.get(
                    name
                )

                if (
                    index is not None
                    and index < len(assignment)
                ):

                    return assignment[
                        index
                    ]

                return default


            return getattr(
                assignment,
                name,
                default
            )


        # =================================================
        # CURRENT VALUES
        # =================================================

        current_employee_id = get_value(
            "employee_id",
            1
        )

        current_project_id = get_value(
            "project_id",
            1
        )

        current_role = get_value(
            "role_in_project",
            ""
        )

        current_allocation = get_value(
            "allocation_percentage",
            100
        )

        current_start_date = get_value(
            "start_date",
            date.today()
        )

        current_end_date = get_value(
            "end_date",
            date.today()
        )


        # =================================================
        # SAFE EMPLOYEE ID
        # =================================================

        try:

            current_employee_id = int(
                current_employee_id
            )

        except (
            TypeError,
            ValueError
        ):

            current_employee_id = 1


        # =================================================
        # SAFE PROJECT ID
        # =================================================

        try:

            current_project_id = int(
                current_project_id
            )

        except (
            TypeError,
            ValueError
        ):

            current_project_id = 1


        # =================================================
        # SAFE ALLOCATION
        # =================================================

        try:

            current_allocation = int(
                current_allocation
            )

        except (
            TypeError,
            ValueError
        ):

            current_allocation = 100


        current_allocation = max(
            1,
            min(
                100,
                current_allocation
            )
        )


        # =================================================
        # SAFE ROLE
        # =================================================

        if current_role is None:

            current_role = ""

        else:

            current_role = str(
                current_role
            )


        # =================================================
        # SAFE START DATE
        # =================================================

        if current_start_date is None:

            current_start_date = date.today()

        elif hasattr(
            current_start_date,
            "date"
        ):

            current_start_date = (
                current_start_date.date()
            )


        # =================================================
        # SAFE END DATE
        # =================================================

        if current_end_date is None:

            current_end_date = (
                current_start_date
            )

        elif hasattr(
            current_end_date,
            "date"
        ):

            current_end_date = (
                current_end_date.date()
            )


        # =================================================
        # DISPLAY CURRENT ASSIGNMENT
        # =================================================

        st.subheader(
            f"Updating Assignment "
            f"{loaded_assignment_id}"
        )

        st.info(
            f"Employee ID: {current_employee_id} | "
            f"Project ID: {current_project_id}"
        )


        # =================================================
        # FORM
        # =================================================

        with st.form(
            "update_assignment_form"
        ):

            allocation_percentage = st.slider(
                "Allocation Percentage",
                min_value=1,
                max_value=100,
                value=current_allocation
            )

            role_in_project = st.text_input(
                "Project Role",
                value=current_role
            )

            start_date = st.date_input(
                "Assignment Start Date",
                value=current_start_date
            )

            end_date = st.date_input(
                "Assignment End Date",
                value=current_end_date
            )

            submitted = st.form_submit_button(
                "Update Assignment",
                use_container_width=True
            )


        # =================================================
        # SAVE UPDATE
        # =================================================

        if submitted:

            try:

                if end_date < start_date:

                    st.error(
                        "End date cannot be before "
                        "start date."
                    )

                else:

                    updated_assignment = Assignment(

                        assignment_id=int(
                            loaded_assignment_id
                        ),

                        employee_id=int(
                            current_employee_id
                        ),

                        project_id=int(
                            current_project_id
                        ),

                        role_in_project=(
                            role_in_project
                        ),

                        allocation_percentage=int(
                            allocation_percentage
                        ),

                        start_date=start_date,

                        end_date=end_date
                    )


                    # IMPORTANT
                    # Object-based service call

                    service.update_assignment(
                        int(
                            loaded_assignment_id
                        ),
                        updated_assignment
                    )


                    st.success(
                        f"Assignment "
                        f"{loaded_assignment_id} "
                        "updated successfully."
                    )


                    # Clear loaded assignment

                    st.session_state.pop(
                        "assignment_to_update",
                        None
                    )

                    st.session_state.pop(
                        "loaded_assignment_id",
                        None
                    )


            except Exception as exc:

                st.error(
                    f"Unable to update assignment: {exc}"
                )


# =========================================================
# DELETE ASSIGNMENT
# =========================================================

elif operation == "Delete Assignment":

    st.header("🗑️ Delete Assignment")

    assignment_id = st.number_input(
        "Assignment ID",
        min_value=1,
        step=1,
        value=1
    )

    st.warning(
        "Deleting an assignment is permanent."
    )

    confirm = st.checkbox(
        "I confirm that I want to delete this assignment."
    )


    if st.button(
        "Delete Assignment",
        type="primary"
    ):

        if not confirm:

            st.error(
                "Please confirm deletion."
            )

        else:

            try:

                result = service.delete_assignment(
                    int(
                        assignment_id
                    )
                )

                if result:

                    st.success(
                        f"Assignment "
                        f"{assignment_id} "
                        "deleted successfully."
                    )

                else:

                    st.warning(
                        "Assignment was not deleted."
                    )

            except Exception as exc:

                st.error(
                    f"Unable to delete assignment: {exc}"
                )