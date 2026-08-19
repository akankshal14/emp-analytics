from backend.repositories.kpi_repository import KPIRepository


class KPIService:
    """
    Service layer mapping repository calls for the 3 Core KPIs.
    """

    def __init__(self):
        self.kpi_repo = KPIRepository()

    # KPI 1: Employee Lookup & Individual YoY Performance
    def get_employee_lookup_list(self):
        return self.kpi_repo.get_employee_lookup_list()

    def get_individual_yoy_performance(self, employee_id: int):
        return self.kpi_repo.get_individual_yoy_performance(employee_id=employee_id)

    # Optional Aggregate YoY (if needed for executive summary card)
    def get_year_over_year_performance(self):
        return self.kpi_repo.get_year_over_year_performance()

    # KPI 2: Top Performers
    def get_top_performers_by_department(self, top_n: int = 5):
        return self.kpi_repo.get_top_performers_by_department(top_n=top_n)

    # KPI 3: Attrition Rate Summary & Department Detail
    def get_attrition_rate_summary(self):
        return self.kpi_repo.get_attrition_rate_summary()

    def get_attrition_by_department(self):
        return self.kpi_repo.get_attrition_by_department()