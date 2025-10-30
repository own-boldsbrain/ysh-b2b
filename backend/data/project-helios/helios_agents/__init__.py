"""
Helios Agents - Sistema de Agentes Autônomos A2A para Homologação Solar
Baseado na arquitetura documentada em AGENT_NODES_ARCHITECTURE.md
"""

__version__ = "0.1.0"

from .core import StatefulAgent, TaskOrchestrator, DecisionMaker
from .execution import (
    BrowserController,
    BrowserAction,
    DataExtractor,
    FileSystemManager,
)
from .events import EventRouter, ConditionalTrigger, Aggregator
from .infrastructure import SessionManager, StateStore, DeploymentController
from .integration import (
    TypeAgentBridge,
    TypedActionConfig,
    StructuredRAGService,
    StructuredRAGIndex,
    AutoGenRuntime,
    AutoGenScenarioResult,
)

__all__ = [
    # Core nodes
    "StatefulAgent",
    "TaskOrchestrator",
    "DecisionMaker",
    # Execution nodes
    "BrowserController",
    "BrowserAction",
    "DataExtractor",
    "FileSystemManager",
    # Event nodes
    "EventRouter",
    "ConditionalTrigger",
    "Aggregator",
    # Infrastructure nodes
    "SessionManager",
    "StateStore",
    "DeploymentController",
    # Integration layer
    "TypeAgentBridge",
    "TypedActionConfig",
    "StructuredRAGService",
    "StructuredRAGIndex",
    "AutoGenRuntime",
    "AutoGenScenarioResult",
]
