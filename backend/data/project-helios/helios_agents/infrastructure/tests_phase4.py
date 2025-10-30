"""
Testes para Phase 4 - Infraestrutura de Produção
Testa SessionManager, DeploymentController e StateStore com funcionalidades avançadas
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import json

from helios_agents.infrastructure.session_manager import SessionManager
from helios_agents.infrastructure.deployment_controller import (
    DeploymentController,
    DeploymentStrategy,
)
from helios_agents.infrastructure.state_store import StateStore, CloudStorageProvider


class TestSessionManager:
    """Testes para SessionManager com integração Steel.dev"""

    @pytest.fixture
    def session_manager(self):
        return SessionManager(steel_api_key="test_key")

    def test_create_steel_session(self, session_manager):
        """Testa criação de sessão Steel.dev"""
        session_id = asyncio.run(
            session_manager.create_steel_session(
                session_type="browser", config={"proxy": True}
            )
        )

        assert session_id.startswith("session_")
        assert session_id in session_manager.sessions

    def test_get_session_health(self, session_manager):
        """Testa verificação de saúde da sessão"""
        session_id = asyncio.run(session_manager.create_steel_session())

        health = asyncio.run(session_manager.get_session_health(session_id))
        assert "status" in health
        assert "age_hours" in health
        assert "idle_hours" in health
        assert "is_expired" in health

    def test_save_load_context(self, session_manager):
        """Testa salvamento e carregamento de contexto"""
        session_id = asyncio.run(session_manager.create_steel_session())
        context = {"cookies": ["test"], "local_storage": {"key": "value"}}

        # Salvar contexto
        asyncio.run(session_manager.save_context(session_id, context))

        # Carregar contexto
        loaded_context = asyncio.run(session_manager.load_context(session_id))
        assert loaded_context == context

    def test_extend_session(self, session_manager):
        """Testa extensão de sessão"""
        session_id = asyncio.run(session_manager.create_steel_session())

        extended = asyncio.run(session_manager.extend_session(session_id, 2))
        assert extended

        session = session_manager.sessions[session_id]
        assert session["extensions"] == 1

    def test_list_active_sessions(self, session_manager):
        """Testa listagem de sessões ativas"""
        session1 = asyncio.run(session_manager.create_steel_session())
        session2 = asyncio.run(session_manager.create_steel_session())

        active = asyncio.run(session_manager.list_active_sessions())
        assert len(active) == 2
        assert session1 in [s["id"] for s in active]
        assert session2 in [s["id"] for s in active]


class TestDeploymentController:
    """Testes para DeploymentController com estratégias de deployment"""

    @pytest.fixture
    def deployment_controller(self):
        return DeploymentController()

    def test_deploy_all_at_once(self, deployment_controller):
        """Testa estratégia all-at-once"""
        agent_config = {
            "agents": [{"name": "agent1"}, {"name": "agent2"}, {"name": "agent3"}]
        }

        deployment_id = asyncio.run(
            deployment_controller.deploy(
                agent_config=agent_config, strategy=DeploymentStrategy.ALL_AT_ONCE.value
            )
        )

        status = asyncio.run(deployment_controller.get_deployment_status(deployment_id))
        assert status["strategy"] == "all_at_once"
        assert len(status["config"]["agents"]) == 3
        assert status["status"].value == "completed"

    def test_deploy_rolling(self, deployment_controller):
        """Testa estratégia rolling"""
        agent_config = {
            "agents": [
                {"name": "agent1"},
                {"name": "agent2"},
                {"name": "agent3"},
                {"name": "agent4"},
            ]
        }

        deployment_id = asyncio.run(
            deployment_controller.deploy(
                agent_config=agent_config, strategy=DeploymentStrategy.ROLLING.value
            )
        )

        status = asyncio.run(deployment_controller.get_deployment_status(deployment_id))
        assert status["strategy"] == "rolling"
        assert len(status["config"]["agents"]) == 4
        assert status["status"].value == "completed"

    def test_deploy_blue_green(self, deployment_controller):
        """Testa estratégia blue-green"""
        agent_config = {"agents": [{"name": "agent1"}, {"name": "agent2"}]}

        deployment_id = asyncio.run(
            deployment_controller.deploy(
                agent_config=agent_config, strategy=DeploymentStrategy.BLUE_GREEN.value
            )
        )

        status = asyncio.run(deployment_controller.get_deployment_status(deployment_id))
        assert status["strategy"] == "blue_green"
        assert len(status["config"]["agents"]) == 2
        assert status["status"].value == "completed"

    def test_deploy_canary(self, deployment_controller):
        """Testa estratégia canary"""
        agent_config = {
            "agents": [
                {"name": "agent1"},
                {"name": "agent2"},
                {"name": "agent3"},
                {"name": "agent4"},
                {"name": "agent5"},
            ]
        }

        deployment_id = asyncio.run(
            deployment_controller.deploy(
                agent_config=agent_config, strategy=DeploymentStrategy.CANARY.value
            )
        )

        status = asyncio.run(deployment_controller.get_deployment_status(deployment_id))
        assert status["strategy"] == "canary"
        assert len(status["config"]["agents"]) == 5

    def test_health_check_failure_rollback(self, deployment_controller):
        """Testa rollback em caso de falha no health check"""
        agent_config = {"agents": [{"name": "agent1"}, {"name": "agent2"}]}

        # Mock health check para falhar
        with patch.object(
            deployment_controller, "_perform_health_check", return_value=False
        ):
            deployment_id = asyncio.run(
                deployment_controller.deploy(
                    agent_config=agent_config,
                    strategy=DeploymentStrategy.ALL_AT_ONCE.value,
                    health_check_url="http://test.com/health",
                )
            )

            status = asyncio.run(
                deployment_controller.get_deployment_status(deployment_id)
            )
            assert status["status"].value == "rolled_back"

    def test_get_active_deployments(self, deployment_controller):
        """Testa obtenção de deployments ativos"""
        agent_config = {"agents": [{"name": "agent1"}]}

        asyncio.run(
            deployment_controller.deploy(
                agent_config=agent_config, strategy=DeploymentStrategy.ALL_AT_ONCE.value
            )
        )

        active = asyncio.run(deployment_controller.get_active_deployments())
        assert DeploymentStrategy.ALL_AT_ONCE.value in active


class TestStateStore:
    """Testes para StateStore com cloud backup"""

    @pytest.fixture
    def state_store(self):
        return StateStore()

    @pytest.fixture
    def state_store_with_cloud(self):
        return StateStore(
            cloud_provider=CloudStorageProvider.S3.value,
            cloud_bucket="test-bucket",
            auto_backup=True,
            backup_interval_hours=1,
        )

    def test_save_load_state(self, state_store):
        """Testa salvamento e carregamento de estado"""
        entity_id = "test_entity"
        state = {"key": "value", "number": 42}

        # Salvar estado
        version_id = state_store.save_state(entity_id, state)
        assert version_id == "test_entity_v1"

        # Carregar estado
        loaded_state = state_store.load_state(entity_id)
        assert loaded_state == state

    def test_state_versioning(self, state_store):
        """Testa versionamento de estados"""
        entity_id = "test_entity"

        # Versão 1
        state_store.save_state(entity_id, {"version": 1})
        # Versão 2
        state_store.save_state(entity_id, {"version": 2})
        # Versão 3
        state_store.save_state(entity_id, {"version": 3})

        # Carregar versão específica
        v1 = state_store.load_state(entity_id, 1)
        v2 = state_store.load_state(entity_id, 2)
        v3 = state_store.load_state(entity_id, 3)

        assert v1["version"] == 1
        assert v2["version"] == 2
        assert v3["version"] == 3

        # Última versão
        latest = state_store.load_state(entity_id)
        assert latest["version"] == 3

    def test_state_diff(self, state_store):
        """Testa diff entre versões"""
        entity_id = "test_entity"

        state_store.save_state(entity_id, {"a": 1, "b": 2})
        state_store.save_state(entity_id, {"a": 1, "c": 3})

        diff = state_store.diff_states(entity_id, 1, 2)

        assert "b" in diff["removed"]
        assert "c" in diff["added"]
        assert diff["modified"] == {}

    def test_local_backup(self, state_store):
        """Testa backup local"""
        entity_id = "test_entity"
        state_store.save_state(entity_id, {"test": "data"})

        # Executar backup
        result = asyncio.run(state_store.backup_to_cloud(entity_id))

        assert result["success"] is True
        assert result["backed_up_entities"] == 1
        assert result["total_versions"] == 1

        # Verificar arquivo criado
        backup_file = state_store.local_backup_path / f"{entity_id}.json"
        assert backup_file.exists()

        # Testar restauração
        # Limpar estado atual
        state_store.states = {}

        result = asyncio.run(state_store.restore_from_cloud(entity_id))
        assert result["success"] is True
        assert result["versions_restored"] == 1

        # Verificar estado restaurado
        restored_state = state_store.load_state(entity_id)
        assert restored_state == {"test": "data"}

    def test_auto_backup_logic(self, state_store_with_cloud):
        """Testa lógica de backup automático"""
        # Inicialmente deve fazer backup (last_backup é None)
        assert state_store_with_cloud.should_backup() is True

        # Após backup, não deve fazer imediatamente
        state_store_with_cloud.last_backup = datetime.now(timezone.utc)
        assert state_store_with_cloud.should_backup() is False

        # Simular tempo passado suficiente para backup
        # Como o intervalo é 1 hora, vamos simular 2 horas atrás
        from datetime import timedelta

        two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
        state_store_with_cloud.last_backup = two_hours_ago
        assert state_store_with_cloud.should_backup() is True

    def test_backup_status(self, state_store_with_cloud):
        """Testa status do backup"""
        status = state_store_with_cloud.get_backup_status()

        assert status["cloud_provider"] == "s3"
        assert status["cloud_bucket"] == "test-bucket"
        assert status["auto_backup_enabled"] is True
        assert status["backup_interval_hours"] == 1
        assert status["entities_count"] == 0
        assert status["total_versions"] == 0

    def test_cloud_provider_fallback(self, state_store):
        """Testa fallback para local quando não há cloud provider"""
        entity_id = "test_entity"
        state_store.save_state(entity_id, {"test": "data"})

        # Backup deve usar local storage
        result = asyncio.run(state_store.backup_to_cloud(entity_id))
        assert result["success"] is True

        # Restore deve funcionar
        state_store.states = {}
        result = asyncio.run(state_store.restore_from_cloud(entity_id))
        assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
