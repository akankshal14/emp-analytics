
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

from backend.services.review_service import ReviewService
from backend.models.review import Review
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Reviews",
    page_icon="⭐",
    layout="wide"
)


# =========================================================
# PAGE TITLE
# =========================================================

st.title("⭐ Employee Reviews")


# =========================================================
# SERVICE
# =========================================================

service = ReviewService()


# =========================================================
# SIDEBAR
# =========================================================

st.subheader("Select Action")

operation = st.radio(
    "Employee Operations",
    [
        
        
        "Add Review",
        "Update Review",
        "View Reviews"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()
# =========================================================
# VIEW REVIEWS
# =========================================================

# if operation == "View Reviews":

#     st.header("📋 Employee Reviews")

#     try:

#         reviews = service.get_all_reviews()

#         if not reviews:

#             st.info(
#                 "No reviews found."
#             )

#         else:

#             df = pd.DataFrame(reviews)

#             st.metric(
#                 "Total Reviews",
#                 len(df)
#             )

#             st.dataframe(
#                 df,
#                 width="stretch",
#                 hide_index=True
#             )

#     except Exception as exc:

#         st.error(
#             f"Unable to load reviews: {exc}"
#         )
if operation == "View Reviews":

    st.header("📋 Employee Reviews")

    try:

        reviews = service.get_all_reviews()

        if not reviews:

            st.info(
                "No reviews found."
            )

        else:

            # Convert database records directly
            # into a DataFrame.
            df = records_to_dataframe(
                reviews
            )

            # Make sure ReviewID and EmployeeID
            # are displayed as numeric values.
            for column in [
                "ReviewID",
                "EmployeeID",
                "PerformanceRating",
                "ReviewerID"
            ]:

                if column in df.columns:

                    df[column] = pd.to_numeric(
                        df[column],
                        errors="coerce"
                    )

            st.metric(
                "Total Reviews",
                len(df)
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

    except Exception as exc:

        st.error(
            f"Unable to load reviews: {exc}"
        )

# =========================================================
# ADD REVIEW
# =========================================================

elif operation == "Add Review":

    st.header("➕ Add Employee Review")

    with st.form("create_review"):

        employee_id = st.number_input(
            "Employee ID",
            min_value=1,
            step=1,
            value=1
        )

        review_date = st.date_input(
            "Review Date",
            value=date.today()
        )

        performance_rating = st.slider(
            "Performance Rating",
            min_value=1,
            max_value=5,
            value=3
        )

        reviewer_id = st.number_input(
            "Reviewer ID",
            min_value=1,
            step=1,
            value=1
        )

        comments = st.text_area(
            "Comments"
        )

        # IMPORTANT:
        # Do NOT use width="stretch" here.
        submitted = st.form_submit_button(
            "Create Review"
        )

    if submitted:

        try:

            if employee_id < 1:

                st.error(
                    "Valid Employee ID is required."
                )

            elif reviewer_id < 1:

                st.error(
                    "Valid Reviewer ID is required."
                )

            else:

                review = Review(
                    employee_id=int(employee_id),
                    review_date=review_date,
                    performance_rating=int(
                        performance_rating
                    ),
                    reviewer_id=int(reviewer_id),
                    comments=comments
                )

                review_id = service.create_review(
                    review
                )

                st.success(
                    f"Review created successfully. "
                    f"Review ID: {review_id}"
                )

        except Exception as exc:

            st.error(
                f"Unable to create review: {exc}"
            )


# =========================================================
# UPDATE REVIEW
# =========================================================

elif operation == "Update Review":

    st.header("✏️ Update Review")

    review_id = st.number_input(
        "Review ID",
        min_value=1,
        step=1,
        value=1
    )


    # =====================================================
    # LOAD REVIEW
    # =====================================================

    if st.button(
        "Load Review",
        type="primary"
    ):

        try:

            review = service.get_review(
                int(review_id)
            )

            if review:

                st.session_state[
                    "review_to_update"
                ] = review

                st.session_state[
                    "loaded_review_id"
                ] = int(review_id)

                st.success(
                    f"Review {review_id} loaded successfully."
                )

            else:

                st.warning(
                    "Review not found."
                )

        except Exception as exc:

            st.error(
                f"Unable to load review: {exc}"
            )


    # =====================================================
    # GET LOADED REVIEW
    # =====================================================

    review = st.session_state.get(
        "review_to_update"
    )

    loaded_review_id = st.session_state.get(
        "loaded_review_id"
    )


    # =====================================================
    # UPDATE FORM
    # =====================================================

    if (
        review is not None
        and loaded_review_id is not None
    ):

        # -------------------------------------------------
        # Helper function
        # -------------------------------------------------

        def get_review_value(
            name,
            default=None
        ):

            # Dictionary result
            if isinstance(
                review,
                dict
            ):

                # Exact key
                if name in review:

                    return review[name]

                # Case-insensitive key
                for key in review.keys():

                    if (
                        str(key).lower()
                        == name.lower()
                    ):

                        return review[key]

                # Database column mappings
                mappings = {

                    "review_id":
                        "ReviewID",

                    "employee_id":
                        "EmployeeID",

                    "review_date":
                        "ReviewDate",

                    "performance_rating":
                        "PerformanceRating",

                    "reviewer_id":
                        "ReviewerID",

                    "comments":
                        "Comments"
                }

                db_key = mappings.get(
                    name
                )

                if (
                    db_key
                    and db_key in review
                ):

                    return review[db_key]

                return default


            # -------------------------------------------------
            # Tuple/list result
            #
            # SELECT order:
            #
            # 0 ReviewID
            # 1 EmployeeID
            # 2 ReviewDate
            # 3 PerformanceRating
            # 4 ReviewerID
            # 5 Comments
            # -------------------------------------------------

            if isinstance(
                review,
                (tuple, list)
            ):

                index_mapping = {

                    "review_id": 0,

                    "employee_id": 1,

                    "review_date": 2,

                    "performance_rating": 3,

                    "reviewer_id": 4,

                    "comments": 5
                }

                index = index_mapping.get(
                    name
                )

                if (
                    index is not None
                    and index < len(review)
                ):

                    return review[index]

                return default


            # -------------------------------------------------
            # Object result
            # -------------------------------------------------

            return getattr(
                review,
                name,
                default
            )


        # =====================================================
        # CURRENT VALUES
        # =====================================================

        current_employee_id = get_review_value(
            "employee_id",
            0
        )

        current_review_date = get_review_value(
            "review_date",
            date.today()
        )

        current_performance_rating = (
            get_review_value(
                "performance_rating",
                3
            )
        )

        current_reviewer_id = get_review_value(
            "reviewer_id",
            None
        )

        current_comments = get_review_value(
            "comments",
            ""
        )


        # =====================================================
        # SAFE EMPLOYEE ID
        # =====================================================

        try:

            current_employee_id = int(
                current_employee_id
            )

        except (
            TypeError,
            ValueError
        ):

            current_employee_id = 1


        # =====================================================
        # SAFE REVIEWER ID
        #
        # ReviewerID may be NULL in MySQL.
        # Therefore DO NOT blindly call int(None).
        # =====================================================

        if current_reviewer_id is None:

            current_reviewer_id = 0

        else:

            try:

                current_reviewer_id = int(
                    current_reviewer_id
                )

            except (
                TypeError,
                ValueError
            ):

                current_reviewer_id = 0


        # =====================================================
        # SAFE PERFORMANCE RATING
        # =====================================================

        try:

            current_performance_rating = int(
                current_performance_rating
            )

        except (
            TypeError,
            ValueError
        ):

            current_performance_rating = 3


        if current_performance_rating < 1:

            current_performance_rating = 1

        if current_performance_rating > 5:

            current_performance_rating = 5


        # =====================================================
        # SAFE REVIEW DATE
        # =====================================================

        if current_review_date is None:

            current_review_date = date.today()

        elif hasattr(
            current_review_date,
            "date"
        ):

            current_review_date = (
                current_review_date.date()
            )


        # =====================================================
        # SAFE COMMENTS
        # =====================================================

        if current_comments is None:

            current_comments = ""

        else:

            current_comments = str(
                current_comments
            )


        # =====================================================
        # DISPLAY
        # =====================================================

        st.subheader(
            f"Updating Review {loaded_review_id}"
        )


        # =====================================================
        # UPDATE FORM
        # =====================================================

        with st.form(
            "update_review"
        ):

            employee_id = st.number_input(
                "Employee ID",
                min_value=1,
                value=current_employee_id,
                step=1,
                disabled=True
            )

            review_date = st.date_input(
                "Review Date",
                value=current_review_date,
                disabled=True
            )

            performance_rating = st.slider(
                "Performance Rating",
                min_value=1,
                max_value=5,
                value=current_performance_rating
            )

            # -------------------------------------------------
            # Reviewer ID
            #
            # 0 means NULL / no reviewer.
            # -------------------------------------------------

            reviewer_id = st.number_input(
                "Reviewer ID",
                min_value=0,
                value=current_reviewer_id,
                step=1
            )

            comments = st.text_area(
                "Comments",
                value=current_comments
            )

            # IMPORTANT:
            # No width="stretch"
            submitted = st.form_submit_button(
                "Update Review"
            )


        # =====================================================
        # UPDATE
        # =====================================================

        if submitted:

            try:

                # ---------------------------------------------
                # Convert reviewer ID 0 -> None
                # ---------------------------------------------

                if reviewer_id == 0:

                    final_reviewer_id = None

                else:

                    final_reviewer_id = int(
                        reviewer_id
                    )


                updated_review = Review(

                    review_id=int(
                        loaded_review_id
                    ),

                    employee_id=int(
                        employee_id
                    ),

                    review_date=review_date,

                    performance_rating=int(
                        performance_rating
                    ),

                    reviewer_id=final_reviewer_id,

                    comments=comments
                )


                service.update_review(
                    int(loaded_review_id),
                    updated_review
                )


                st.success(
                    f"Review {loaded_review_id} "
                    "updated successfully."
                )


                # ---------------------------------------------
                # Clear cached review
                # ---------------------------------------------

                if (
                    "review_to_update"
                    in st.session_state
                ):

                    del st.session_state[
                        "review_to_update"
                    ]


                if (
                    "loaded_review_id"
                    in st.session_state
                ):

                    del st.session_state[
                        "loaded_review_id"
                    ]


            except Exception as exc:

                st.error(
                    f"Unable to update review: {exc}"
                )


# =========================================================
# DELETE REVIEW
# =========================================================

elif operation == "Delete Review":

    st.header("🗑️ Delete Review")

    review_id = st.number_input(
        "Review ID",
        min_value=1,
        step=1,
        value=1
    )

    st.warning(
        "Deleting a review is permanent."
    )

    confirm = st.checkbox(
        "I confirm that I want to delete this review."
    )


    if st.button(
        "Delete Review",
        type="primary"
    ):

        if not confirm:

            st.error(
                "Please confirm deletion first."
            )

        else:

            try:

                result = service.delete_review(
                    int(review_id)
                )

                if result:

                    st.success(
                        f"Review {review_id} "
                        "deleted successfully."
                    )

                else:

                    st.warning(
                        "Review was not deleted."
                    )

            except Exception as exc:

                st.error(
                    f"Unable to delete review: {exc}"
                )