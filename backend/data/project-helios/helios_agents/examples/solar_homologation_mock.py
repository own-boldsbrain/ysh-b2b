"""
Fluxo mock de homologação solar usando os nós Execution, Events e Infrastructure.

Execute:
  python -m helios_agents.examples.solar_homologation_mock
"""

import asyncio
from typing import Dict, Any
from datetime import datetime

from helios_agents.infrastructure.session_manager import SessionManager
from helios_agents.execution.browser_controller import BrowserController, BrowserAction
from helios_agents.execution.data_extractor import DataExtractor
from helios_agents.execution.file_system_manager import FileSystemManager
from helios_agents.core.decision_maker import DecisionMaker, DecisionType


async def main() -> None:
    # Infra e execução (simulados)
    sessions = SessionManager(max_session_hours=1)
    browser = BrowserController(headless=True)
    extractor = DataExtractor()
    files = FileSystemManager(base_path="./_artifacts")
    decision = DecisionMaker(model="gpt-4o", enable_llm=False)  # LLM desativado no mock

    # 1) Cria sessão e abre portal (simulado)
    session_id = await sessions.create_session("browser")
    await browser.start_session(url="https://portal.distribuidora.example/login")

    print(f"[sessao] criada: {session_id}")

    # 2) Navegação e ações básicas (simuladas)
    await browser.execute_action(
        BrowserAction.NAVIGATE,
        {"url": "https://portal.distribuidora.example/formulario"},
    )
    await browser.execute_action(
        BrowserAction.TYPE, {"selector": "#cpf", "text": "123.456.789-00"}
    )
    await browser.execute_action(
        BrowserAction.TYPE, {"selector": "#senha", "text": "senha-super-secreta"}
    )
    await browser.execute_action(BrowserAction.CLICK, {"selector": "#entrar"})

    # 3) Extração de dados da página (simulado)
    html = "<html><body><div id='protocolo'>HX-2025-0001</div></body></html>"
    data = extractor.extract_from_html(html, selectors={"protocolo": "#protocolo"})
    print(f"[extracao] dados: {data}")

    # 4) Decisão sobre próximo passo (regra simulada)
    d = decision.decide(
        type=DecisionType.ROUTE,
        context={"status": "form_ok", "has_protocolo": True},
        options=["upload_documentos", "revisar_dados"],
        rules=[
            {
                "name": "route_upload",
                "type": "ROUTE",
                "priority": 10,
                "condition": {
                    "field": "has_protocolo",
                    "operator": "eq",
                    "value": True,
                },
                "action": "upload_documentos",
            }
        ],
    )
    print(f"[decisao] {d.chosen_option} (conf={d.confidence}) -> {d.reasoning}")

    # 5) Salvamento de um arquivo (simulado)
    doc_id = files.save_file(
        file_content=b"conteudo-pdf-simulado",
        filename="comprovante-protocolo.pdf",
        project_id="proj-abc-123",
        metadata={
            "protocolo": "HX-2025-0001",
            "gerado_em": datetime.utcnow().isoformat(),
        },
    )
    print(f"[files] salvo: {doc_id} -> {files.get_file(doc_id)}")

    # 6) Encerra sessão
    await sessions.terminate_session(session_id)
    await browser.close_session()


if __name__ == "__main__":
    asyncio.run(main())
