"""
TaskOrchestrator - Coordenação de tarefas complexas e multi-agent
Inspirado no SST stage management e Browser-Use task decomposition
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import json
import logging
import base64
from pathlib import Path

from helios_agents.execution.browser_controller import (
    BrowserAction,
    BrowserController,
)
from helios_agents.execution.data_extractor import DataExtractor
from helios_agents.execution.file_system_manager import FileSystemManager


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status de uma tarefa"""

    PENDING = "pending"
    DECOMPOSING = "decomposing"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SubtaskStatus(Enum):
    """Status de uma subtarefa"""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RecoveryAction(Enum):
    """Ações de recuperação para falhas"""

    RETRY = "retry"
    SKIP = "skip"
    ESCALATE = "escalate"
    ROLLBACK = "rollback"


class ExecutionMode(Enum):
    """Modo de execução das subtarefas."""

    SIMULATED = "SIMULATED"
    REAL = "REAL"


@dataclass
class Subtask:
    """Representa uma subtarefa no plano de execução"""

    id: str
    description: str
    agent_type: str  # Tipo de agente necessário
    dependencies: Set[str] = field(default_factory=set)  # IDs de subtarefas dependentes
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: SubtaskStatus = SubtaskStatus.PENDING
    assigned_agent: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def is_ready(self) -> bool:
        """Verifica se a subtarefa está pronta para execução"""
        return self.status == SubtaskStatus.READY

    def can_start(self, completed_tasks: Set[str]) -> bool:
        """Verifica se pode iniciar baseado nas dependências"""
        return self.dependencies.issubset(completed_tasks)

    def mark_running(self) -> None:
        """Marca como em execução"""
        self.status = SubtaskStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)

    def mark_completed(self, result: Any = None) -> None:
        """Marca como completa"""
        self.status = SubtaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now(timezone.utc)

    def mark_failed(self, error: str) -> None:
        """Marca como falha"""
        self.status = SubtaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.now(timezone.utc)

    def mark_skipped(self) -> None:
        """Marca como pulada"""
        self.status = SubtaskStatus.SKIPPED
        self.completed_at = datetime.now(timezone.utc)


@dataclass
class ExecutionPlan:
    """Plano de execução com DAG de subtarefas"""

    task_id: str
    subtasks: Dict[str, Subtask] = field(default_factory=dict)
    dependencies: Dict[str, Set[str]] = field(
        default_factory=dict
    )  # task_id -> dependent_tasks
    execution_order: List[str] = field(default_factory=list)  # Ordem topológica
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_subtask(self, subtask: Subtask) -> None:
        """Adiciona subtarefa ao plano"""
        self.subtasks[subtask.id] = subtask

        # Atualiza dependências reversas
        for dep in subtask.dependencies:
            if dep not in self.dependencies:
                self.dependencies[dep] = set()
            self.dependencies[dep].add(subtask.id)

    def get_ready_tasks(self, completed_tasks: Set[str]) -> List[Subtask]:
        """Retorna tarefas prontas para execução"""
        ready = []
        for subtask in self.subtasks.values():
            if subtask.status == SubtaskStatus.PENDING and subtask.can_start(
                completed_tasks
            ):
                subtask.status = SubtaskStatus.READY
                ready.append(subtask)
        return ready

    def get_next_batch(
        self, completed_tasks: Set[str], batch_size: int = 5
    ) -> List[Subtask]:
        """Retorna próximo lote de tarefas para execução paralela"""
        ready_tasks = self.get_ready_tasks(completed_tasks)
        return ready_tasks[:batch_size]

    def is_complete(self) -> bool:
        """Verifica se o plano está completo"""
        return all(
            subtask.status in [SubtaskStatus.COMPLETED, SubtaskStatus.SKIPPED]
            for subtask in self.subtasks.values()
        )

    def get_progress(self) -> Dict[str, Any]:
        """Retorna progresso do plano"""
        total = len(self.subtasks)
        completed = sum(
            1 for s in self.subtasks.values() if s.status == SubtaskStatus.COMPLETED
        )
        failed = sum(
            1 for s in self.subtasks.values() if s.status == SubtaskStatus.FAILED
        )
        running = sum(
            1 for s in self.subtasks.values() if s.status == SubtaskStatus.RUNNING
        )

        return {
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": total - completed - failed - running,
            "progress_percentage": (completed / total * 100) if total > 0 else 0,
            "is_complete": self.is_complete(),
        }


@dataclass
class ProgressReport:
    """Relatório de progresso da tarefa"""

    task_id: str
    status: TaskStatus
    progress: Dict[str, Any]
    current_subtasks: List[Dict[str, Any]]
    completed_subtasks: List[Dict[str, Any]]
    failed_subtasks: List[Dict[str, Any]]
    estimated_completion: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "progress": self.progress,
            "current_subtasks": self.current_subtasks,
            "completed_subtasks": self.completed_subtasks,
            "failed_subtasks": self.failed_subtasks,
            "estimated_completion": (
                self.estimated_completion.isoformat()
                if self.estimated_completion
                else None
            ),
            "created_at": self.created_at.isoformat(),
        }


