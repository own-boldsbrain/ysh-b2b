"""
Testes para Aggregator
"""

import pytest
from datetime import datetime, timedelta, timezone
from helios_agents.events.aggregator import Aggregator


class TestAggregator:
    """Testes para Aggregator"""

    def setup_method(self):
        """Setup para cada teste"""
        self.aggregator = Aggregator(window_size_seconds=300)  # 5 minutos

    def test_initialization(self):
        """Testa inicialização do aggregator"""
        assert self.aggregator.window_size == 300
        assert self.aggregator.event_buffer == {}
        assert self.aggregator.aggregation_history == []

    def test_add_event(self):
        """Testa adição de evento"""
        event = {"event_type": "user_action", "user_id": "123", "action": "login"}

        self.aggregator.add_event(event)

        assert "user_action" in self.aggregator.event_buffer
        assert len(self.aggregator.event_buffer["user_action"]) == 1

        stored_event = self.aggregator.event_buffer["user_action"][0]
        assert stored_event["user_id"] == "123"
        assert stored_event["action"] == "login"
        assert "received_at" in stored_event

    def test_add_multiple_events_same_type(self):
        """Testa adição de múltiplos eventos do mesmo tipo"""
        events = [
            {"event_type": "click", "element": "button1"},
            {"event_type": "click", "element": "button2"},
            {"event_type": "click", "element": "button1"},
        ]

        for event in events:
            self.aggregator.add_event(event)

        assert len(self.aggregator.event_buffer["click"]) == 3

    def test_add_events_different_types(self):
        """Testa adição de eventos de tipos diferentes"""
        events = [
            {"event_type": "click", "element": "button"},
            {"event_type": "view", "page": "home"},
            {"event_type": "click", "element": "link"},
        ]

        for event in events:
            self.aggregator.add_event(event)

        assert len(self.aggregator.event_buffer["click"]) == 2
        assert len(self.aggregator.event_buffer["view"]) == 1

    def test_aggregate_empty_buffer(self):
        """Testa agregação com buffer vazio"""
        results = self.aggregator.aggregate()

        assert results == []

    def test_aggregate_single_event_type(self):
        """Testa agregação de um tipo de evento"""
        events = [
            {"event_type": "click", "element": "button1", "user_id": "1"},
            {"event_type": "click", "element": "button2", "user_id": "2"},
            {"event_type": "click", "element": "button1", "user_id": "1"},
        ]

        for event in events:
            self.aggregator.add_event(event)

        results = self.aggregator.aggregate()

        assert len(results) == 1
        result = results[0]

        assert result["event_type"] == "click_aggregated"
        assert result["count"] == 3
        assert len(result["events"]) == 3
        assert result["summary"]["total_events"] == 3
        assert result["summary"]["event_types"] == ["click"]
        assert "aggregated_at" in result

        # Buffer deve estar vazio após agregação
        assert len(self.aggregator.event_buffer["click"]) == 0

        # Histórico deve conter a agregação
        assert len(self.aggregator.aggregation_history) == 1

    def test_aggregate_multiple_event_types(self):
        """Testa agregação de múltiplos tipos de evento"""
        events = [
            {"event_type": "click", "element": "button"},
            {"event_type": "view", "page": "home"},
            {"event_type": "view", "page": "about"},
            {"event_type": "click", "element": "link"},
        ]

        for event in events:
            self.aggregator.add_event(event)

        results = self.aggregator.aggregate()

        assert len(results) == 2

        # Encontra resultados por tipo
        click_result = next(r for r in results if r["event_type"] == "click_aggregated")
        view_result = next(r for r in results if r["event_type"] == "view_aggregated")

        assert click_result["count"] == 2
        assert view_result["count"] == 2

    def test_aggregate_specific_event_type(self):
        """Testa agregação de tipo específico"""
        events = [
            {"event_type": "click", "element": "button"},
            {"event_type": "view", "page": "home"},
            {"event_type": "click", "element": "link"},
        ]

        for event in events:
            self.aggregator.add_event(event)

        results = self.aggregator.aggregate("click")

        assert len(results) == 1
        result = results[0]

        assert result["event_type"] == "click_aggregated"
        assert result["count"] == 2

        # Outros tipos devem permanecer no buffer
        assert len(self.aggregator.event_buffer["view"]) == 1
        assert len(self.aggregator.event_buffer.get("click", [])) == 0

    def test_aggregate_window_filtering(self):
        """Testa filtragem por janela temporal"""
        # Adiciona evento "recente"
        recent_event = {"event_type": "click", "element": "button"}
        self.aggregator.add_event(recent_event)

        # Simula evento antigo modificando timestamp
        old_timestamp = (
            datetime.now(timezone.utc) - timedelta(seconds=400)
        ).isoformat()
        self.aggregator.event_buffer["click"][0]["received_at"] = old_timestamp

        # Adiciona outro evento recente
        self.aggregator.add_event({"event_type": "click", "element": "link"})

        results = self.aggregator.aggregate()

        assert len(results) == 1
        result = results[0]

        # Deve conter apenas o evento recente
        assert result["count"] == 1
        assert result["events"][0]["element"] == "link"

    def test_generate_summary(self):
        """Testa geração de resumo"""
        events = [
            {"event_type": "click", "source_agent": "agent1", "element": "btn1"},
            {"event_type": "click", "source_agent": "agent2", "element": "btn2"},
            {"event_type": "view", "source_agent": "agent1", "page": "home"},
        ]

        summary = self.aggregator._generate_summary(events)

        assert summary["total_events"] == 3
        assert set(summary["event_types"]) == {"click", "view"}
        assert set(summary["source_agents"]) == {"agent1", "agent2"}

    def test_generate_summary_empty_events(self):
        """Testa geração de resumo com lista vazia"""
        summary = self.aggregator._generate_summary([])

        assert summary["total_events"] == 0
        assert summary["event_types"] == []
        assert summary["source_agents"] == []
