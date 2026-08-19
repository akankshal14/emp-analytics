import streamlit as st


st.set_page_config(
    page_title="Enterprise Employee Analytics",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .hero {
        padding: 25px 30px;
        border-radius: 14px;
        background: linear-gradient(
            135deg,
            #1f2937,
            #111827
        );
        border: 1px solid #374151;
        margin-bottom: 25px;
    }

    .hero h1 {
        margin-bottom: 8px;
        font-size: 34px;
    }

    .hero p {
        color: #d1d5db;
        font-size: 16px;
        margin-bottom: 0;
    }

    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .module-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #374151;
        background-color: #1f2937;
        min-height: 125px;
        margin-bottom: 15px;
    }

    .module-card h3 {
        margin-top: 0;
        font-size: 18px;
    }

    .module-card p {
        color: #9ca3af;
        font-size: 14px;
    }

    .architecture-card {
        padding: 18px;
        text-align: center;
        border-radius: 12px;
        border: 1px solid #374151;
        background-color: #111827;
        min-height: 100px;
    }

    .architecture-card h4 {
        margin-bottom: 8px;
    }

    .architecture-card p {
        color: #9ca3af;
        margin: 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HERO SECTION
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🏢 Enterprise Employee Analytics</h1>
        <p>
            Centralized employee management, project tracking,
            performance monitoring and executive analytics.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# QUICK INTRODUCTION
# =========================================================

st.markdown(
    '<div class="section-title">Welcome 👋</div>',
    unsafe_allow_html=True
)

st.write(
    """
    Use the sidebar to access employee management, departments,
    projects, assignments, reviews and analytics.
    """
)


# =========================================================
# CORE MODULES
# =========================================================

st.markdown(
    '<div class="section-title">Core Modules</div>',
    unsafe_allow_html=True
)


col1, col2, col3 = st.columns(3)


with col1:

    st.markdown(
        """
        <div class="module-card">
            <h3>👨‍💼 Employee Management</h3>
            <p>
                Manage employee records, details and employment status.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="module-card">
            <h3>📁 Project Management</h3>
            <p>
                Create and manage organizational projects.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        """
        <div class="module-card">
            <h3>🏢 Department Management</h3>
            <p>
                Manage departments and organizational structure.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="module-card">
            <h3>🔗 Project Assignments</h3>
            <p>
                Track employee allocation across projects.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        """
        <div class="module-card">
            <h3>⭐ Employee Reviews</h3>
            <p>
                Track employee performance reviews and evaluations.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="module-card">
            <h3>📊 Analytics & Dashboard</h3>
            <p>
                Analyze performance, attrition and executive KPIs.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# SYSTEM ARCHITECTURE
# =========================================================

st.divider()


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Enterprise Employee Analytics & Data Warehouse"
)