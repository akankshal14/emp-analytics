# HR Analytics Data Pipeline & Streamlit Dashboard

## Project Overview
Running heavy analytical queries and complex reporting directly on live operational databases can severely degrade daily business operations. This project implements a **Dual-Database Architecture** (OLTP + OLAP) that isolates high-frequency operational transactions from analytical workloads.

Using a dataset of **100,000 synthetic HR records**, the system handles daily operational workflows while delivering sub-second business intelligence reporting through a pre-aggregated Star Schema Data Warehouse and an interactive Streamlit Dashboard.

## Architecture & System Design
<img width="2072" height="283" alt="Architecture-Page-8 drawio (1)" src="https://github.com/user-attachments/assets/4c667594-deaa-4015-9834-7ccbd52a7dff" />

Here is a breakdown of how data moves through the system:

### 1. Ingestion Layer
This layer is responsible for the initial data extraction and loading. 
* **Components:** A raw `CSV File` (100,000 synthetic records) and a Python-based `Ingestion Script` (Pandas + SQLAlchemy).
* **Function:** It reads the CSV in memory-safe chunks and pushes the raw data directly into the database staging area, preventing system crashes during bulk loads.

### 2. Presentation Layer
This is the front-end user interface where users interact with the system.
* **Components:** Streamlit `Dashboards & Forms`.
* **Function:** Renders the interactive KPIs, charts, and data entry forms. It passes user inputs (like a salary update) down to the Service Layer.

### 3. Service Layer
The "brain" of the application that sits between the UI and the database.
* **Components:** `Business Logic & Rules`.
* **Function:** Validates user inputs and enforces business rules before any data touches the database. For example, it ensures a new salary is not a negative number before passing the request forward.

### 4. Data Access Layer
This layer handles all direct communication with the database to keep SQL queries out of the UI and Service layers.
* **Components:** `Repositories & DTOs` (Data Transfer Objects) and a `Connection Singleton`.
* **Function:** Repositories contain the actual SQL execution code. The Connection Singleton ensures the application reuses database connections efficiently without exhausting MySQL's connection limits during UI refreshes.

### 5. Database Engine
The robust MySQL backend handling both operational workflows and analytical reporting.
* **Components & Flow:** 
  * **Staging Area:** Holds the raw, un-normalized data from the Ingestion Layer.
  * **3NF Operational Schema (OLTP):** The highly normalized relational tables (Employees, Departments) optimized for daily, real-time CRUD operations.
  * **ETL Stored Procedures:** The transformation routines (`sp_load_dimensions` and `sp_load_fact_performance`) which are called directly and sequentially to process the data.
  * **Star Schema Warehouse (OLAP):** The dimensional database (Fact and Dimension tables) optimized for lightning-fast reads and historical tracking (SCD Type 2).
 
    Key Features & Highlights
Memory-Safe Ingestion: Safely processes 100,000+ CSV rows using Pandas chunking and SQLAlchemy bulk inserts to prevent memory spikes.

Dual-Database Isolation: Separates write-optimized operational workflows (3NF OLTP) from high-speed analytical reporting (Star Schema OLAP).

SCD Type 2 Tracking: Preserves historical employee changes (like salary bumps or promotions) using active flags and effective dates.

Singleton Connection Manager: Efficiently reuses database connections to prevent exhaustion during UI refreshes and auto-heals broken sockets.

Core Business Intelligence Metrics

The Streamlit dashboard queries pre-aggregated warehouse views to display 8 key HR analytics KPIs:

Year-over-Year Performance Trends: Historical tracking of employee evaluation scores.

Top Performers by Department: High-performer ranking across business units for succession planning.

Employee Attrition Rate: Turnover analysis sliced by department, tenure, and overtime status.

Tech Stack
Database Engine: MySQL Server 8.0+

Core Language: Python 3.9+

Database Connectors: mysql-connector-python, SQLAlchemy, PyMySQL

Data Processing: Pandas, NumPy, MySQL Stored Procedures (CTEs & Window Functions)

Frontend & Visualization: Streamlit, Plotly

## Setup & Installation Guide

### Prerequisites
* **Python 3.9+** installed.
* **MySQL Server 8.0+** running locally or remotely.
* **Git** command-line tools.

---

### Step 1: Clone Repository & Virtual Environment

```bash
# Clone repository
git clone <repository-url>
cd <repository-folder>

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

Configure Environment Variables
Create a .env file in the project root directory:

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_OLTP=mini_project
DB_OLAP=mini_project_olap

Initialize Database Schemas & Stored Procedures
Open your MySQL client (Workbench, DBeaver, or CLI) and run the script files in order:

# Or execute directly via MySQL CLI:
mysql -u root -p < database/scripts/01_create_oltp_schema.sql
mysql -u root -p < database/scripts/02_create_olap_schema.sql

Run Data Ingestion & ETL Pipeline
Ingest Synthetic CSV into MySQL Staging (stg_employees):
python -m backend.ingestion.dataset_generation

Launch the Streamlit Dashboard

streamlit run app.py



