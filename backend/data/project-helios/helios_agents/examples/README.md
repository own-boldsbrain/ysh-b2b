# Exemplos de Workflows

Este diretório contém exemplos mínimos e executáveis que demonstram o uso dos 12 nós criados para o Project Helios.

## Pré-requisitos
- Python 3.12 ativo na venv
- Estar no diretório raiz do repositório

## Exemplos

1) basic_event_workflow.py
- Mostra o roteamento de eventos (EventRouter), uso de gatilho condicional (ConditionalTrigger) e agregação por janela temporal (Aggregator).
- Executa um fluxo assíncrono simples com publicação e consumo de eventos.

Como executar:
```pwsh
python -m helios_agents.examples.basic_event_workflow
```

2) solar_homologation_mock.py
- Demonstra um fluxo mock de homologação com SessionManager, BrowserController (simulado), DataExtractor (simulado), FileSystemManager e DecisionMaker (LLM simulado + regras).
- Útil para entender a orquestração sem dependências externas.

Como executar:
```pwsh
python -m helios_agents.examples.solar_homologation_mock
```

## Notas
- Estes exemplos usam implementações simuladas ("TODO") para BrowserController e DataExtractor. Servem para validar a integração entre nós e o padrão de uso.
- Substitua as partes marcadas como TODO por integrações reais (Playwright, BeautifulSoup/pdfplumber, jsonschema) conforme necessário.
