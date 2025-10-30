# Agent Nodes Architecture - Project Helios

## Análise de Workflows e Proposta de Arquitetura A2A

**Data:** 22 de outubro de 2025  
**Versão:** 1.2

---

## 1. Workflows Identificados

### 1.1 Huginn - Event-Driven Agent System

#### Arquitetura Base

```tsx
┌─────────────┐
│ Event Source│
└──────┬──────┘
       │ emit event
       ▼
┌─────────────────┐
│  Agent.receive()│
│  - validate     │
│  - interpolate  │
│  - process      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Memory/State    │
│ - persistent    │
│ - liquid vars   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ create_event()  │
│ - emit to       │
│   receivers     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Receiver Agents │
└─────────────────┘
```

#### Padrões de Processamento Huginn

**WebsiteAgent Pattern:**

```ruby
HTTP Request → Parse (JSON/HTML/XML) → Extract (XPath/CSS/JSONPath) → 
Transform (Liquid) → Create Event → Emit to Receivers
```

**TriggerAgent Pattern:**

```ruby
Receive Event → Rule Matching (regex/field/negated) → 
Conditional Logic → Create Event (if match) → Emit
```

**DigestAgent Pattern:**

```ruby
Accumulate Events → Memory Queue → Schedule Check → 
Batch Process → Create Single Event → Clear/Retain Queue
```

**Key Components:**

- **Agent Base Class**: `receive()`, `check()`, `working?()`, `create_event()`
- **Memory System**: Persistent hash between runs
- **Scheduler**: Cron-like expressions for periodic execution
- **Link System**: DAG através de `sources` e `receivers`
- **Liquid Templating**: Dynamic data transformation

---

### 1.2 Browser-Use - AI Agent Browser Automation

#### Main Execution Loop

```tsx
┌──────────────┐
│  Agent.run() │
│  max_steps   │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────┐
│ STEP LOOP (até max_steps)      │
│                                 │
│  ┌─────────────────────────┐   │
│  │ 1. _prepare_context()   │   │
│  │    - Browser state      │   │
│  │    - DOM snapshot       │   │
│  │    - Screenshot         │   │
│  │    - Update actions     │   │
│  └───────────┬─────────────┘   │
│              │                  │
│              ▼                  │
│  ┌─────────────────────────┐   │
│  │ 2. _get_next_action()   │   │
│  │    - Build messages     │   │
│  │    - LLM.ainvoke()      │   │
│  │    - Parse AgentOutput  │   │
│  └───────────┬─────────────┘   │
│              │                  │
│              ▼                  │
│  ┌─────────────────────────┐   │
│  │ 3. _execute_actions()   │   │
│  │    - multi_act()        │   │
│  │    - Action results     │   │
│  └───────────┬─────────────┘   │
│              │                  │
│              ▼                  │
│  ┌─────────────────────────┐   │
│  │ 4. _post_process()      │   │
│  │    - Downloads check    │   │
│  │    - Log results        │   │
│  └───────────┬─────────────┘   │
│              │                  │
│              ▼                  │
│  ┌─────────────────────────┐   │
│  │ 5. _finalize()          │   │
│  │    - Save history       │   │
│  │    - Check done         │   │
│  └───────────┬─────────────┘   │
│              │                  │
└──────────────┼──────────────────┘
               │
               ▼
         [Done or Error]
```

#### Data Flow Detail

```tsx
Task Input
    ↓
┌─────────────────────────────────────┐
│ Agent State                         │
│ - task: str                         │
│ - n_steps: int                      │
│ - last_result: ActionResult[]       │
│ - last_model_output: AgentOutput    │
│ - consecutive_failures: int         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Browser State Summary               │
│ - url: str                          │
│ - title: str                        │
│ - tabs: Tab[]                       │
│ - dom_state: DOMState               │
│ - screenshot: base64                │
│ - selector_map: dict[int, Element]  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Message Manager                     │
│ - system_message                    │
│ - agent_history_description         │
│ - browser_state_message             │
│ - action_descriptions               │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ LLM Decision (AgentOutput)          │
│ - evaluation_previous_goal: str     │
│ - memory: str (5 sentences max)     │
│ - next_goal: str                    │
│ - action: ActionModel[]             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Action Execution                    │
│ - Tools.act()                       │
│ - BrowserSession operations         │
│ - FileSystem operations             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Action Results                      │
│ - extracted_content: str            │
│ - error: str | None                 │
│ - is_done: bool                     │
│ - include_in_memory: bool           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ History Update                      │
│ - AgentHistory item added           │
│ - Telemetry sent                    │
└─────────────────────────────────────┘
```

