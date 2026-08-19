class Department:

    def __init__(
        self,
        department_id=None,
        department_name=None
    ):

        self.department_id = department_id
        self.department_name = department_name

    def to_dict(self):

        return self.__dict__.copy()