"""
Multi-Agent Coordination - Coordenação entre múltiplos agentes
Inspirado no Huginn agent network e SST resource linking
"""

from typing import Any, Dict, List, Optional, Set, Callable
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import json
from pathlib import Path
import uuid


class AgentStatus(Enum):
    """Status de um agente"""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class MessageType(Enum):
    """Tipos de mensagens entre agentes"""

    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    EVENT_NOTIFICATION = "event_notification"
    COORDINATION_SIGNAL = "coordination_signal"
    HEALTH_CHECK = "health_check"


class CoordinationMode(Enum):
    """Modos de coordenação"""

    SEQUENTIAL = "sequential"  # Um agente por vez
    PARALLEL = "parallel"  # Múltiplos agentes simultâneos
    PIPELINE = "pipeline"  # Encadeamento de agentes
    COMPETITION = "competition"  # Melhor resultado vence
    COLLABORATION = "collaboration"  # Agentes colaboram


@dataclass
class AgentInfo:
    """Informações sobre um agente registrado"""

    id: str
    name: str
    agent_type: str
    capabilities: Set[str]
    status: AgentStatus = AgentStatus.IDLE
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_score: float = 1.0  # 0.0 a 1.0

    def is_available(self) -> bool:
        """Verifica se o agente está disponível"""
        return self.status == AgentStatus.IDLE

    def update_last_seen(self) -> None:
        """Atualiza timestamp de última atividade"""
        self.last_seen = datetime.now(timezone.utc)

    def calculate_performance_score(
        self, success_rate: float, avg_response_time: float
    ) -> None:
        """Calcula score de performance baseado em métricas"""
        # Score baseado em taxa de sucesso e tempo de resposta
        time_factor = max(0, 1 - (avg_response_time / 60))  # Penaliza tempos > 60s
        self.performance_score = (success_rate * 0.7) + (time_factor * 0.3)


@dataclass
class Message:
    """Mensagem entre agentes"""

    message_type: MessageType
    sender: str
    recipient: str
    payload: Dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None  # Para rastrear conversas
    priority: int = 1  # 1-5, 5 sendo mais alta

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "type": self.message_type.value,
            "sender": self.sender,
            "recipient": self.recipient,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "priority": self.priority,
        }


@dataclass
class CoordinationContext:
    """Contexto de coordenação entre agentes"""

    coordination_id: str
    mode: CoordinationMode
    participants: List[str]  # IDs dos agentes participantes
    shared_state: Dict[str, Any] = field(default_factory=dict)
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def add_message(self, message: Message) -> None:
        """Adiciona mensagem ao contexto"""
        self.messages.append(message)

    def get_messages_for_agent(self, agent_id: str) -> List[Message]:
        """Retorna mensagens para um agente específico"""
        return [msg for msg in self.messages if msg.recipient == agent_id]

    def update_shared_state(self, key: str, value: Any) -> None:
        """Atualiza estado compartilhado"""
        self.shared_state[key] = value

    def get_shared_state(self, key: str, default: Any = None) -> Any:
        """Obtém valor do estado compartilhado"""
        return self.shared_state.get(key, default)


