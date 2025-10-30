"""
DecisionMaker - Motor de decisões com LLM para agentes autônomos
Inspirado no browser-use get_next_action() e Huginn Liquid templates
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
from enum import Enum
import json


class DecisionType(Enum):
    """Tipos de decisão"""
    ROUTE = "route"  # Roteamento entre agentes
    ACTION = "action"  # Escolha de ação
    VALIDATION = "validation"  # Validação de dados
    ESCALATION = "escalation"  # Escalonamento para humano


class ConfidenceLevel(Enum):
    """Nível de confiança na decisão"""
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


class Decision:
    """Representa uma decisão tomada pelo sistema"""

    def __init__(
        self,
        decision_id: str,
        decision_type: DecisionType,
        chosen_option: str,
        confidence: float,
        reasoning: str,
        alternatives: Optional[List[Dict[str, Any]]] = None,
    ):
        self.decision_id = decision_id
        self.decision_type = decision_type
        self.chosen_option = chosen_option
        self.confidence = confidence
        self.reasoning = reasoning
        self.alternatives = alternatives or []
        self.created_at = datetime.now(timezone.utc)


class DecisionMaker:
    """
    Motor de decisões com suporte a LLM e regras.
    
    Inspirado em:
    - browser-use get_next_action(): LLM escolhe próxima ação baseado em estado
    - Huginn Liquid templates: Regras declarativas com interpolação
    
    Funcionalidades:
    - Decisões baseadas em LLM (via litellm)
    - Sistema de regras declarativas (fallback)
    - Histórico de decisões para aprendizado
    - Validação de confiança e escalação
    """

    def __init__(
        self,
        llm_model: str = "gpt-4",
        min_confidence: float = 0.6,
        enable_llm: bool = True,
    ):
        self.llm_model = llm_model
        self.min_confidence = min_confidence
        self.enable_llm = enable_llm

        # Histórico de decisões
        self.decision_history: List[Decision] = []

        # Regras declarativas (fallback)
        self.rules: Dict[str, List[Dict[str, Any]]] = {}

        # Estatísticas
        self.total_decisions = 0
        self.llm_decisions = 0
        self.rule_based_decisions = 0
        self.escalated_decisions = 0

    def decide(
        self,
        decision_type: DecisionType,
        context: Dict[str, Any],
        options: List[str],
        rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Decision:
        """
        Toma decisão baseada em contexto e opções disponíveis.
        
        Args:
            decision_type: Tipo de decisão
            context: Contexto atual (estado, memória, etc)
            options: Opções disponíveis
            rules: Regras específicas (opcional)
            
        Returns:
            Decisão tomada
        """
        self.total_decisions += 1
        decision_id = (
            f"dec_{self.total_decisions}_{datetime.now(timezone.utc).timestamp()}"
        )

        # Tenta decisão via LLM
        if self.enable_llm:
            try:
                decision = self._decide_with_llm(
                    decision_id, decision_type, context, options
                )
                self.llm_decisions += 1

                # Valida confiança
                if decision.confidence >= self.min_confidence:
                    self.decision_history.append(decision)
                    return decision

            except Exception as e:
                # Fallback para regras
                pass

        # Decisão baseada em regras
        decision = self._decide_with_rules(
            decision_id, decision_type, context, options, rules
        )
        self.rule_based_decisions += 1

        # Escalação se confiança muito baixa
        if decision.confidence < ConfidenceLevel.LOW.value:
            decision = self._escalate_decision(decision_id, decision_type, context, options)
            self.escalated_decisions += 1

        self.decision_history.append(decision)
        return decision

    def add_rule(
        self,
        rule_name: str,
        decision_type: DecisionType,
        condition: Dict[str, Any],
        action: str,
        priority: int = 1,
    ) -> None:
        """
        Adiciona regra declarativa ao sistema.
        
        Args:
            rule_name: Nome da regra
            decision_type: Tipo de decisão que a regra atende
            condition: Condição de ativação (dict com operadores)
            action: Ação a ser tomada
            priority: Prioridade da regra (maior = mais prioritária)
        """
        rule_key = decision_type.value

        if rule_key not in self.rules:
            self.rules[rule_key] = []

        rule = {
            "name": rule_name,
            "condition": condition,
            "action": action,
            "priority": priority,
        }

        self.rules[rule_key].append(rule)

        # Ordena por prioridade
        self.rules[rule_key].sort(key=lambda r: r["priority"], reverse=True)

    def explain_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """
        Explica uma decisão tomada (interpretabilidade).
        
        Args:
            decision_id: ID da decisão
            
        Returns:
            Explicação detalhada
        """
        decision = self._find_decision(decision_id)

        if not decision:
            return None

        return {
            "decision_id": decision.decision_id,
            "decision_type": decision.decision_type.value,
            "chosen_option": decision.chosen_option,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "alternatives": decision.alternatives,
            "created_at": decision.created_at.isoformat(),
            "confidence_level": self._classify_confidence(decision.confidence),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de decisões"""
        return {
            "total_decisions": self.total_decisions,
            "llm_decisions": self.llm_decisions,
            "rule_based_decisions": self.rule_based_decisions,
            "escalated_decisions": self.escalated_decisions,
            "llm_usage_percent": (
                self.llm_decisions / self.total_decisions * 100
                if self.total_decisions > 0 else 0
            ),
            "average_confidence": (
                sum(d.confidence for d in self.decision_history) / len(self.decision_history)
                if self.decision_history else 0
            ),
        }

    # Métodos privados

    def _decide_with_llm(
        self,
        decision_id: str,
        decision_type: DecisionType,
        context: Dict[str, Any],
        options: List[str],
    ) -> Decision:
        """
        Toma decisão usando LLM.
        
        Simula chamada LLM (browser-use style):
        - Prepara prompt com contexto
        - Solicita escolha entre opções
        - Extrai reasoning e confidence
        """
        # TODO: Implementar integração real com litellm
        # Por enquanto, simulação

        prompt = self._build_decision_prompt(decision_type, context, options)

        # Simulação de resposta LLM
        chosen_option = options[0]  # Placeholder
        confidence = 0.85
        reasoning = "Decisão baseada em análise LLM do contexto atual"

        alternatives = [
            {"option": opt, "score": 0.5} for opt in options if opt != chosen_option
        ]

        return Decision(
            decision_id=decision_id,
            decision_type=decision_type,
            chosen_option=chosen_option,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
        )

    def _decide_with_rules(
        self,
        decision_id: str,
        decision_type: DecisionType,
        context: Dict[str, Any],
        options: List[str],
        custom_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> Decision:
        """
        Toma decisão baseada em regras declarativas.
        
        Inspirado em Huginn Liquid templates:
        - Avalia condições em ordem de prioridade
        - Suporta operadores: eq, gt, lt, contains, matches
        """
        rules_to_eval = custom_rules or self.rules.get(decision_type.value, [])

        for rule in rules_to_eval:
            if self._evaluate_condition(rule["condition"], context):
                return Decision(
                    decision_id=decision_id,
                    decision_type=decision_type,
                    chosen_option=rule["action"],
                    confidence=0.75,  # Confiança média para regras
                    reasoning=f"Regra aplicada: {rule['name']}",
                    alternatives=[],
                )

        # Fallback: primeira opção disponível
        return Decision(
            decision_id=decision_id,
            decision_type=decision_type,
            chosen_option=options[0] if options else "no_action",
            confidence=0.5,
            reasoning="Nenhuma regra aplicável, usando fallback",
            alternatives=[],
        )

    def _escalate_decision(
        self,
        decision_id: str,
        decision_type: DecisionType,
        context: Dict[str, Any],
        options: List[str],
    ) -> Decision:
        """
        Escalona decisão para revisão humana.
        """
        return Decision(
            decision_id=decision_id,
            decision_type=decision_type,
            chosen_option="ESCALATE_TO_HUMAN",
            confidence=0.0,
            reasoning="Confiança insuficiente, requer revisão humana",
            alternatives=[{"option": opt, "score": 0.0} for opt in options],
        )

    def _build_decision_prompt(
        self,
        decision_type: DecisionType,
        context: Dict[str, Any],
        options: List[str],
    ) -> str:
        """Constrói prompt para LLM"""
        prompt = f"""
Você é um assistente de decisão para um sistema de homologação solar.

Tipo de decisão: {decision_type.value}

Contexto atual:
{json.dumps(context, indent=2)}

Opções disponíveis:
{chr(10).join(f"- {opt}" for opt in options)}

Escolha a melhor opção e explique seu raciocínio.
Forneça também seu nível de confiança (0.0 a 1.0).

Responda em JSON com formato:
{{
    "chosen_option": "...",
    "confidence": 0.0,
    "reasoning": "...",
    "alternatives": [...]
}}
"""
        return prompt

    def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """
        Avalia condição declarativa.
        
        Suporta operadores:
        - eq: igual
        - ne: diferente
        - gt/gte: maior que / maior ou igual
        - lt/lte: menor que / menor ou igual
        - contains: contém substring
        - in: está na lista
        """
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        # Extrai valor do contexto
        context_value = context.get(field)

        if operator == "eq":
            return context_value == value
        elif operator == "ne":
            return context_value != value
        elif operator == "gt":
            return context_value > value
        elif operator == "gte":
            return context_value >= value
        elif operator == "lt":
            return context_value < value
        elif operator == "lte":
            return context_value <= value
        elif operator == "contains":
            return value in str(context_value)
        elif operator == "in":
            return context_value in value

        return False

    def _classify_confidence(self, confidence: float) -> str:
        """Classifica nível de confiança"""
        if confidence >= ConfidenceLevel.VERY_HIGH.value:
            return "VERY_HIGH"
        elif confidence >= ConfidenceLevel.HIGH.value:
            return "HIGH"
        elif confidence >= ConfidenceLevel.MEDIUM.value:
            return "MEDIUM"
        elif confidence >= ConfidenceLevel.LOW.value:
            return "LOW"
        else:
            return "VERY_LOW"

    def _find_decision(self, decision_id: str) -> Optional[Decision]:
        """Busca decisão no histórico"""
        for decision in self.decision_history:
            if decision.decision_id == decision_id:
                return decision
        return None
