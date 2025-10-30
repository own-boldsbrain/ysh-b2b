"""Tests for webhook service functionality."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.webhook_service import WebhookService
from app.models.webhooks import WebhookConfig, WebhookDelivery
from app.database import SessionLocal


class TestWebhookService:
    """Test cases for WebhookService."""

    @pytest.fixture
    def webhook_service(self):
        """Create a webhook service instance."""
        return WebhookService()

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        with patch('app.services.webhook_service.SessionLocal') as mock_session:
            mock_db = Mock(spec=Session)
            mock_session.return_value = mock_db
            yield mock_db

    @pytest.fixture
    def sample_webhook_config(self):
        """Sample webhook configuration."""
        return WebhookConfig(
            id="test-config",
            name="Test Webhook",
            url="https://example.com/webhook",
            secret="test-secret",
            events=["connection.created", "validation.completed"],
            active=True,
            created_at=datetime.utcnow()
        )

    def test_webhook_service_initialization(self, webhook_service):
        """Test webhook service initialization."""
        assert webhook_service.max_retries == 3
        assert webhook_service.retry_delay == 60
        assert webhook_service.session is None

    @pytest.mark.asyncio
    async def test_context_manager_lifecycle(self, webhook_service):
        """Test webhook service context manager."""
        async with webhook_service as service:
            assert service.session is not None
        # Session should be closed after context exit
        assert webhook_service.session is None or webhook_service.session.closed

    def test_get_webhook_config_by_id(self, webhook_service, mock_db_session, sample_webhook_config):
        """Test getting webhook config by ID."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_webhook_config
        
        result = webhook_service.get_webhook_config("test-config")
        
        assert result == sample_webhook_config
        mock_db_session.query.assert_called_once()

    def test_get_webhook_config_by_name_fallback(self, webhook_service, mock_db_session, sample_webhook_config):
        """Test getting webhook config by name when ID not found."""
        # First call returns None, second call returns config
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [None, sample_webhook_config]
        
        result = webhook_service.get_webhook_config("test-config")
        
        assert result == sample_webhook_config
        assert mock_db_session.query.call_count == 2

    def test_get_webhook_config_not_found(self, webhook_service, mock_db_session):
        """Test getting webhook config when not found."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = webhook_service.get_webhook_config("nonexistent")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_send_webhook_success(self, webhook_service):
        """Test successful webhook delivery."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value="OK")
            mock_post.return_value.__aenter__.return_value = mock_response

            webhook_service.session = AsyncMock()
            
            payload = {"event": "test", "data": {"id": "123"}}
            config = Mock()
            config.url = "https://example.com/webhook"
            config.secret = "test-secret"
            
            result = await webhook_service._send_webhook(config, payload)
            
            assert result["success"] is True
            assert result["status_code"] == 200

    @pytest.mark.asyncio
    async def test_send_webhook_failure(self, webhook_service):
        """Test webhook delivery failure."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value="Internal Server Error")
            mock_post.return_value.__aenter__.return_value = mock_response

            webhook_service.session = AsyncMock()
            
            payload = {"event": "test", "data": {"id": "123"}}
            config = Mock()
            config.url = "https://example.com/webhook"
            config.secret = "test-secret"
            
            result = await webhook_service._send_webhook(config, payload)
            
            assert result["success"] is False
            assert result["status_code"] == 500

    def test_generate_signature(self, webhook_service):
        """Test HMAC signature generation."""
        payload = '{"test": "data"}'
        secret = "test-secret"
        
        signature = webhook_service._generate_signature(payload, secret)
        
        assert signature.startswith("sha256=")
        assert len(signature) > 7  # More than just the prefix

    def test_validate_signature(self, webhook_service):
        """Test signature validation."""
        payload = '{"test": "data"}'
        secret = "test-secret"
        
        # Generate a valid signature
        valid_signature = webhook_service._generate_signature(payload, secret)
        
        # Test valid signature
        assert webhook_service._validate_signature(payload, valid_signature, secret) is True
        
        # Test invalid signature
        assert webhook_service._validate_signature(payload, "invalid", secret) is False

    @pytest.mark.asyncio
    async def test_retry_mechanism(self, webhook_service):
        """Test webhook retry mechanism."""
        with patch.object(webhook_service, '_send_webhook') as mock_send:
            # First two attempts fail, third succeeds
            mock_send.side_effect = [
                {"success": False, "status_code": 500},
                {"success": False, "status_code": 502},
                {"success": True, "status_code": 200}
            ]
            
            config = Mock()
            payload = {"test": "data"}
            
            result = await webhook_service._send_with_retry(config, payload)
            
            assert result["success"] is True
            assert mock_send.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhaustion(self, webhook_service):
        """Test webhook retry exhaustion."""
        with patch.object(webhook_service, '_send_webhook') as mock_send:
            # All attempts fail
            mock_send.return_value = {"success": False, "status_code": 500}
            
            config = Mock()
            payload = {"test": "data"}
            
            result = await webhook_service._send_with_retry(config, payload)
            
            assert result["success"] is False
            assert mock_send.call_count == webhook_service.max_retries

    def test_create_delivery_record(self, webhook_service, mock_db_session):
        """Test creation of webhook delivery record."""
        config = Mock()
        config.id = "test-config"
        
        payload = {"event": "test", "data": {"id": "123"}}
        response = {"success": True, "status_code": 200}
        
        webhook_service._create_delivery_record(config, payload, response)
        
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_webhook_queue(self, webhook_service):
        """Test processing webhook queue."""
        with patch.object(webhook_service, 'get_webhook_config') as mock_get_config, \
             patch.object(webhook_service, '_send_with_retry') as mock_send:
            
            mock_config = Mock()
            mock_get_config.return_value = mock_config
            mock_send.return_value = {"success": True, "status_code": 200}
            
            # Mock queue with one item
            webhook_service._webhook_queue = asyncio.Queue()
            await webhook_service._webhook_queue.put({
                "config_id": "test-config",
                "event": "test.event",
                "payload": {"data": "test"}
            })
            
            # Process one item
            await webhook_service._process_webhook_item()
            
            mock_get_config.assert_called_once_with("test-config")
            mock_send.assert_called_once()

    def test_format_webhook_payload(self, webhook_service):
        """Test webhook payload formatting."""
        event = "connection.created"
        data = {"id": "123", "status": "pending"}
        
        payload = webhook_service._format_payload(event, data)
        
        assert payload["event"] == event
        assert payload["data"] == data
        assert "timestamp" in payload
        assert "id" in payload

    @pytest.mark.asyncio
    async def test_webhook_service_cleanup(self, webhook_service):
        """Test webhook service cleanup."""
        webhook_service.session = AsyncMock()
        
        await webhook_service.cleanup()
        
        webhook_service.session.close.assert_called_once()

    def test_webhook_config_validation(self, webhook_service):
        """Test webhook configuration validation."""
        # Valid config
        valid_config = {
            "url": "https://example.com/webhook",
            "secret": "test-secret",
            "events": ["test.event"]
        }
        
        assert webhook_service._validate_config(valid_config) is True
        
        # Invalid config - missing URL
        invalid_config = {
            "secret": "test-secret",
            "events": ["test.event"]
        }
        
        assert webhook_service._validate_config(invalid_config) is False

    @pytest.mark.asyncio
    async def test_webhook_timeout_handling(self, webhook_service):
        """Test webhook timeout handling."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = asyncio.TimeoutError("Request timeout")
            
            webhook_service.session = AsyncMock()
            
            config = Mock()
            config.url = "https://example.com/webhook"
            config.secret = "test-secret"
            
            payload = {"event": "test", "data": {"id": "123"}}
            
            result = await webhook_service._send_webhook(config, payload)
            
            assert result["success"] is False
            assert "timeout" in result.get("error", "").lower()