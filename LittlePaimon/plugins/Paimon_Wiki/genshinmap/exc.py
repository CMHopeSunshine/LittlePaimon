class StatusError(ValueError):
    """米游社状态异常"""

    def __init__(self, status: int, message: str, *args: object) -> None:
        super().__init__(status, message, *args)
        self.status = status
        self.message = message

    def __str__(self) -> str:
        return f"miHoYo API {self.status}: {self.message}"

    def __repr__(self) -> str:
        return f"<StatusError status={self.status}, message={self.message}>"
