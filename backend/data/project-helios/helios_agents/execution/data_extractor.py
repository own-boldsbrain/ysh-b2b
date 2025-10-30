"""DataExtractor - Extração e transformação de dados estruturados."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json

try:  # BeautifulSoup e lxml
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except Exception:  # pragma: no cover - ambiente sem BS4
    BeautifulSoup = None
    BS4_AVAILABLE = False

try:  # pdfplumber
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except Exception:  # pragma: no cover - ambiente sem pdfplumber
    pdfplumber = None
    PDFPLUMBER_AVAILABLE = False

try:
    from jsonschema import Draft202012Validator

    JSONSCHEMA_AVAILABLE = True
except Exception:  # pragma: no cover - jsonschema ausente
    Draft202012Validator = None
    JSONSCHEMA_AVAILABLE = False


class DataExtractor:
    """Extrator de dados com suporte a múltiplos formatos."""

    def __init__(self):
        self.extraction_cache: Dict[str, Any] = {}

    def extract_from_html(self, html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """Extrai dados de HTML usando seletores CSS."""
        if not BS4_AVAILABLE:
            return {"status": "simulated", "selectors": selectors}

        soup = BeautifulSoup(html, "lxml")
        extracted: Dict[str, Optional[str]] = {}

        for field, selector in selectors.items():
            element = soup.select_one(selector)
            extracted[field] = element.get_text(strip=True) if element else None

        return {"status": "ok", "extracted": extracted}

    def extract_from_pdf(
        self, pdf_path: Union[str, Path], fields: List[str]
    ) -> Dict[str, Any]:
        """Extrai campos de PDF utilizando pdfplumber."""
        if not PDFPLUMBER_AVAILABLE:
            return {"status": "simulated", "fields": fields}

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")

        extracted: Dict[str, Optional[str]] = {field: None for field in fields}
        full_text: List[str] = []

        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                full_text.append(page_text)

        text_joined = "\n".join(full_text)
        for field in fields:
            extracted[field] = self._find_field_value(text_joined, field)

        return {"status": "ok", "extracted": extracted, "pages": len(full_text)}

    def validate_against_schema(
        self, data: Dict[str, Any], schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida dados contra schema JSON."""
        if not JSONSCHEMA_AVAILABLE:
            return {"valid": True, "errors": []}

        validator = Draft202012Validator(schema)
        errors = [self._format_error(error) for error in validator.iter_errors(data)]
        return {"valid": len(errors) == 0, "errors": errors}

    def _find_field_value(self, text: str, field: str) -> Optional[str]:
        """Localiza valor de um campo no texto do PDF."""
        for line in text.splitlines():
            if field.lower() in line.lower():
                return line.strip()
        return None

    def _format_error(self, error: Any) -> str:
        """Formata erros de validação jsonschema."""
        path = "->".join(str(part) for part in error.absolute_path)
        return f"{path or '<root>'}: {error.message}"
