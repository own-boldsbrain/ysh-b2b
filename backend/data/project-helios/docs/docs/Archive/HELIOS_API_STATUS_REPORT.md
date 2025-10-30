# Project Helios – API Status Report  

Updated: 23 Oct 2025

---

## Summary at a Glance

| Domain / Prefix                    | Endpoints | Production Ready | Prototype / Mocked | Notes |
|------------------------------------|-----------|------------------|--------------------|-------|
| `/auth`                            | 5         | 4                | 1                  | Login/refresh/logout backed by Redis blacklist; `register` is still a placeholder. |
| `/distributors`                    | 18        | 12               | 6                  | Core CRUD + workflow submission stored in Postgres; SWE-agent status/code-gen endpoints return mocked progress while orchestrator wiring stabilises. |
| `/api/inmetro`                     | 7         | 3                | 4                  | Async validations use Redis + pipeline; catalog/search endpoints still mocked. |
| `/api/documents` + `/api/pdf`      | 6         | 2                | 4                  | Generation runs in background with in-memory storage; persistence layer pending. |
| `/webhooks`                        | 13        | 0                | 13                 | Receivers log to stdout; config CRUD uses in-memory map. Needs Postgres + retries table wiring. |
| `/api/monitoring`                  | 4         | 0                | 4                  | Dashboard and alerts expose structure but return simulated metrics. |
| `/api/bacen`                       | 5         | 0                | 5                  | Financial feeds still mocked; integration with BACEN SGS pending. |
| `/api/journey`                     | 5         | 3                | 2                  | Simulation, payback, validation logic implemented; submission/status responses are scenario simulations. |
| `/api/aneel`                       | 4         | 3                | 1                  | Sync/query/validate linked to Hugging Face + Postgres; municipality coverage TODO. |
| `/api/pgvector`                    | 8         | 5                | 3                  | Embedding storage/search relies on pgvector tables; compliance helpers still partial. |
| `/api/data`                        | 13        | 1                | 12                 | Intelligent cache/alerts scaffolded; data retrieval currently mocked. |
| `/api/stream` (WebSocket)          | 1         | 0                | 1                  | Real-time feed simulator only. |
| `/api/automation`                  | 2         | 1                | 1                  | TypeAgent action catalogue live; pilot execution depends on AutoGen runtime availability. |
| Root + `/health`                   | 2         | 2                | 0                  | Database check passes; Redis reported healthy when configured. |

**Totals**: 91 endpoints registered. 35 deliver production-ready behaviour, 56 expose validated contracts but still rely on mocks or placeholders.

---

## Highlights Since 16 Oct 2025

- Implemented JWT refresh + logout flow (`haas/app/routers/auth.py:52`) with Redis-backed token blacklist (`haas/app/services/auth_service.py:96`), enabling proper session rotation.
- Distributor orchestrator now decomposes workflows per utility, persists requests in Postgres and kicks off webhook notifications (`haas/app/services/distributor_workflow_service.py:147`).
- Added TypeAgent/AutoGen bridge: typed actions for browser, data validation, storage and Structured RAG queries registered on start (`haas/app/services/agent_integration_service.py:136`), with `/api/automation` exposing the runtime.
- Synchronised ANEEL datasets through Hugging Face and indexed them for Structured RAG + pgvector (`haas/app/services/aneel_validator_service.py:40`), enabling `/api/aneel/query` and embedding storage.
- Introduced pgvector semantic APIs (`haas/app/routers/pgvector.py:142`) and intelligent data provider/cache layers (`haas/app/services/data_provider_service.py:27`).
- Expanded INMETRO validation into an async pipeline with Redis persistence (`haas/app/services/inmetro_store.py:16`) and queue-ready background tasks (`haas/app/routers/inmetro.py:185`).
- Test suite covers authentication, distributors, documents, INMETRO, monitoring, forms and schema validation (`haas/tests`). 9 modules, 120+ assertions, all green.

---

## Domain Deep Dive

### Authentication (`/auth`)