#### Components Architecture

**Tools Registry:**

```python
# Dynamic action model creation
ActionModel = registry.create_action_model()

# Available actions:
- navigate(url, new_tab)
- click(index)
- input(index, text)
- upload_file(index, file_path)
- scroll(amount, direction)
- search(query, engine)
- extract(question)
- evaluate(javascript_code)
- done(text)
```

**Browser Session:**

```python
# CDP connection management
- get_current_page()
- get_browser_state_summary()
- new_page()
- close_tab(tab_id)
```

**File System:**

```python
# Persistent storage
- available_file_paths: list[str]
- read_file(path)
- write_file(path, content)
- replace_file_str(path, old, new)
```

---

### 1.3 Steel.dev - Browser Infrastructure

#### Session Lifecycle

```tsx
┌────────────────────┐
│ API: POST /session │
│ - create()         │
└─────────┬──────────┘
          │
          ▼
┌────────────────────────┐
│ Browser Launch         │
│ - Chromium/Firefox     │
│ - Profile setup        │
│ - Proxy config         │
│ - <1s startup          │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│ CDP/Playwright Connect │
│ - ws://cdp-url         │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│ Automation Execution   │
│ - Up to 24h            │
│ - CAPTCHA solving      │
│ - Fingerprint mgmt     │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│ Context Management     │
│ - Save cookies         │
│ - Save localStorage    │
│ - Session replay       │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│ Session Destroy        │
│ - API: DELETE /session │
└────────────────────────┘
```

#### Infrastructure Features

```tsx
┌─────────────────────────────────────┐
│ Sessions API                        │
│ - On-demand provisioning            │
│ - Average start: <1s                │
│ - 500ms in same region              │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Proxy & Fingerprinting              │
│ - Residential proxies               │
│ - Browser fingerprint rotation      │
│ - User-agent randomization          │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Auto CAPTCHA Solving                │
│ - reCAPTCHA v2/v3                   │
│ - hCaptcha                          │
│ - Cloudflare Turnstile              │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Session Viewer                      │
│ - Live session monitoring           │
│ - Recorded playback                 │
│ - Debug tools                       │
└─────────────────────────────────────┘
```

---

### 1.4 SST Workflow - Infrastructure as Code

#### Deployment Pipeline

```tsx
┌────────────────────┐
│ sst.config.ts      │
│ - Components       │
│ - Resources        │
│ - Links            │
└─────────┬──────────┘
          │
          ▼
┌────────────────────────┐
│ sst dev/deploy         │
│ - Parse config         │
│ - Resolve dependencies │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│ State Manager          │
│ - Load .sst/state      │
│ - Calculate diff       │
│ - Plan changes         │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│ Provider Bridge        │
│ - AWS API calls        │
│ - Cloudflare API       │
│ - Resource CRUD        │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│ State Update           │
│ - Save new state       │
│ - Backup to S3         │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│ Link Resolution        │
│ - Generate SDK types   │
│ - Resource.XYZ.name    │
└────────────────────────┘
```

#### Stage Management

```tsx
Personal Stages (dev)
    ↓
┌──────────────────────┐
│ sst dev              │
│ - Live functions     │
│ - Local frontend     │
│ - VPC tunnel         │
└──────────────────────┘

Development Stage
    ↓
┌──────────────────────┐
│ sst deploy --stage   │
│         dev          │
│ - Full deployment    │
│ - Team testing       │
└──────────────────────┘

Production Stage
    ↓
┌──────────────────────┐
│ sst deploy --stage   │
│      production      │
│ - Removal: retain    │
│ - Full resources     │
└──────────────────────┘

PR Environments
    ↓
┌──────────────────────┐
│ sst deploy --stage   │
│      pr-12           │
│ - Ephemeral          │
│ - Auto-remove        │
└──────────────────────┘
```

---

## 2. Arquitetura de Nós Proposta

### 2.1 Core Agent Nodes

#### Node: StatefulAgent

