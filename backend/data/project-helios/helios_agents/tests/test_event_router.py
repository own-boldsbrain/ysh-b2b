"""
Testes para EventRouter
"""

import pytest
import asyncio
from unittest.mock import AsyncMock
from helios_agents.events.event_router import EventRouter


class TestEventRouter:
    """Testes para EventRouter"""

    def setup_method(self):
        """Setup para cada teste"""
        self.router = EventRouter()

    def test_initialization(self):
        """Testa inicialização do router"""
        assert self.router.subscriptions == {}
        assert self.router.event_log == []
        assert self.router.total_events_routed == 0

    def test_subscribe_without_filter(self):
        """Testa subscrição sem filtro"""
        handler = AsyncMock()
        subscription_id = self.router.subscribe("test_event", handler)

        assert subscription_id.startswith("sub_")
        assert "test_event" in self.router.subscriptions
        assert len(self.router.subscriptions["test_event"]) == 1

        subscription = self.router.subscriptions["test_event"][0]
        assert subscription["handler"] == handler
        assert subscription["filter"] is None

    def test_subscribe_with_filter(self):
        """Testa subscrição com filtro"""
        handler = AsyncMock()
        filter_func = lambda event: event.get("priority") == "high"

        subscription_id = self.router.subscribe("test_event", handler, filter_func)

        subscription = self.router.subscriptions["test_event"][0]
        assert subscription["filter"] == filter_func

    @pytest.mark.asyncio
    async def test_publish_without_subscribers(self):
        """Testa publicação sem subscribers"""
        event = {"event_type": "test_event", "data": "test"}

        handlers_called = await self.router.publish(event)

        assert handlers_called == 0
        assert self.router.total_events_routed == 1
        assert len(self.router.event_log) == 1

    @pytest.mark.asyncio
    async def test_publish_with_subscriber(self):
        """Testa publicação com subscriber"""
        handler = AsyncMock()
        self.router.subscribe("test_event", handler)

        event = {"event_type": "test_event", "data": "test"}

        handlers_called = await self.router.publish(event)

        assert handlers_called == 1
        handler.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_publish_with_filter_passing(self):
        """Testa publicação com filtro que passa"""
        handler = AsyncMock()
        filter_func = lambda event: event.get("priority") == "high"

        self.router.subscribe("test_event", handler, filter_func)

        event = {"event_type": "test_event", "priority": "high", "data": "test"}

        handlers_called = await self.router.publish(event)

        assert handlers_called == 1
        handler.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_publish_with_filter_blocking(self):
        """Testa publicação com filtro que bloqueia"""
        handler = AsyncMock()
        filter_func = lambda event: event.get("priority") == "high"

        self.router.subscribe("test_event", handler, filter_func)

        event = {"event_type": "test_event", "priority": "low", "data": "test"}

        handlers_called = await self.router.publish(event)

        assert handlers_called == 0
        handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_multiple_subscribers(self):
        """Testa publicação com múltiplos subscribers"""
        handler1 = AsyncMock()
        handler2 = AsyncMock()

        self.router.subscribe("test_event", handler1)
        self.router.subscribe("test_event", handler2)

        event = {"event_type": "test_event", "data": "test"}

        handlers_called = await self.router.publish(event)

        assert handlers_called == 2
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_publish_different_event_types(self):
        """Testa publicação para diferentes tipos de evento"""
        handler1 = AsyncMock()
        handler2 = AsyncMock()

        self.router.subscribe("event_a", handler1)
        self.router.subscribe("event_b", handler2)

        event_a = {"event_type": "event_a", "data": "a"}
        event_b = {"event_type": "event_b", "data": "b"}

        await self.router.publish(event_a)
        await self.router.publish(event_b)

        handler1.assert_called_once_with(event_a)
        handler2.assert_called_once_with(event_b)

    @pytest.mark.asyncio
    async def test_publish_handler_exception(self):
        """Testa publicação quando handler lança exceção"""
        handler1 = AsyncMock(side_effect=Exception("Test error"))
        handler2 = AsyncMock()

        self.router.subscribe("test_event", handler1)
        self.router.subscribe("test_event", handler2)

        event = {"event_type": "test_event", "data": "test"}

        handlers_called = await self.router.publish(event)

        # Deve continuar processando outros handlers mesmo com erro
        assert handlers_called == 1  # Apenas handler2 foi chamado com sucesso
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)

    def test_get_statistics_empty(self):
        """Testa estatísticas quando vazio"""
        stats = self.router.get_statistics()

        assert stats["total_events"] == 0
        assert stats["active_subscriptions"] == 0
        assert stats["event_types"] == []

    @pytest.mark.asyncio
    async def test_get_statistics_with_data(self):
        """Testa estatísticas com dados"""
        handler1 = AsyncMock()
        handler2 = AsyncMock()

        self.router.subscribe("event_a", handler1)
        self.router.subscribe("event_b", handler2)

        await self.router.publish({"event_type": "event_a"})
        await self.router.publish({"event_type": "event_b"})

        stats = self.router.get_statistics()

        assert stats["total_events"] == 2
        assert stats["active_subscriptions"] == 2
        assert "event_a" in stats["event_types"]
        assert "event_b" in stats["event_types"]
