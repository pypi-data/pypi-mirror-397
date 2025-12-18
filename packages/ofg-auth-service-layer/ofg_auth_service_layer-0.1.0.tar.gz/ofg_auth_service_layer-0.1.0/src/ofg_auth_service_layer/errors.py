class AppError(Exception):
    def __init__(self, error, status_code: int = 400):
        self.status_code = status_code

        if isinstance(error, str):
            self.message = error
        elif isinstance(error, AppError):
            self.message = error.message
            self.status_code = error.status_code
        elif isinstance(error, Exception):
            self.message = str(error)
        else:
            self.message = f"{error}"

        super().__init__(self.message)
