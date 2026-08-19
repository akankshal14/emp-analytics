class Project:

    def __init__(
        self,
        project_id=None,
        project_name=None,
        start_date=None,
        end_date=None,
        status="Active"
    ):

        self.project_id = project_id
        self.project_name = project_name
        self.start_date = start_date
        self.end_date = end_date
        self.status = status

    def to_dict(self):

        return self.__dict__.copy()