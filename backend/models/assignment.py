class Assignment:

    def __init__(
        self,
        assignment_id=None,
        employee_id=None,
        project_id=None,
        role_in_project=None,
        allocation_percentage=None,
        start_date=None,
        end_date=None
    ):

        self.assignment_id = assignment_id
        self.employee_id = employee_id
        self.project_id = project_id
        self.role_in_project = role_in_project
        self.allocation_percentage = allocation_percentage
        self.start_date = start_date
        self.end_date = end_date

    def to_dict(self):

        return self.__dict__.copy()