class MultiAgentCoordinator:
    """
    Coordenador de múltiplos agentes com comunicação e compartilhamento de estado.

    Inspirado no Huginn agent network e SST resource linking.
    """

    def __init__(
        self,
        state_persistence_path: Optional[str] = None,
        max_message_queue: int = 1000,
        health_check_interval: int = 30,
    ):
        self.agents: Dict[str, AgentInfo] = {}
        self.coordination_contexts: Dict[str, CoordinationContext] = {}
        self.message_queue: asyncio.Queue[Message] = asyncio.Queue(
            maxsize=max_message_queue
        )

        # Persistência
        self.state_path = Path(state_persistence_path or "./coordinator_state.json")
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

        # Callbacks para integração com agentes reais
        self.agent_callbacks: Dict[str, Callable] = {}

        # Health monitoring
        self.health_check_interval = health_check_interval
        self._health_task: Optional[asyncio.Task] = None

        # Carrega estado se existir
        self._load_state()

    def register_agent(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        capabilities: Set[str],
        callback: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Registra um agente no sistema de coordenação.

        Args:
            agent_id: ID único do agente
            name: Nome descritivo
            agent_type: Tipo do agente (BrowserController, DataExtractor, etc.)
            capabilities: Conjunto de capacidades do agente
            callback: Função para invocar o agente real
            metadata: Metadados adicionais
        """
        agent = AgentInfo(
            id=agent_id,
            name=name,
            agent_type=agent_type,
            capabilities=capabilities,
            metadata=metadata or {},
        )

        self.agents[agent_id] = agent

        if callback:
            self.agent_callbacks[agent_id] = callback

        self._save_state()

    def unregister_agent(self, agent_id: str) -> bool:
        """
        Remove agente do sistema.

        Args:
            agent_id: ID do agente

        Returns:
            True se removido com sucesso
        """
        if agent_id in self.agents:
            del self.agents[agent_id]
            if agent_id in self.agent_callbacks:
                del self.agent_callbacks[agent_id]
            self._save_state()
            return True
        return False

    async def start_coordination(
        self,
        coordination_mode: CoordinationMode,
        participants: List[str],
        initial_state: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Inicia uma sessão de coordenação entre agentes.

        Args:
            coordination_mode: Modo de coordenação
            participants: Lista de IDs dos agentes participantes
            initial_state: Estado inicial compartilhado

        Returns:
            ID da coordenação
        """
        coordination_id = f"coord_{len(self.coordination_contexts)}_{datetime.now(timezone.utc).timestamp()}"

        context = CoordinationContext(
            coordination_id=coordination_id,
            mode=coordination_mode,
            participants=participants,
            shared_state=initial_state or {},
        )

        self.coordination_contexts[coordination_id] = context

        # Inicia monitoramento de saúde se não estiver rodando
        if not self._health_task or self._health_task.done():
            self._health_task = asyncio.create_task(self._health_monitor())

        return coordination_id

    async def send_message(
        self, message: Message, coordination_id: Optional[str] = None
    ) -> None:
        """
        Envia mensagem para um agente.

        Args:
            message: Mensagem a enviar
            coordination_id: ID da coordenação (opcional)
        """
        # Adiciona à fila
        await self.message_queue.put(message)

        # Registra no contexto se aplicável
        if coordination_id and coordination_id in self.coordination_contexts:
            self.coordination_contexts[coordination_id].add_message(message)

    async def broadcast_message(
        self,
        sender: str,
        recipients: List[str],
        message_type: MessageType,
        payload: Dict[str, Any],
        coordination_id: Optional[str] = None,
        priority: int = 1,
    ) -> None:
        """
        Envia mensagem para múltiplos agentes.

        Args:
            sender: ID do agente remetente
            recipients: Lista de IDs dos destinatários
            message_type: Tipo da mensagem
            payload: Conteúdo da mensagem
            coordination_id: ID da coordenação
            priority: Prioridade da mensagem
        """
        for recipient in recipients:
            message = Message(
                message_type=message_type,
                sender=sender,
                recipient=recipient,
                payload=payload,
                correlation_id=coordination_id,
                priority=priority,
            )
            await self.send_message(message, coordination_id)

    async def request_task_execution(
        self,
        requester: str,
        target_agent: str,
        task_description: str,
        parameters: Optional[Dict[str, Any]] = None,
        coordination_id: Optional[str] = None,
        timeout: int = 300,  # 5 minutos
    ) -> Dict[str, Any]:
        """
        Solicita execução de tarefa para um agente específico.

        Args:
            requester: ID do agente solicitante
            target_agent: ID do agente alvo
            task_description: Descrição da tarefa
            parameters: Parâmetros da tarefa
            coordination_id: ID da coordenação
            timeout: Timeout em segundos

        Returns:
            Resultado da execução
        """
        if target_agent not in self.agents:
            raise ValueError(f"Agent {target_agent} not registered")

        # Marca agente como ocupado
        self.agents[target_agent].status = AgentStatus.BUSY

        try:
            # Cria mensagem de requisição
            request_message = Message(
                message_type=MessageType.TASK_REQUEST,
                sender=requester,
                recipient=target_agent,
                payload={
                    "task_description": task_description,
                    "parameters": parameters or {},
                    "timeout": timeout,
                },
                correlation_id=coordination_id,
                priority=3,
            )

            await self.send_message(request_message, coordination_id)

            # Aguarda resposta (simplificado - em produção usaria callbacks)
            response = await self._wait_for_response(
                request_message.id, target_agent, timeout
            )

            return response

        finally:
            # Libera agente
            self.agents[target_agent].status = AgentStatus.IDLE
            self.agents[target_agent].update_last_seen()

    async def _wait_for_response(
        self, request_id: str, from_agent: str, timeout: int
    ) -> Dict[str, Any]:
        """Aguarda resposta de um agente (simplificado)"""
        # Em implementação real, isso seria feito com callbacks ou pub/sub
        await asyncio.sleep(1)  # Simula processamento

        return {
            "request_id": request_id,
            "status": "completed",
            "result": {"simulated": True},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def coordinate_sequential(
        self, coordination_id: str, tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Coordenação sequencial: executa tarefas uma após a outra.

        Args:
            coordination_id: ID da coordenação
            tasks: Lista de tarefas a executar

        Returns:
            Resultados da coordenação
        """
        context = self.coordination_contexts.get(coordination_id)
        if not context:
            raise ValueError(f"Coordination {coordination_id} not found")

        results = []

        for task in tasks:
            agent_id = task["agent_id"]
            task_desc = task["description"]
            params = task.get("parameters", {})

            try:
                result = await self.request_task_execution(
                    requester="coordinator",
                    target_agent=agent_id,
                    task_description=task_desc,
                    parameters=params,
                    coordination_id=coordination_id,
                )

                results.append({"task": task, "result": result, "status": "success"})

                # Atualiza estado compartilhado
                context.update_shared_state(f"task_{len(results)}", result)

            except Exception as e:
                results.append({"task": task, "error": str(e), "status": "failed"})

        return {
            "coordination_id": coordination_id,
            "mode": "sequential",
            "total_tasks": len(tasks),
            "completed_tasks": len([r for r in results if r["status"] == "success"]),
            "failed_tasks": len([r for r in results if r["status"] == "failed"]),
            "results": results,
        }

    async def coordinate_parallel(
        self, coordination_id: str, tasks: List[Dict[str, Any]], max_concurrent: int = 5
    ) -> Dict[str, Any]:
        """
        Coordenação paralela: executa múltiplas tarefas simultaneamente.

        Args:
            coordination_id: ID da coordenação
            tasks: Lista de tarefas a executar
            max_concurrent: Máximo de tarefas simultâneas

        Returns:
            Resultados da coordenação
        """
        context = self.coordination_contexts.get(coordination_id)
        if not context:
            raise ValueError(f"Coordination {coordination_id} not found")

        semaphore = asyncio.Semaphore(max_concurrent)
        results = []

        async def execute_with_semaphore(task):
            async with semaphore:
                agent_id = task["agent_id"]
                task_desc = task["description"]
                params = task.get("parameters", {})

                try:
                    result = await self.request_task_execution(
                        requester="coordinator",
                        target_agent=agent_id,
                        task_description=task_desc,
                        parameters=params,
                        coordination_id=coordination_id,
                    )

                    return {"task": task, "result": result, "status": "success"}

                except Exception as e:
                    return {"task": task, "error": str(e), "status": "failed"}

        # Executa todas as tarefas em paralelo
        task_coroutines = [execute_with_semaphore(task) for task in tasks]
        parallel_results = await asyncio.gather(
            *task_coroutines, return_exceptions=True
        )

        # Processa resultados
        for result in parallel_results:
            if isinstance(result, Exception):
                results.append({"error": str(result), "status": "exception"})
            else:
                results.append(result)

        return {
            "coordination_id": coordination_id,
            "mode": "parallel",
            "total_tasks": len(tasks),
            "max_concurrent": max_concurrent,
            "completed_tasks": len(
                [r for r in results if r.get("status") == "success"]
            ),
            "failed_tasks": len([r for r in results if r.get("status") == "failed"]),
            "results": results,
        }

    async def coordinate_pipeline(
        self, coordination_id: str, pipeline_stages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Coordenação em pipeline: cada estágio processa resultado do anterior.

        Args:
            coordination_id: ID da coordenação
            pipeline_stages: Estágios do pipeline

        Returns:
            Resultados da coordenação
        """
        context = self.coordination_contexts.get(coordination_id)
        if not context:
            raise ValueError(f"Coordination {coordination_id} not found")

        current_data = None
        results = []

        for stage in pipeline_stages:
            agent_id = stage["agent_id"]
            task_desc = stage["description"]
            params = stage.get("parameters", {})

            # Adiciona dados do estágio anterior aos parâmetros
            if current_data:
                params["input_data"] = current_data

            try:
                result = await self.request_task_execution(
                    requester="coordinator",
                    target_agent=agent_id,
                    task_description=task_desc,
                    parameters=params,
                    coordination_id=coordination_id,
                )

                results.append({"stage": stage, "result": result, "status": "success"})

                # Passa resultado para próximo estágio
                current_data = result.get("result")

            except Exception as e:
                results.append({"stage": stage, "error": str(e), "status": "failed"})
                break  # Para pipeline em caso de erro

        return {
            "coordination_id": coordination_id,
            "mode": "pipeline",
            "total_stages": len(pipeline_stages),
            "completed_stages": len([r for r in results if r["status"] == "success"]),
            "results": results,
        }

    async def coordinate_competition(
        self,
        coordination_id: str,
        task_description: str,
        candidate_agents: List[str],
        evaluation_criteria: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Coordenação competitiva: múltiplos agentes executam mesma tarefa,
        melhor resultado vence.

        Args:
            coordination_id: ID da coordenação
            task_description: Descrição da tarefa
            candidate_agents: Lista de agentes candidatos
            evaluation_criteria: Critérios para escolher vencedor

        Returns:
            Resultado da competição
        """
        context = self.coordination_contexts.get(coordination_id)
        if not context:
            raise ValueError(f"Coordination {coordination_id} not found")

        # Executa tarefa em paralelo com todos os candidatos
        tasks = [
            {
                "agent_id": agent_id,
                "description": task_description,
                "parameters": {"competition_mode": True},
            }
            for agent_id in candidate_agents
        ]

        parallel_result = await self.coordinate_parallel(coordination_id, tasks)

        # Avalia resultados e escolhe vencedor
        successful_results = [
            r for r in parallel_result["results"] if r.get("status") == "success"
        ]

        if not successful_results:
            return {
                "coordination_id": coordination_id,
                "mode": "competition",
                "status": "failed",
                "error": "No successful results",
            }

        # Seleção simples: primeiro resultado (em produção usaria evaluation_criteria)
        winner = successful_results[0]

        return {
            "coordination_id": coordination_id,
            "mode": "competition",
            "total_candidates": len(candidate_agents),
            "successful_candidates": len(successful_results),
            "winner": winner["task"]["agent_id"],
            "winning_result": winner["result"],
            "all_results": parallel_result["results"],
        }

    async def coordinate_collaboration(
        self,
        coordination_id: str,
        collaborative_task: Dict[str, Any],
        team_agents: List[str],
    ) -> Dict[str, Any]:
        """
        Coordenação colaborativa: agentes trabalham juntos em uma tarefa complexa.

        Args:
            coordination_id: ID da coordenação
            collaborative_task: Descrição da tarefa colaborativa
            team_agents: Agentes da equipe

        Returns:
            Resultado da colaboração
        """
        context = self.coordination_contexts.get(coordination_id)
        if not context:
            raise ValueError(f"Coordination {coordination_id} not found")

        # Divide tarefa em subtarefas para diferentes agentes
        subtasks = collaborative_task.get("subtasks", [])
        if not subtasks:
            # Decomposição automática baseada em capacidades dos agentes
            subtasks = self._decompose_collaborative_task(
                collaborative_task, team_agents
            )

        # Executa subtarefas em paralelo
        tasks = []
        for i, subtask in enumerate(subtasks):
            agent_id = team_agents[i % len(team_agents)]  # Round-robin assignment
            tasks.append(
                {
                    "agent_id": agent_id,
                    "description": subtask["description"],
                    "parameters": subtask.get("parameters", {}),
                }
            )

        parallel_result = await self.coordinate_parallel(coordination_id, tasks)

        # Agrega resultados
        successful_results = [
            r for r in parallel_result["results"] if r.get("status") == "success"
        ]

        return {
            "coordination_id": coordination_id,
            "mode": "collaboration",
            "team_size": len(team_agents),
            "total_subtasks": len(subtasks),
            "completed_subtasks": len(successful_results),
            "aggregated_result": self._aggregate_collaborative_results(
                successful_results
            ),
            "individual_results": parallel_result["results"],
        }

    def _decompose_collaborative_task(
        self, task: Dict[str, Any], team_agents: List[str]
    ) -> List[Dict[str, Any]]:
        """Decompõe tarefa para trabalho colaborativo"""
        # Lógica simplificada - em produção usaria capacidades dos agentes
        base_description = task.get("description", "")
        return [
            {
                "description": f"{base_description} - Análise inicial",
                "parameters": {"phase": "analysis"},
            },
            {
                "description": f"{base_description} - Processamento principal",
                "parameters": {"phase": "processing"},
            },
            {
                "description": f"{base_description} - Validação final",
                "parameters": {"phase": "validation"},
            },
        ]

    def _aggregate_collaborative_results(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Agrega resultados de trabalho colaborativo"""
        # Lógica simplificada de agregação
        return {
            "total_contributions": len(results),
            "aggregated_data": [r.get("result") for r in results],
            "consensus_reached": len(results) > 0,
        }

    async def get_coordination_status(
        self, coordination_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtém status de uma coordenação.

        Args:
            coordination_id: ID da coordenação

        Returns:
            Status da coordenação ou None se não encontrada
        """
        context = self.coordination_contexts.get(coordination_id)
        if not context:
            return None

        return {
            "coordination_id": coordination_id,
            "mode": context.mode.value,
            "participants": context.participants,
            "message_count": len(context.messages),
            "shared_state_keys": list(context.shared_state.keys()),
            "created_at": context.created_at.isoformat(),
            "completed_at": (
                context.completed_at.isoformat() if context.completed_at else None
            ),
            "is_active": context.completed_at is None,
        }

    def get_registered_agents(self) -> List[Dict[str, Any]]:
        """Retorna lista de agentes registrados"""
        return [
            {
                "id": agent.id,
                "name": agent.name,
                "type": agent.agent_type,
                "capabilities": list(agent.capabilities),
                "status": agent.status.value,
                "performance_score": agent.performance_score,
                "last_seen": agent.last_seen.isoformat(),
            }
            for agent in self.agents.values()
        ]

    async def _health_monitor(self) -> None:
        """Monitor de saúde dos agentes"""
        while True:
            try:
                # Verifica saúde de todos os agentes
                for agent in self.agents.values():
                    # Simula health check
                    time_since_seen = datetime.now(timezone.utc) - agent.last_seen
                    if time_since_seen.total_seconds() > 300:  # 5 minutos
                        agent.status = AgentStatus.OFFLINE
                    elif agent.status == AgentStatus.OFFLINE:
                        agent.status = AgentStatus.IDLE

                await asyncio.sleep(self.health_check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Health monitor error: {e}")
                await asyncio.sleep(self.health_check_interval)

    def _save_state(self) -> None:
        """Salva estado do coordenador"""
        state = {
            "agents": {
                aid: {
                    "id": agent.id,
                    "name": agent.name,
                    "type": agent.agent_type,
                    "capabilities": list(agent.capabilities),
                    "status": agent.status.value,
                    "last_seen": agent.last_seen.isoformat(),
                    "metadata": agent.metadata,
                    "performance_score": agent.performance_score,
                }
                for aid, agent in self.agents.items()
            },
            "coordination_contexts": {
                cid: {
                    "coordination_id": context.coordination_id,
                    "mode": context.mode.value,
                    "participants": context.participants,
                    "shared_state": context.shared_state,
                    "messages": [msg.to_dict() for msg in context.messages],
                    "created_at": context.created_at.isoformat(),
                    "completed_at": (
                        context.completed_at.isoformat()
                        if context.completed_at
                        else None
                    ),
                }
                for cid, context in self.coordination_contexts.items()
            },
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }

        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=2, default=str)

    def _load_state(self) -> None:
        """Carrega estado do coordenador"""
        if not self.state_path.exists():
            return

        try:
            with open(self.state_path, "r") as f:
                state = json.load(f)

            # Restaura agentes
            for aid, adata in state.get("agents", {}).items():
                agent = AgentInfo(
                    id=adata["id"],
                    name=adata["name"],
                    agent_type=adata["type"],
                    capabilities=set(adata["capabilities"]),
                    status=AgentStatus(adata["status"]),
                    last_seen=datetime.fromisoformat(adata["last_seen"]),
                    metadata=adata["metadata"],
                    performance_score=adata["performance_score"],
                )
                self.agents[aid] = agent

            # Restaura contextos de coordenação
            for cid, cdata in state.get("coordination_contexts", {}).items():
                context = CoordinationContext(
                    coordination_id=cdata["coordination_id"],
                    mode=CoordinationMode(cdata["mode"]),
                    participants=cdata["participants"],
                    shared_state=cdata["shared_state"],
                    created_at=datetime.fromisoformat(cdata["created_at"]),
                )

                if cdata["completed_at"]:
                    context.completed_at = datetime.fromisoformat(cdata["completed_at"])

                # Restaura mensagens
                for mdata in cdata["messages"]:
                    message = Message(
                        message_type=MessageType(mdata["type"]),
                        sender=mdata["sender"],
                        recipient=mdata["recipient"],
                        payload=mdata["payload"],
                        id=mdata["id"],
                        timestamp=datetime.fromisoformat(mdata["timestamp"]),
                        correlation_id=mdata["correlation_id"],
                        priority=mdata["priority"],
                    )
                    context.add_message(message)

                self.coordination_contexts[cid] = context

        except Exception as e:
            print(f"Warning: Could not load coordinator state: {e}")

    async def shutdown(self) -> None:
        """Encerra o coordenador graciosamente"""
        if self._health_task and not self._health_task.done():
            self._health_task.cancel()
            try:
                await self._health_task
            except asyncio.CancelledError:
                pass

        self._save_state()