```python
class StatefulAgent(BaseNode):
    """
    Agente base com gerenciamento de estado, histórico e memória.
    Inspirado em: Browser-Use Agent + Huginn Agent
    """
    
    # State
    state: AgentState = {
        'task': str,
        'n_steps': int,
        'consecutive_failures': int,
        'last_result': list[ActionResult],
        'last_model_output': dict
    }
    
    # History
    history: list[AgentHistoryItem] = []
    
    # Memory (persistent across runs)
    memory: dict[str, Any] = {}
    
    # Methods
    def step(self) -> StepResult:
        """Execute one iteration"""
        
    def receive(self, events: list[Event]) -> None:
        """Process incoming events (Huginn pattern)"""
        
    def working(self) -> bool:
        """Health check"""
        
    def create_event(self, payload: dict) -> Event:
        """Emit event to receivers"""
```

#### Node: TaskOrchestrator

```python
class TaskOrchestrator(BaseNode):
    """
    Quebra tarefas complexas em subtarefas gerenciáveis.
    Inspirado em: SST Stage Management + Browser-Use initial_actions
    """
    
    def decompose_task(self, task: str) -> list[Subtask]:
        """Break down complex task using LLM"""
        
    def create_execution_plan(self, subtasks: list[Subtask]) -> ExecutionPlan:
        """Generate DAG of subtasks with dependencies"""
        
    def monitor_progress(self) -> ProgressReport:
        """Track completion status"""
        
    def handle_failure(self, subtask: Subtask, error: Error) -> RecoveryAction:
        """Retry or skip failed subtasks"""
```

#### Node: DecisionMaker

```python
class DecisionMaker(BaseNode):
    """
    Nó de planejamento com LLM.
    Inspirado em: Browser-Use get_model_output()
    """
    
    def build_context(
        self,
        current_state: dict,
        history: list[HistoryItem],
        available_actions: list[Action]
    ) -> LLMContext:
        """Construct prompt with state, history, actions"""
        
    async def plan_next_actions(
        self,
        context: LLMContext
    ) -> AgentDecision:
        """
        Returns:
        - evaluation_previous: str
        - memory: str (key insights)
        - next_goal: str
        - actions: list[ActionModel]
        """
        
    def validate_decision(self, decision: AgentDecision) -> bool:
        """Check if decision is executable"""
```

---

### 2.2 Action Execution Nodes

#### Node: BrowserController

```python
class BrowserController(BaseNode):
    """
    CDP wrapper para controle de navegador.
    Inspirado em: Browser-Use BrowserSession + Steel Sessions API
    """
    
    # Browser Management
    def create_session(self, profile: BrowserProfile) -> Session:
        """Launch browser with profile"""
        
    def navigate(self, url: str, new_tab: bool = False) -> NavigateResult:
        """Navigate to URL"""
        
    def get_state(self) -> BrowserState:
        """Get current browser state (URL, title, tabs)"""
        
    # Interaction
    def click(self, selector: str | int) -> ActionResult:
        """Click element by selector or index"""
        
    def input_text(self, selector: str | int, text: str) -> ActionResult:
        """Type text into element"""
        
    def scroll(self, amount: int, direction: str) -> ActionResult:
        """Scroll page"""
        
    # Context Management (Steel pattern)
    def save_context(self) -> Context:
        """Save cookies, localStorage"""
        
    def restore_context(self, context: Context) -> None:
        """Restore saved context"""
```

#### Node: DataExtractor

```python
class DataExtractor(BaseNode):
    """
    Extração estruturada de dados do DOM.
    Inspirado em: Huginn WebsiteAgent + Browser-Use extract action
    """
    
    def extract_with_selectors(
        self,
        page: Page,
        selectors: dict[str, str]  # CSS/XPath
    ) -> dict[str, Any]:
        """Extract using CSS/XPath selectors"""
        
    def extract_with_llm(
        self,
        page: Page,
        question: str
    ) -> ExtractResult:
        """Use LLM to extract specific information"""
        
    def parse_structured_data(
        self,
        content: str,
        format: str  # json, html, xml, text
    ) -> ParsedData:
        """Parse and structure content"""
        
    def apply_liquid_template(
        self,
        data: dict,
        template: str
    ) -> dict:
        """Transform data using Liquid templates (Huginn pattern)"""
```

#### Node: FileSystemManager

