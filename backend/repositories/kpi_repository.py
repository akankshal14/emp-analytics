import pandas as pd

from backend.database.db_manager import DatabaseConnection
from backend.exceptions import DatabaseException
from backend.utils.logger import get_logger


logger = get_logger(__name__)


class KPIRepository:
    """
    Repository executing the 3 core KPI queries against the OLAP Star Schema.
    """

    def __init__(self):
        self.db = DatabaseConnection()
        logger.info("KPIRepository initialized for 3 core KPIs.")

    
    def _execute_to_df(
        self,
        query_str: str,
        params: dict = None
    ) -> pd.DataFrame:
        """
        Execute SQL query using the existing cursor-based
        DatabaseConnection and return the result as a DataFrame.
        """

        cursor = None

        try:
            cursor = self.db.get_cursor(database="olap")

            # Convert named parameter :top_n to MySQL connector %s
            if params:
                query_str = query_str.replace(":top_n", "%s")

                cursor.execute(
                    query_str,
                    tuple(params.values())
                )
            else:
                cursor.execute(query_str)

            records = cursor.fetchall()

            if cursor.description:
                columns = [
                    description[0]
                    for description in cursor.description
                ]
            else:
                columns = []

            return pd.DataFrame(
                records,
                columns=columns
            )

        except Exception as exc:
            logger.exception(
                "Failed to execute KPI query."
            )

            raise DatabaseException(
                f"Failed to execute KPI query: {exc}"
            ) from exc

        finally:
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    pass

    # ============================================================
    # KPI 1: YEAR-OVER-YEAR PERFORMANCE TREND
    # ============================================================
    def get_year_over_year_performance(self) -> pd.DataFrame:
        """
        KPI 1 (Aggregate):

        Tracks company-wide average performance rating
        and review volume across years.

        Tables:
            - fact_performancereviews
            - dim_date
        """

        query = """
            SELECT
                d.Year AS PerformanceYear,

                ROUND(
                    AVG(f.PerformanceRating),
                    2
                ) AS AveragePerformance,

                COUNT(
                    DISTINCT f.EmployeeSK
                ) AS EmployeeCount,

                COUNT(
                    f.PerformanceReviewSK
                ) AS ReviewCount

            FROM fact_performancereviews f

            INNER JOIN dim_date d
                ON f.ReviewDateKey = d.DateKey

            WHERE f.PerformanceRating IS NOT NULL

            GROUP BY d.Year

            ORDER BY d.Year ASC;
        """

        return self._execute_to_df(query)

    # ============================================================
    # KPI 2: TOP PERFORMERS BY DEPARTMENT
    # ============================================================
    def get_top_performers_by_department(
        self,
        top_n: int = 5
    ) -> pd.DataFrame:
        """
        KPI 2:

        Identifies the top-performing employees within
        each department based on average performance rating.

        Raw performance rating is not returned to the UI.

        Tables:
            - fact_performancereviews
            - dim_employee
            - dim_department
        """

        query = """
            WITH EmployeePerformance AS (

                SELECT
                    dep.DepartmentName,

                    e.EmployeeID,

                    CONCAT(
                        'Employee #',
                        e.EmployeeID
                    ) AS EmployeeName,

                    e.JobRole,

                    AVG(
                        f.PerformanceRating
                    ) AS RawPerf

                FROM fact_performancereviews f

                INNER JOIN dim_employee e
                    ON f.EmployeeSK = e.EmployeeSK

                INNER JOIN dim_department dep
                    ON f.DepartmentSK = dep.DepartmentSK

                WHERE f.PerformanceRating IS NOT NULL

                  AND e.IsCurrent = 1

                GROUP BY
                    dep.DepartmentName,
                    e.EmployeeID,
                    e.JobRole
            ),

            RankedEmployees AS (

                SELECT
                    DepartmentName,
                    EmployeeID,
                    EmployeeName,
                    JobRole,

                    DENSE_RANK() OVER (
                        PARTITION BY DepartmentName
                        ORDER BY
                            RawPerf DESC,
                            EmployeeID ASC
                    ) AS DepartmentRank

                FROM EmployeePerformance
            )

            SELECT
                DepartmentName,
                EmployeeID,
                EmployeeName,
                JobRole,
                DepartmentRank

            FROM RankedEmployees

            WHERE DepartmentRank <= :top_n

            ORDER BY
                DepartmentName ASC,
                DepartmentRank ASC;
        """

        return self._execute_to_df(
            query,
            params={
                "top_n": top_n
            }
        )

    # ============================================================
    # KPI 3: EMPLOYEE ATTRITION RATE SUMMARY
    # ============================================================
    def get_attrition_rate_summary(self) -> pd.DataFrame:
        """
        KPI 3 (Summary):

        Calculates organization-wide:

        - Total employees
        - Attrited employees
        - Overall attrition rate

        Table:
            - dim_employee
        """

        query = """
            SELECT

                COUNT(
                    DISTINCT EmployeeID
                ) AS TotalEmployees,

                COUNT(
                    DISTINCT CASE
                        WHEN IsActive = 0
                             OR UPPER(Attrition) = 'YES'
                        THEN EmployeeID
                    END
                ) AS AttritedEmployees,

                ROUND(

                    COUNT(
                        DISTINCT CASE
                            WHEN IsActive = 0
                                 OR UPPER(Attrition) = 'YES'
                            THEN EmployeeID
                        END
                    ) * 100.0

                    / NULLIF(
                        COUNT(
                            DISTINCT EmployeeID
                        ),
                        0
                    ),

                    2

                ) AS AttritionRate

            FROM dim_employee

            WHERE IsCurrent = 1;
        """

        return self._execute_to_df(query)

    # ============================================================
    # KPI 3: ATTRITION BY DEPARTMENT
    # ============================================================
    def get_attrition_by_department(self) -> pd.DataFrame:
        """
        KPI 3 (Detail):

        Calculates employee attrition rate for each department.

        Tables:
            - dim_employee
            - fact_performancereviews
            - dim_department
        """

        query = """
            SELECT

                dep.DepartmentName,

                COUNT(
                    DISTINCT e.EmployeeID
                ) AS TotalEmployees,

                COUNT(
                    DISTINCT CASE
                        WHEN e.IsActive = 0
                             OR UPPER(e.Attrition) = 'YES'
                        THEN e.EmployeeID
                    END
                ) AS AttritedEmployees,

                ROUND(

                    COUNT(
                        DISTINCT CASE
                            WHEN e.IsActive = 0
                                 OR UPPER(e.Attrition) = 'YES'
                            THEN e.EmployeeID
                        END
                    ) * 100.0

                    / NULLIF(
                        COUNT(
                            DISTINCT e.EmployeeID
                        ),
                        0
                    ),

                    2

                ) AS AttritionRate

            FROM dim_employee e

            INNER JOIN fact_performancereviews f
                ON e.EmployeeSK = f.EmployeeSK

            INNER JOIN dim_department dep
                ON f.DepartmentSK = dep.DepartmentSK

            WHERE e.IsCurrent = 1

            GROUP BY
                dep.DepartmentName

            ORDER BY
                AttritionRate DESC;
        """

        return self._execute_to_df(query)