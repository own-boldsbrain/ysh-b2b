"""
Testes unitários para StateStore
"""

import pytest
from helios_agents.infrastructure.state_store import StateStore


class TestStateStore:
    """Testes para StateStore"""

    def test_initialization(self):
        """Testa inicialização do store"""
        store = StateStore()

        assert store.storage_backend == "memory"
        assert store.states == {}

    def test_save_and_load_state(self):
        """Testa salvamento e carregamento de estado"""
        store = StateStore()

        state = {"counter": 1, "status": "active"}
        version_id = store.save_state("agent_1", state)

        assert version_id == "agent_1_v1"

        loaded_state = store.load_state("agent_1")
        assert loaded_state == state

    def test_multiple_versions(self):
        """Testa múltiplas versões de estado"""
        store = StateStore()

        # Versão 1
        state1 = {"version": 1}
        store.save_state("agent_1", state1)

        # Versão 2
        state2 = {"version": 2}
        store.save_state("agent_1", state2)

        # Carrega última versão
        loaded = store.load_state("agent_1")
        assert loaded == state2

        # Carrega versão específica
        loaded_v1 = store.load_state("agent_1", 1)
        assert loaded_v1 == state1

        loaded_v2 = store.load_state("agent_1", 2)
        assert loaded_v2 == state2

    def test_diff_states(self):
        """Testa comparação entre versões"""
        store = StateStore()

        state1 = {"a": 1, "b": 2}
        state2 = {"a": 1, "c": 3}

        store.save_state("agent_1", state1)
        store.save_state("agent_1", state2)

        diff = store.diff_states("agent_1", 1, 2)

        assert "a" not in diff["added"]
        assert "b" in diff["removed"]
        assert "c" in diff["added"]
        assert diff["modified"] == {}

    def test_nonexistent_entity(self):
        """Testa carregamento de entidade inexistente"""
        store = StateStore()

        loaded = store.load_state("nonexistent")
        assert loaded is None
