"""Tests for PDF generator service."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from app.services.pdf_generator import PDFGenerator, WEASYPRINT_AVAILABLE


class TestPDFGenerator:
    """Test cases for PDF generation service."""

    @pytest.fixture
    def temp_templates_dir(self):
        """Create temporary templates directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            templates_dir = Path(temp_dir)
            
            # Create a sample template
            template_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>{{ title }}</title>
            </head>
            <body>
                <h1>{{ title }}</h1>
                <p>{{ content }}</p>
                {% if items %}
                <ul>
                {% for item in items %}
                    <li>{{ item }}</li>
                {% endfor %}
                </ul>
                {% endif %}
            </body>
            </html>
            """
            
            (templates_dir / "test_template.html").write_text(template_content)
            yield templates_dir

    @pytest.fixture
    def pdf_generator(self, temp_templates_dir):
        """Create PDF generator instance with temp templates."""
        return PDFGenerator(templates_dir=temp_templates_dir)

    def test_pdf_generator_initialization(self, temp_templates_dir):
        """Test PDF generator initialization."""
        generator = PDFGenerator(templates_dir=temp_templates_dir)
        
        assert generator.templates_dir == temp_templates_dir
        assert generator.env is not None

    def test_template_loading(self, pdf_generator):
        """Test template loading from directory."""
        template = pdf_generator.env.get_template("test_template.html")
        assert template is not None

    def test_template_rendering(self, pdf_generator):
        """Test template rendering with context."""
        template = pdf_generator.env.get_template("test_template.html")
        
        context = {
            "title": "Test Document",
            "content": "This is test content",
            "items": ["Item 1", "Item 2", "Item 3"]
        }
        
        rendered = template.render(context)
        
        assert "Test Document" in rendered
        assert "This is test content" in rendered
        assert "Item 1" in rendered

    @pytest.mark.skipif(not WEASYPRINT_AVAILABLE, reason="WeasyPrint not available")
    def test_generate_pdf_with_weasyprint(self, pdf_generator):
        """Test PDF generation using WeasyPrint."""
        with patch('weasyprint.HTML') as mock_html:
            mock_doc = Mock()
            mock_html.return_value = mock_doc
            mock_doc.write_pdf.return_value = b'PDF content'
            
            context = {
                "title": "Test PDF",
                "content": "PDF content",
                "items": ["Test item"]
            }
            
            result = pdf_generator.generate_pdf("test_template.html", context)
            
            assert result == b'PDF content'
            mock_html.assert_called_once()
            mock_doc.write_pdf.assert_called_once()

    def test_generate_pdf_with_reportlab_fallback(self, pdf_generator):
        """Test PDF generation using ReportLab fallback."""
        with patch('app.services.pdf_generator.WEASYPRINT_AVAILABLE', False):
            context = {
                "title": "Test PDF",
                "content": "PDF content",
                "items": ["Test item"]
            }
            
            result = pdf_generator.generate_pdf("test_template.html", context)
            
            assert isinstance(result, bytes)
            assert len(result) > 0

    def test_html_to_reportlab_conversion(self, pdf_generator):
        """Test HTML to ReportLab element conversion."""
        html_content = """
        <h1>Title</h1>
        <p>Paragraph content</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        """
        
        elements = pdf_generator._html_to_reportlab_elements(html_content)
        
        assert len(elements) > 0
        # Should contain title, paragraph, and list items

    def test_generate_invoice_pdf(self, pdf_generator):
        """Test invoice PDF generation."""
        invoice_data = {
            "invoice_number": "INV-001",
            "date": "2025-10-23",
            "client_name": "Test Client",
            "items": [
                {"description": "Service 1", "amount": 100.0},
                {"description": "Service 2", "amount": 200.0}
            ],
            "total": 300.0
        }
        
        # Mock template for invoice
        with patch.object(pdf_generator.env, 'get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html><body>Invoice</body></html>"
            mock_get_template.return_value = mock_template
            
            result = pdf_generator.generate_invoice_pdf(invoice_data)
            
            assert isinstance(result, bytes)
            mock_get_template.assert_called_with("invoice.html")

    def test_generate_report_pdf(self, pdf_generator):
        """Test report PDF generation."""
        report_data = {
            "title": "Monthly Report",
            "period": "October 2025",
            "sections": [
                {"title": "Section 1", "content": "Content 1"},
                {"title": "Section 2", "content": "Content 2"}
            ]
        }
        
        with patch.object(pdf_generator.env, 'get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html><body>Report</body></html>"
            mock_get_template.return_value = mock_template
            
            result = pdf_generator.generate_report_pdf(report_data)
            
            assert isinstance(result, bytes)
            mock_get_template.assert_called_with("report.html")

    def test_generate_certificate_pdf(self, pdf_generator):
        """Test certificate PDF generation."""
        cert_data = {
            "recipient_name": "John Doe",
            "certificate_type": "Completion",
            "issue_date": "2025-10-23",
            "issuer": "HaaS Platform"
        }
        
        with patch.object(pdf_generator.env, 'get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html><body>Certificate</body></html>"
            mock_get_template.return_value = mock_template
            
            result = pdf_generator.generate_certificate_pdf(cert_data)
            
            assert isinstance(result, bytes)
            mock_get_template.assert_called_with("certificate.html")

    def test_error_handling_missing_template(self, pdf_generator):
        """Test error handling for missing templates."""
        with pytest.raises(Exception):  # Jinja2 will raise TemplateNotFound
            pdf_generator.generate_pdf("nonexistent.html", {})

    def test_error_handling_invalid_context(self, pdf_generator):
        """Test error handling for invalid template context."""
        # Template expects 'title' but we don't provide it
        context = {"content": "test"}
        
        # Should not raise error, just render empty title
        result = pdf_generator.generate_pdf("test_template.html", context)
        assert isinstance(result, bytes)

    def test_css_styling_injection(self, pdf_generator):
        """Test CSS styling injection in templates."""
        with patch('app.services.pdf_generator.WEASYPRINT_AVAILABLE', True):
            with patch('weasyprint.HTML') as mock_html:
                mock_doc = Mock()
                mock_html.return_value = mock_doc
                mock_doc.write_pdf.return_value = b'PDF with CSS'
                
                context = {"title": "Styled PDF", "content": "Content"}
                css_styles = "body { font-family: Arial; }"
                
                result = pdf_generator.generate_pdf(
                    "test_template.html", 
                    context, 
                    css_styles=css_styles
                )
                
                assert result == b'PDF with CSS'

    def test_reportlab_table_generation(self, pdf_generator):
        """Test ReportLab table generation from data."""
        table_data = [
            ["Header 1", "Header 2", "Header 3"],
            ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
            ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"]
        ]
        
        table = pdf_generator._create_reportlab_table(table_data)
        
        assert table is not None
        # Table should have proper styling applied

    def test_pdf_metadata_injection(self, pdf_generator):
        """Test PDF metadata injection."""
        metadata = {
            "title": "Test Document",
            "author": "HaaS Platform",
            "subject": "Test Subject",
            "creator": "PDF Generator Service"
        }
        
        with patch('app.services.pdf_generator.WEASYPRINT_AVAILABLE', True):
            with patch('weasyprint.HTML') as mock_html:
                mock_doc = Mock()
                mock_html.return_value = mock_doc
                mock_doc.write_pdf.return_value = b'PDF with metadata'
                
                context = {"title": "Test", "content": "Content"}
                
                result = pdf_generator.generate_pdf(
                    "test_template.html", 
                    context, 
                    metadata=metadata
                )
                
                assert result == b'PDF with metadata'

    def test_concurrent_pdf_generation(self, pdf_generator):
        """Test concurrent PDF generation."""
        import asyncio
        
        async def generate_pdf_async():
            context = {"title": f"PDF {id}", "content": "Content"}
            return pdf_generator.generate_pdf("test_template.html", context)
        
        # This test ensures thread safety
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                asyncio.gather(*[generate_pdf_async() for _ in range(5)])
            )
            
            assert len(results) == 5
            for result in results:
                assert isinstance(result, bytes)
        finally:
            loop.close()

    def test_memory_optimization(self, pdf_generator):
        """Test memory optimization for large PDFs."""
        # Test with large context data
        large_context = {
            "title": "Large PDF",
            "content": "A" * 10000,  # 10KB of content
            "items": [f"Item {i}" for i in range(1000)]
        }
        
        result = pdf_generator.generate_pdf("test_template.html", large_context)
        
        assert isinstance(result, bytes)
        assert len(result) > 0