
import sys
from pathlib import Path
from datetime import date, datetime

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

from backend.services.project_service import ProjectService
from backend.models.project import Project


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Projects",
    page_icon="📁",
    layout="wide"
)


# =========================================================
# SERVICE
# =========================================================

service = ProjectService()


# =========================================================
# PAGE TITLE
# =========================================================

st.title("📁 Project Management")

st.caption(
    "Create, view, update and delete project records."
)


# =========================================================
# SIDEBAR
# =========================================================

st.subheader("Select Action")

operation = st.radio(
    "Employee Operations",
    [
        "Add Project",
        "Update Project",
        "Search Project",
        "View Projects"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

# =========================================================
# HELPER
# =========================================================

def project_to_dict(project):
    """
    Converts project result returned from repository/service
    into a dictionary.

    Supports:
    - dict
    - named tuple
    - normal tuple/list
    - Project object
    """

    # -----------------------------------------------------
    # Dictionary
    # -----------------------------------------------------

    if isinstance(project, dict):

        return {
            key: value
            for key, value in project.items()
        }


    # -----------------------------------------------------
    # Named tuple / Row object
    # -----------------------------------------------------

    if hasattr(project, "_asdict"):

        return dict(
            project._asdict()
        )


    # -----------------------------------------------------
    # Project model/object
    # -----------------------------------------------------

    if hasattr(project, "__dict__"):

        data = {}

        for key, value in vars(project).items():

            if not key.startswith("_"):

                data[key] = value

        if data:

            return data


    # -----------------------------------------------------
    # Tuple / List
    # -----------------------------------------------------

    if isinstance(
        project,
        (tuple, list)
    ):

        data = {}

        if len(project) > 0:
            data["ProjectID"] = project[0]

        if len(project) > 1:
            data["ProjectName"] = project[1]

        if len(project) > 2:
            data["StartDate"] = project[2]

        if len(project) > 3:
            data["EndDate"] = project[3]

        if len(project) > 4:
            data["Status"] = project[4]

        return data


    return {
        "Project": project
    }


# =========================================================
# 1. VIEW ALL PROJECTS
# =========================================================

if operation == "View Projects":

    st.header("📋 All Projects")

    try:

        projects = service.get_all_projects()

        # -------------------------------------------------
        # No records
        # -------------------------------------------------

        if not projects:

            st.info(
                "No projects found."
            )

        else:

            # -------------------------------------------------
            # Convert every record safely
            # -------------------------------------------------

            project_rows = []

            for project in projects:

                project_rows.append(
                    project_to_dict(project)
                )


            df = records_to_dataframe(
                project_rows
            )


            st.metric(
                "Total Projects",
                len(df)
            )


            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

    except Exception as exc:

        st.error(
            f"Unable to load projects: {exc}"
        )


# =========================================================
# 2. VIEW SINGLE PROJECT
# =========================================================

elif operation == "Search Project":

    st.header("🔍 Find Project")


    # -----------------------------------------------------
    # PROJECT ID
    # -----------------------------------------------------

    project_id = st.number_input(
        "Project ID",
        min_value=1,
        step=1,
        value=1,
        key="view_project_id"
    )


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if st.button(
        "Search Project",
        type="primary",
        key="search_project_button"
    ):

        try:

            project_id = int(
                project_id
            )


            # -------------------------------------------------
            # SERVICE CALL
            # -------------------------------------------------

            project = service.get_project(
                project_id
            )


            # -------------------------------------------------
            # NOT FOUND
            # -------------------------------------------------

            if project is None:

                st.warning(
                    f"Project ID {project_id} was not found."
                )


            else:

                st.success(
                    f"Project {project_id} found successfully."
                )


                # -------------------------------------------------
                # Convert to dictionary
                # -------------------------------------------------

                project_data = project_to_dict(
                    project
                )


                # -------------------------------------------------
                # Display project
                # -------------------------------------------------

                st.subheader(
                    "Project Details"
                )


                df = records_to_dataframe(
                    [project_data]
                )


                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )


                # -------------------------------------------------
                # Optional clean display
                # -------------------------------------------------

                col1, col2 = st.columns(2)


                with col1:

                    project_name = (
                        project_data.get(
                            "ProjectName",
                            project_data.get(
                                "project_name",
                                ""
                            )
                        )
                    )

                    st.write(
                        f"**Project Name:** {project_name}"
                    )


                    start_date = (
                        project_data.get(
                            "StartDate",
                            project_data.get(
                                "start_date",
                                ""
                            )
                        )
                    )

                    st.write(
                        f"**Start Date:** {start_date}"
                    )


                with col2:

                    status = (
                        project_data.get(
                            "Status",
                            project_data.get(
                                "status",
                                ""
                            )
                        )
                    )

                    st.write(
                        f"**Status:** {status}"
                    )


                    end_date = (
                        project_data.get(
                            "EndDate",
                            project_data.get(
                                "end_date",
                                ""
                            )
                        )
                    )

                    st.write(
                        f"**End Date:** {end_date}"
                    )


        except Exception as exc:

            st.error(
                f"Unable to find project: {exc}"
            )


# =========================================================
# 3. ADD PROJECT
# =========================================================

elif operation == "Add Project":

    st.header("➕ Add Project")

    with st.form(
        "create_project"
    ):

        project_name = st.text_input(
            "Project Name"
        )

        start_date = st.date_input(
            "Start Date",
            value=date.today()
        )

        end_date = st.date_input(
            "End Date",
            value=None
        )

        status = st.selectbox(
            "Status",
            [
                "Planned",
                "Active",
                "Completed",
                "Cancelled"
            ],
            index=1
        )

        submitted = st.form_submit_button(
            "Create Project"
        )


    # =====================================================
    # CREATE
    # =====================================================

    if submitted:

        if not project_name.strip():

            st.error(
                "Project name is required."
            )

        elif (
            end_date is not None
            and end_date < start_date
        ):

            st.error(
                "End date cannot be before start date."
            )

        else:

            try:

                project = Project(

                    project_name=(
                        project_name.strip()
                    ),

                    start_date=start_date,

                    end_date=end_date,

                    status=status
                )


                result = (
                    service
                    .create_project(
                        project
                    )
                )


                st.success(
                    "Project created successfully."
                )


                st.info(
                    f"Created Project ID: {result}"
                )


                st.session_state.pop(
                    "project_to_update",
                    None
                )

                st.session_state.pop(
                    "loaded_project_id",
                    None
                )


            except Exception as exc:

                st.error(
                    f"Unable to create project: {exc}"
                )


# =========================================================
# 4. UPDATE PROJECT
# =========================================================

elif operation == "Update Project":

    st.header("✏️ Update Project")


    project_id = st.number_input(
        "Project ID",
        min_value=1,
        step=1,
        value=1,
        key="update_project_id_input"
    )


    # =====================================================
    # LOAD PROJECT
    # =====================================================

    if st.button(
        "Load Project",
        type="primary"
    ):

        try:

            project_id = int(
                project_id
            )


            project = service.get_project(
                project_id
            )


            if project:

                st.session_state[
                    "project_to_update"
                ] = project

                st.session_state[
                    "loaded_project_id"
                ] = project_id


                st.success(
                    f"Project {project_id} "
                    "loaded successfully."
                )

            else:

                st.warning(
                    "Project not found."
                )


        except Exception as exc:

            st.error(
                f"Unable to load project: {exc}"
            )


    # =====================================================
    # GET LOADED PROJECT
    # =====================================================

    project = st.session_state.get(
        "project_to_update"
    )

    loaded_project_id = st.session_state.get(
        "loaded_project_id"
    )


    # =====================================================
    # UPDATE FORM
    # =====================================================

    if (
        project is not None
        and loaded_project_id is not None
    ):

        st.info(
            f"Editing Project ID: "
            f"{loaded_project_id}"
        )


        # -------------------------------------------------
        # Convert project to dictionary
        # -------------------------------------------------

        project_data = project_to_dict(
            project
        )


        current_name = project_data.get(
            "ProjectName",
            project_data.get(
                "project_name",
                ""
            )
        )


        current_start_date = project_data.get(
            "StartDate",
            project_data.get(
                "start_date",
                date.today()
            )
        )


        current_end_date = project_data.get(
            "EndDate",
            project_data.get(
                "end_date",
                None
            )
        )


        current_status = project_data.get(
            "Status",
            project_data.get(
                "status",
                "Active"
            )
        )


        # -------------------------------------------------
        # Convert datetime to date
        # -------------------------------------------------

        if (
            current_start_date
            and hasattr(
                current_start_date,
                "date"
            )
        ):

            current_start_date = (
                current_start_date.date()
            )


        if (
            current_end_date
            and hasattr(
                current_end_date,
                "date"
            )
        ):

            current_end_date = (
                current_end_date.date()
            )


        if current_start_date is None:

            current_start_date = date.today()


        statuses = [
            "Planned",
            "Active",
            "Completed",
            "Cancelled"
        ]


        if current_status not in statuses:

            current_status = "Active"


        # =================================================
        # FORM
        # =================================================

        with st.form(
            "update_project"
        ):

            project_name = st.text_input(
                "Project Name",
                value=str(
                    current_name or ""
                )
            )


            start_date = st.date_input(
                "Start Date",
                value=current_start_date
            )


            end_date = st.date_input(
                "End Date",
                value=current_end_date
            )


            status = st.selectbox(
                "Status",
                statuses,
                index=statuses.index(
                    current_status
                )
            )


            submitted = st.form_submit_button(
                "Update Project"
            )


        # =================================================
        # UPDATE
        # =================================================

        if submitted:

            if not project_name.strip():

                st.error(
                    "Project name is required."
                )

            elif (
                end_date is not None
                and end_date < start_date
            ):

                st.error(
                    "End date cannot be before "
                    "start date."
                )

            else:

                try:

                    data = {

                        "project_name":
                            project_name.strip(),

                        "start_date":
                            start_date,

                        "end_date":
                            end_date,

                        "status":
                            status
                    }


                    result = (
                        service
                        .update_project(
                            int(
                                loaded_project_id
                            ),
                            data
                        )
                    )


                    if result > 0:

                        st.success(
                            f"Project "
                            f"{loaded_project_id} "
                            "updated successfully."
                        )


                        st.info(
                            f"Rows updated: {result}"
                        )


                    else:

                        st.warning(
                            "No project was updated."
                        )


                    st.session_state.pop(
                        "project_to_update",
                        None
                    )

                    st.session_state.pop(
                        "loaded_project_id",
                        None
                    )


                except Exception as exc:

                    st.error(
                        f"Unable to update project: "
                        f"{exc}"
                    )


# =========================================================
# 5. DELETE PROJECT
# =========================================================

elif operation == "Delete Project":

    st.header("🗑️ Delete Project")


    project_id = st.number_input(
        "Project ID",
        min_value=1,
        step=1,
        value=1,
        key="delete_project_id_input"
    )


    st.warning(
        "Deleting a project is permanent."
    )


    confirm = st.checkbox(
        "I confirm that I want to delete this project."
    )


    if st.button(
        "Delete Project",
        type="primary"
    ):

        if not confirm:

            st.error(
                "Please confirm deletion first."
            )

        else:

            try:

                result = (
                    service
                    .delete_project(
                        int(project_id)
                    )
                )


                if result > 0:

                    st.success(
                        f"Project {int(project_id)} "
                        "deleted successfully."
                    )


                else:

                    st.warning(
                        "No project was deleted."
                    )


            except Exception as exc:

                error_message = str(
                    exc
                )


                if (
                    "1451" in error_message
                    or
                    "foreign key constraint"
                    in error_message.lower()
                ):

                    st.error(
                        f"Project {int(project_id)} "
                        "cannot be permanently deleted."
                    )


                    st.warning(
                        "This project has assignment "
                        "records associated with it."
                    )


                    st.info(
                        "To preserve assignment history, "
                        "change the project status to "
                        "'Cancelled' instead of deleting it."
                    )


                else:

                    st.error(
                        f"Unable to delete project: "
                        f"{exc}"
                    )