```python
class FileSystemManager(BaseNode):
    """
    Gerenciamento de arquivos persistentes.
    Inspirado em: Browser-Use FileSystem
    """
    
    available_file_paths: list[str] = []
    
    def read_file(self, path: str) -> FileContent:
        """Read file (PDF, CSV, TXT)"""
        
    def write_file(self, path: str, content: str | bytes) -> WriteResult:
        """Write content to file"""
        
    def replace_in_file(
        self,
        path: str,
        old_str: str,
        new_str: str
    ) -> ReplaceResult:
        """Find and replace in file"""
        
    def list_files(self, pattern: str = "*") -> list[str]:
        """List available files"""
        
    def manage_downloads(self) -> list[Download]:
        """Track and manage browser downloads"""
```

---

### 2.3 Event Processing Nodes

#### Node: EventRouter

```python
class EventRouter(BaseNode):
    """
    Sistema de roteamento de eventos entre agentes.
    Inspirado em: Huginn Links (sources → receivers)
    """
    
    # Topology
    sources: list[Agent] = []
    receivers: list[Agent] = []
    
    def emit_event(self, event: Event) -> None:
        """Send event to all receivers"""
        
    def route_to_specific(
        self,
        event: Event,
        receiver_ids: list[str]
    ) -> None:
        """Route to specific receivers"""
        
    def propagate(self) -> PropagateResult:
        """Trigger propagation of pending events"""
        
    def build_dag(self, agents: list[Agent]) -> DAG:
        """Build directed acyclic graph of agents"""
```

#### Node: ConditionalTrigger

```python
class ConditionalTrigger(BaseNode):
    """
    Filtragem condicional de eventos.
    Inspirado em: Huginn TriggerAgent
    """
    
    rules: list[Rule] = []
    
    class Rule:
        type: str  # regex, field, negated
        path: str  # JSONPath to field
        value: Any  # Value to match
        
    def receive(self, events: list[Event]) -> None:
        """Process events and trigger on match"""
        
    def match_rule(self, event: Event, rule: Rule) -> bool:
        """Check if event matches rule"""
        
    def create_triggered_event(
        self,
        original: Event,
        matched_value: Any
    ) -> Event:
        """Create new event with match info"""
```

#### Node: Aggregator

```python
class Aggregator(BaseNode):
    """
    Agregação e batch processing de eventos.
    Inspirado em: Huginn DigestAgent
    """
    
    queue: list[Event] = []
    schedule: str  # cron expression
    
    def receive(self, events: list[Event]) -> None:
        """Add events to queue"""
        
    def check(self) -> None:
        """Scheduled check to process queue"""
        
    def create_digest(self, events: list[Event]) -> Event:
        """Create single aggregated event"""
        
    def retain_events(self, count: int) -> None:
        """Keep N events for next digest"""
```

---

### 2.4 Infrastructure Nodes

#### Node: SessionManager

```python
class SessionManager(BaseNode):
    """
    Gerenciamento de ciclo de vida de sessões.
    Inspirado em: Steel Sessions API
    """
    
    def create_session(
        self,
        profile: SessionProfile
    ) -> Session:
        """
        Create browser session:
        - Launch browser (<1s)
        - Setup proxy/fingerprint
        - Configure CAPTCHA solver
        """
        
    def keep_alive(self, session_id: str) -> None:
        """Extend session lifetime (max 24h)"""
        
    def get_session_viewer_url(self, session_id: str) -> str:
        """Get URL to observe live session"""
        
    def destroy_session(self, session_id: str) -> None:
        """Clean up session resources"""
        
    def reuse_session(
        self,
        session_id: str,
        context: Context
    ) -> Session:
        """Resume session with saved context"""
```

#### Node: StateStore

```python
class StateStore(BaseNode):
    """
    Armazenamento persistente de estado.
    Inspirado em: SST State Management
    """
    
    def save_state(self, state: dict) -> None:
        """
        Save state:
        - Local .sst/state file
        - Backup to S3/storage
        - Version tracking
        """
        
    def load_state(self, stage: str) -> dict:
        """Load state for specific stage"""
        
    def calculate_diff(
        self,
        old_state: dict,
        new_state: dict
    ) -> StateDiff:
        """Calculate changes between states"""
        
    def backup_state(self) -> BackupResult:
        """Backup state to cloud storage"""
        
    def restore_from_backup(self, backup_id: str) -> dict:
        """Restore state from backup"""
```

#### Node: DeploymentController

