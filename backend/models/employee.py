class Employee:

    def __init__(
        self,
        employee_id=None,
        first_name=None,
        last_name=None,
        age=None,
        gender=None,
        marital_status=None,
        department_id=None,
        job_role=None,
        job_level=None,
        monthly_income=None,
        daily_rate=None,
        hourly_rate=None,
        monthly_rate=None,
        percent_salary_hike=None,
        stock_option_level=None,
        over_time=None,
        business_travel=None,
        distance_from_home=None,
        education=None,
        education_field=None,
        environment_satisfaction=None,
        job_involvement=None,
        job_satisfaction=None,
        relationship_satisfaction=None,
        work_life_balance=None,
        total_working_years=None,
        training_times_last_year=None,
        years_at_company=None,
        years_in_current_role=None,
        years_since_last_promotion=None,
        years_with_curr_manager=None,
        is_active=True,
        hire_date=None,
        termination_date=None
    ):


        self.employee_id = employee_id

        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.gender = gender
        self.marital_status = marital_status

        self.department_id = department_id
        self.job_role = job_role
        self.job_level = job_level

        self.monthly_income = monthly_income
        self.daily_rate = daily_rate
        self.hourly_rate = hourly_rate
        self.monthly_rate = monthly_rate

        self.percent_salary_hike = percent_salary_hike
        self.stock_option_level = stock_option_level

        self.over_time = over_time
        self.business_travel = business_travel
        self.distance_from_home = distance_from_home

        self.education = education
        self.education_field = education_field

        self.environment_satisfaction = (
            environment_satisfaction
        )

        self.job_involvement = job_involvement
        self.job_satisfaction = job_satisfaction

        self.relationship_satisfaction = (
            relationship_satisfaction
        )

        self.work_life_balance = work_life_balance

        self.total_working_years = (
            total_working_years
        )

        self.training_times_last_year = (
            training_times_last_year
        )

        self.years_at_company = (
            years_at_company
        )

        self.years_in_current_role = (
            years_in_current_role
        )

        self.years_since_last_promotion = (
            years_since_last_promotion
        )

        self.years_with_curr_manager = (
            years_with_curr_manager
        )

        self.is_active = is_active

        self.hire_date = hire_date
        self.termination_date = termination_date

    

    def get_full_name(self):

        return (
            f"{self.first_name} "
            f"{self.last_name}"
        )

    

    def to_dict(self):

        return self.__dict__.copy()