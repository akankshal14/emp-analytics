import sys
from pathlib import Path

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
from backend.services.department_service import DepartmentService


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Departments",
    page_icon="🏢",
    layout="wide"
)


# =========================================================
# SERVICE
# =========================================================

service = DepartmentService()


# =========================================================
# PAGE TITLE
# =========================================================

st.title("🏢 Department Management")


# =========================================================
# SIDEBAR
# =========================================================

operation = st.radio(
    "Employee Operations",
    [
       
        "Add Department",
        "Update Department",
        "View Departments",
        "Search Department"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_department_value(
    department,
    field,
    default=None
):
    """
    Safely extracts a department field from:
    - dictionary
    - named tuple
    - tuple/list
    - object
    """

    if department is None:
        return default

    # -----------------------------------------------------
    # Dictionary
    # -----------------------------------------------------

    if isinstance(department, dict):

        if field in department:
            return department[field]

        field_lower = field.lower()

        for key, value in department.items():

            if str(key).lower() == field_lower:
                return value

        mappings = {
            "department_id": "DepartmentID",
            "department_name": "DepartmentName"
        }

        db_key = mappings.get(field)

        if db_key in department:
            return department[db_key]

        return default

    # -----------------------------------------------------
    # Named tuple
    # -----------------------------------------------------

    if hasattr(department, "_asdict"):

        row = department._asdict()

        if field in row:
            return row[field]

        field_lower = field.lower()

        for key, value in row.items():

            if str(key).lower() == field_lower:
                return value

        mappings = {
            "department_id": "DepartmentID",
            "department_name": "DepartmentName"
        }

        db_key = mappings.get(field)

        if db_key in row:
            return row[db_key]

        return default

    # -----------------------------------------------------
    # Tuple / List
    # -----------------------------------------------------

    if isinstance(
        department,
        (tuple, list)
    ):

        index_mapping = {
            "department_id": 0,
            "department_name": 1
        }

        index = index_mapping.get(field)

        if (
            index is not None
            and index < len(department)
        ):

            return department[index]

        return default

    # -----------------------------------------------------
    # Object
    # -----------------------------------------------------

    return getattr(
        department,
        field,
        default
    )


def department_to_dict(department):
    """
    Converts a department result into
    a consistent dictionary.
    """

    return {
        "DepartmentID": get_department_value(
            department,
            "department_id"
        ),
        "DepartmentName": get_department_value(
            department,
            "department_name"
        )
    }


# =========================================================
# VIEW ALL DEPARTMENTS
# =========================================================

if operation == "View Departments":

    st.header("📋 All Departments")

    try:

        departments = service.get_all_departments()

        if not departments:

            st.info(
                "No departments found."
            )

        else:

            df = records_to_dataframe(
                departments
            )

            st.metric(
                "Total Departments",
                len(df)
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

    except Exception as exc:

        st.error(
            f"Unable to load departments: {exc}"
        )


# =========================================================
# VIEW SINGLE DEPARTMENT
# =========================================================

elif operation == "Search Department":

    st.header("🔍 Find Department")

    department_id = st.number_input(
        "Department ID",
        min_value=1,
        step=1,
        value=1
    )

    if st.button(
        "Search Department",
        type="primary"
    ):

        try:

            department = service.get_department(
                int(department_id)
            )

            if department:

                data = department_to_dict(
                    department
                )

                st.success(
                    f"Department {int(department_id)} found."
                )

                st.dataframe(
                    records_to_dataframe(
                        [data]
                    ),
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.warning(
                    f"Department {int(department_id)} "
                    "was not found."
                )

        except Exception as exc:

            st.error(
                f"Unable to find department: {exc}"
            )


# =========================================================
# ADD DEPARTMENT
# =========================================================

elif operation == "Add Department":

    st.header("➕ Add Department")

    with st.form(
        "department_create"
    ):

        department_name = st.text_input(
            "Department Name"
        )

        submitted = st.form_submit_button(
            "Create Department",
            use_container_width=True
        )

    if submitted:

        department_name = (
            department_name.strip()
        )

        if not department_name:

            st.error(
                "Department name is required."
            )

        else:

            try:

                result = service.create_department(
                    department_name
                )

                st.success(
                    "Department created successfully."
                )

                if result is not None:

                    st.info(
                        f"Created Department ID: {result}"
                    )

            except Exception as exc:

                error_message = str(exc)

                if (
                    "Duplicate" in error_message
                    or "already exists" in error_message
                    or "1062" in error_message
                ):

                    st.error(
                        "A department with this name "
                        "already exists."
                    )

                else:

                    st.error(
                        f"Unable to create department: {exc}"
                    )


# =========================================================
# UPDATE DEPARTMENT
# =========================================================

elif operation == "Update Department":

    st.header("✏️ Update Department")

    # -----------------------------------------------------
    # Department ID
    # -----------------------------------------------------

    department_id = st.number_input(
        "Department ID",
        min_value=1,
        step=1,
        value=1,
        key="update_department_id"
    )


    # =====================================================
    # LOAD DEPARTMENT
    # =====================================================

    if st.button(
        "Load Department",
        type="primary",
        key="load_department_button"
    ):

        try:

            department = service.get_department(
                int(department_id)
            )

            if department:

                department_data = (
                    department_to_dict(
                        department
                    )
                )

                st.session_state[
                    "department_to_update"
                ] = department_data

                st.success(
                    f"Department {int(department_id)} "
                    "loaded successfully."
                )

            else:

                st.session_state.pop(
                    "department_to_update",
                    None
                )

                st.warning(
                    f"Department {int(department_id)} "
                    "was not found."
                )

        except Exception as exc:

            st.error(
                f"Unable to load department: {exc}"
            )


    # =====================================================
    # UPDATE FORM
    # =====================================================

    department = st.session_state.get(
        "department_to_update"
    )

    if department:

        loaded_id = department[
            "DepartmentID"
        ]

        current_name = department[
            "DepartmentName"
        ]

        if current_name is None:
            current_name = ""

        current_name = str(
            current_name
        )

        st.subheader(
            f"Editing Department {loaded_id}"
        )

        st.info(
            f"Department ID: {loaded_id}"
        )

        with st.form(
            "department_update_form"
        ):

            department_name = st.text_input(
                "Department Name",
                value=current_name
            )

            submitted = st.form_submit_button(
                "Update Department",
                use_container_width=True
            )


        # =================================================
        # UPDATE
        # =================================================

        if submitted:

            department_name = (
                department_name.strip()
            )

            if not department_name:

                st.error(
                    "Department name is required."
                )

            else:

                try:

                    result = (
                        service.update_department(
                            int(loaded_id),
                            department_name
                        )
                    )

                    if result:

                        st.success(
                            f"Department {loaded_id} "
                            "updated successfully."
                        )

                        st.info(
                            f"Rows updated: {result}"
                        )

                        # Clear loaded department

                        st.session_state.pop(
                            "department_to_update",
                            None
                        )

                    else:

                        st.warning(
                            "No department was updated."
                        )

                except Exception as exc:

                    error_message = str(exc)

                    if (
                        "Duplicate" in error_message
                        or "already exists" in error_message
                        or "1062" in error_message
                    ):

                        st.error(
                            "Another department with "
                            "this name already exists."
                        )

                    else:

                        st.error(
                            f"Unable to update department: "
                            f"{exc}"
                        )


# =========================================================
# DELETE DEPARTMENT
# =========================================================

elif operation == "Delete Department":

    st.header("🗑️ Delete Department")

    department_id = st.number_input(
        "Department ID",
        min_value=1,
        step=1,
        value=1,
        key="delete_department_id"
    )

    st.warning(
        "Deleting a department is permanent."
    )

    confirm = st.checkbox(
        "I confirm that I want to delete this department.",
        key="delete_department_confirmation"
    )


    if st.button(
        "Delete Department",
        type="primary",
        key="delete_department_button"
    ):

        if not confirm:

            st.error(
                "Please confirm deletion first."
            )

        else:

            try:

                result = (
                    service.delete_department(
                        int(department_id)
                    )
                )

                if result:

                    st.success(
                        f"Department {int(department_id)} "
                        "deleted successfully."
                    )

                else:

                    st.warning(
                        "No department was deleted. "
                        "The department may not exist."
                    )

            except Exception as exc:

                error_message = str(exc)

                # -----------------------------------------
                # Foreign key constraint
                # -----------------------------------------

                if (
                    "1451" in error_message
                    or "foreign key constraint"
                    in error_message.lower()
                    or "cannot delete or update a parent row"
                    in error_message.lower()
                ):

                    st.error(
                        "This department cannot be deleted "
                        "because employees are currently "
                        "assigned to this department."
                    )

                    st.info(
                        "Reassign or remove those employees "
                        "first, then try deleting the department."
                    )

                else:

                    st.error(
                        f"Unable to delete department: {exc}"
                    )