"""
Testes unitários para DataExtractor
"""

import pytest
from helios_agents.execution.data_extractor import DataExtractor


class TestDataExtractor:
    """Testes para DataExtractor"""

    def test_initialization(self):
        """Testa inicialização do DataExtractor"""
        extractor = DataExtractor()

        assert extractor.extraction_cache == {}

    def test_extract_from_html(self):
        """Testa extração de HTML (simulada)"""
        extractor = DataExtractor()

        html = "<html><body><h1>Test</h1></body></html>"
        selectors = {"title": "h1", "content": "body"}

        result = extractor.extract_from_html(html, selectors)

        assert result["status"] == "simulated"
        assert result["selectors"] == selectors

    def test_extract_from_pdf(self):
        """Testa extração de PDF (simulada)"""
        extractor = DataExtractor()

        pdf_path = "/path/to/document.pdf"
        fields = ["name", "date", "value"]

        result = extractor.extract_from_pdf(pdf_path, fields)

        assert result["status"] == "simulated"
        assert result["fields"] == fields

    def test_validate_against_schema(self):
        """Testa validação contra schema (simulada)"""
        extractor = DataExtractor()

        data = {"name": "Test", "value": 100}
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}

        result = extractor.validate_against_schema(data, schema)

        assert result["valid"] is True
        assert result["errors"] == []
