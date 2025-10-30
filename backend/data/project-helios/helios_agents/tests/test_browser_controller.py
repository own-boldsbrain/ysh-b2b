"""
Testes unitários para BrowserController
"""

import pytest
from helios_agents.execution.browser_controller import BrowserController, BrowserAction


class TestBrowserController:
    """Testes para BrowserController"""

    @pytest.mark.asyncio
    async def test_initialization(self):
        """Testa inicialização do controlador"""
        controller = BrowserController()

        assert controller.headless is True
        assert controller.timeout == 30000
        assert controller.session is None
        assert controller.action_history == []

    @pytest.mark.asyncio
    async def test_start_session(self):
        """Testa início de sessão"""
        controller = BrowserController()

        session_id = await controller.start_session("https://example.com")

        assert session_id.startswith("session_")
        assert controller.session is not None
        assert controller.session["url"] == "https://example.com"
        assert "created_at" in controller.session

    @pytest.mark.asyncio
    async def test_execute_action(self):
        """Testa execução de ação (simulada)"""
        controller = BrowserController()

        result = await controller.execute_action(
            BrowserAction.NAVIGATE, {"url": "https://example.com"}
        )

        assert result["status"] == "simulated"
        assert result["action"] == "navigate"
        assert result["params"] == {"url": "https://example.com"}
        assert len(controller.action_history) == 1

    @pytest.mark.asyncio
    async def test_close_session(self):
        """Testa fechamento de sessão"""
        controller = BrowserController()

        await controller.start_session()
        assert controller.session is not None

        await controller.close_session()
        assert controller.session is None
