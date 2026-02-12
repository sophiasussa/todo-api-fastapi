class AppError(Exception):
    def __init__(
        self,
        *,
        title: str,
        detail: str,
        status_code: int,
        error_code: str,
        type_: str,
    ):
        self.title = title
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        self.type = type_

        super().__init__(detail)
