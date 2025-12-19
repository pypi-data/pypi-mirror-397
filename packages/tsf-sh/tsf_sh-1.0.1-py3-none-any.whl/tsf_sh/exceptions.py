"""
Исключения для tsf-sh библиотеки
"""


class Error(Exception):
    """Базовое исключение для всех ошибок tsf-sh"""
    pass


class APIError(Error):
    """Базовое исключение для ошибок API"""
    def __init__(self, message: str, code: str = None, status_code: int = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(APIError):
    """Ошибка валидации (400)"""
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR", status_code=400)


class UnauthorizedError(APIError):
    """Ошибка авторизации (401)"""
    def __init__(self, message: str = "Неверный API ключ"):
        super().__init__(message, code="INVALID_API_KEY", status_code=401)


class ForbiddenError(APIError):
    """Ошибка доступа (403)"""
    def __init__(self, message: str = "Требуется премиум"):
        super().__init__(message, code="PREMIUM_REQUIRED", status_code=403)


class NotFoundError(APIError):
    """Ресурс не найден (404)"""
    def __init__(self, message: str = "Ссылка не найдена"):
        super().__init__(message, code="LINK_NOT_FOUND", status_code=404)


class ConflictError(APIError):
    """Конфликт (409)"""
    def __init__(self, message: str, existing_code: str = None):
        self.existing_code = existing_code
        super().__init__(message, code="LINK_ALREADY_EXISTS", status_code=409)


class RateLimitError(APIError):
    """Превышен лимит запросов (429)"""
    def __init__(self, message: str, reset_time: int = None):
        self.reset_time = reset_time
        super().__init__(message, code="RATE_LIMIT_EXCEEDED", status_code=429)


class InternalServerError(APIError):
    """Внутренняя ошибка сервера (500)"""
    def __init__(self, message: str = "Внутренняя ошибка сервера"):
        super().__init__(message, code="INTERNAL_SERVER_ERROR", status_code=500)