class TaskOrchestrator:
    """
    Orquestrador de tarefas complexas com decomposição e coordenação multi-agent.

    Inspirado em SST stage management e Browser-Use task decomposition.
    """

    def __init__(
        self,
        max_concurrent_tasks: int = 10,
        max_retries: int = 3,
        state_persistence_path: Optional[str] = None,
        execution_mode: "ExecutionMode | str" = ExecutionMode.SIMULATED,
        storage_path: Optional[str] = None,
    ):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.max_retries = max_retries

        if isinstance(execution_mode, ExecutionMode):
            self.execution_mode = execution_mode
        else:
            self.execution_mode = ExecutionMode(str(execution_mode).upper())

        # Estado das tarefas
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.execution_plans: Dict[str, ExecutionPlan] = {}
        self.active_tasks: Set[str] = set()

        # Persistência
        self.state_path = Path(state_persistence_path or "./orchestrator_state.json")
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

        # Storage para documentos manipulados pelos agentes
        self.storage_path = Path(storage_path or "./agent_storage")
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Agentes de execução real
        self.browser_controller = BrowserController()
        self.data_extractor = DataExtractor()
        self.file_manager = FileSystemManager(str(self.storage_path))

        # Carrega estado se existir
        self._load_state()

    async def decompose_task(
        self, task_description: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Subtask]:
        """
        Decompõe tarefa complexa em subtarefas gerenciáveis usando LLM.

        Args:
            task_description: Descrição da tarefa complexa
            context: Contexto adicional (domínio, restrições, etc.)

        Returns:
            Lista de subtarefas
        """
        # TODO: Implementar chamada real para LLM
        # Por enquanto, simula decomposição baseada em padrões

        subtasks: List[Subtask] = []
        context = context or {}

        distributor_info = context.get("distributor", {})
        distributor_code = context.get("distributor_code") or distributor_info.get(
            "code"
        )
        workflow_key = context.get("workflow") or distributor_info.get("workflow")

        if distributor_code and workflow_key:
            subtasks = self._decompose_distributor_workflow(
                distributor_code, workflow_key, context
            )
            if subtasks:
                return subtasks

        # Padrões comuns de decomposição para homologação solar
        if (
            "homologação" in task_description.lower()
            and "solar" in task_description.lower()
        ):
            subtasks = self._decompose_solar_homologation(task_description, context)
        elif "login" in task_description.lower():
            subtasks = self._decompose_login_task(task_description, context)
        elif (
            "form" in task_description.lower()
            or "formulário" in task_description.lower()
        ):
            subtasks = self._decompose_form_task(task_description, context)
        elif (
            "código" in task_description.lower()
            or "script" in task_description.lower()
            or "gerar" in task_description.lower()
        ):
            subtasks = self._decompose_code_generation_task(task_description, context)
        else:
            # Decomposição genérica
            subtasks = self._decompose_generic_task(task_description, context)

        return subtasks

    def _decompose_solar_homologation(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Subtask]:
        """Decompõe tarefa de homologação solar"""
        subtasks = [
            Subtask(
                id="login_distribuidora",
                description="Fazer login no sistema da distribuidora",
                agent_type="BrowserController",
                dependencies=set(),
            ),
            Subtask(
                id="navigate_homologation",
                description="Navegar para seção de homologação",
                agent_type="BrowserController",
                dependencies={"login_distribuidora"},
            ),
            Subtask(
                id="fill_project_data",
                description="Preencher dados do projeto solar",
                agent_type="DataExtractor",
                dependencies={"navigate_homologation"},
            ),
            Subtask(
                id="upload_documents",
                description="Fazer upload dos documentos necessários",
                agent_type="FileSystemManager",
                dependencies={"fill_project_data"},
            ),
            Subtask(
                id="validate_submission",
                description="Validar e submeter formulário",
                agent_type="BrowserController",
                dependencies={"upload_documents"},
            ),
            Subtask(
                id="check_status",
                description="Verificar status da homologação",
                agent_type="DataExtractor",
                dependencies={"validate_submission"},
            ),
        ]
        return subtasks

    def _decompose_login_task(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Subtask]:
        """Decompõe tarefa de login"""
        subtasks = [
            Subtask(
                id="navigate_login",
                description="Navegar para página de login",
                agent_type="BrowserController",
                dependencies=set(),
            ),
            Subtask(
                id="fill_credentials",
                description="Preencher credenciais de login",
                agent_type="BrowserController",
                dependencies={"navigate_login"},
            ),
            Subtask(
                id="submit_login",
                description="Submeter formulário de login",
                agent_type="BrowserController",
                dependencies={"fill_credentials"},
            ),
            Subtask(
                id="verify_login",
                description="Verificar se login foi bem-sucedido",
                agent_type="DataExtractor",
                dependencies={"submit_login"},
            ),
        ]
        return subtasks

    def _decompose_form_task(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Subtask]:
        """Decompõe tarefa de preenchimento de formulário"""
        subtasks = [
            Subtask(
                id="extract_form_fields",
                description="Extrair campos do formulário",
                agent_type="DataExtractor",
                dependencies=set(),
            ),
            Subtask(
                id="validate_data",
                description="Validar dados antes do preenchimento",
                agent_type="DataExtractor",
                dependencies={"extract_form_fields"},
            ),
            Subtask(
                id="fill_form_fields",
                description="Preencher campos do formulário",
                agent_type="BrowserController",
                dependencies={"validate_data"},
            ),
            Subtask(
                id="handle_captchas",
                description="Resolver CAPTCHAs se necessário",
                agent_type="BrowserController",
                dependencies={"fill_form_fields"},
            ),
            Subtask(
                id="submit_form",
                description="Submeter formulário preenchido",
                agent_type="BrowserController",
                dependencies={"handle_captchas"},
            ),
        ]
        return subtasks

    def _decompose_generic_task(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Subtask]:
        """Decomposição genérica de tarefa"""
        subtasks = [
            Subtask(
                id="analyze_task",
                description="Analisar requisitos da tarefa",
                agent_type="DecisionMaker",
                dependencies=set(),
            ),
            Subtask(
                id="plan_execution",
                description="Planejar passos de execução",
                agent_type="DecisionMaker",
                dependencies={"analyze_task"},
            ),
            Subtask(
                id="execute_plan",
                description="Executar plano definido",
                agent_type="BrowserController",
                dependencies={"plan_execution"},
            ),
            Subtask(
                id="validate_results",
                description="Validar resultados da execução",
                agent_type="DataExtractor",
                dependencies={"execute_plan"},
            ),
        ]
        return subtasks

    def _decompose_code_generation_task(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Subtask]:
        """Decompõe tarefa de geração de código via SWE-agent"""
        context = context or {}
        data_source = context.get("data_source", "aneel_datasets")
        script_type = context.get("script_type", "extraction")
        output_format = context.get("output_format", "csv")

        subtasks = [
            Subtask(
                id="analyze_requirements",
                description="Analisar requisitos de geração de código",
                agent_type="DecisionMaker",
                dependencies=set(),
                parameters={
                    "task_description": task,
                    "data_source": data_source,
                    "script_type": script_type,
                },
            ),
            Subtask(
                id="design_script_structure",
                description="Projetar estrutura do script de extração",
                agent_type="SWEAgent",
                dependencies={"analyze_requirements"},
                parameters={
                    "script_type": script_type,
                    "data_source": data_source,
                    "output_format": output_format,
                },
            ),
            Subtask(
                id="generate_extraction_code",
                description="Gerar código de extração de dados específicos",
                agent_type="SWEAgent",
                dependencies={"design_script_structure"},
                parameters={
                    "data_source": data_source,
                    "fields": context.get("fields", []),
                    "filters": context.get("filters", {}),
                },
            ),
            Subtask(
                id="add_error_handling",
                description="Adicionar tratamento de erros e validações",
                agent_type="SWEAgent",
                dependencies={"generate_extraction_code"},
                parameters={
                    "error_scenarios": ["network_errors", "data_format_errors", "permission_errors"],
                },
            ),
            Subtask(
                id="test_script_execution",
                description="Testar execução do script gerado",
                agent_type="SWEAgent",
                dependencies={"add_error_handling"},
                parameters={
                    "test_data": context.get("test_data", {}),
                    "expected_output": context.get("expected_output", {}),
                },
            ),
            Subtask(
                id="optimize_performance",
                description="Otimizar performance e eficiência do script",
                agent_type="SWEAgent",
                dependencies={"test_script_execution"},
                parameters={
                    "performance_metrics": ["execution_time", "memory_usage", "data_throughput"],
                },
            ),
        ]
        return subtasks

    def _decompose_distributor_workflow(
        self,
        distributor_code: str,
        workflow: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Subtask]:
        """Decompõe workflow especializado por distribuidora."""
        code = (distributor_code or "").upper()
        workflow_key = (workflow or "").lower()
        context = context or {}

        if code == "CPFL" and workflow_key == "solicitacao_acesso":
            return self._build_cpfl_solicitacao(context)
        if code in {"ENEL", "ENEL_SP"} and workflow_key == "solicitacao_acesso":
            return self._build_enel_solicitacao(context)
        if code == "CEMIG" and workflow_key == "solicitacao_acesso":
            return self._build_cemig_solicitacao(context)

        return []

    def _build_cpfl_solicitacao(self, context: Dict[str, Any]) -> List[Subtask]:
        """Plano CPFL - Solicitação de Acesso."""
        login = context.get("login", {})
        captcha = context.get("captcha", {})
        form_data = context.get("form_data", {})
        schema = context.get("schema")
        documents = context.get("documents", [])
        metadata = context.get("metadata", {})
        project_id = metadata.get("project_id", "cpfl_project")
        portal = context.get("portal", {})

        login_url = portal.get(
            "login_url",
            "https://servicosonline.cpfl.com.br/agencia-webapp/login",
        )
        workflow_url = portal.get(
            "workflow_url",
            "https://servicosonline.cpfl.com.br/agencia-webapp/solicitar-acesso",
        )

        subtasks: List[Subtask] = []

        login_actions = [
            {"type": "NAVIGATE", "url": login_url},
            {"type": "WAIT", "timeout_ms": 1500},
        ]
        if login.get("username"):
            login_actions.append(
                {
                    "type": "TYPE",
                    "selector": "input[name='usuario']",
                    "text": login["username"],
                }
            )
        if login.get("password"):
            login_actions.append(
                {
                    "type": "TYPE",
                    "selector": "input[name='senha']",
                    "text": login["password"],
                }
            )
        if captcha.get("solution"):
            login_actions.append(
                {
                    "type": "TYPE",
                    "selector": "input[name='captcha']",
                    "text": captcha["solution"],
                }
            )
        login_actions.append({"type": "CLICK", "selector": "button[type='submit']"})

        subtasks.append(
            Subtask(
                id="cpfl_login",
                description="Realizar login no portal CPFL",
                agent_type="BrowserController",
                parameters={"actions": login_actions},
            )
        )

        subtasks.append(
            Subtask(
                id="cpfl_nav_form",
                description="Navegar para o formulário de solicitação CPFL",
                agent_type="BrowserController",
                dependencies={"cpfl_login"},
                parameters={
                    "actions": [
                        {"type": "NAVIGATE", "url": workflow_url},
                        {"type": "WAIT", "timeout_ms": 1200},
                    ]
                },
            )
        )

        field_map = {
            "nome_solicitante": "input[name='nomeSolicitante']",
            "cpf_cnpj": "input[name='cpfCnpj']",
            "numero_cliente": "input[name='numeroCliente']",
            "potencia_instalada_kw": "input[name='potenciaInstalada']",
        }
        select_map = {
            "tipo_geracao": "select[name='tipoGeracao']",
            "modalidade_compensacao": "select[name='modalidadeCompensacao']",
        }

        form_actions = self._build_form_actions(form_data, field_map, select_map)
        if form_data.get("endereco_instalacao"):
            endereco = form_data["endereco_instalacao"]
            complemento = endereco.get("complemento")
            if complemento:
                form_actions.append(
                    {
                        "type": "TYPE",
                        "selector": "input[name='complementoEndereco']",
                        "text": complemento,
                    }
                )

        form_actions.append({"type": "CLICK", "selector": "button#salvarSolicitacao"})

        subtasks.append(
            Subtask(
                id="cpfl_fill_form",
                description="Preencher formulário CPFL",
                agent_type="BrowserController",
                dependencies={"cpfl_nav_form"},
                parameters={"actions": form_actions},
            )
        )

        if documents:
            subtasks.append(
                Subtask(
                    id="cpfl_store_docs",
                    description="Armazenar documentos para CPFL",
                    agent_type="FileSystemManager",
                    dependencies={"cpfl_fill_form"},
                    parameters={
                        "documents": documents,
                        "project_id": project_id,
                    },
                )
            )

        validation_dependency = "cpfl_fill_form"
        if schema:
            subtasks.append(
                Subtask(
                    id="cpfl_validate_schema",
                    description="Validar dados do formulário CPFL",
                    agent_type="DataExtractor",
                    dependencies={"cpfl_fill_form"},
                    parameters={
                        "method": "validate",
                        "data": form_data,
                        "schema": schema,
                    },
                )
            )
            validation_dependency = "cpfl_validate_schema"

        subtasks.append(
            Subtask(
                id="cpfl_submit",
                description="Submeter solicitação CPFL",
                agent_type="BrowserController",
                dependencies={validation_dependency},
                parameters={
                    "actions": [
                        {"type": "CLICK", "selector": "button#confirmarEnvio"},
                        {"type": "WAIT", "timeout_ms": 1500},
                    ]
                },
            )
        )

        subtasks.append(
            Subtask(
                id="cpfl_status",
                description="Verificar status do protocolo CPFL",
                agent_type="BrowserController",
                dependencies={"cpfl_submit"},
                parameters={
                    "actions": [
                        {"type": "EXTRACT", "selector": "div.status-protocolo"}
                    ]
                },
            )
        )

        return subtasks

    def _build_enel_solicitacao(self, context: Dict[str, Any]) -> List[Subtask]:
        """Plano ENEL - Solicitação de Acesso."""
        login = context.get("login", {})
        captcha = context.get("captcha", {})
        form_data = context.get("form_data", {})
        schema = context.get("schema")
        documents = context.get("documents", [])
        metadata = context.get("metadata", {})
        project_id = metadata.get("project_id", "enel_project")
        portal = context.get("portal", {})

        login_url = portal.get(
            "login_url", "https://www.enel.com.br/pt-br/clientes/login"
        )
        workflow_url = portal.get(
            "workflow_url",
            "https://www.enel.com.br/pt-br/clientes/solicitar-acesso.html",
        )

        subtasks: List[Subtask] = []

        login_actions = [
            {"type": "NAVIGATE", "url": login_url},
            {"type": "WAIT", "timeout_ms": 2000},
        ]
        if login.get("username"):
            login_actions.append(
                {
                    "type": "TYPE",
                    "selector": "input[name='email']",
                    "text": login["username"],
                }
            )
        if login.get("password"):
            login_actions.append(
                {
                    "type": "TYPE",
                    "selector": "input[name='password']",
                    "text": login["password"],
                }
            )
        if captcha.get("solution"):
            login_actions.append(
                {
                    "type": "TYPE",
                    "selector": "input[name='captcha']",
                    "text": captcha["solution"],
                }
            )
        login_actions.append({"type": "CLICK", "selector": "button[type='submit']"})

        subtasks.append(
            Subtask(
                id="enel_login",
                description="Realizar login no portal Enel",
                agent_type="BrowserController",
                parameters={"actions": login_actions},
            )
        )

        subtasks.append(
            Subtask(
                id="enel_nav_form",
                description="Navegar para formulário Enel",
                agent_type="BrowserController",
                dependencies={"enel_login"},
                parameters={
                    "actions": [
                        {"type": "NAVIGATE", "url": workflow_url},
                        {"type": "WAIT", "timeout_ms": 1500},
                    ]
                },
            )
        )

        field_map = {
            "nome_solicitante": "input[name='nomeSolicitante']",
            "cpf_cnpj": "input[name='cpfCnpj']",
            "numero_instalacao": "input[name='numeroInstalacao']",
            "potencia_instalada_kw": "input[name='potenciaInstalada']",
        }
        select_map = {
            "tipo_sistema": "select[name='tipoSistema']",
            "modalidade_compensacao": "select[name='modalidadeCompensacao']",
        }

        form_actions = self._build_form_actions(form_data, field_map, select_map)
        form_actions.append({"type": "CLICK", "selector": "button#salvarForm"})

        subtasks.append(
            Subtask(
                id="enel_fill_form",
                description="Preencher formulário Enel",
                agent_type="BrowserController",
                dependencies={"enel_nav_form"},
                parameters={"actions": form_actions},
            )
        )

        if documents:
            subtasks.append(
                Subtask(
                    id="enel_store_docs",
                    description="Armazenar documentos Enel",
                    agent_type="FileSystemManager",
                    dependencies={"enel_fill_form"},
                    parameters={
                        "documents": documents,
                        "project_id": project_id,
                    },
                )
            )

        validation_dependency = "enel_fill_form"
        if schema:
            subtasks.append(
                Subtask(
                    id="enel_validate_schema",
                    description="Validar dados do formulário Enel",
                    agent_type="DataExtractor",
                    dependencies={"enel_fill_form"},
                    parameters={
                        "method": "validate",
                        "data": form_data,
                        "schema": schema,
                    },
                )
            )
            validation_dependency = "enel_validate_schema"

        subtasks.append(
            Subtask(
                id="enel_submit",
                description="Submeter solicitação Enel",
                agent_type="BrowserController",
                dependencies={validation_dependency},
                parameters={
                    "actions": [
                        {"type": "CLICK", "selector": "button#submitForm"},
                        {"type": "WAIT", "timeout_ms": 1500},
                    ]
                },
            )
        )

        subtasks.append(
            Subtask(
                id="enel_status",
                description="Verificar status Enel",
                agent_type="BrowserController",
                dependencies={"enel_submit"},
                parameters={
                    "actions": [
                        {"type": "EXTRACT", "selector": "div.status-label"}
                    ]
                },
            )
        )

        return subtasks

    def _build_cemig_solicitacao(self, context: Dict[str, Any]) -> List[Subtask]:
        """Plano CEMIG - Solicitação de Acesso."""
        login = context.get("login", {})
        captcha = context.get("captcha", {})
        form_data = context.get("form_data", {})
        schema = context.get("schema")
        documents = context.get("documents", [])
        metadata = context.get("metadata", {})
        project_id = metadata.get("project_id", "cemig_project")
        portal = context.get("portal", {})

        login_url = portal.get(
            "login_url",
            "https://www.cemig.com.br/atendimento/login",
        )
        workflow_url = portal.get(
            "workflow_url",
            "https://www.cemig.com.br/atendimento/geracao-distribuida/",
        )

        subtasks: List[Subtask] = []

        login_actions = [
            {"type": "NAVIGATE", "url": login_url},
            {"type": "WAIT", "timeout_ms": 1800},
        ]
        if login.get("username"):
            login_actions.append(
                {
                    "type": "TYPE",
                    "selector": "input[name='cpfCnpj']",
                    "text": login["username"],
                }
            )
        if login.get("password"):
            login_actions.append(
                {
                    "type": "TYPE",
                    "selector": "input[name='senha']",
                    "text": login["password"],
                }
            )
        if captcha.get("solution"):
            login_actions.append(
                {
                    "type": "TYPE",
                    "selector": "input[name='captcha']",
                    "text": captcha["solution"],
                }
            )
        login_actions.append({"type": "CLICK", "selector": "button[type='submit']"})

        subtasks.append(
            Subtask(
                id="cemig_login",
                description="Realizar login no portal CEMIG",
                agent_type="BrowserController",
                parameters={"actions": login_actions},
            )
        )

        subtasks.append(
            Subtask(
                id="cemig_nav_form",
                description="Navegar para formulário CEMIG",
                agent_type="BrowserController",
                dependencies={"cemig_login"},
                parameters={
                    "actions": [
                        {"type": "NAVIGATE", "url": workflow_url},
                        {"type": "WAIT", "timeout_ms": 1500},
                    ]
                },
            )
        )

        field_map = {
            "nome_solicitante": "input[name='nomeSolicitante']",
            "cpf_cnpj": "input[name='cpfCnpj']",
            "numero_cliente": "input[name='numeroCliente']",
            "potencia_instalada_kw": "input[name='potenciaInstalada']",
        }
        select_map = {
            "fonte_energia": "select[name='fonteEnergia']",
            "modalidade_compensacao": "select[name='modalidadeCompensacao']",
        }

        form_actions = self._build_form_actions(form_data, field_map, select_map)
        form_actions.append({"type": "CLICK", "selector": "button#salvarGD"})

        subtasks.append(
            Subtask(
                id="cemig_fill_form",
                description="Preencher formulário CEMIG",
                agent_type="BrowserController",
                dependencies={"cemig_nav_form"},
                parameters={"actions": form_actions},
            )
        )

        if documents:
            subtasks.append(
                Subtask(
                    id="cemig_store_docs",
                    description="Armazenar documentos CEMIG",
                    agent_type="FileSystemManager",
                    dependencies={"cemig_fill_form"},
                    parameters={
                        "documents": documents,
                        "project_id": project_id,
                    },
                )
            )

        validation_dependency = "cemig_fill_form"
        if schema:
            subtasks.append(
                Subtask(
                    id="cemig_validate_schema",
                    description="Validar dados do formulário CEMIG",
                    agent_type="DataExtractor",
                    dependencies={"cemig_fill_form"},
                    parameters={
                        "method": "validate",
                        "data": form_data,
                        "schema": schema,
                    },
                )
            )
            validation_dependency = "cemig_validate_schema"

        subtasks.append(
            Subtask(
                id="cemig_submit",
                description="Submeter solicitação CEMIG",
                agent_type="BrowserController",
                dependencies={validation_dependency},
                parameters={
                    "actions": [
                        {"type": "CLICK", "selector": "button#enviarGD"},
                        {"type": "WAIT", "timeout_ms": 1500},
                    ]
                },
            )
        )

        subtasks.append(
            Subtask(
                id="cemig_status",
                description="Verificar status CEMIG",
                agent_type="BrowserController",
                dependencies={"cemig_submit"},
                parameters={
                    "actions": [
                        {"type": "EXTRACT", "selector": "div.status-atual"}
                    ]
                },
            )
        )

        return subtasks

    def _build_form_actions(
        self,
        form_data: Dict[str, Any],
        text_fields: Dict[str, str],
        select_fields: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """Gera ações de preenchimento de formulário."""
        actions: List[Dict[str, Any]] = []

        for field, selector in text_fields.items():
            value = form_data.get(field)
            if value is not None:
                actions.append(
                    {
                        "type": "TYPE",
                        "selector": selector,
                        "text": str(value),
                    }
                )

        for field, selector in select_fields.items():
            value = form_data.get(field)
            if value is not None:
                actions.append(
                    {
                        "type": "SELECT",
                        "selector": selector,
                        "value": str(value),
                    }
                )

        return actions

    async def create_execution_plan(
        self, task_id: str, subtasks: List[Subtask]
    ) -> ExecutionPlan:
        """
        Cria plano de execução com DAG de subtarefas.

        Args:
            task_id: ID da tarefa principal
            subtasks: Lista de subtarefas

        Returns:
            Plano de execução estruturado
        """
        plan = ExecutionPlan(task_id=task_id)

        # Adiciona todas as subtarefas
        for subtask in subtasks:
            plan.add_subtask(subtask)

        # Calcula ordem topológica (simplificada)
        plan.execution_order = self._calculate_execution_order(plan)

        return plan

    def _calculate_execution_order(self, plan: ExecutionPlan) -> List[str]:
        """Calcula ordem topológica de execução (simplificada)"""
        # Algoritmo de Kahn simplificado
        order: List[str] = []
        remaining_deps: Dict[str, Set[str]] = {
            sid: set(sub.dependencies) for sid, sub in plan.subtasks.items()
        }

        no_deps = [sid for sid, deps in remaining_deps.items() if not deps]

        while no_deps:
            current = no_deps.pop(0)
            order.append(current)

            for successor in plan.dependencies.get(current, set()):
                deps = remaining_deps[successor]
                deps.discard(current)
                if not deps:
                    no_deps.append(successor)

        return order

    async def execute_task(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
        max_parallel: int = 3,
    ) -> str:
        """
        Executa tarefa complexa de ponta a ponta.

        Args:
            task_description: Descrição da tarefa
            context: Contexto adicional
            max_parallel: Máximo de subtarefas em paralelo

        Returns:
            ID da tarefa para acompanhamento
        """
        task_id = f"task_{len(self.tasks)}_{datetime.now(timezone.utc).timestamp()}"

        # Inicializa tarefa
        self.tasks[task_id] = {
            "id": task_id,
            "description": task_description,
            "context": context or {},
            "status": TaskStatus.DECOMPOSING,
            "created_at": datetime.now(timezone.utc),
            "started_at": None,
            "completed_at": None,
            "progress": {},
            "errors": [],
        }

        # Adiciona às tarefas ativas
        self.active_tasks.add(task_id)

        # Inicia execução em background
        asyncio.create_task(self._execute_task_async(task_id, max_parallel))

        return task_id

    async def _execute_task_async(self, task_id: str, max_parallel: int) -> None:
        """Execução assíncrona da tarefa"""
        try:
            task = self.tasks[task_id]
            task["status"] = TaskStatus.DECOMPOSING
            task["started_at"] = datetime.now(timezone.utc)

            # Fase 1: Decomposição
            subtasks = await self.decompose_task(task["description"], task["context"])
            task["status"] = TaskStatus.PLANNING

            # Fase 2: Planejamento
            plan = await self.create_execution_plan(task_id, subtasks)
            self.execution_plans[task_id] = plan
            task["status"] = TaskStatus.EXECUTING

            # Fase 3: Execução
            await self._execute_plan(task_id, plan, max_parallel)

            # Finaliza
            task["status"] = TaskStatus.COMPLETED
            task["completed_at"] = datetime.now(timezone.utc)

        except Exception as e:
            task["status"] = TaskStatus.FAILED
            task["error"] = str(e)
            task["completed_at"] = datetime.now(timezone.utc)

        finally:
            self.active_tasks.discard(task_id)
            self._save_state()

    async def _execute_plan(
        self, task_id: str, plan: ExecutionPlan, max_parallel: int
    ) -> None:
        """Executa plano de subtarefas"""
        completed_tasks = set()
        running_tasks = set()

        while not plan.is_complete():
            # Obtém próximas tarefas prontas
            ready_tasks = plan.get_next_batch(completed_tasks, max_parallel)

            if not ready_tasks:
                # Verifica se há deadlock
                if running_tasks:
                    await asyncio.sleep(1)  # Espera tarefas em execução
                    continue
                else:
                    break  # Deadlock detectado

            # Executa tarefas em paralelo
            tasks = []
            for subtask in ready_tasks:
                if len(running_tasks) >= max_parallel:
                    break

                subtask.mark_running()
                running_tasks.add(subtask.id)

                task = asyncio.create_task(self._execute_subtask(task_id, subtask))
                tasks.append(task)

            # Aguarda conclusão
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Processa resultados
                for i, result in enumerate(results):
                    subtask = ready_tasks[i]
                    running_tasks.discard(subtask.id)

                    if isinstance(result, Exception):
                        await self._handle_subtask_failure(
                            task_id, subtask, str(result)
                        )
                    else:
                        subtask.mark_completed(result)
                        completed_tasks.add(subtask.id)

    async def _execute_subtask(self, task_id: str, subtask: Subtask) -> Any:
        """Executa uma subtarefa individual"""
        # TODO: Implementar delegação real para agentes específicos
        # Por enquanto, simula execução baseada no tipo de agente

        if subtask.agent_type == "BrowserController":
            return await self._simulate_browser_action(subtask)
        elif subtask.agent_type == "DataExtractor":
            return await self._simulate_data_extraction(subtask)
        elif subtask.agent_type == "FileSystemManager":
            return await self._simulate_file_operation(subtask)
        elif subtask.agent_type == "DecisionMaker":
            return await self._simulate_decision_making(subtask)
        elif subtask.agent_type == "SWEAgent":
            return await self._simulate_swe_agent_action(subtask)
        else:
            return await self._simulate_generic_action(subtask)

    async def _simulate_browser_action(self, subtask: Subtask) -> Dict[str, Any]:
        """Simula ação do browser"""
        await asyncio.sleep(0.5)  # Simula latência
        return {
            "action": "browser_interaction",
            "description": subtask.description,
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _simulate_data_extraction(self, subtask: Subtask) -> Dict[str, Any]:
        """Simula extração de dados"""
        await asyncio.sleep(0.3)
        return {
            "action": "data_extraction",
            "description": subtask.description,
            "extracted_data": {"sample": "data"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _simulate_file_operation(self, subtask: Subtask) -> Dict[str, Any]:
        """Simula operação de arquivo"""
        await asyncio.sleep(0.2)
        return {
            "action": "file_operation",
            "description": subtask.description,
            "files_processed": 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _simulate_decision_making(self, subtask: Subtask) -> Dict[str, Any]:
        """Simula tomada de decisão"""
        await asyncio.sleep(0.1)
        return {
            "action": "decision_making",
            "description": subtask.description,
            "decision": "proceed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _simulate_swe_agent_action(self, subtask: Subtask) -> Dict[str, Any]:
        """Simula ação do SWE-agent para geração de código"""
        await asyncio.sleep(1.0)  # Simula tempo de geração de código

        # Simula diferentes tipos de ações baseadas nos parâmetros
        action_type = "code_generation"
        if "analyze" in subtask.id:
            result = {
                "analysis": "Requisitos analisados com sucesso",
                "script_requirements": subtask.parameters,
            }
        elif "design" in subtask.id:
            result = {
                "script_structure": "Estrutura do script definida",
                "components": ["data_loader", "extractor", "validator", "output_writer"],
            }
        elif "generate" in subtask.id:
            result = {
                "generated_code": "# Script de extração gerado automaticamente\nprint('Extração concluída')",
                "language": "python",
                "lines_of_code": 45,
            }
        elif "error_handling" in subtask.id:
            result = {
                "error_handlers_added": True,
                "exceptions_handled": ["ValueError", "ConnectionError", "TimeoutError"],
            }
        elif "test" in subtask.id:
            result = {
                "tests_passed": True,
                "execution_time": "2.3s",
                "test_coverage": "85%",
            }
        elif "optimize" in subtask.id:
            result = {
                "optimizations_applied": ["vectorization", "caching", "async_processing"],
                "performance_improvement": "35%",
            }
        else:
            result = {"status": "completed"}

        return {
            "action": action_type,
            "description": subtask.description,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _simulate_generic_action(self, subtask: Subtask) -> Dict[str, Any]:
        """Simula ação genérica"""
        await asyncio.sleep(0.4)
        return {
            "action": "generic",
            "description": subtask.description,
            "result": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def _handle_subtask_failure(
        self, task_id: str, subtask: Subtask, error: str
    ) -> None:
        """Lida com falha de subtarefa"""
        subtask.retry_count += 1
        subtask.error = error

        if subtask.retry_count < subtask.max_retries:
            # Retry
            subtask.status = SubtaskStatus.PENDING
            subtask.error = None
        else:
            # Falha definitiva
            subtask.mark_failed(error)

            # Registra erro na tarefa principal
            task = self.tasks[task_id]
            task["errors"].append(
                {
                    "subtask": subtask.id,
                    "error": error,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

    async def monitor_progress(self, task_id: str) -> ProgressReport:
        """
        Monitora progresso de uma tarefa.

        Args:
            task_id: ID da tarefa

        Returns:
            Relatório de progresso detalhado
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.tasks[task_id]
        plan = self.execution_plans.get(task_id)

        if not plan:
            return ProgressReport(
                task_id=task_id,
                status=task["status"],
                progress={"error": "No execution plan available"},
                current_subtasks=[],
                completed_subtasks=[],
                failed_subtasks=[],
            )

        progress = plan.get_progress()

        # Detalhes das subtarefas
        current_subtasks = [
            {
                "id": s.id,
                "description": s.description,
                "status": s.status.value,
                "agent_type": s.agent_type,
                "started_at": s.started_at.isoformat() if s.started_at else None,
            }
            for s in plan.subtasks.values()
            if s.status == SubtaskStatus.RUNNING
        ]

        completed_subtasks = [
            {
                "id": s.id,
                "description": s.description,
                "result": str(s.result)[:100] if s.result else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in plan.subtasks.values()
            if s.status == SubtaskStatus.COMPLETED
        ]

        failed_subtasks = [
            {
                "id": s.id,
                "description": s.description,
                "error": s.error,
                "retry_count": s.retry_count,
                "failed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in plan.subtasks.values()
            if s.status == SubtaskStatus.FAILED
        ]

        return ProgressReport(
            task_id=task_id,
            status=task["status"],
            progress=progress,
            current_subtasks=current_subtasks,
            completed_subtasks=completed_subtasks,
            failed_subtasks=failed_subtasks,
        )

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancela execução de uma tarefa.

        Args:
            task_id: ID da tarefa

        Returns:
            True se cancelada com sucesso
        """
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        if task["status"] in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        ]:
            return False

        task["status"] = TaskStatus.CANCELLED
        task["cancelled_at"] = datetime.now(timezone.utc)
        self.active_tasks.discard(task_id)

        # Cancela subtarefas em execução
        plan = self.execution_plans.get(task_id)
        if plan:
            for subtask in plan.subtasks.values():
                if subtask.status == SubtaskStatus.RUNNING:
                    subtask.mark_skipped()

        self._save_state()
        return True

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Retorna lista de tarefas ativas"""
        return [
            {
                "id": task_id,
                "description": self.tasks[task_id]["description"],
                "status": self.tasks[task_id]["status"].value,
                "created_at": self.tasks[task_id]["created_at"].isoformat(),
                "progress": (
                    self.execution_plans.get(task_id).get_progress()
                    if task_id in self.execution_plans
                    else {}
                ),
            }
            for task_id in self.active_tasks
        ]

    def _save_state(self) -> None:
        """Salva estado do orquestrador"""
        state = {
            "tasks": self.tasks,
            "execution_plans": {
                task_id: {
                    "task_id": plan.task_id,
                    "subtasks": {
                        sid: self._subtask_to_dict(s)
                        for sid, s in plan.subtasks.items()
                    },
                    "execution_order": plan.execution_order,
                    "created_at": plan.created_at.isoformat(),
                }
                for task_id, plan in self.execution_plans.items()
            },
            "active_tasks": list(self.active_tasks),
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }

        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=2, default=str)

    def _load_state(self) -> None:
        """Carrega estado do orquestrador"""
        if not self.state_path.exists():
            return

        try:
            with open(self.state_path, "r") as f:
                state = json.load(f)

            self.tasks = state.get("tasks", {})
            self.active_tasks = set(state.get("active_tasks", []))

            # Reconstrói execution plans
            for task_id, plan_data in state.get("execution_plans", {}).items():
                plan = ExecutionPlan(
                    task_id=plan_data["task_id"],
                    execution_order=plan_data["execution_order"],
                    created_at=datetime.fromisoformat(plan_data["created_at"]),
                )

                for sid, sdata in plan_data["subtasks"].items():
                    subtask = self._dict_to_subtask(sdata)
                    plan.add_subtask(subtask)

                self.execution_plans[task_id] = plan

        except Exception as e:
            print(f"Warning: Could not load orchestrator state: {e}")

    def _subtask_to_dict(self, subtask: Subtask) -> Dict[str, Any]:
        """Converte Subtask para dicionário"""
        return {
            "id": subtask.id,
            "description": subtask.description,
            "agent_type": subtask.agent_type,
            "dependencies": list(subtask.dependencies),
            "status": subtask.status.value,
            "assigned_agent": subtask.assigned_agent,
            "result": subtask.result,
            "error": subtask.error,
            "retry_count": subtask.retry_count,
            "max_retries": subtask.max_retries,
            "created_at": subtask.created_at.isoformat(),
            "started_at": (
                subtask.started_at.isoformat() if subtask.started_at else None
            ),
            "completed_at": (
                subtask.completed_at.isoformat() if subtask.completed_at else None
            ),
        }

    def _dict_to_subtask(self, data: Dict[str, Any]) -> Subtask:
        """Converte dicionário para Subtask"""
        return Subtask(
            id=data["id"],
            description=data["description"],
            agent_type=data["agent_type"],
            dependencies=set(data["dependencies"]),
            status=SubtaskStatus(data["status"]),
            assigned_agent=data["assigned_agent"],
            result=data["result"],
            error=data["error"],
            retry_count=data["retry_count"],
            max_retries=data["max_retries"],
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=(
                datetime.fromisoformat(data["started_at"])
                if data["started_at"]
                else None
            ),
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data["completed_at"]
                else None
            ),
        )
