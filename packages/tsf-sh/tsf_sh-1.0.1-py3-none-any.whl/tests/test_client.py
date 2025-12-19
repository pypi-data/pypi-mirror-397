"""
Тесты для tsf-sh библиотеки
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch
from datetime import datetime

from tsf_sh import Client, Link, LinkStats, HealthStatus
from tsf_sh.exceptions import (
    Error,
    APIError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    InternalServerError
)


@pytest.fixture
def api_key():
    return "test-api-key"


@pytest.fixture
def client(api_key):
    return Client(api_key=api_key, base_url="https://test.tsf.sh")


@pytest.fixture
def mock_response():
    """Создает мок ответа"""
    def _create_response(status_code=200, json_data=None, headers=None):
        response = AsyncMock(spec=httpx.Response)
        response.status_code = status_code
        response.headers = headers or {}
        response.json = AsyncMock(return_value=json_data or {})
        response.text = str(json_data) if json_data else ""
        return response
    return _create_response


class TestClientInitialization:
    """Тесты инициализации клиента"""
    
    def test_client_init(self, api_key):
        client = Client(api_key=api_key)
        assert client.api_key == api_key
        assert client.base_url == "https://tsf.sh"
        assert client.timeout == 30.0
        assert client._client is None
    
    def test_client_init_custom_base_url(self, api_key):
        client = Client(api_key=api_key, base_url="https://custom.com")
        assert client.base_url == "https://custom.com"
    
    def test_client_init_custom_timeout(self, api_key):
        client = Client(api_key=api_key, timeout=60.0)
        assert client.timeout == 60.0
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        async with client as c:
            assert c._client is not None
            assert isinstance(c._client, httpx.AsyncClient)
        assert c._client is None


class TestCreateLink:
    """Тесты создания ссылки"""
    
    @pytest.mark.asyncio
    async def test_create_link_success(self, client, mock_response):
        response_data = {
            "success": True,
            "data": {
                "code": "abc123",
                "short_url": "https://tsf.sh/abc123",
                "original_url": "https://example.com",
                "ttl_seconds": 86400,
                "expires_at": 1234567890,
                "has_password": False
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.post = AsyncMock(return_value=mock_response(200, response_data))
            
            link = await client.create_link("https://example.com", ttl_hours=24)
            
            assert isinstance(link, Link)
            assert link.code == "abc123"
            assert link.short_url == "https://tsf.sh/abc123"
            assert link.original_url == "https://example.com"
            assert link.ttl_seconds == 86400
            assert link.has_password is False
            client._client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_link_with_password(self, client, mock_response):
        response_data = {
            "success": True,
            "data": {
                "code": "def456",
                "short_url": "https://tsf.sh/def456",
                "original_url": "https://example.com",
                "ttl_seconds": 43200,
                "expires_at": 1234567890,
                "has_password": True
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.post = AsyncMock(return_value=mock_response(200, response_data))
            
            link = await client.create_link(
                "https://example.com",
                ttl_hours=12,
                password="secret123"
            )
            
            assert link.has_password is True
            call_args = client._client.post.call_args
            assert call_args[1]["json"]["password"] == "secret123"
            assert call_args[1]["json"]["ttl_hours"] == 12
    
    @pytest.mark.asyncio
    async def test_create_link_validation_error(self, client, mock_response):
        error_data = {
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "URL должен начинаться с http:// или https://"
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.post = AsyncMock(return_value=mock_response(400, error_data))
            
            with pytest.raises(ValidationError) as exc_info:
                await client.create_link("invalid-url")
            
            assert "URL должен начинаться" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_create_link_unauthorized(self, client, mock_response):
        error_data = {
            "success": False,
            "error": {
                "code": "INVALID_API_KEY",
                "message": "Неверный API ключ"
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.post = AsyncMock(return_value=mock_response(401, error_data))
            
            with pytest.raises(UnauthorizedError):
                await client.create_link("https://example.com")
    
    @pytest.mark.asyncio
    async def test_create_link_forbidden(self, client, mock_response):
        error_data = {
            "success": False,
            "error": {
                "code": "PREMIUM_REQUIRED",
                "message": "Требуется премиум"
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.post = AsyncMock(return_value=mock_response(403, error_data))
            
            with pytest.raises(ForbiddenError):
                await client.create_link("https://example.com")
    
    @pytest.mark.asyncio
    async def test_create_link_conflict(self, client, mock_response):
        error_data = {
            "success": False,
            "error": {
                "code": "LINK_ALREADY_EXISTS",
                "message": "Эта ссылка уже была сокращена",
                "existing_code": "xyz789"
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.post = AsyncMock(return_value=mock_response(409, error_data))
            
            with pytest.raises(ConflictError) as exc_info:
                await client.create_link("https://example.com")
            
            assert exc_info.value.existing_code == "xyz789"
    
    @pytest.mark.asyncio
    async def test_create_link_rate_limit(self, client, mock_response):
        error_data = {
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Превышен лимит запросов"
            }
        }
        
        headers = {"X-RateLimit-Reset": "1234567890"}
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.post = AsyncMock(return_value=mock_response(429, error_data, headers))
            
            with pytest.raises(RateLimitError) as exc_info:
                await client.create_link("https://example.com")
            
            assert exc_info.value.reset_time == 1234567890


class TestGetLinks:
    """Тесты получения списка ссылок"""
    
    @pytest.mark.asyncio
    async def test_get_links_success(self, client, mock_response):
        response_data = {
            "success": True,
            "data": {
                "links": [
                    {
                        "code": "abc123",
                        "short_url": "https://tsf.sh/abc123",
                        "original_url": "https://example.com",
                        "clicks": 10,
                        "ttl_seconds": 86400,
                        "created_at": 1234567890,
                        "expires_at": 1234654290,
                        "has_password": False
                    },
                    {
                        "code": "def456",
                        "short_url": "https://tsf.sh/def456",
                        "original_url": "https://test.com",
                        "clicks": 5,
                        "ttl_seconds": 43200,
                        "created_at": 1234500000,
                        "expires_at": 1234543200,
                        "has_password": True
                    }
                ]
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.get = AsyncMock(return_value=mock_response(200, response_data))
            
            links = await client.get_links()
            
            assert len(links) == 2
            assert all(isinstance(link, Link) for link in links)
            assert links[0].code == "abc123"
            assert links[1].code == "def456"
    
    @pytest.mark.asyncio
    async def test_get_links_empty(self, client, mock_response):
        response_data = {
            "success": True,
            "data": {
                "links": []
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.get = AsyncMock(return_value=mock_response(200, response_data))
            
            links = await client.get_links()
            
            assert len(links) == 0


class TestGetLink:
    """Тесты получения информации о ссылке"""
    
    @pytest.mark.asyncio
    async def test_get_link_success(self, client, mock_response):
        response_data = {
            "success": True,
            "data": {
                "code": "abc123",
                "short_url": "https://tsf.sh/abc123",
                "original_url": "https://example.com",
                "clicks": 42,
                "ttl_seconds": 86400,
                "created_at": 1234567890,
                "expires_at": 1234654290,
                "has_password": False
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.get = AsyncMock(return_value=mock_response(200, response_data))
            
            link = await client.get_link("abc123")
            
            assert link.code == "abc123"
            assert link.clicks == 42
            assert link.original_url == "https://example.com"
    
    @pytest.mark.asyncio
    async def test_get_link_not_found(self, client, mock_response):
        error_data = {
            "success": False,
            "error": {
                "code": "LINK_NOT_FOUND",
                "message": "Ссылка не найдена"
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.get = AsyncMock(return_value=mock_response(404, error_data))
            
            with pytest.raises(NotFoundError):
                await client.get_link("nonexistent")


class TestDeleteLink:
    """Тесты удаления ссылки"""
    
    @pytest.mark.asyncio
    async def test_delete_link_success(self, client, mock_response):
        response_data = {
            "success": True,
            "message": "Ссылка удалена"
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.delete = AsyncMock(return_value=mock_response(200, response_data))
            
            result = await client.delete_link("abc123")
            
            assert result is True
            client._client.delete.assert_called_once_with("/api/links/abc123")
    
    @pytest.mark.asyncio
    async def test_delete_link_not_found(self, client, mock_response):
        error_data = {
            "success": False,
            "error": {
                "code": "LINK_NOT_FOUND",
                "message": "Ссылка не найдена"
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.delete = AsyncMock(return_value=mock_response(404, error_data))
            
            with pytest.raises(NotFoundError):
                await client.delete_link("nonexistent")


class TestExtendLink:
    """Тесты продления времени жизни ссылки"""
    
    @pytest.mark.asyncio
    async def test_extend_link_success(self, client, mock_response):
        extend_response = {
            "success": True,
            "data": {
                "code": "abc123",
                "ttl_seconds": 86400,
                "expires_at": 1234654290
            }
        }
        
        get_response = {
            "success": True,
            "data": {
                "code": "abc123",
                "short_url": "https://tsf.sh/abc123",
                "original_url": "https://example.com",
                "clicks": 10,
                "ttl_seconds": 86400,
                "created_at": 1234567890,
                "expires_at": 1234654290,
                "has_password": False
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.patch = AsyncMock(return_value=mock_response(200, extend_response))
            client._client.get = AsyncMock(return_value=mock_response(200, get_response))
            
            link = await client.extend_link("abc123", ttl_hours=24)
            
            assert isinstance(link, Link)
            client._client.patch.assert_called_once()
            call_args = client._client.patch.call_args
            assert call_args[1]["json"]["ttl_hours"] == 24


class TestPasswordOperations:
    """Тесты операций с паролем"""
    
    @pytest.mark.asyncio
    async def test_set_password_success(self, client, mock_response):
        response_data = {
            "success": True,
            "data": {
                "message": "Пароль установлен"
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.post = AsyncMock(return_value=mock_response(200, response_data))
            
            result = await client.set_password("abc123", "newpassword")
            
            assert result is True
            call_args = client._client.post.call_args
            assert call_args[0][0] == "/api/links/abc123/password"
            assert call_args[1]["json"]["password"] == "newpassword"
    
    @pytest.mark.asyncio
    async def test_remove_password_success(self, client, mock_response):
        response_data = {
            "success": True,
            "data": {
                "message": "Пароль удален"
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.delete = AsyncMock(return_value=mock_response(200, response_data))
            
            result = await client.remove_password("abc123")
            
            assert result is True
            client._client.delete.assert_called_once_with("/api/links/abc123/password")


class TestRerollCode:
    """Тесты перегенерации кода"""
    
    @pytest.mark.asyncio
    async def test_reroll_code_success(self, client, mock_response):
        response_data = {
            "success": True,
            "data": {
                "old_code": "abc123",
                "new_code": "xyz789",
                "short_url": "https://tsf.sh/xyz789"
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.post = AsyncMock(return_value=mock_response(200, response_data))
            
            new_code = await client.reroll_code("abc123")
            
            assert new_code == "xyz789"
            client._client.post.assert_called_once_with("/api/links/abc123/reroll")


class TestGetStats:
    """Тесты получения статистики"""
    
    @pytest.mark.asyncio
    async def test_get_stats_success(self, client, mock_response):
        response_data = {
            "success": True,
            "data": {
                "links_count": 5,
                "total_clicks": 150
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.get = AsyncMock(return_value=mock_response(200, response_data))
            
            stats = await client.get_stats()
            
            assert isinstance(stats, LinkStats)
            assert stats.links_count == 5
            assert stats.total_clicks == 150


class TestHealthCheck:
    """Тесты проверки здоровья API"""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, client, mock_response):
        response_data = {
            "success": True,
            "status": "healthy",
            "services": {
                "redis": "ok",
                "api": "ok"
            },
            "timestamp": 1234567890
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.get = AsyncMock(return_value=mock_response(200, response_data))
            
            health = await client.health_check()
            
            assert isinstance(health, HealthStatus)
            assert health.status == "healthy"
            assert health.is_healthy is True
            assert health.services["redis"] == "ok"
    
    @pytest.mark.asyncio
    async def test_health_check_degraded(self, client, mock_response):
        response_data = {
            "success": True,
            "status": "degraded",
            "services": {
                "redis": "error",
                "api": "ok"
            },
            "timestamp": 1234567890
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.get = AsyncMock(return_value=mock_response(200, response_data))
            
            health = await client.health_check()
            
            assert health.status == "degraded"
            assert health.is_healthy is False


class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    @pytest.mark.asyncio
    async def test_invalid_json_response(self, client, mock_response):
        response = mock_response(200, None)
        response.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
        response.text = "Not JSON"
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.get = AsyncMock(return_value=response)
            
            with pytest.raises(APIError) as exc_info:
                await client.get_links()
            
            assert "Неверный формат ответа" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_internal_server_error(self, client, mock_response):
        error_data = {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Внутренняя ошибка сервера"
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.get = AsyncMock(return_value=mock_response(500, error_data))
            
            with pytest.raises(InternalServerError):
                await client.get_links()
    
    @pytest.mark.asyncio
    async def test_unknown_error_code(self, client, mock_response):
        error_data = {
            "success": False,
            "error": {
                "code": "UNKNOWN_ERROR",
                "message": "Неизвестная ошибка"
            }
        }
        
        with patch.object(client, '_ensure_client', new_callable=AsyncMock):
            client._client = AsyncMock()
            client._client.get = AsyncMock(return_value=mock_response(418, error_data))
            
            with pytest.raises(APIError) as exc_info:
                await client.get_links()
            
            assert exc_info.value.status_code == 418
            assert exc_info.value.code == "UNKNOWN_ERROR"


class TestLinkModel:
    """Тесты модели Link"""
    
    def test_link_from_dict(self):
        data = {
            "code": "abc123",
            "short_url": "https://tsf.sh/abc123",
            "original_url": "https://example.com",
            "clicks": 10,
            "ttl_seconds": 86400,
            "created_at": 1234567890,
            "expires_at": 1234654290,
            "has_password": False
        }
        
        link = Link.from_dict(data)
        
        assert link.code == "abc123"
        assert link.clicks == 10
        assert link.has_password is False
    
    def test_link_datetime_properties(self):
        data = {
            "code": "abc123",
            "short_url": "https://tsf.sh/abc123",
            "original_url": "https://example.com",
            "clicks": 0,
            "ttl_seconds": 86400,
            "created_at": 1234567890,
            "expires_at": 1234654290,
            "has_password": False
        }
        
        link = Link.from_dict(data)
        
        assert isinstance(link.created_datetime, datetime)
        assert isinstance(link.expires_datetime, datetime)
    
    def test_link_is_expired(self):
        import time
        current_time = int(time.time())
        
        expired_data = {
            "code": "abc123",
            "short_url": "https://tsf.sh/abc123",
            "original_url": "https://example.com",
            "clicks": 0,
            "ttl_seconds": 86400,
            "created_at": current_time - 100000,
            "expires_at": current_time - 1000,
            "has_password": False
        }
        
        link = Link.from_dict(expired_data)
        assert link.is_expired is True
        
        active_data = {
            "code": "abc123",
            "short_url": "https://tsf.sh/abc123",
            "original_url": "https://example.com",
            "clicks": 0,
            "ttl_seconds": 86400,
            "created_at": current_time,
            "expires_at": current_time + 86400,
            "has_password": False
        }
        
        link = Link.from_dict(active_data)
        assert link.is_expired is False
    
    def test_link_remaining_seconds(self):
        import time
        current_time = int(time.time())
        
        data = {
            "code": "abc123",
            "short_url": "https://tsf.sh/abc123",
            "original_url": "https://example.com",
            "clicks": 0,
            "ttl_seconds": 86400,
            "created_at": current_time,
            "expires_at": current_time + 3600,
            "has_password": False
        }
        
        link = Link.from_dict(data)
        remaining = link.remaining_seconds
        
        assert 0 < remaining <= 3600


class TestLinkStatsModel:
    """Тесты модели LinkStats"""
    
    def test_link_stats(self):
        stats = LinkStats(links_count=5, total_clicks=150)
        
        assert stats.links_count == 5
        assert stats.total_clicks == 150


class TestHealthStatusModel:
    """Тесты модели HealthStatus"""
    
    def test_health_status_from_dict(self):
        data = {
            "success": True,
            "status": "healthy",
            "services": {
                "redis": "ok",
                "api": "ok"
            },
            "timestamp": 1234567890
        }
        
        health = HealthStatus.from_dict(data)
        
        assert health.status == "healthy"
        assert health.is_healthy is True
        assert health.services["redis"] == "ok"
    
    def test_health_status_degraded(self):
        data = {
            "success": True,
            "status": "degraded",
            "services": {
                "redis": "error",
                "api": "ok"
            },
            "timestamp": 1234567890
        }
        
        health = HealthStatus.from_dict(data)
        
        assert health.status == "degraded"
        assert health.is_healthy is False

