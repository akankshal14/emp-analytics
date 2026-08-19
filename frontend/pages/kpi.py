import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.services.kpi_service import KPIService

st.set_page_config(
    page_title="Core HR Executive Analytics",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for spacing and full-sized charts
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .stMetric {
        background-color: #1E222D;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2D313E;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_kpi_service():
    return KPIService()


service = get_kpi_service()


@st.cache_data(ttl=300)
def load_employee_lookup():
    return service.get_employee_lookup_list()


@st.cache_data(ttl=300)
def load_individual_yoy_data(emp_id):
    return service.get_individual_yoy_performance(emp_id)


@st.cache_data(ttl=300)
def load_yoy_data():
    return service.get_year_over_year_performance()


@st.cache_data(ttl=300)
def load_top_performers_data(top_n):
    return service.get_top_performers_by_department(top_n)


@st.cache_data(ttl=300)
def load_attrition_summary_data():
    return service.get_attrition_rate_summary()


@st.cache_data(ttl=300)
def load_attrition_dept_data():
    return service.get_attrition_by_department()


st.title(":bar_chart: Core Executive HR Dashboard")

st.markdown(
    "Focused analytics covering **Performance Trends**, "
    "**Top Performers**, and **Departmental Attrition**."
)

st.sidebar.title(":gear: Dashboard Controls")
st.sidebar.markdown("Use controls below to adjust chart filtering.")

if st.sidebar.button(":arrows_counterclockwise: Refresh Data Cache"):
    st.cache_data.clear()
    st.rerun()


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

st.header(":pushpin: Executive Summary")

with st.spinner("Loading executive overview..."):
    attr_summary_df = load_attrition_summary_data()

if not attr_summary_df.empty:

    col1, col2, col3 = st.columns(3)

    total_emp = attr_summary_df["TotalEmployees"].iloc[0]
    attr_emp = attr_summary_df["AttritedEmployees"].iloc[0]
    attr_rate = attr_summary_df["AttritionRate"].iloc[0]

    col1.metric(
        ":busts_in_silhouette: Total Active Headcount",
        f"{total_emp:,}"
    )

    col2.metric(
        ":chart_with_downwards_trend: Total Attrited Employees",
        f"{attr_emp:,}"
    )

    col3.metric(
        ":bar_chart: Overall Attrition Rate",
        f"{attr_rate:.2f}%"
    )

else:
    st.warning("Could not load executive summary metrics.")


st.divider()


# ============================================================
# TABS
# ============================================================

tabs = st.tabs([
    ":chart_with_upwards_trend: 1. YoY Performance Trend",
    ":trophy: 2. Top Performers by Dept",
    ":chart_with_downwards_trend: 3. Employee Attrition Rate"
])


# ============================================================
# TAB 1: YEAR-OVER-YEAR PERFORMANCE TREND
# ============================================================

with tabs[0]:

    st.header(":one: Year-over-Year Performance & Review Volume Trend")

    st.caption(
        "Tracks company-wide performance rating trajectories alongside "
        "review evaluation volumes across years."
    )

    yoy_df = load_yoy_data()

    if yoy_df.empty:

        st.info("No YoY performance data available.")

    else:

        yoy_df["PerformanceYear"] = pd.to_numeric(
            yoy_df["PerformanceYear"],
            errors="coerce"
        ).astype(int)

        # Optional Year Range Filter
        years = sorted(
            yoy_df["PerformanceYear"].unique()
        )

        if len(years) > 1:

            selected_range = st.slider(
                "Filter Year Range",
                min_value=min(years),
                max_value=max(years),
                value=(min(years), max(years)),
                key="yoy_year_slider"
            )

            filtered_yoy = yoy_df[
                yoy_df["PerformanceYear"].between(
                    selected_range[0],
                    selected_range[1]
                )
            ]

        else:

            filtered_yoy = yoy_df

        # ====================================================
        # DUAL-AXIS PLOTLY CHART
        # ====================================================

        fig_yoy = go.Figure()

        # Review Evaluation Volume Bars
        fig_yoy.add_trace(
            go.Bar(
                x=filtered_yoy["PerformanceYear"],
                y=filtered_yoy["ReviewCount"],
                name="Total Reviews Evaluated",
                marker_color="#1E88E5",
                opacity=0.35,
                yaxis="y2"
            )
        )

        # Average Performance Trajectory Line
        fig_yoy.add_trace(
            go.Scatter(
                x=filtered_yoy["PerformanceYear"],
                y=filtered_yoy["AveragePerformance"],
                mode="lines+markers+text",
                name="Avg Performance Rating",
                text=filtered_yoy["AveragePerformance"].astype(str),
                textposition="top center",
                line=dict(
                    color="#00E676",
                    width=4
                ),
                marker=dict(
                    size=10
                )
            )
        )

        fig_yoy.update_layout(
            height=520,
            margin=dict(
                l=40,
                r=40,
                t=30,
                b=40
            ),
            template="plotly_dark",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                title="Calendar Year",
                tickmode="linear",
                dtick=1
            ),
            yaxis=dict(
                title="Average Performance Rating (1-5)",
                range=[0, 5.5]
            ),
            yaxis2=dict(
                title="Total Reviews Evaluated",
                overlaying="y",
                side="right",
                showgrid=False
            )
        )

        st.plotly_chart(
            fig_yoy,
            use_container_width=True
        )

        # Raw Aggregated Summary Data
        with st.expander(
            ":mag: View Raw YoY Aggregate Performance Table"
        ):

            st.dataframe(
                filtered_yoy,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# TAB 2: TOP PERFORMERS BY DEPARTMENT
# ============================================================

with tabs[1]:

    st.header(
        ":trophy: Departmental Top Performers Leaderboard"
    )

    st.caption(
        "Displays the top ranked employees per department "
        "based on evaluation history."
    )

    col_ctrl1, col_ctrl2 = st.columns([1, 2])

    with col_ctrl1:

        top_n = st.selectbox(
            "Top N Ranks to Display",
            [3, 5, 10],
            index=0,
            key="top_n_select"
        )

    top_df = load_top_performers_data(top_n)

    if top_df.empty:

        st.info("No top performer data available.")

    else:

        departments = sorted(
            top_df["DepartmentName"]
            .dropna()
            .unique()
            .tolist()
        )

        with col_ctrl2:

            selected_dept = st.selectbox(
                "Filter Department",
                ["All Departments"] + departments,
                key="top_dept_select"
            )

        if selected_dept != "All Departments":

            filtered_top = top_df[
                top_df["DepartmentName"] == selected_dept
            ].copy()

        else:

            filtered_top = top_df.copy()

        # ====================================================
        # CLEAN EMPLOYEE IDENTIFIER LABEL
        # ====================================================

        filtered_top["EmployeeLabel"] = (
            filtered_top["EmployeeName"]
            + " (ID: #"
            + filtered_top["EmployeeID"].astype(str)
            + ") - "
            + filtered_top["JobRole"]
        )

        # Reversely scale rank for plotting
        # so Rank 1 appears first
        max_rank = (
            filtered_top["DepartmentRank"].max() + 1
        )

        filtered_top["InvertedRank"] = (
            max_rank
            - filtered_top["DepartmentRank"]
        )

        # ====================================================
        # RANK-BASED DOT CHART
        # ====================================================

        fig_leaderboard = px.scatter(
            filtered_top.sort_values(
                ["DepartmentName", "DepartmentRank"],
                ascending=[True, False]
            ),
            x="DepartmentRank",
            y="EmployeeLabel",
            color="DepartmentName",
            size_max=18,
            symbol="DepartmentRank",
            title="Employee Departmental Rank Placement",
            labels={
                "DepartmentRank": "Department Rank Position",
                "EmployeeLabel": "Employee Details",
                "DepartmentName": "Department"
            },
            template="plotly_dark"
        )

        fig_leaderboard.update_traces(
            marker=dict(
                size=14,
                line=dict(
                    width=2,
                    color="White"
                )
            ),
            selector=dict(
                mode="markers"
            )
        )

        fig_leaderboard.update_layout(
            height=max(
                450,
                len(filtered_top) * 35
            ),
            margin=dict(
                l=40,
                r=40,
                t=40,
                b=40
            ),
            xaxis=dict(
                title="Department Rank Placement "
                      "(1 = Highest Performer)",
                tickmode="linear",
                dtick=1,
                autorange="reversed"
            ),
            yaxis=dict(
                title="Employee"
            )
        )

        st.plotly_chart(
            fig_leaderboard,
            use_container_width=True
        )

        # ====================================================
        # CLEAN TABLE
        # ====================================================

        st.subheader(
            ":clipboard: Top Performer Directory"
        )

        clean_table = filtered_top[
            [
                "DepartmentRank",
                "EmployeeID",
                "EmployeeName",
                "JobRole",
                "DepartmentName"
            ]
        ].rename(
            columns={
                "DepartmentRank": "Rank Position",
                "EmployeeID": "Employee ID",
                "EmployeeName": "Full Name",
                "JobRole": "Job Role",
                "DepartmentName": "Department"
            }
        )

        st.dataframe(
            clean_table,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# TAB 3: EMPLOYEE ATTRITION RATE
# ============================================================

with tabs[2]:

    st.header(
        ":three: Employee Attrition Rate by Department"
    )

    st.caption(
        "Evaluates percentage employee turnover across "
        "departments against a threshold limit."
    )

    attr_dept_df = load_attrition_dept_data()

    if attr_dept_df.empty:

        st.info("No attrition data available.")

    else:

        threshold = st.slider(
            "Highlight Attrition Warning Threshold (%)",
            0.0,
            50.0,
            15.0,
            step=1.0,
            key="attr_thresh"
        )

        # ====================================================
        # ATTRITION BAR CHART
        # ====================================================

        fig_attr = px.bar(
            attr_dept_df.sort_values(
                "AttritionRate",
                ascending=False
            ),
            x="DepartmentName",
            y="AttritionRate",
            text="AttritionRate",
            color="AttritionRate",
            color_continuous_scale="Reds",
            title="Departmental Attrition Comparison",
            labels={
                "DepartmentName": "Department",
                "AttritionRate": "Attrition Rate (%)"
            },
            template="plotly_dark"
        )

        fig_attr.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )

        fig_attr.add_hline(
            y=threshold,
            line_dash="dash",
            line_color="yellow",
            annotation_text=(
                f"Warning Threshold ({threshold:.1f}%)"
            ),
            annotation_position="top left"
        )

        fig_attr.update_layout(
            height=520,
            margin=dict(
                l=40,
                r=40,
                t=40,
                b=40
            ),
            yaxis=dict(
                range=[
                    0,
                    max(
                        attr_dept_df["AttritionRate"].max() + 5,
                        threshold + 10
                    )
                ]
            )
        )

        st.plotly_chart(
            fig_attr,
            use_container_width=True
        )

        # ====================================================
        # HIGH ATTRITION DEPARTMENTS
        # ====================================================

        high_attrition = attr_dept_df[
            attr_dept_df["AttritionRate"] >= threshold
        ]

        if not high_attrition.empty:

            st.subheader(
                ":warning: Departments Exceeding Attrition Threshold"
            )

            st.dataframe(
                high_attrition,
                use_container_width=True,
                hide_index=True
            )

        # ====================================================
        # COMPLETE DEPARTMENT ATTRITION TABLE
        # ====================================================

        with st.expander(
            ":mag: View Complete Department Attrition Table"
        ):

            st.dataframe(
                attr_dept_df,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Employee Analytics Data Warehouse | "
    "Restricted 3 Core KPI Module"
)