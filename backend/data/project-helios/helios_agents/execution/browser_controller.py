"""BrowserController - Controlador de automação web com Playwright."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum

try:  # Playwright é opcional no modo simulado
    from playwright.async_api import async_playwright, Browser, Page

    PLAYWRIGHT_AVAILABLE = True
except Exception:  # pragma: no cover - ambiente sem playwright
    async_playwright = None
    Browser = Page = None
    PLAYWRIGHT_AVAILABLE = False


class BrowserAction(Enum):
    """Ações disponíveis no browser."""

    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    EXTRACT = "extract"
    SCREENSHOT = "screenshot"
    WAIT = "wait"
    SCROLL = "scroll"
    UPLOAD = "upload"


class BrowserController:
    """Controlador de automação web baseado em Playwright."""

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.session: Optional[Dict[str, Any]] = None
        self.action_history: List[Dict[str, Any]] = []
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None

    async def start_session(self, url: Optional[str] = None) -> str:
        """Inicia nova sessão de browser."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError(
                "Playwright não está disponível. Instale com 'pip install playwright' e 'playwright install'."
            )

        if self._playwright is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless
            )

        if self._browser is None:
            raise RuntimeError("Falha ao inicializar navegador Playwright.")

        context = await self._browser.new_context()
        self._page = await context.new_page()

        if url:
            await self._page.goto(url, timeout=self.timeout)

        session_id = f"session_{datetime.now(timezone.utc).timestamp()}"
        self.session = {
            "id": session_id,
            "url": url,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return session_id

    async def execute_action(
        self, action: BrowserAction, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa ação no browser usando Playwright."""
        if not PLAYWRIGHT_AVAILABLE:
            result = {"status": "simulated", "action": action.value, "params": params}
            self.action_history.append(result)
            return result

        if self._page is None:
            await self.start_session(params.get("url"))

        assert self._page is not None  # para mypy

        if action == BrowserAction.NAVIGATE:
            url = params["url"]
            await self._page.goto(url, timeout=params.get("timeout", self.timeout))
            result: Dict[str, Any] = {"status": "ok", "navigated_to": url}
        elif action == BrowserAction.CLICK:
            await self._page.click(
                params["selector"], timeout=params.get("timeout", self.timeout)
            )
            result = {"status": "ok", "clicked": params["selector"]}
        elif action == BrowserAction.TYPE:
            selector = params["selector"]
            text = params.get("text", "")
            await self._page.fill(
                selector, text, timeout=params.get("timeout", self.timeout)
            )
            result = {"status": "ok", "typed": len(text), "selector": selector}
        elif action == BrowserAction.SELECT:
            selector = params["selector"]
            value = params.get("value")
            await self._page.select_option(selector, value)
            result = {"status": "ok", "selected": value, "selector": selector}
        elif action == BrowserAction.WAIT:
            timeout_ms = params.get("timeout_ms", 1000)
            await self._page.wait_for_timeout(timeout_ms)
            result = {"status": "ok", "waited_ms": timeout_ms}
        elif action == BrowserAction.SCROLL:
            await self._page.evaluate(
                "window.scrollBy(0, arguments[0]);", params.get("pixels", 500)
            )
            result = {"status": "ok", "scrolled": params.get("pixels", 500)}
        elif action == BrowserAction.SCREENSHOT:
            path = (
                params.get("path")
                or f"screenshot_{datetime.now(timezone.utc).timestamp()}.png"
            )
            await self._page.screenshot(
                path=path, full_page=params.get("full_page", True)
            )
            result = {"status": "ok", "screenshot_path": path}
        elif action == BrowserAction.UPLOAD:
            selector = params["selector"]
            files = params.get("files")
            if not isinstance(files, list):
                files = [files]
            await self._page.set_input_files(selector, files)
            result = {"status": "ok", "uploaded_files": files}
        elif action == BrowserAction.EXTRACT:
            selector = params.get("selector")
            if selector:
                element = await self._page.query_selector(selector)
                content = await element.inner_text() if element else None
            else:
                content = await self._page.content()
            result = {"status": "ok", "content": content}
        else:  # pragma: no cover - ação extra
            raise ValueError(f"Ação não suportada: {action.value}")

        self.action_history.append(
            {"status": result["status"], "action": action.value, "params": params}
        )
        return result

    async def close_session(self) -> None:
        """Encerra sessão atual."""
        if self._page is not None:
            await self._page.close()
            self._page = None

        if self._browser is not None:
            await self._browser.close()
            self._browser = None

        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

        self.session = None
