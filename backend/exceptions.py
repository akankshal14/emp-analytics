
class AppException(Exception):
    """
    Base exception for application-specific errors.
    """

    def __init__(
        self,
        message="Application error."
    ):
        self.message = message
        super().__init__(message)



class DatabaseException(AppException):
    """
    Raised when a database operation fails.
    """

    def __init__(
        self,
        message="Database error."
    ):
        super().__init__(message)



class BadRequestException(AppException):
    """
    Raised when the client provides invalid input.
    """

    def __init__(
        self,
        message="Bad request."
    ):
        super().__init__(message)




class NotFoundException(AppException):
    """
    Raised when a requested resource does not exist.
    """

    def __init__(
        self,
        message="Resource not found."
    ):
        super().__init__(message)




class ValidationException(AppException):
    """Raised when input validation fails."""
    pass

class DuplicateException(AppException):
    """Raised when a duplicate record is detected."""
    pass


class BusinessRuleException(AppException):
    """Raised when a business rule is violated."""
    pass