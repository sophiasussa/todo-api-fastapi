class AppError(Exception):
    """
    Base application exception for business and validation errors.

    This class defines a standardized error format that can be
    directly converted into consistent HTTP responses by the API.
    It is captured by a global FastAPI exception handler.
    """

    def __init__(
        self,
        *,
        title: str,
        detail: str,
        status_code: int,
        error_code: str,
        type_: str,
    ):
        """
        Creates a new application error instance.

        Args:
            title (str): Short, human-readable error title.
            detail (str): Detailed description of the error.
            status_code (int): HTTP status code to be returned.
            error_code (str): Internal application error code.
            type_ (str): Categorical error type (e.g., validation_error, not_found).
        """
        self.title = title
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        self.type = type_

        super().__init__(detail)