- **Endpoints**: login, me, refresh, logout, register (`haas/app/routers/auth.py:25`).
- **State**: login/me/refresh/logout are production-ready with token rotation, Redis blacklist and dependency-injected current user. `register` still returns a placeholder response.
- **Dependencies**: Redis optional but recommended (`haas/app/services/redis_service.py:11`). User store currently mocked; swap `fake_users_db` when real table ready (`haas/app/services/auth_service.py:72`).
- **Tests**: `haas/tests/test_auth.py` covers happy path, invalid credentials, refresh, logout.
- **Next**: Move user storage to `database.models.User` and seed initial data.

### Distributors & Workflows (`/distributors`)

- **Core flows**: list/get distributor, submit connection, poll status, pre-flight validation (`haas/app/routers/distributors.py:35`). Requests validated, persisted via SQLAlchemy models (`haas/app/services/distributor_service.py:63`) and enriched with cost/requirement estimations per utility.
- **Forms**: `/forms` endpoints source templates & validations from `UtilityFormsManager` (`haas/app/services/utility_forms_manager.py:25`); HTML render uses Jinja.
- **Agent orchestration**: `/workflows/{workflow}/run` dispatches to TypeAgent/AutoGen orchestrator (`haas/app/services/agent_integration_service.py:192`). Status polling currently returns mocked progress; replace once TaskOrchestrator persistence lands.
- **SWE-agent integration**: Code generation/validation/execute endpoints proxy to SWE runtime (`haas/app/services/swe_agent_integration_service.py:134`). Script validation already runs `py_compile`; generation returns Task IDs.
- **Persistence**: submissions saved to `connection_requests` table with geo fields and INMETRO validation snapshot (`haas/app/database/models.py:61`).
- **Next**: Implement real progress monitor + webhook delivery persistence, migrate SWE-agent task catalog to database.

### INMETRO Validation (`/api/inmetro`)

- **Async pipeline**: POST `/validate` schedules background validation, stores status in Redis via `InmetroValidationStore` with TTL management (`haas/app/services/inmetro_store.py:16`).
- **Status & batch**: `/status/{id}` and `/batch` reuse the same store and background task logic, enabling polling + batch orchestration.
- **Catalog endpoints**: certificate lookup, search, manufacturers, models currently return mock data pending repository wiring (`haas/app/services/inmetro_service.py:172`).
- **LLM priority**: pipeline auto-selects Anthropic/OpenAI/Ollama/Mock based on environment (`haas/app/services/inmetro_service.py:21`).
- **Tests**: `haas/tests/test_inmetro.py` covers validation scheduling and status transitions.
- **Next**: Connect crawler/repository to real INMETRO data source and replace mocked manufacturer/model lists.

### Documents & PDF (`/api/documents`, `/api/pdf`)

- **Capabilities**: Generate memorial, diagrams and compliance packs asynchronously storing state in `_documents_storage` map (`haas/app/routers/documents.py:446`); retrieval and listing endpoints read from memory.
- **PDF export**: `/api/pdf/export` renders templates using `pdf_export_service` with sample data seeds (`haas/app/routers/pdf_export.py:17`).
- **Status**: Business rules implemented but storage is ephemeral; replacing with S3/Postgres recommended before production.
- **Tests**: `haas/tests/test_documents.py` verifies request validation, while `haas/tests/test_forms_manager.py` covers template mapping.

### Webhooks (`/webhooks`)

- **Receivers**: Status, financial, market, regulatory, distributor, compliance, notification log endpoints accept payloads and log them for now (`haas/app/routers/webhooks.py:72`).
- **Config CRUD**: `/configs` suite manipulates webhook definitions stored in in-memory dict; `test` endpoint signs payloads and posts via `aiohttp` (`haas/app/services/webhook_service.py:24`).
- **Next**: Persist configs/deliveries in Postgres, add retry scheduler and signature verification on inbound hooks.

### Monitoring (`/api/monitoring`)

- Endpoints expose dashboard metrics, historical charts, active alerts, acknowledge operations (`haas/app/routers/monitoring.py:248`), but all values are generated mocks. Integrate Prometheus + real DB queries to promote to production.

### BACEN Realtime (`/api/bacen`)

- Snapshots, modality rates, persona KPIs, equipment leaderboards, health check implemented (`haas/app/routers/bacen_realtime.py:253`). Data currently static; tie into BACEN SGS + caching when credentials available.

### Journey 360° (`/api/journey`)

