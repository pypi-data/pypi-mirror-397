"""
Асинхронный клиент для работы с tsf.sh API
"""

import json
from typing import Optional, List
from urllib.parse import urljoin

import httpx

from .exceptions import (
    APIError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ConflictError,
    InternalServerError
)
from .models import Link, LinkStats, HealthStatus


class Client:
    """Асинхронный клиент для работы с tsf.sh API"""
    
    BASE_URL = "https://tsf.sh"
    
    def __init__(self, api_key: str, base_url: str = None, timeout: float = 30.0):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ для аутентификации
            base_url: Базовый URL API (по умолчанию https://tsf.sh)
            timeout: Таймаут запросов в секундах
        """
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
        await self.close()
    
    async def _ensure_client(self):
        """Создает HTTP клиент если его нет"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
    
    async def close(self):
        """Закрывает HTTP клиент"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    def _handle_response(self, response: httpx.Response) -> dict:
        """Обрабатывает ответ API и выбрасывает исключения при ошибках"""
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise APIError(
                f"Неверный формат ответа: {response.text}",
                status_code=response.status_code
            )
        
        if not data.get("success", False):
            error = data.get("error", {})
            error_code = error.get("code", "UNKNOWN_ERROR")
            error_message = error.get("message", "Неизвестная ошибка")
            
            if response.status_code == 400:
                raise ValidationError(error_message)
            elif response.status_code == 401:
                raise UnauthorizedError(error_message)
            elif response.status_code == 403:
                raise ForbiddenError(error_message)
            elif response.status_code == 404:
                raise NotFoundError(error_message)
            elif response.status_code == 409:
                existing_code = error.get("existing_code")
                raise ConflictError(error_message, existing_code=existing_code)
            elif response.status_code == 429:
                reset_time = None
                if "X-RateLimit-Reset" in response.headers:
                    try:
                        reset_time = int(response.headers["X-RateLimit-Reset"])
                    except ValueError:
                        pass
                raise RateLimitError(error_message, reset_time=reset_time)
            elif response.status_code == 500:
                raise InternalServerError(error_message)
            else:
                raise APIError(error_message, code=error_code, status_code=response.status_code)
        
        return data
    
    async def create_link(
        self,
        url: str,
        ttl_hours: int = 24,
        password: Optional[str] = None
    ) -> Link:
        """
        Создает короткую ссылку
        
        Args:
            url: URL для сокращения (должен начинаться с http:// или https://)
            ttl_hours: Время жизни ссылки в часах (от 1 до 24). По умолчанию: 24
            password: Пароль для защиты ссылки (1-32 символа). По умолчанию: None
        
        Returns:
            Link: Объект созданной ссылки
        
        Raises:
            ValidationError: Ошибка валидации
            UnauthorizedError: Неверный API ключ
            ForbiddenError: Отсутствует премиум
            ConflictError: Ссылка уже существует
            RateLimitError: Превышен лимит запросов или кулдаун
        """
        await self._ensure_client()
        
        payload = {
            "url": url,
            "ttl_hours": ttl_hours
        }
        if password:
            payload["password"] = password
        
        response = await self._client.post("/api/links", json=payload)
        data = self._handle_response(response)
        
        return Link.from_dict(data["data"])
    
    async def get_links(self) -> List[Link]:
        """
        Получает список всех ссылок пользователя
        
        Returns:
            List[Link]: Список ссылок, отсортированный по дате создания (новые первые)
        
        Raises:
            UnauthorizedError: Неверный API ключ
            ForbiddenError: Отсутствует премиум
        """
        await self._ensure_client()
        
        response = await self._client.get("/api/links")
        data = self._handle_response(response)
        
        return [Link.from_dict(link_data) for link_data in data["data"]["links"]]
    
    async def get_link(self, code: str) -> Link:
        """
        Получает информацию о ссылке
        
        Args:
            code: Код короткой ссылки
        
        Returns:
            Link: Объект ссылки
        
        Raises:
            UnauthorizedError: Неверный API ключ
            ForbiddenError: Отсутствует премиум
            NotFoundError: Ссылка не найдена
        """
        await self._ensure_client()
        
        response = await self._client.get(f"/api/links/{code}")
        data = self._handle_response(response)
        
        return Link.from_dict(data["data"])
    
    async def delete_link(self, code: str) -> bool:
        """
        Удаляет ссылку
        
        Args:
            code: Код короткой ссылки
        
        Returns:
            bool: True если ссылка успешно удалена
        
        Raises:
            UnauthorizedError: Неверный API ключ
            ForbiddenError: Отсутствует премиум
            NotFoundError: Ссылка не найдена
        """
        await self._ensure_client()
        
        response = await self._client.delete(f"/api/links/{code}")
        self._handle_response(response)
        
        return True
    
    async def extend_link(self, code: str, ttl_hours: int) -> Link:
        """
        Продлевает время жизни ссылки
        
        Args:
            code: Код короткой ссылки
            ttl_hours: Новое время жизни в часах (от 1 до 24)
        
        Returns:
            Link: Обновленный объект ссылки
        
        Raises:
            ValidationError: Ошибка валидации
            UnauthorizedError: Неверный API ключ
            ForbiddenError: Отсутствует премиум
            NotFoundError: Ссылка не найдена
            RateLimitError: Превышен кулдаун
        """
        await self._ensure_client()
        
        payload = {"ttl_hours": ttl_hours}
        response = await self._client.patch(f"/api/links/{code}/extend", json=payload)
        data = self._handle_response(response)
        
        return await self.get_link(code)
    
    async def set_password(self, code: str, password: str) -> bool:
        """
        Устанавливает или изменяет пароль для ссылки
        
        Args:
            code: Код короткой ссылки
            password: Пароль (1-32 символа)
        
        Returns:
            bool: True если пароль успешно установлен
        
        Raises:
            ValidationError: Ошибка валидации
            UnauthorizedError: Неверный API ключ
            ForbiddenError: Отсутствует премиум
            NotFoundError: Ссылка не найдена
        """
        await self._ensure_client()
        
        payload = {"password": password}
        response = await self._client.post(f"/api/links/{code}/password", json=payload)
        self._handle_response(response)
        
        return True
    
    async def remove_password(self, code: str) -> bool:
        """
        Удаляет пароль у ссылки
        
        Args:
            code: Код короткой ссылки
        
        Returns:
            bool: True если пароль успешно удален
        
        Raises:
            UnauthorizedError: Неверный API ключ
            ForbiddenError: Отсутствует премиум
            NotFoundError: Ссылка не найдена
        """
        await self._ensure_client()
        
        response = await self._client.delete(f"/api/links/{code}/password")
        self._handle_response(response)
        
        return True
    
    async def reroll_code(self, code: str) -> str:
        """
        Перегенерирует код ссылки
        
        Args:
            code: Старый код ссылки
        
        Returns:
            str: Новый код ссылки
        
        Raises:
            UnauthorizedError: Неверный API ключ
            ForbiddenError: Отсутствует премиум
            NotFoundError: Ссылка не найдена
            RateLimitError: Превышен кулдаун
        """
        await self._ensure_client()
        
        response = await self._client.post(f"/api/links/{code}/reroll")
        data = self._handle_response(response)
        
        return data["data"]["new_code"]
    
    async def get_stats(self) -> LinkStats:
        """
        Получает статистику пользователя
        
        Returns:
            LinkStats: Статистика пользователя
        
        Raises:
            UnauthorizedError: Неверный API ключ
            ForbiddenError: Отсутствует премиум
        """
        await self._ensure_client()
        
        response = await self._client.get("/api/stats")
        data = self._handle_response(response)
        
        stats_data = data["data"]
        return LinkStats(
            links_count=stats_data["links_count"],
            total_clicks=stats_data["total_clicks"]
        )
    
    async def health_check(self) -> HealthStatus:
        """
        Проверяет работоспособность API
        
        Returns:
            HealthStatus: Статус здоровья API
        """
        await self._ensure_client()
        
        response = await self._client.get("/api/health")
        data = self._handle_response(response)
        
        return HealthStatus.from_dict(data)

