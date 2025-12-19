"""
Модели данных для tsf-sh библиотеки
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Link:
    """Модель короткой ссылки"""
    code: str
    short_url: str
    original_url: str
    clicks: int
    ttl_seconds: int
    created_at: int
    expires_at: int
    has_password: bool
    
    @property
    def created_datetime(self) -> datetime:
        """Возвращает datetime объект для created_at"""
        return datetime.fromtimestamp(self.created_at)
    
    @property
    def expires_datetime(self) -> datetime:
        """Возвращает datetime объект для expires_at"""
        return datetime.fromtimestamp(self.expires_at)
    
    @property
    def is_expired(self) -> bool:
        """Проверяет, истекла ли ссылка"""
        return datetime.now().timestamp() > self.expires_at
    
    @property
    def remaining_seconds(self) -> int:
        """Возвращает оставшееся время жизни в секундах"""
        remaining = self.expires_at - int(datetime.now().timestamp())
        return max(0, remaining)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Link":
        """Создает объект Link из словаря"""
        clicks = data.get("clicks", 0)
        ttl_seconds = data["ttl_seconds"]
        expires_at = data["expires_at"]
        
        if "created_at" in data:
            created_at = data["created_at"]
        else:
            created_at = expires_at - ttl_seconds
        
        return cls(
            code=data["code"],
            short_url=data["short_url"],
            original_url=data["original_url"],
            clicks=clicks,
            ttl_seconds=ttl_seconds,
            created_at=created_at,
            expires_at=expires_at,
            has_password=data.get("has_password", False)
        )


@dataclass
class LinkStats:
    """Статистика пользователя"""
    links_count: int
    total_clicks: int


@dataclass
class HealthStatus:
    """Статус здоровья API"""
    success: bool
    status: str
    services: dict
    timestamp: int
    
    @property
    def is_healthy(self) -> bool:
        """Проверяет, здоров ли API"""
        return self.status == "healthy"
    
    @classmethod
    def from_dict(cls, data: dict) -> "HealthStatus":
        """Создает объект HealthStatus из словаря"""
        return cls(
            success=data["success"],
            status=data["status"],
            services=data["services"],
            timestamp=data["timestamp"]
        )