```python
class DeploymentController(BaseNode):
    """
    Controle de deployment e stages.
    Inspirado em: SST Workflow
    """
    
    stages: dict[str, Stage] = {
        'personal': Stage(type='dev', lifecycle='ephemeral'),
        'dev': Stage(type='shared', lifecycle='persistent'),
        'production': Stage(type='shared', lifecycle='persistent')
    }
    
    def deploy(
        self,
        stage: str,
        config: dict
    ) -> DeployResult:
        """
        Deploy to stage:
        - Calculate state diff
        - Apply changes
        - Update state
        """
        
    def create_pr_environment(self, pr_number: int) -> Stage:
        """Create ephemeral PR stage"""
        
    def autodeploy_on_push(
        self,
        branch: str,
        stage: str
    ) -> None:
        """Setup git hook for autodeploy"""
        
    def remove_stage(self, stage: str) -> RemoveResult:
        """Remove all resources from stage"""
```

---

## 3. Fluxo de Dados Integrado

### 3.1 Exemplo: Homologação Solar Automatizada

```tsx
┌─────────────────────────────────────────────────────────────┐
│ TASK: "Submeter projeto solar para homologação na CPFL"    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ TaskOrchestrator     │
              │ - Decompose task     │
              └──────────┬───────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    [Subtask 1]    [Subtask 2]    [Subtask 3]
    Login CPFL     Fill Form      Upload Docs
         │               │               │
         │               │               │
         ▼               ▼               ▼
    ┌────────────────────────────────────────┐
    │ StatefulAgent (Agent Loop)             │
    │                                        │
    │  Step 1: ┌────────────────────┐       │
    │          │ DecisionMaker      │       │
    │          │ - Plan: navigate   │       │
    │          └──────┬─────────────┘       │
    │                 │                     │
    │                 ▼                     │
    │          ┌────────────────────┐       │
    │          │ BrowserController  │       │
    │          │ - Navigate to CPFL │       │
    │          └──────┬─────────────┘       │
    │                 │                     │
    │                 ▼                     │
    │          [Action Result]              │
    │                 │                     │
    │  Step 2:        ▼                     │
    │          ┌────────────────────┐       │
    │          │ DecisionMaker      │       │
    │          │ - Plan: login      │       │
    │          └──────┬─────────────┘       │
    │                 │                     │
    │                 ▼                     │
    │          ┌────────────────────┐       │
    │          │ BrowserController  │       │
    │          │ - Fill credentials │       │
    │          │ - Click login      │       │
    │          └──────┬─────────────┘       │
    │                 │                    
                         │
                         ▼
              ┌──────────────────────┐
              │ EventRouter          │
              │ - Emit success event │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ ConditionalTrigger   │
              │ - Check completion   │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Aggregator           │
              │ - Log to digest      │
              └──────────────────────┘
```

### 3.2 Exemplo: Monitoramento de Distribuidoras

```tsx
┌──────────────────────┐
│ Scheduler            │
│ - Cron: every_1h     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ StatefulAgent        │
│ - Task: check sites  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ BrowserController    │
│ - Navigate to site   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ DataExtractor        │
│ - Extract info       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ ConditionalTrigger   │
│ - Detect changes     │
└──────────┬───────────┘
           │
           ▼ (if changed)
┌──────────────────────┐
│ EventRouter          │
│ - Notify team        │
└──────────────────────┘
```

---

## 4. Padrões de Integração

### 4.1 Agent-to-Agent Communication (A2A)

```python
# Pattern 1: Event-Driven (Huginn style)
agent_a.create_event({
    'type': 'document_validated',
    'document_id': 'INV-12345',
    'status': 'approved'
})
# EventRouter automatically sends to agent_a.receivers

# Pattern 2: Direct Invocation (Browser-Use style)
result = await agent_b.run(
    task="Upload validated document",
    context={'document_id': 'INV-12345'}
)

# Pattern 3: Pub/Sub via StateStore
state_store.publish('document_channel', {
    'event': 'validated',
    'data': {...}
})
# Subscribed agents receive notification
```

### 4.2 Memory Sharing

```python
# Shared Memory via StateStore
state_store.set('shared/cpfl_credentials', {
    'username': '***',
    'password': '***'
}, scope='production')

# Agent A writes
agent_a.memory['last_protocol'] = 'CPFL-2025-0123'
state_store.save_state(agent_a.state)

# Agent B reads
agent_b_state = state_store.load_state('agent_b')
protocol = agent_b_state.memory.get('last_protocol')
```

### 4.3 Error Handling & Recovery

