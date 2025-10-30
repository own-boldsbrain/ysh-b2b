"""
Testes unitários para StatefulAgent
"""

import pytest
from datetime import datetime
from helios_agents.core.stateful_agent import StatefulAgent, AgentState


class TestStatefulAgent:
    """Testes para StatefulAgent"""

    def test_initialization(self):
        """Testa inicialização do agente"""
        agent = StatefulAgent("test_agent", "Test Agent")

        assert agent.agent_id == "test_agent"
        assert agent.name == "Test Agent"
        assert agent.state == AgentState.IDLE
        assert agent.memory == []
        assert agent.next_goal is None
        assert agent.actions == []
        assert agent.execution_count == 0

    def test_receive_events(self):
        """Testa processamento de eventos recebidos"""
        agent = StatefulAgent("test_agent", "Test Agent")

        events = [
            {
                "id": "event_1",
                "event_type": "test_event",
                "payload": {"message": "hello"},
            }
        ]

        output_events = agent.receive(events)

        assert len(output_events) == 1
        assert output_events[0]["event_type"] == "event_processed"
        assert agent.execution_count == 1
        assert len(agent.memory) == 1

    def test_check_method(self):
        """Testa método check (scheduled)"""
        agent = StatefulAgent("test_agent", "Test Agent")

        # Por padrão, _should_trigger retorna False
        output_events = agent.check()

        assert len(output_events) == 0
        assert agent.execution_count == 0  # check não incrementa execution_count

    def test_create_event(self):
        """Testa criação de eventos"""
        agent = StatefulAgent("test_agent", "Test Agent")

        event = agent.create_event(event_type="test_event", payload={"data": "test"})

        assert event["source_agent"] == "test_agent"
        assert event["event_type"] == "test_event"
        assert event["payload"] == {"data": "test"}
        assert "id" in event
        assert "created_at" in event

    def test_state_persistence(self):
        """Testa salvamento e carregamento de estado"""
        agent = StatefulAgent("test_agent", "Test Agent")

        # Modifica estado
        agent.memory.append({"test": "data"})
        agent.execution_count = 5

        # Salva estado
        state = agent.get_state()

        # Cria novo agente e carrega estado
        new_agent = StatefulAgent("test_agent", "Test Agent")
        new_agent.load_state(state)

        assert new_agent.memory == [{"test": "data"}]
        assert new_agent.execution_count == 5

    def test_error_handling(self):
        """Testa tratamento de erros"""
        agent = StatefulAgent("test_agent", "Test Agent")

        # Simula erro sobrescrevendo _process_event
        def failing_process(event):
            raise ValueError("Test error")

        agent._process_event = failing_process

        events = [{"id": "event_1", "event_type": "test"}]
        output_events = agent.receive(events)

        assert len(output_events) == 1
        assert output_events[0]["event_type"] == "agent_error"
        assert "Test error" in output_events[0]["payload"]["error"]
        assert agent.state == AgentState.ERROR