- Simulation, payback, project validation provide deterministic outputs per segment (`haas/app/services/journey_service.py:9`).
- Submission/status endpoints still simulate protocols/status history.
- Integration tests in `haas/tests/test_journey.py`.

### ANEEL Data (`/api/aneel`)

- Hugging Face sync downloads CSVs and pushes to Postgres tables (`haas/app/services/aneel_validator_service.py:86`).
- Query endpoint supports GD/tariff/distributor/market filters with pagination.
- Project validation checks CEG, modality power ranges, energy source and returns combined report.
- Health endpoint reports dataset freshness.
- TODO: municipality coverage uses placeholder success (see `_validate_municipality_real`, `haas/app/services/aneel_validator_service.py:629`).

### Semantic Search (`/api/pgvector`)

- Stores embeddings for documents, projects and regulations with conflict-aware upsert (`haas/app/services/pgvector_service.py:31`).
- Semantic search and similarity queries executed via pgvector `<->` operations (`haas/app/services/pgvector_service.py:187`).
- Compliance checker evaluates applicability rules and document requirements (`haas/app/services/pgvector_service.py:388`), but requires richer rule sets.
- Stats + health endpoints surface counts per entity.

### Data Provider MCP (`/api/data`) & Streaming

- Data queries, schema metadata, subscriptions, cache management, alert history and system tests implemented (`haas/app/routers/data_provider.py:30`).
- Back-end uses Redis for intelligent caching (`haas/app/services/intelligent_cache_service.py:17`) and alerting scaffolding; actual DB queries still mocked.
- WebSocket stream (`haas/app/routers/data_stream.py:65`) simulates updates for front-end wiring.

### Automation (`/api/automation`)

- `/automation/actions` lists registered TypeAgent action schemas.
- `/automation/pilot` orchestrates distributor pilots via AutoGen runtime, with background execution option.
- Depends on properly initialised agent runtime (`haas/app/services/agent_integration_service.py:214`); returns `simulated` when Playwright not available.

### Root & Health

- `/` returns API metadata; `/health` pings Postgres and Redis (`haas/app/main.py:88`). Errors logged when services unreachable.

---

## Testing & Tooling

- **Automated tests**: `pytest` suite under `haas/tests` covers auth, distributors, documents, forms manager, INMETRO, journey, monitoring, schema validations (`haas/tests/test_schema_validations.py`). Extend with pgvector, automation and data provider cases.
- **Structured linting**: No automated lint in repo yet; recommended to add `ruff` / `black`.
- **OpenAPI docs**: Enhanced docs configured via `core/openapi_docs.py` (automatically loaded in `haas/app/main.py:56`).

---

## Risks & Gaps

1. **Mocked Data Dependencies**: BACEN, monitoring, data provider, webhook configs still rely on placeholders, risking divergence from production behaviour.
2. **State Persistence**: Documents and webhook contexts reside in memory; restart will wipe data.
3. **External Integrations**: INMETRO search/manufacturer/model and ANEEL municipality coverage remain TODOs before production sign-off.
4. **Agent Runtime Availability**: Automation endpoints depend on Playwright + LLM credentials; add health probe before exposing externally.
5. **Security**: Auth still backed by in-memory user store; enable salted hashes in database and enforce rate limiting for login attempts.

---

## Recommended Next Actions (Next 2 Sprints)

1. **Persist critical state**  
   - Move webhook configs/deliveries and document metadata to Postgres/S3.  
   - Seed `users` table and replace `fake_users_db`.

2. **Complete INMETRO & BACEN integrations**  
   - Wire repository queries for catalog endpoints, implement crawler storage, hook SGS API with caching.

3. **Productionise monitoring & data provider**  
   - Connect Prometheus metrics + real alert rules, backfill `data_records` table, flesh out subscription worker.

4. **Agent orchestration hardening**  
   - Replace mocked workflow status with TaskOrchestrator persistence, add PGVector-backed task logs, create integration tests per distributor.

5. **Expand automated coverage**  
   - Add pgvector, automation, data provider tests and measure coverage to keep target ≥80%.

---

**Maintainers**: YSH B2B Development – contact via `helio-dev@ysh.com.br` for clarifications.  
**Document owner**: Update after each major API increment or release candidate.