```python
# Retry Pattern
class ResilientAgent(StatefulAgent):
    def step(self):
        try:
            result = super().step()
        except RecoverableError as e:
            self.state.consecutive_failures += 1
            if self.state.consecutive_failures < 3:
                self.retry_with_backoff()
            else:
                self.escalate_to_human()
        return result

# Circuit Breaker Pattern
if session_manager.health_check() == 'unhealthy':
    # Switch to backup browser provider
    session_manager.switch_provider('steel_backup')
```

---

## 5. Roadmap de Implementação

### Fase 1: Core Foundation (2 semanas)

- [x] Implementar `StatefulAgent` base class
- [x] Implementar `BrowserController` com CDP
- [x] Implementar `StateStore` local
- [x] Testes unitários básicos
- [x] **Revisão de Qualidade**: Corrigir avisos de depreciação datetime.utcnow() → datetime.now(timezone.utc)

### Fase 2: Intelligence Layer (3 semanas)

- [x] Implementar `DecisionMaker` com LLM
- [x] Implementar `DataExtractor` com seletores
- [x] Implementar `FileSystemManager`
- [x] Integração com haas/validators

### Fase 3: Event System (2 semanas)

- [x] Implementar `EventRouter` (Huginn pattern)
- [x] Implementar `ConditionalTrigger`
- [x] Implementar `Aggregator`
- [x] DAG builder para agents
- [x] **Testes Completos**: 34 testes passando para EventRouter, ConditionalTrigger e Aggregator

### Fase 4: Infrastructure (2 semanas)

- [x] Implementar `SessionManager` com integração Steel.dev
- [x] Implementar `DeploymentController` com estratégias de deployment
- [x] Cloud state backup (S3/GCS/Azure) no `StateStore`
- [x] **Testes Completos**: 18 testes passando para infraestrutura de produção

### Fase 5: Orchestration (3 semanas)

- [x] Implementar `TaskOrchestrator` com decomposição de tarefas complexas
- [x] Implementar `MultiAgentCoordinator` para coordenação entre múltiplos agentes
- [x] Sistema de mensagens assíncronas entre agentes
- [x] Coordenação sequencial, paralela, pipeline e colaborativa
- [x] Monitoramento de progresso e recuperação de falhas
- [x] Persistência de estado para coordenação
- [x] **Testes abrangentes para orquestração**: 20 testes passando (TaskOrchestrator: 6, MultiAgentCoordinator: 13, Integration: 1)
- [x] **Status**: ✅ **COMPLETA** - TaskOrchestrator e MultiAgentCoordinator implementados com testes completos

---

## 6. Tecnologias Recomendadas

### Core Stack

```yaml
Language: Python 3.11+
Framework: FastAPI (já em uso no HaaS)
Browser Automation: Playwright / Puppeteer
State Management: Redis + PostgreSQL
Message Queue: RabbitMQ / Redis Streams
LLM Integration: LangChain / OpenAI SDK
```

### Infrastructure

```yaml
Container: Docker
Orchestration: Kubernetes / Docker Compose
CI/CD: GitHub Actions
Monitoring: Prometheus + Grafana
Logging: ELK Stack
```

### External Services

```yaml
Browser Cloud: Steel.dev (opcional)
LLM Provider: OpenAI GPT-4 / Claude
Vector DB: Pinecone (para RAG)
File Storage: AWS S3
```

---

## 7. Métricas de Sucesso

### Agent Performance

- **Task Success Rate**: >95%
- **Average Steps per Task**: <10
- **Recovery from Failure**: <3 retries
- **End-to-End Latency**: <5 min per homologação

### System Performance

- **Session Start Time**: <2s
- **State Save/Load**: <100ms
- **Event Propagation**: <50ms
- **Browser Action**: <1s average

### Business Metrics

- **Automation Coverage**: 80% dos fluxos de homologação
- **Manual Intervention**: <10% dos casos
- **Cost Reduction**: 70% vs processo manual
- **Time to Homologação**: 48h → 6h

---

## 8. Próximos Passos

1. **Validar Arquitetura** com equipe técnica
2. **Criar POC** com `StatefulAgent` + `BrowserController`
3. **Testar com 1 distribuidora** (CPFL ou Elektro)
4. **Iterar e refinar** baseado em feedback
5. **Escalar para outras distribuidoras**

---

**Documento vivo** - Atualizar conforme implementação progride.
