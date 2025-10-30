"""
SessionManager - Gerenciador de sessões de browser/API
Inspirado no Steel.dev session lifecycle
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from enum import Enum


class SessionStatus(Enum):
    """Status da sessão"""
    CREATING = "creating"
    ACTIVE = "active"
    IDLE = "idle"
    TERMINATED = "terminated"
    ERROR = "error"


class SessionManager:
    """
    Gerenciador de sessões com lifecycle management.

    Inspirado em Steel.dev:
    - <1s session start
    - 24h max session duration
    - Context preservation
    - Automatic cleanup
    - Health monitoring
    - Steel.dev integration
    """

    def __init__(
        self, max_session_hours: int = 24, steel_api_key: Optional[str] = None
    ):
        self.max_session_hours = max_session_hours
        self.steel_api_key = steel_api_key
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_count = 0
        self.steel_sessions: Dict[str, str] = {}  # session_id -> steel_session_id

    async def create_session(
        self,
        session_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Cria nova sessão"""
        self.session_count += 1
        session_id = (
            f"session_{self.session_count}_{datetime.now(timezone.utc).timestamp()}"
        )

        self.sessions[session_id] = {
            "id": session_id,
            "type": session_type,
            "status": SessionStatus.ACTIVE,
            "config": config or {},
            "created_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
            "context": {},
        }

        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Recupera sessão existente"""
        session = self.sessions.get(session_id)

        if session:
            # Atualiza last_activity
            session["last_activity"] = datetime.now(timezone.utc)

            # Verifica timeout
            if self._is_expired(session):
                await self.terminate_session(session_id)
                return None

        return session

    async def terminate_session(self, session_id: str) -> bool:
        """Encerra sessão"""
        if session_id in self.sessions:
            self.sessions[session_id]["status"] = SessionStatus.TERMINATED
            self.sessions[session_id]["terminated_at"] = datetime.now(timezone.utc)
            return True
        return False

    async def cleanup_expired_sessions(self) -> int:
        """Remove sessões expiradas"""
        expired_count = 0

        for session_id, session in list(self.sessions.items()):
            if self._is_expired(session):
                await self.terminate_session(session_id)
                expired_count += 1

        return expired_count

    def _is_expired(self, session: Dict[str, Any]) -> bool:
        """Verifica se sessão expirou"""
        age = datetime.now(timezone.utc) - session["created_at"]
        return age > timedelta(hours=self.max_session_hours)

    async def save_context(self, session_id: str, context: Dict[str, Any]) -> bool:
        """Salva contexto da sessão (cookies, localStorage, etc)"""
        session = self.sessions.get(session_id)
        if not session:
            return False

        session["context"] = context
        session["context_saved_at"] = datetime.now(timezone.utc)
        return True

    async def load_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Carrega contexto salvo da sessão"""
        session = self.sessions.get(session_id)
        return session.get("context") if session else None

    async def create_steel_session(
        self, session_type: str = "browser", config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Cria sessão usando Steel.dev API.

        Simula integração com Steel.dev:
        - Cria sessão via API
        - Configura proxy/fingerprint
        - Retorna session_id local
        """
        # TODO: Implementar chamada real para Steel.dev API
        # Por enquanto, simula criação

        session_id = await self.create_session(session_type, config)

        # Simula steel_session_id
        steel_session_id = f"steel_{session_id}"
        self.steel_sessions[session_id] = steel_session_id

        # Adiciona metadados Steel.dev
        self.sessions[session_id]["steel_session_id"] = steel_session_id
        self.sessions[session_id]["steel_config"] = {
            "proxy_enabled": config.get("proxy", True) if config else True,
            "fingerprint_rotated": True,
            "captcha_solver": "enabled",
            "max_duration": f"{self.max_session_hours}h",
        }

        return session_id

    async def get_session_health(self, session_id: str) -> Dict[str, Any]:
        """Retorna status de saúde da sessão"""
        session = self.sessions.get(session_id)

        if not session:
            return {"status": "not_found"}

        age = datetime.now(timezone.utc) - session["created_at"]
        time_since_activity = datetime.now(timezone.utc) - session["last_activity"]

        health = {
            "status": session["status"].value,
            "age_hours": age.total_seconds() / 3600,
            "idle_hours": time_since_activity.total_seconds() / 3600,
            "is_expired": self._is_expired(session),
            "has_context": bool(session.get("context")),
        }

        # Adiciona métricas Steel.dev se aplicável
        if "steel_session_id" in session:
            health["steel_metrics"] = {
                "session_id": session["steel_session_id"],
                "proxy_active": session["steel_config"]["proxy_enabled"],
                "captcha_solved": 0,  # TODO: implementar tracking
                "pages_loaded": 0,  # TODO: implementar tracking
            }

        return health

    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """Lista todas as sessões ativas"""
        active_sessions = []

        for session in self.sessions.values():
            if session["status"] == SessionStatus.ACTIVE and not self._is_expired(
                session
            ):
                active_sessions.append(
                    {
                        "id": session["id"],
                        "type": session["type"],
                        "created_at": session["created_at"].isoformat(),
                        "last_activity": session["last_activity"].isoformat(),
                        "has_steel": "steel_session_id" in session,
                    }
                )

        return active_sessions

    async def extend_session(self, session_id: str, additional_hours: int) -> bool:
        """Estende duração máxima da sessão"""
        session = self.sessions.get(session_id)
        if not session:
            return False

        # Atualiza created_at para "renovar" a sessão
        session["created_at"] = datetime.now(timezone.utc) - timedelta(
            hours=self.max_session_hours - additional_hours
        )
        session["extended_at"] = datetime.now(timezone.utc)
        session["extensions"] = session.get("extensions", 0) + 1

        return True
