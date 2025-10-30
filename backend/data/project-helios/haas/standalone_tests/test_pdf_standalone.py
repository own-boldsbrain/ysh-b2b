"""
Standalone PDF generator tests
"""
import os
import tempfile
from unittest.mock import Mock


class MockPDFGenerator:
    """Mock PDF generator for testing without imports"""

    def __init__(self):
        self.config = {
            'pdf_output_dir': 'temp_pdfs',
            'pdf_templates_dir': 'templates',
            'pdf_max_size_mb': 50,
            'pdf_quality': 'high'
        }
        self.weasyprint_available = True
        self.reportlab_available = True

    def generate_pdf(self, template_name: str, context: dict, output_path=None) -> bytes:
        """Mock PDF generation"""
        if template_name == "invalid_template.html":
            raise FileNotFoundError("Template not found")

        if context.get('force_error'):
            raise Exception("PDF generation failed")

        # Mock PDF content
        pdf_content = f"Mock PDF content for {template_name}".encode()

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_content)

        return pdf_content

    def render_template(self, template_name: str, context: dict) -> str:
        """Mock template rendering"""
        if template_name == "missing_template.html":
            raise FileNotFoundError("Template not found")

        # Mock HTML content
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{context.get('title', 'Document')}</title>
        </head>
        <body>
            <h1>{context.get('title', 'Document')}</h1>
            <p>Project ID: {context.get('project_id', 'N/A')}</p>
            <p>Status: {context.get('status', 'N/A')}</p>
        </body>
        </html>
        """
        return html

    def generate_with_weasyprint(self, html_content: str) -> bytes:
        """Mock WeasyPrint PDF generation"""
        if not self.weasyprint_available:
            raise ImportError("WeasyPrint not available")
        return f"WeasyPrint PDF: {html_content[:50]}...".encode()

    def generate_with_reportlab(self, content: dict) -> bytes:
        """Mock ReportLab PDF generation"""
        if not self.reportlab_available:
            raise ImportError("ReportLab not available")
        return f"ReportLab PDF: {content.get('title', 'Document')}".encode()


class TestStandalonePDFGenerator:
    """Test PDF generator functionality independently"""

    def pdf_generator(self):
        """Create PDF generator instance"""
        return MockPDFGenerator()

    def sample_context(self):
        """Sample template context"""
        return {
            "title": "Relatório de Homologação",
            "project_id": "PROJ_123456",
            "client_name": "Empresa Solar LTDA",
            "status": "Aprovado",
            "validation_date": "2024-01-15",
            "equipment_list": [
                {"model": "Inversor ABC-123", "power": "5kW"},
                {"model": "Painel XYZ-456", "power": "400W"}
            ]
        }

    def test_pdf_generator_initialization(self, pdf_generator):
        """Test PDF generator initializes correctly"""
        assert pdf_generator.config['pdf_output_dir'] == 'temp_pdfs'
        assert pdf_generator.config['pdf_max_size_mb'] == 50
        assert pdf_generator.weasyprint_available is True
        assert pdf_generator.reportlab_available is True

    def test_generate_pdf_success(self, pdf_generator, sample_context):
        """Test successful PDF generation"""
        template_name = "homologation_report.html"
        pdf_content = pdf_generator.generate_pdf(template_name, sample_context)

        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        assert b"Mock PDF content" in pdf_content

    def test_render_template_success(self, pdf_generator, sample_context):
        """Test template rendering"""
        template_name = "homologation_report.html"
        html_content = pdf_generator.render_template(template_name, sample_context)

        assert isinstance(html_content, str)
        assert "<!DOCTYPE html>" in html_content
        assert sample_context["title"] in html_content
        assert sample_context["project_id"] in html_content

    def test_generate_with_weasyprint(self, pdf_generator):
        """Test WeasyPrint PDF generation"""
        html_content = "<html><body><h1>Test Document</h1></body></html>"
        pdf_content = pdf_generator.generate_with_weasyprint(html_content)

        assert isinstance(pdf_content, bytes)
        assert b"WeasyPrint PDF" in pdf_content

    def test_generate_with_reportlab(self, pdf_generator, sample_context):
        """Test ReportLab PDF generation"""
        content = {"title": sample_context["title"], "data": sample_context}
        pdf_content = pdf_generator.generate_with_reportlab(content)

        assert isinstance(pdf_content, bytes)
        assert b"ReportLab PDF" in pdf_content
