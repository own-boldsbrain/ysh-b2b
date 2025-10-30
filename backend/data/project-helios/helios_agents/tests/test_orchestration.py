"""
Testes para TaskOrchestrator e MultiAgentCoordinator
"""

import pytest
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import json

from helios_agents.infrastructure.task_orchestrator import (
    TaskOrchestrator,
    ExecutionPlan,
    Subtask,
    TaskStatus,
    RecoveryAction,
    ProgressReport,
)
from helios_agents.infrastructure.multi_agent_coordinator import (
    MultiAgentCoordinator,
    AgentStatus,
    MessageType,
    CoordinationMode,
    AgentInfo,
    Message,
)


class TestTaskOrchestrator:
    """Testes para TaskOrchestrator"""

    @pytest.fixture
    def orchestrator(self):
        """Fixture para TaskOrchestrator"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield TaskOrchestrator(
                state_persistence_path=f"{temp_dir}/orchestrator_state.json"
            )

    def test_initialization(self, orchestrator):
        """Testa inicialização do orchestrator"""
        assert orchestrator.tasks == {}
        assert orchestrator.execution_plans == {}

    def test_initialization(self, orchestrator):
        """Testa inicialização do orchestrator"""
        assert orchestrator.tasks == {}
        assert orchestrator.execution_plans == {}
        assert orchestrator.active_tasks == set()

    @pytest.mark.asyncio
    async def test_decompose_task_solar_homologation(self, orchestrator):
        """Testa decomposição de tarefa de homologação solar"""
        task_description = (
            "Realizar homologação solar completa do projeto fotovoltaico XYZ"
        )

        subtasks = await orchestrator.decompose_task(task_description)

        assert len(subtasks) > 0
        assert all(isinstance(subtask, Subtask) for subtask in subtasks)

        # Verifica se contém subtarefas esperadas
        descriptions = [s.description for s in subtasks]
        assert any("login" in desc.lower() for desc in descriptions)
        assert any(
            "navegar" in desc.lower() or "formulário" in desc.lower()
            for desc in descriptions
        )

    @pytest.mark.asyncio
    async def test_create_execution_plan(self, orchestrator):
        """Testa criação de plano de execução"""
        subtasks = [
            Subtask(
                id="1",
                description="Login no sistema",
                agent_type="BrowserController",
                dependencies=set(),
            ),
            Subtask(
                id="2",
                description="Preencher formulário",
                agent_type="BrowserController",
                dependencies={"1"},
            ),
            Subtask(
                id="3",
                description="Enviar documentos",
                agent_type="FileSystemManager",
                dependencies={"2"},
            ),
        ]

        plan = await orchestrator.create_execution_plan("task_123", subtasks)

        assert isinstance(plan, ExecutionPlan)
        assert plan.task_id == "task_123"
        assert len(plan.subtasks) == 3
        assert len(plan.execution_order) == 3

        # Verifica ordem topológica
        assert plan.execution_order[0] == "1"  # Sem dependências
        assert "2" in plan.execution_order[1:]  # Depois da 1
        assert "3" in plan.execution_order[2:]  # Depois da 2

    @pytest.mark.asyncio
    async def test_execute_task_sequential(self, orchestrator):
        """Testa execução sequencial de tarefa"""
        task_id = await orchestrator.execute_task("Test task description")

        # Aguarda um pouco para execução
        await asyncio.sleep(0.1)

        # Verifica se tarefa foi criada
        assert task_id in orchestrator.tasks
        task = orchestrator.tasks[task_id]
        assert task["description"] == "Test task description"
        assert task["status"] in [
            TaskStatus.DECOMPOSING,
            TaskStatus.PLANNING,
            TaskStatus.EXECUTING,
            TaskStatus.COMPLETED,
        ]

    @pytest.mark.asyncio
    async def test_progress_monitoring(self, orchestrator):
        """Testa monitoramento de progresso"""
        task_id = await orchestrator.execute_task("Test monitoring task")

        # Aguarda execução completa
        await asyncio.sleep(2)  # Tempo suficiente para completar todas as subtarefas

        # Monitora progresso
        progress = await orchestrator.monitor_progress(task_id)

        assert isinstance(progress, ProgressReport)
        assert progress.task_id == task_id
        # Verifica se tarefa foi completada
        assert progress.status == TaskStatus.COMPLETED

    def test_state_persistence(self, orchestrator):
        """Testa persistência de estado"""
        # Adiciona alguns dados
        orchestrator.tasks["test_task"] = {"description": "Test task"}

        # Salva estado
        orchestrator._save_state()

        # Cria novo orchestrator e carrega estado
        new_orchestrator = TaskOrchestrator(
            state_persistence_path=orchestrator.state_path
        )

        assert "test_task" in new_orchestrator.tasks


class TestMultiAgentCoordinator:
    """Testes para MultiAgentCoordinator"""

    @pytest.fixture
    def coordinator(self):
        """Fixture para MultiAgentCoordinator"""
        with tempfile.TemporaryDirectory() as temp_dir:
            coord = MultiAgentCoordinator(
                state_persistence_path=f"{temp_dir}/coordinator_state.json"
            )
            yield coord
            # Shutdown is synchronous in this case

    @pytest.mark.asyncio
    async def test_agent_registration(self, coordinator):
        """Testa registro de agentes"""
        coordinator.register_agent(
            agent_id="agent_1",
            name="Browser Controller",
            agent_type="BrowserController",
            capabilities={"web_navigation", "form_filling"},
        )

        assert "agent_1" in coordinator.agents
        agent = coordinator.agents["agent_1"]
        assert agent.name == "Browser Controller"
        assert "web_navigation" in agent.capabilities
        assert agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_agent_unregistration(self, coordinator):
        """Testa remoção de agentes"""
        coordinator.register_agent("agent_1", "Test Agent", "TestType", {"test"})

        assert coordinator.unregister_agent("agent_1") == True
        assert "agent_1" not in coordinator.agents
        assert coordinator.unregister_agent("nonexistent") == False

    @pytest.mark.asyncio
    async def test_coordination_start(self, coordinator):
        """Testa início de coordenação"""
        coord_id = await coordinator.start_coordination(
            coordination_mode=CoordinationMode.SEQUENTIAL,
            participants=["agent_1", "agent_2"],
        )

        assert coord_id in coordinator.coordination_contexts
        context = coordinator.coordination_contexts[coord_id]
        assert context.mode == CoordinationMode.SEQUENTIAL
        assert context.participants == ["agent_1", "agent_2"]

    @pytest.mark.asyncio
    async def test_message_sending(self, coordinator):
        """Testa envio de mensagens"""
        message = Message(
            message_type=MessageType.TASK_REQUEST,
            sender="coordinator",
            recipient="agent_1",
            payload={"task": "test"},
        )

        coord_id = await coordinator.start_coordination(
            CoordinationMode.SEQUENTIAL, ["agent_1"]
        )

        await coordinator.send_message(message, coord_id)

        # Verifica se mensagem foi adicionada ao contexto
        context = coordinator.coordination_contexts[coord_id]
        assert len(context.messages) == 1
        assert context.messages[0].message_type == MessageType.TASK_REQUEST

    @pytest.mark.asyncio
    async def test_broadcast_message(self, coordinator):
        """Testa broadcast de mensagens"""
        coord_id = await coordinator.start_coordination(
            CoordinationMode.PARALLEL, ["agent_1", "agent_2", "agent_3"]
        )

        await coordinator.broadcast_message(
            sender="coordinator",
            recipients=["agent_1", "agent_2", "agent_3"],
            message_type=MessageType.STATUS_UPDATE,
            payload={"status": "ready"},
            coordination_id=coord_id,
        )

        context = coordinator.coordination_contexts[coord_id]
        assert len(context.messages) == 3
        assert all(
            msg.message_type == MessageType.STATUS_UPDATE for msg in context.messages
        )

    @pytest.mark.asyncio
    async def test_sequential_coordination(self, coordinator):
        """Testa coordenação sequencial"""
        # Registra agentes mock
        coordinator.register_agent("agent_1", "Agent 1", "Test", {"task1"})
        coordinator.register_agent("agent_2", "Agent 2", "Test", {"task2"})

        coord_id = await coordinator.start_coordination(
            CoordinationMode.SEQUENTIAL, ["agent_1", "agent_2"]
        )

        tasks = [
            {"agent_id": "agent_1", "description": "Task 1", "parameters": {}},
            {"agent_id": "agent_2", "description": "Task 2", "parameters": {}},
        ]

        # Mock da execução de tarefas
        with patch.object(
            coordinator, "request_task_execution", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"status": "completed", "result": "mock_result"}

            result = await coordinator.coordinate_sequential(coord_id, tasks)

            assert result["mode"] == "sequential"
            assert result["total_tasks"] == 2
            assert result["completed_tasks"] == 2
            assert len(result["results"]) == 2

            # Verifica se request_task_execution foi chamado para cada tarefa
            assert mock_request.call_count == 2

    @pytest.mark.asyncio
    async def test_parallel_coordination(self, coordinator):
        """Testa coordenação paralela"""
        coordinator.register_agent("agent_1", "Agent 1", "Test", {"task1"})
        coordinator.register_agent("agent_2", "Agent 2", "Test", {"task2"})

        coord_id = await coordinator.start_coordination(
            CoordinationMode.PARALLEL, ["agent_1", "agent_2"]
        )

        tasks = [
            {"agent_id": "agent_1", "description": "Task 1", "parameters": {}},
            {"agent_id": "agent_2", "description": "Task 2", "parameters": {}},
        ]

        with patch.object(
            coordinator, "request_task_execution", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = {"status": "completed", "result": "mock_result"}

            result = await coordinator.coordinate_parallel(
                coord_id, tasks, max_concurrent=2
            )

            assert result["mode"] == "parallel"
            assert result["total_tasks"] == 2
            assert result["completed_tasks"] == 2
            assert result["max_concurrent"] == 2

    @pytest.mark.asyncio
    async def test_pipeline_coordination(self, coordinator):
        """Testa coordenação em pipeline"""
        coordinator.register_agent("agent_1", "Agent 1", "Test", {"analysis"})
        coordinator.register_agent("agent_2", "Agent 2", "Test", {"processing"})

        coord_id = await coordinator.start_coordination(
            CoordinationMode.PIPELINE, ["agent_1", "agent_2"]
        )

        pipeline_stages = [
            {"agent_id": "agent_1", "description": "Analysis stage", "parameters": {}},
            {
                "agent_id": "agent_2",
                "description": "Processing stage",
                "parameters": {},
            },
        ]

        with patch.object(
            coordinator, "request_task_execution", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = [
                {"status": "completed", "result": {"analysis": "done"}},
                {"status": "completed", "result": {"processing": "done"}},
            ]

            result = await coordinator.coordinate_pipeline(coord_id, pipeline_stages)

            assert result["mode"] == "pipeline"
            assert result["total_stages"] == 2
            assert result["completed_stages"] == 2

            # Verifica se dados foram passados entre estágios
            calls = mock_request.call_args_list
            assert (
                "input_data" in calls[1][1]["parameters"]
            )  # Segundo estágio recebeu dados do primeiro

    @pytest.mark.asyncio
    async def test_competition_coordination(self, coordinator):
        """Testa coordenação competitiva"""
        coordinator.register_agent("agent_1", "Agent 1", "Test", {"competition"})
        coordinator.register_agent("agent_2", "Agent 2", "Test", {"competition"})

        coord_id = await coordinator.start_coordination(
            CoordinationMode.COMPETITION, ["agent_1", "agent_2"]
        )

        with patch.object(
            coordinator, "coordinate_parallel", new_callable=AsyncMock
        ) as mock_parallel:
            mock_parallel.return_value = {
                "results": [
                    {
                        "task": {"agent_id": "agent_1"},
                        "result": {"score": 0.8},
                        "status": "success",
                    },
                    {
                        "task": {"agent_id": "agent_2"},
                        "result": {"score": 0.9},
                        "status": "success",
                    },
                ]
            }

            result = await coordinator.coordinate_competition(
                coord_id, "Competitive task", ["agent_1", "agent_2"]
            )

            assert result["mode"] == "competition"
            assert result["total_candidates"] == 2
            assert result["successful_candidates"] == 2
            assert "winner" in result
            assert "winning_result" in result

    @pytest.mark.asyncio
    async def test_collaboration_coordination(self, coordinator):
        """Testa coordenação colaborativa"""
        coordinator.register_agent("agent_1", "Agent 1", "Test", {"analysis"})
        coordinator.register_agent("agent_2", "Agent 2", "Test", {"processing"})
        coordinator.register_agent("agent_3", "Agent 3", "Test", {"validation"})

        coord_id = await coordinator.start_coordination(
            CoordinationMode.COLLABORATION, ["agent_1", "agent_2", "agent_3"]
        )

        collaborative_task = {
            "description": "Complex collaborative task",
            "subtasks": [
                {"description": "Analysis phase", "parameters": {"phase": "analysis"}},
                {
                    "description": "Processing phase",
                    "parameters": {"phase": "processing"},
                },
                {
                    "description": "Validation phase",
                    "parameters": {"phase": "validation"},
                },
            ],
        }

        with patch.object(
            coordinator, "coordinate_parallel", new_callable=AsyncMock
        ) as mock_parallel:
            mock_parallel.return_value = {
                "results": [
                    {"status": "success", "result": {"phase": "analysis"}},
                    {"status": "success", "result": {"phase": "processing"}},
                    {"status": "success", "result": {"phase": "validation"}},
                ]
            }

            result = await coordinator.coordinate_collaboration(
                coord_id, collaborative_task, ["agent_1", "agent_2", "agent_3"]
            )

            assert result["mode"] == "collaboration"
            assert result["team_size"] == 3
            assert result["total_subtasks"] == 3
            assert result["completed_subtasks"] == 3
            assert "aggregated_result" in result

    def test_get_registered_agents(self, coordinator):
        """Testa obtenção de lista de agentes registrados"""
        coordinator.register_agent("agent_1", "Agent 1", "Type1", {"cap1", "cap2"})
        coordinator.register_agent("agent_2", "Agent 2", "Type2", {"cap3"})

        agents = coordinator.get_registered_agents()

        assert len(agents) == 2
        agent_ids = [a["id"] for a in agents]
        assert "agent_1" in agent_ids
        assert "agent_2" in agent_ids

    @pytest.mark.asyncio
    async def test_coordination_status(self, coordinator):
        """Testa obtenção de status de coordenação"""
        coord_id = await coordinator.start_coordination(
            CoordinationMode.SEQUENTIAL, ["agent_1", "agent_2"]
        )

        status = await coordinator.get_coordination_status(coord_id)

        assert status is not None
        assert status["coordination_id"] == coord_id
        assert status["mode"] == "sequential"
        assert status["participants"] == ["agent_1", "agent_2"]
        assert status["is_active"] == True

    def test_state_persistence_coordinator(self, coordinator):
        """Testa persistência de estado do coordinator"""
        # Registra agentes
        coordinator.register_agent("agent_1", "Agent 1", "Type1", {"cap1"})

        # Inicia coordenação
        coord_id = asyncio.run(
            coordinator.start_coordination(CoordinationMode.SEQUENTIAL, ["agent_1"])
        )

        # Salva estado
        coordinator._save_state()

        # Cria novo coordinator e carrega estado
        new_coordinator = MultiAgentCoordinator(
            state_persistence_path=coordinator.state_path
        )

        assert "agent_1" in new_coordinator.agents
        assert coord_id in new_coordinator.coordination_contexts


class TestIntegration:
    """Testes de integração entre componentes"""

    @pytest.mark.asyncio
    async def test_orchestrator_with_coordinator(self):
        """Testa integração entre TaskOrchestrator e MultiAgentCoordinator"""
        with tempfile.TemporaryDirectory() as temp_dir:
            orchestrator = TaskOrchestrator(
                state_persistence_path=f"{temp_dir}/orchestrator.json"
            )
            coordinator = MultiAgentCoordinator(
                state_persistence_path=f"{temp_dir}/coordinator.json"
            )

            try:
                # Registra agentes no coordinator
                coordinator.register_agent(
                    "browser_agent",
                    "Browser Controller",
                    "BrowserController",
                    {"web_navigation", "form_filling"},
                )
                coordinator.register_agent(
                    "data_agent",
                    "Data Extractor",
                    "DataExtractor",
                    {"data_extraction", "validation"},
                )

                # Decompõe tarefa no orchestrator
                task_desc = "Processar formulário de homologação solar"
                subtasks = await orchestrator.decompose_task(task_desc)

                # Cria plano de execução
                plan = await orchestrator.create_execution_plan(
                    "integration_test", subtasks
                )

                # Executa tarefa integrada (retorna task_id)
                task_id = await orchestrator.execute_task(task_desc)

                # Verifica se tarefa foi criada
                assert task_id in orchestrator.tasks
                assert orchestrator.tasks[task_id]["description"] == task_desc

            finally:
                await coordinator.shutdown()


if __name__ == "__main__":
    pytest.main([__file__])
