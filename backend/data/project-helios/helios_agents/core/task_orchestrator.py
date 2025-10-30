"""
TaskOrchestrator - Orquestrador de tarefas para workflow A2A
Inspirado no SST deploy pipeline e browser-use step loop
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import asyncio


class TaskStatus(Enum):
    """Status de execução de uma tarefa"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Prioridade de execução"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Task:
    """Representa uma tarefa no workflow"""

    def __init__(
        self,
        task_id: str,
        task_type: str,
        agent_id: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.agent_id = agent_id
        self.payload = payload
        self.priority = priority
        self.dependencies = dependencies or []

        self.status = TaskStatus.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None

        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.retry_count = 0


class TaskOrchestrator:
    """
    Orquestrador central de tarefas A2A.

    Inspirado em:
    - SST deploy pipeline: parse → diff → execute → update
    - Browser-use step loop: prepare → decide → execute → finalize

    Funcionalidades:
    - Gerenciamento de fila de tarefas
    - Resolução de dependências
    - Execução paralela quando possível
    - Retry automático com backoff
    - Agregação de resultados
    """

    def __init__(self, max_parallel_tasks: int = 5):
        self.max_parallel_tasks = max_parallel_tasks

        # Filas de tarefas
        self.pending_tasks: List[Task] = []
        self.running_tasks: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []

        # Registro de agentes executores
        self.agent_executors: Dict[str, Callable] = {}

        # Estatísticas
        self.total_tasks_created = 0
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0

    def register_agent_executor(
        self, agent_id: str, executor: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """
        Registra função executora para um agente.

        Args:
            agent_id: ID do agente
            executor: Função que executa tarefas do agente
        """
        self.agent_executors[agent_id] = executor

    def submit_task(
        self,
        task_type: str,
        agent_id: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
    ) -> str:
        """
        Submete nova tarefa para execução.

        Args:
            task_type: Tipo da tarefa
            agent_id: ID do agente executor
            payload: Dados da tarefa
            priority: Prioridade de execução
            dependencies: IDs de tarefas dependentes

        Returns:
            ID da tarefa criada
        """
        self.total_tasks_created += 1
        task_id = f"task_{self.total_tasks_created}_{datetime.utcnow().timestamp()}"

        task = Task(
            task_id=task_id,
            task_type=task_type,
            agent_id=agent_id,
            payload=payload,
            priority=priority,
            dependencies=dependencies,
        )

        self.pending_tasks.append(task)
        self._sort_pending_tasks()

        return task_id

    def submit_workflow(self, workflow: List[Dict[str, Any]]) -> List[str]:
        """
        Submete workflow completo (múltiplas tarefas).

        Args:
            workflow: Lista de definições de tarefas com dependências

        Returns:
            Lista de IDs das tarefas criadas
        """
        task_ids = []

        for step in workflow:
            task_id = self.submit_task(
                task_type=step["task_type"],
                agent_id=step["agent_id"],
                payload=step.get("payload", {}),
                priority=TaskPriority[step.get("priority", "MEDIUM")],
                dependencies=step.get("dependencies", []),
            )
            task_ids.append(task_id)

        return task_ids

    async def execute_tasks(self) -> Dict[str, Any]:
        """
        Executa tarefas pendentes respeitando dependências e paralelismo.

        Returns:
            Resumo da execução
        """
        execution_start = datetime.utcnow()

        while self.pending_tasks or self.running_tasks:
            # Identifica tarefas prontas para execução
            ready_tasks = self._get_ready_tasks()

            # Executa tarefas em paralelo (limitado)
            if ready_tasks:
                tasks_to_run = ready_tasks[
                    : self.max_parallel_tasks - len(self.running_tasks)
                ]

                await asyncio.gather(
                    *[self._execute_task(task) for task in tasks_to_run]
                )

            # Aguarda se não há tarefas prontas
            if not ready_tasks and self.running_tasks:
                await asyncio.sleep(0.1)
            elif not ready_tasks and not self.running_tasks:
                break

        execution_end = datetime.utcnow()
        duration = (execution_end - execution_start).total_seconds()

        return {
            "status": "completed" if not self.failed_tasks else "completed_with_errors",
            "total_tasks": self.total_tasks_created,
            "completed": len(self.completed_tasks),
            "failed": len(self.failed_tasks),
            "duration_seconds": duration,
            "failed_task_ids": [t.task_id for t in self.failed_tasks],
        }

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de uma tarefa específica"""
        task = self._find_task(task_id)

        if not task:
            return None

        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "agent_id": task.agent_id,
            "status": task.status.value,
            "priority": task.priority.value,
            "result": task.result,
            "error": task.error,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": (
                task.completed_at.isoformat() if task.completed_at else None
            ),
            "retry_count": task.retry_count,
        }

    def get_workflow_status(self, task_ids: List[str]) -> Dict[str, Any]:
        """Retorna status agregado de um workflow"""
        statuses = [self.get_task_status(tid) for tid in task_ids]
        statuses = [s for s in statuses if s is not None]

        return {
            "total_tasks": len(task_ids),
            "pending": sum(1 for s in statuses if s["status"] == "pending"),
            "running": sum(1 for s in statuses if s["status"] == "running"),
            "completed": sum(1 for s in statuses if s["status"] == "completed"),
            "failed": sum(1 for s in statuses if s["status"] == "failed"),
            "tasks": statuses,
        }

    # Métodos privados

    def _sort_pending_tasks(self) -> None:
        """Ordena tarefas pendentes por prioridade"""
        self.pending_tasks.sort(key=lambda t: t.priority.value, reverse=True)

    def _get_ready_tasks(self) -> List[Task]:
        """Identifica tarefas prontas para execução (sem dependências pendentes)"""
        ready = []

        for task in self.pending_tasks:
            if self._dependencies_satisfied(task):
                ready.append(task)

        return ready

    def _dependencies_satisfied(self, task: Task) -> bool:
        """Verifica se todas as dependências foram concluídas"""
        if not task.dependencies:
            return True

        completed_ids = {t.task_id for t in self.completed_tasks}
        return all(dep_id in completed_ids for dep_id in task.dependencies)

    async def _execute_task(self, task: Task) -> None:
        """Executa uma tarefa individual"""
        # Move para running
        self.pending_tasks.remove(task)
        self.running_tasks.append(task)

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()

        try:
            # Obtém executor do agente
            executor = self.agent_executors.get(task.agent_id)

            if not executor:
                raise ValueError(f"No executor registered for agent {task.agent_id}")

            # Executa tarefa
            result = await self._run_with_retry(executor, task)

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()

            # Move para completed
            self.running_tasks.remove(task)
            self.completed_tasks.append(task)
            self.total_tasks_completed += 1

        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()

            # Move para failed
            self.running_tasks.remove(task)
            self.failed_tasks.append(task)
            self.total_tasks_failed += 1

    async def _run_with_retry(
        self, executor: Callable, task: Task, max_retries: int = 3
    ) -> Dict[str, Any]:
        """Executa com retry e backoff exponencial"""
        last_error = None

        for attempt in range(max_retries):
            try:
                task.retry_count = attempt

                # Executa (pode ser sync ou async)
                if asyncio.iscoroutinefunction(executor):
                    result = await executor(task.payload)
                else:
                    result = executor(task.payload)

                return result

            except Exception as e:
                last_error = e

                if attempt < max_retries - 1:
                    # Backoff exponencial
                    await asyncio.sleep(2**attempt)

        raise last_error

    def _find_task(self, task_id: str) -> Optional[Task]:
        """Busca tarefa em todas as filas"""
        for task_list in [
            self.pending_tasks,
            self.running_tasks,
            self.completed_tasks,
            self.failed_tasks,
        ]:
            for task in task_list:
                if task.task_id == task_id:
                    return task
        return None
