"""
Testes unitários para DecisionMaker
"""

import pytest
from helios_agents.core.decision_maker import (
    DecisionMaker,
    DecisionType,
    Decision,
    ConfidenceLevel,
)


class TestDecisionMaker:
    """Testes para DecisionMaker"""

    def test_initialization(self):
        """Testa inicialização do DecisionMaker"""
        dm = DecisionMaker()

        assert dm.llm_model == "gpt-4"
        assert dm.min_confidence == 0.6
        assert dm.enable_llm is True
        assert dm.decision_history == []
        assert dm.rules == {}
        assert dm.total_decisions == 0

    def test_decide_with_rules(self):
        """Testa decisão baseada em regras"""
        dm = DecisionMaker(enable_llm=False)  # Desabilita LLM para usar regras

        # Adiciona regra
        dm.add_rule(
            rule_name="test_rule",
            decision_type=DecisionType.ACTION,
            condition={"field": "status", "operator": "eq", "value": "active"},
            action="proceed",
        )

        context = {"status": "active"}
        options = ["proceed", "wait", "stop"]

        decision = dm.decide(DecisionType.ACTION, context, options)

        assert decision.chosen_option == "proceed"
        assert decision.confidence == 0.75
        assert "test_rule" in decision.reasoning
        assert dm.rule_based_decisions == 1

    def test_decide_fallback(self):
        """Testa fallback quando nenhuma regra aplica"""
        dm = DecisionMaker(enable_llm=False)

        context = {"status": "inactive"}
        options = ["wait", "stop"]

        decision = dm.decide(DecisionType.ACTION, context, options)

        assert decision.chosen_option == "wait"  # Primeira opção
        assert decision.confidence == 0.5
        assert "fallback" in decision.reasoning

    def test_decide_escalation(self):
        """Testa escalação para humano quando confiança baixa"""
        # TODO: Implementar teste quando lógica de escalação estiver completa
        pass

    def test_add_rule(self):
        """Testa adição de regras"""
        dm = DecisionMaker()

        dm.add_rule(
            rule_name="priority_high",
            decision_type=DecisionType.ACTION,
            condition={"field": "priority", "operator": "eq", "value": "high"},
            action="urgent_action",
            priority=10,
        )

        dm.add_rule(
            rule_name="priority_low",
            decision_type=DecisionType.ACTION,
            condition={"field": "priority", "operator": "eq", "value": "low"},
            action="normal_action",
            priority=1,
        )

        rules = dm.rules[DecisionType.ACTION.value]
        assert len(rules) == 2
        assert rules[0]["priority"] == 10  # Ordenado por prioridade
        assert rules[1]["priority"] == 1

    def test_explain_decision(self):
        """Testa explicação de decisão"""
        dm = DecisionMaker(enable_llm=False)

        dm.add_rule(
            rule_name="test_rule",
            decision_type=DecisionType.ACTION,
            condition={"field": "test", "operator": "eq", "value": True},
            action="test_action",
        )

        context = {"test": True}
        options = ["test_action", "other"]

        decision = dm.decide(DecisionType.ACTION, context, options)

        explanation = dm.explain_decision(decision.decision_id)

        assert explanation is not None
        assert explanation["chosen_option"] == "test_action"
        assert explanation["confidence"] == 0.75
        assert "confidence_level" in explanation

    def test_get_statistics(self):
        """Testa obtenção de estatísticas"""
        dm = DecisionMaker(enable_llm=False)

        # Toma algumas decisões
        dm.decide(DecisionType.ACTION, {}, ["action1"])
        dm.decide(DecisionType.ACTION, {}, ["action2"])

        stats = dm.get_statistics()

        assert stats["total_decisions"] == 2
        assert stats["rule_based_decisions"] == 2
        assert stats["llm_decisions"] == 0
        assert "average_confidence" in stats

    def test_evaluate_condition(self):
        """Testa avaliação de condições"""
        dm = DecisionMaker()

        # Testa operadores
        context = {"count": 5, "status": "active", "tags": ["urgent", "important"]}

        assert (
            dm._evaluate_condition(
                {"field": "count", "operator": "gt", "value": 3}, context
            )
            is True
        )

        assert (
            dm._evaluate_condition(
                {"field": "status", "operator": "eq", "value": "active"}, context
            )
            is True
        )

        assert (
            dm._evaluate_condition(
                {"field": "status", "operator": "eq", "value": "inactive"}, context
            )
            is False
        )

        assert (
            dm._evaluate_condition(
                {"field": "tags", "operator": "contains", "value": "urgent"}, context
            )
            is True
        )
