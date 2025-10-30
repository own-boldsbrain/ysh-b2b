"""
HaaS Platform - OpenAPI Documentation Enhancement
Enhanced documentation for INMETRO API endpoints with examples and detailed descriptions
"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any


def enhance_openapi_schema(app: FastAPI) -> Dict[str, Any]:
    """
    Enhance the OpenAPI schema with detailed INMETRO API documentation.

    Args:
        app: FastAPI application instance

    Returns:
        Enhanced OpenAPI schema dictionary
    """
    # Get base schema
    schema = get_openapi(
        title="HaaS Platform API - Homologação como Serviço",
        version="1.0.0",
        description="""
        # HaaS Platform - API de Homologação como Serviço

        Plataforma completa para automatização do processo de homologação de projetos fotovoltaicos junto às concessionárias de energia brasileiras.

        ## Funcionalidades Principais

        - **Validação INMETRO**: Verificação automática de certificações de equipamentos fotovoltaicos
        - **Integração com Concessionárias**: Submissão automática de projetos para homologação
        - **Análise de Viabilidade**: Cálculos técnicos e econômicos de projetos solares
        - **Monitoramento em Tempo Real**: Acompanhamento do status de homologações

        ## Autenticação

        Todos os endpoints requerem autenticação via JWT token no header `Authorization: Bearer <token>`.

        ## Rate Limiting

        - 60 requisições por minuto
        - 1000 requisições por hora

        ## Versionamento

        A API utiliza versionamento semântico. A versão atual é **v1.0.0**.

        ## Suporte

        Para dúvidas ou suporte técnico, entre em contato com a equipe de desenvolvimento.
        """,
        routes=app.routes,
    )

    # Enhance INMETRO endpoints with detailed documentation
    if "paths" in schema:
        # Validate endpoint enhancement
        if "/api/inmetro/validate" in schema["paths"]:
            validate_path = schema["paths"]["/api/inmetro/validate"]
            if "post" in validate_path:
                validate_post = validate_path["post"]
                validate_post["description"] = """
                **Validação de Equipamento INMETRO**

                Inicia o processo de validação assíncrona de um equipamento fotovoltaico no portal do INMETRO.

                **Processo de Validação:**
                1. Recebe os dados do equipamento (categoria, fabricante, modelo)
                2. Consulta o portal do INMETRO em background
                3. Extrai informações de certificação usando IA
                4. Valida conformidade com normas técnicas
                5. Retorna resultado da validação

                **Tipos de Equipamento Suportados:**
                - `inversores`: Inversores fotovoltaicos
                - `modulos`: Módulos solares
                - `cabos`: Cabos elétricos
                - `conectores`: Conectores elétricos
                - `disjuntores`: Disjuntores e proteção

                **Tempo Estimado:** 30-120 segundos por equipamento
                """
                validate_post["requestBody"]["content"]["application/json"]["example"] = {
                    "categoria": "inversores",
                    "fabricante": "Fronius",
                    "modelo": "Primo 8.2-1",
                    "registry_id": "REG-2025-001"
                }
                validate_post["responses"]["202"]["content"]["application/json"]["example"] = {
                    "request_id": "req_a1b2c3d4",
                    "status": "pending",
                    "equipment_type": "inversores",
                    "model": "Primo 8.2-1",
                    "manufacturer": "Fronius",
                    "message": "Validação agendada. Use GET /status/{request_id} para acompanhar.",
                    "created_at": "2025-01-15T10:30:00Z"
                }

        # Status endpoint enhancement
        if "/api/inmetro/status/{request_id}" in schema["paths"]:
            status_path = schema["paths"]["/api/inmetro/status/{request_id}"]
            if "get" in status_path:
                status_get = status_path["get"]
                status_get["description"] = """
                **Consulta Status de Validação**

                Retorna o status atual de uma validação em andamento ou concluída.

                **Estados Possíveis:**
                - `pending`: Aguardando processamento
                - `in_progress`: Processamento em andamento
                - `completed`: Validação concluída com sucesso
                - `failed`: Falha na validação

                **Polling Recomendado:** Consultar a cada 5-10 segundos até conclusão
                """
                status_get["responses"]["200"]["content"]["application/json"]["examples"] = {
                    "pending": {
                        "summary": "Validação Pendente",
                        "value": {
                            "request_id": "req_a1b2c3d4",
                            "status": "pending",
                            "equipment_type": "inversores",
                            "message": "Validação agendada",
                            "created_at": "2025-01-15T10:30:00Z"
                        }
                    },
                    "completed": {
                        "summary": "Validação Concluída",
                        "value": {
                            "request_id": "req_a1b2c3d4",
                            "status": "completed",
                            "equipment_type": "inversores",
                            "model": "Primo 8.2-1",
                            "manufacturer": "Fronius",
                            "certification_number": "BRA-2024-001234",
                            "valid": True,
                            "message": "Equipamento validado no INMETRO",
                            "created_at": "2025-01-15T10:30:00Z",
                            "completed_at": "2025-01-15T10:31:45Z"
                        }
                    },
                    "failed": {
                        "summary": "Validação Falhou",
                        "value": {
                            "request_id": "req_a1b2c3d4",
                            "status": "failed",
                            "equipment_type": "inversores",
                            "valid": False,
                            "message": "Erro: Equipamento não encontrado no INMETRO",
                            "created_at": "2025-01-15T10:30:00Z",
                            "completed_at": "2025-01-15T10:31:00Z"
                        }
                    }
                }

        # Manufacturers endpoint enhancement
        if "/api/inmetro/manufacturers" in schema["paths"]:
            manufacturers_path = schema["paths"]["/api/inmetro/manufacturers"]
            if "get" in manufacturers_path:
                manufacturers_get = manufacturers_path["get"]
                manufacturers_get["description"] = """
                **Lista Fabricantes Certificados**

                Retorna a lista de fabricantes que possuem equipamentos certificados no INMETRO.

                **Filtros Disponíveis:**
                - `categoria`: Filtrar por tipo de equipamento

                **Fabricantes Principais:**
                - Fronius (Inversores)
                - Canadian Solar (Módulos)
                - SMA (Inversores)
                - ABB (Inversores)
                - Huawei (Inversores)
                """
                manufacturers_get["responses"]["200"]["content"]["application/json"]["example"] = [
                    "Fronius",
                    "Canadian Solar",
                    "SMA",
                    "ABB",
                    "Huawei",
                    "Sungrow"
                ]

        # Models endpoint enhancement
        if "/api/inmetro/models/{manufacturer}" in schema["paths"]:
            models_path = schema["paths"]["/api/inmetro/models/{manufacturer}"]
            if "get" in models_path:
                models_get = models_path["get"]
                models_get["description"] = """
                **Lista Modelos de Fabricante**

                Retorna todos os modelos certificados de um fabricante específico.

                **Parâmetros:**
                - `manufacturer`: Nome do fabricante (path parameter)
                - `categoria`: Filtrar por categoria (opcional)

                **Exemplos de Modelos:**
                - Inversores: Primo 8.2-1, Symo 10.0-3-M
                - Módulos: CS3W-450MS, HiKu7 Mono 670W
                """
                models_get["responses"]["200"]["content"]["application/json"]["example"] = [
                    "Primo 8.2-1",
                    "Primo 5.0-1",
                    "Symo 10.0-3-M",
                    "Eco 25.0-3-S"
                ]

        # Certificate details endpoint enhancement
        if "/api/inmetro/certificate/{certificate_number}" in schema["paths"]:
            cert_path = schema["paths"]["/api/inmetro/certificate/{certificate_number}"]
            if "get" in cert_path:
                cert_get = cert_path["get"]
                cert_get["description"] = """
                **Detalhes de Certificado INMETRO**

                Retorna informações completas e detalhadas de um certificado específico.

                **Informações Incluídas:**
                - Dados do fabricante e modelo
                - Especificações técnicas
                - Data de validade
                - Links para documentação
                - Status de verificação
                """
                cert_get["responses"]["200"]["content"]["application/json"]["example"] = {
                    "certificate_number": "BRA-2024-001234",
                    "equipment_type": "Inversor Fotovoltaico",
                    "manufacturer": "Fronius",
                    "model": "Primo 8.2-1",
                    "power_rating": "8.2 kW",
                    "valid_until": "2026-12-31T00:00:00Z",
                    "technical_specs": {
                        "efficiency": "97.3%",
                        "voltage_input": "580-1000 VDC",
                        "voltage_output": "220/380 VAC",
                        "mppt_inputs": 2,
                        "max_current": "16 A"
                    },
                    "inmetro_url": "https://www.inmetro.gov.br/certificacao/certificado.asp?certificado=BRA-2024-001234",
                    "datasheet_url": "https://www.fronius.com/en/solar-energy/installers/products/all-products/inverters/primo/primo-8-2-1",
                    "last_verified": "2025-01-15T10:00:00Z"
                }

        # Search endpoint enhancement
        if "/api/inmetro/search" in schema["paths"]:
            search_path = schema["paths"]["/api/inmetro/search"]
            if "get" in search_path:
                search_get = search_path["get"]
                search_get["description"] = """
                **Busca de Equipamentos Certificados**

                Busca equipamentos certificados por fabricante, modelo ou categoria.

                **Parâmetros de Busca:**
                - `query`: Termo de busca (mínimo 3 caracteres)
                - `category`: Filtrar por categoria
                - `page`: Número da página (padrão: 1)
                - `page_size`: Itens por página (1-100, padrão: 10)

                **Resultados Incluem:**
                - Número do certificado
                - Fabricante e modelo
                - Tipo de equipamento
                - Especificações básicas
                """
                search_get["responses"]["200"]["content"]["application/json"]["example"] = {
                    "total": 25,
                    "page": 1,
                    "page_size": 10,
                    "results": [
                        {
                            "certificate_number": "BRA-2024-001234",
                            "equipment_type": "Inversor",
                            "manufacturer": "Fronius",
                            "model": "Primo 8.2-1",
                            "power_rating": "8.2 kW",
                            "technical_specs": {"efficiency": "97.3%"},
                            "last_verified": "2025-01-15T10:00:00Z"
                        }
                    ]
                }

        # Batch validation endpoint enhancement
        if "/api/inmetro/batch" in schema["paths"]:
            batch_path = schema["paths"]["/api/inmetro/batch"]
            if "post" in batch_path:
                batch_post = batch_path["post"]
                batch_post["description"] = """
                **Validação em Lote**

                Valida múltiplos equipamentos simultaneamente (até 50 equipamentos por lote).

                **Vantagens:**
                - Processamento paralelo
                - Economia de tempo
                - Resultados consolidados

                **Limitações:**
                - Máximo 50 equipamentos por requisição
                - Mesmo tipo de processamento para todos

                **Retorno:** Mapeamento de índices para request_ids individuais
                """
                batch_post["requestBody"]["content"]["application/json"]["example"] = {
                    "equipments": [
                        {
                            "categoria": "inversores",
                            "fabricante": "Fronius",
                            "modelo": "Primo 8.2-1"
                        },
                        {
                            "categoria": "modulos",
                            "fabricante": "Canadian Solar",
                            "modelo": "CS3W-450MS"
                        }
                    ]
                }
                batch_post["responses"]["202"]["content"]["application/json"]["example"] = {
                    "0": "req_a1b2c3d4",
                    "1": "req_e5f6g7h8",
                    "message": "2 validações agendadas"
                }

    # Add metrics endpoint documentation
    if "/metrics" not in schema["paths"]:
        schema["paths"]["/metrics"] = {
            "get": {
                "summary": "Prometheus Metrics",
                "description": "Endpoint para coleta de métricas Prometheus com dados de performance da API.",
                "tags": ["Monitoring"],
                "responses": {
                    "200": {
                        "description": "Métricas Prometheus em formato texto",
                        "content": {
                            "text/plain": {
                                "example": "# HELP haas_http_requests_total Total number of HTTP requests\n# TYPE haas_http_requests_total counter\nhaas_http_requests_total{method=\"GET\",endpoint=\"/health\",status_code=\"200\"} 42\n"
                            }
                        }
                    }
                }
            }
        }

    # Add enhanced health check documentation
    if "/health/metrics" not in schema["paths"]:
        schema["paths"]["/health/metrics"] = {
            "get": {
                "summary": "Health Check com Métricas",
                "description": "Verificação de saúde da aplicação incluindo métricas de performance.",
                "tags": ["Monitoring"],
                "responses": {
                    "200": {
                        "description": "Status de saúde da aplicação",
                        "content": {
                            "application/json": {
                                "example": {
                                    "status": "healthy",
                                    "service": "haas-api",
                                    "version": "1.0.0",
                                    "timestamp": "2025-01-15T10:30:00Z",
                                    "checks": {
                                        "database": "healthy",
                                        "redis": "healthy"
                                    },
                                    "metrics": {
                                        "total_requests": 150,
                                        "total_validations": 25,
                                        "cache_hit_ratio": 0.85
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    return schema


def setup_openapi_enhancement(app: FastAPI) -> None:
    """
    Configure enhanced OpenAPI documentation for the FastAPI app.

    Args:
        app: FastAPI application instance
    """

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        app.openapi_schema = enhance_openapi_schema(app)
        return app.openapi_schema

    app.openapi = custom_openapi