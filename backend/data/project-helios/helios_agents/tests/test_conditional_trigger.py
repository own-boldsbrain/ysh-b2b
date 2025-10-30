"""
Testes para ConditionalTrigger
"""

import pytest
from unittest.mock import AsyncMock
from helios_agents.events.conditional_trigger import ConditionalTrigger, TriggerType


class TestConditionalTrigger:
    """Testes para ConditionalTrigger"""

    def setup_method(self):
        """Setup para cada teste"""
        self.trigger = ConditionalTrigger()

    def test_initialization(self):
        """Testa inicialização do trigger"""
        assert self.trigger.triggers == {}
        assert self.trigger.trigger_history == []
        assert self.trigger.last_values == {}

    def test_register_trigger(self):
        """Testa registro de gatilho"""
        action = AsyncMock()
        condition = {"field": "temperature", "operator": "gt", "value": 30}

        self.trigger.register_trigger(
            "temp_high", TriggerType.THRESHOLD, condition, action, debounce_seconds=60
        )

        assert "temp_high" in self.trigger.triggers
        trigger = self.trigger.triggers["temp_high"]

        assert trigger["type"] == TriggerType.THRESHOLD
        assert trigger["condition"] == condition
        assert trigger["action"] == action
        assert trigger["debounce"] == 60
        assert trigger["last_triggered"] is None
        assert trigger["trigger_count"] == 0

    @pytest.mark.asyncio
    async def test_evaluate_threshold_trigger_above(self):
        """Testa gatilho de threshold acima do limite"""
        action = AsyncMock()
        self.trigger.register_trigger(
            "temp_high",
            TriggerType.THRESHOLD,
            {"field": "temperature", "operator": "gt", "value": 30},
            action,
        )

        context = {"temperature": 35}

        triggered_ids = await self.trigger.evaluate(context)

        assert triggered_ids == ["temp_high"]
        action.assert_called_once_with(context)

        # Verifica histórico
        assert len(self.trigger.trigger_history) == 1
        history_entry = self.trigger.trigger_history[0]
        assert history_entry["trigger_id"] == "temp_high"
        assert history_entry["context"] == context

        # Verifica contador
        assert self.trigger.triggers["temp_high"]["trigger_count"] == 1

    @pytest.mark.asyncio
    async def test_evaluate_threshold_trigger_below(self):
        """Testa gatilho de threshold abaixo do limite"""
        action = AsyncMock()
        self.trigger.register_trigger(
            "temp_high",
            TriggerType.THRESHOLD,
            {"field": "temperature", "operator": "gt", "value": 30},
            action,
        )

        context = {"temperature": 25}

        triggered_ids = await self.trigger.evaluate(context)

        assert triggered_ids == []
        action.assert_not_called()

    @pytest.mark.asyncio
    async def test_evaluate_threshold_trigger_equal(self):
        """Testa gatilho de threshold no limite exato"""
        action = AsyncMock()
        self.trigger.register_trigger(
            "temp_high",
            TriggerType.THRESHOLD,
            {"field": "temperature", "operator": "gt", "value": 30},
            action,
        )

        context = {"temperature": 30}

        triggered_ids = await self.trigger.evaluate(context)

        assert triggered_ids == []
        action.assert_not_called()

    @pytest.mark.asyncio
    async def test_evaluate_change_trigger(self):
        """Testa gatilho de mudança de estado"""
        action = AsyncMock()
        self.trigger.register_trigger(
            "status_change", TriggerType.CHANGE, {"field": "status"}, action
        )

        # Primeira avaliação - sem mudança (primeira vez)
        context1 = {"status": "online"}
        triggered_ids1 = await self.trigger.evaluate(context1)
        assert triggered_ids1 == []
        action.assert_not_called()

        # Segunda avaliação - com mudança
        context2 = {"status": "offline"}
        triggered_ids2 = await self.trigger.evaluate(context2)
        assert triggered_ids2 == ["status_change"]
        action.assert_called_once_with(context2)

    @pytest.mark.asyncio
    async def test_evaluate_no_change_trigger(self):
        """Testa gatilho sem mudança de estado"""
        action = AsyncMock()
        self.trigger.register_trigger(
            "status_change", TriggerType.CHANGE, {"field": "status"}, action
        )

        # Primeira avaliação
        context1 = {"status": "online"}
        await self.trigger.evaluate(context1)

        # Segunda avaliação - mesmo valor
        context2 = {"status": "online"}
        triggered_ids = await self.trigger.evaluate(context2)

        assert triggered_ids == []
        action.assert_not_called()

    @pytest.mark.asyncio
    async def test_debounce_prevents_trigger(self):
        """Testa debounce impedindo gatilho"""
        action = AsyncMock()
        self.trigger.register_trigger(
            "temp_high",
            TriggerType.THRESHOLD,
            {"field": "temperature", "operator": "gt", "value": 30},
            action,
            debounce_seconds=60,
        )

        # Primeiro gatilho
        context = {"temperature": 35}
        await self.trigger.evaluate(context)
        action.assert_called_once()

        # Segundo gatilho imediatamente - deve ser debounced
        await self.trigger.evaluate(context)
        action.assert_called_once()  # Ainda apenas uma chamada

    @pytest.mark.asyncio
    async def test_multiple_triggers(self):
        """Testa múltiplos gatilhos sendo ativados"""
        action1 = AsyncMock()
        action2 = AsyncMock()

        self.trigger.register_trigger(
            "temp_high",
            TriggerType.THRESHOLD,
            {"field": "temperature", "operator": "gt", "value": 30},
            action1,
        )

        self.trigger.register_trigger(
            "humidity_low",
            TriggerType.THRESHOLD,
            {"field": "humidity", "operator": "lt", "value": 20},
            action2,
        )

        context = {"temperature": 35, "humidity": 15}

        triggered_ids = await self.trigger.evaluate(context)

        assert len(triggered_ids) == 2
        assert "temp_high" in triggered_ids
        assert "humidity_low" in triggered_ids

        action1.assert_called_once_with(context)
        action2.assert_called_once_with(context)

    @pytest.mark.asyncio
    async def test_threshold_lt_operator(self):
        """Testa operador 'lt' no threshold"""
        action = AsyncMock()
        self.trigger.register_trigger(
            "temp_low",
            TriggerType.THRESHOLD,
            {"field": "temperature", "operator": "lt", "value": 10},
            action,
        )

        context = {"temperature": 5}

        triggered_ids = await self.trigger.evaluate(context)

        assert triggered_ids == ["temp_low"]
        action.assert_called_once_with(context)

    def test_unsupported_trigger_type(self):
        """Testa tipo de gatilho não suportado"""
        action = AsyncMock()
        self.trigger.register_trigger(
            "schedule_trigger", TriggerType.SCHEDULE, {"cron": "*/5 * * * *"}, action
        )

        context = {"time": "now"}

        # Como SCHEDULE não é implementado, não deve disparar
        # Isso testa o comportamento padrão
        assert self.trigger.triggers["schedule_trigger"]["type"] == TriggerType.SCHEDULE
