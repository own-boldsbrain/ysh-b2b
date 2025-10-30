"""
Testes de integração com haas/validators
"""

import pytest
from helios_agents.execution.data_extractor import DataExtractor


class TestHaasValidatorsIntegration:
    """Testes de integração com validadores do haas"""

    def test_data_extractor_with_validator(self):
        """Testa integração entre DataExtractor e validadores"""
        # Este teste demonstra como o DataExtractor pode usar validadores do haas
        extractor = DataExtractor()

        # Dados extraídos (simulados)
        extracted_data = {
            "equipamentos": [
                {
                    "numero_certificado": "12345",
                    "data_emissao": "2023-01-01",
                    "validade": "2025-01-01",
                }
            ]
        }

        # Schema de validação (simulado baseado no INMETRO)
        schema = {
            "type": "object",
            "properties": {
                "equipamentos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "numero_certificado": {"type": "string"},
                            "data_emissao": {"type": "string", "format": "date"},
                            "validade": {"type": "string", "format": "date"},
                        },
                        "required": ["numero_certificado", "data_emissao", "validade"],
                    },
                }
            },
        }

        # Validação usando DataExtractor
        validation_result = extractor.validate_against_schema(extracted_data, schema)

        # Em implementação real, isso seria integrado com RecordValidator do haas
        assert validation_result["valid"] is True
        assert validation_result["errors"] == []

    def test_agent_workflow_with_validation(self):
        """Testa workflow de agente com validação integrada"""
        # Simula um workflow onde dados são extraídos e validados
        extractor = DataExtractor()

        # Dados de homologação extraídos
        homologation_data = {
            "projeto": "Solar Farm ABC",
            "potencia_instalada": 1000,
            "documentos": ["certificado_inmetro.pdf", "laudo_tecnico.pdf"],
        }

        # Validação básica (em produção usaria validadores do haas)
        validation_schema = {
            "type": "object",
            "properties": {
                "projeto": {"type": "string"},
                "potencia_instalada": {"type": "number", "minimum": 0},
                "documentos": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["projeto", "potencia_instalada"],
        }

        result = extractor.validate_against_schema(homologation_data, validation_schema)

        assert result["valid"] is True
