from fastapi import HTTPException

class ApiError(HTTPException):
    """Base class for API errors."""
    
    def __init__(self, status_code: int, message: str, error_code: str):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        super().__init__(status_code=status_code, detail=message)

    def __str__(self):
        return f"{self.error_code} - {self.status_code} - {self.message}"