"""PDF generation service using Jinja2 templates and WeasyPrint or ReportLab."""

import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Import ReportLab for fallback
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

# Template directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _check_weasyprint_available():
    """Check if WeasyPrint is available."""
    try:
        import weasyprint
        return True
    except (ImportError, OSError):
        return False


WEASYPRINT_AVAILABLE = _check_weasyprint_available()


class PDFGenerator:
    """PDF generator using Jinja2 and WeasyPrint."""

    def __init__(self, templates_dir: Path = TEMPLATES_DIR):
        """
        Initialize PDF generator.

        Args:
            templates_dir: Directory containing Jinja2 templates
        """
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Add custom filters
        self.env.filters["format_date"] = self._format_date
        self.env.filters["format_currency"] = self._format_currency
        self.env.filters["format_power"] = self._format_power

    @staticmethod
    def _format_date(value: datetime, format_str: str = "%d/%m/%Y") -> str:
        """Format datetime to Brazilian date."""
        if isinstance(value, datetime):
            return value.strftime(format_str)
        return str(value)

    @staticmethod
    def _format_currency(value: float) -> str:
        """Format value as Brazilian currency."""
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def _format_power(value: float, unit: str = "kWp") -> str:
        """Format power value."""
        return (
            f"{value:,.2f} {unit}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render Jinja2 template to HTML.

        Args:
            template_name: Template filename (e.g., 
memorial.html)
            context: Template context variables

        Returns:
            Rendered HTML string
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as exc:
            logger.error("Template rendering failed: %s", exc)
            raise

    def generate_pdf(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Path,
        stylesheets: list[str] = None,
    ) -> Path:
        """
        Generate PDF from template.

        Args:
            template_name: Template filename
            context: Template context
            output_path: Output PDF path
            stylesheets: Optional CSS stylesheet filenames

        Returns:
            Path to generated PDF
        """
        try:
            # Import WeasyPrint here to avoid module-level import issues
            from weasyprint import HTML, CSS

            # Render HTML
            html_content = self.render_template(template_name, context)

            # Load CSS stylesheets
            css_list = []
            if stylesheets:
                for css_file in stylesheets:
                    css_path = self.templates_dir / css_file
                    if css_path.exists():
                        css_list.append(CSS(filename=str(css_path)))
                    else:
                        logger.warning("CSS file not found: %s", css_file)

            # Generate PDF
            html = HTML(string=html_content, base_url=str(self.templates_dir))
            html.write_pdf(str(output_path), stylesheets=css_list)

            logger.info(
                "PDF generated: %s (%d bytes)", output_path, output_path.stat().st_size
            )
            return output_path

        except Exception as exc:
            logger.error("PDF generation failed: %s", exc)
            raise


class ReportLabPDFGenerator:
    """PDF generator using ReportLab as fallback when WeasyPrint is unavailable."""

    def __init__(self, templates_dir: Path = TEMPLATES_DIR):
        """
        Initialize ReportLab PDF generator.

        Args:
            templates_dir: Directory containing Jinja2 templates
        """
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Add custom filters
        self.env.filters["format_date"] = self._format_date
        self.env.filters["format_currency"] = self._format_currency
        self.env.filters["format_power"] = self._format_power

        # Custom styles for professional documents
        self.styles = getSampleStyleSheet()

        # Add custom styles
        self.styles.add(ParagraphStyle(
            name="CustomTitle",
            parent=self.styles["Title"],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
        ))

        self.styles.add(ParagraphStyle(
            name="CustomSubtitle",
            parent=self.styles["Heading2"],
            fontSize=14,
            spaceAfter=20,
            textColor=colors.darkgreen,
        ))

        self.styles.add(ParagraphStyle(
            name="CustomNormal",
            parent=self.styles["Normal"],
            fontSize=10,
            spaceAfter=12,
        ))

        self.styles.add(ParagraphStyle(
            name="TableHeader",
            parent=self.styles["Normal"],
            fontSize=10,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        ))

    @staticmethod
    def _format_date(value: datetime, format_str: str = "%d/%m/%Y") -> str:
        """Format datetime to Brazilian date."""
        if isinstance(value, datetime):
            return value.strftime(format_str)
        return str(value)

    @staticmethod
    def _format_currency(value: float) -> str:
        """Format value as Brazilian currency."""
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def _format_power(value: float, unit: str = "kWp") -> str:
        """Format power value."""
        return (
            f"{value:,.2f} {unit}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render Jinja2 template to HTML.

        Args:
            template_name: Template filename (e.g., memorial.html)
            context: Template context variables

        Returns:
            Rendered HTML string
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as exc:
            logger.error("Template rendering failed: %s", exc)
            raise

    def _html_to_reportlab_elements(self, html_content: str) -> list:
        """
        Convert HTML content to ReportLab elements.

        Args:
            html_content: HTML string to convert

        Returns:
            List of ReportLab elements
        """
        elements = []
        soup = BeautifulSoup(html_content, "html.parser")

        for element in soup.find_all(["h1", "h2", "h3", "p", "table", "div"]):
            if element.name in ["h1", "h2", "h3"]:
                # Handle headings
                style_name = "CustomTitle" if element.name == "h1" else "CustomSubtitle"
                text = element.get_text().strip()
                if text:
                    elements.append(Paragraph(text, self.styles[style_name]))
                    elements.append(Spacer(1, 12))

            elif element.name == "p":
                # Handle paragraphs
                text = element.get_text().strip()
                if text:
                    elements.append(Paragraph(text, self.styles["CustomNormal"]))
                    elements.append(Spacer(1, 6))

            elif element.name == "table":
                # Handle tables
                table_data = []
                headers = []

                # Extract headers
                header_rows = element.find_all("thead")
                if header_rows:
                    for header_row in header_rows:
                        header_cells = header_row.find_all(["th", "td"])
                        headers = [cell.get_text().strip() for cell in header_cells]
                        table_data.append(headers)

                # Extract data rows
                body_rows = element.find_all("tbody")
                if body_rows:
                    for body in body_rows:
                        rows = body.find_all("tr")
                        for row in rows:
                            cells = row.find_all("td")
                            row_data = [cell.get_text().strip() for cell in cells]
                            if row_data:
                                table_data.append(row_data)

                if table_data:
                    # Create table
                    table = Table(table_data, colWidths=[4*cm] * len(table_data[0]))

                    # Style the table
                    table_style = TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ])
                    table.setStyle(table_style)
                    elements.append(table)
                    elements.append(Spacer(1, 12))

            elif element.name == "div" and "signature-section" in element.get("class", []):
                # Handle signature section
                elements.append(Spacer(1, 24))
                elements.append(Paragraph("Assinatura do Responsável Técnico", self.styles["CustomNormal"]))
                elements.append(Spacer(1, 48))  # Space for signature

        return elements

    def generate_pdf(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Path,
        stylesheets: list[str] = None,
    ) -> Path:
        """
        Generate PDF from template using ReportLab.

        Args:
            template_name: Template filename
            context: Template context
            output_path: Output PDF path
            stylesheets: Optional CSS stylesheet filenames (ignored in ReportLab)

        Returns:
            Path to generated PDF
        """
        try:
            # Render HTML
            html_content = self.render_template(template_name, context)

            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            # Convert HTML to ReportLab elements
            elements = self._html_to_reportlab_elements(html_content)

            # Build PDF
            doc.build(elements)

            logger.info(
                "PDF generated with ReportLab: %s (%d bytes)",
                output_path,
                output_path.stat().st_size
            )
            return output_path

        except Exception as exc:
            logger.error("ReportLab PDF generation failed: %s", exc)
            raise


class MemorialGenerator:
    """Memorial Descritivo PDF generator."""

    def __init__(self, pdf_generator=None):
        """Initialize memorial generator."""
        self.pdf_gen = pdf_generator or get_pdf_generator()

    def generate_memorial(
        self, project_data: Dict[str, Any], output_path: Path
    ) -> Path:
        """
        Generate Memorial Descritivo PDF.

        Args:
            project_data: Project data dictionary
            output_path: Output PDF path

        Returns:
            Path to generated PDF
        """
        # Enrich context with metadata
        context = {
            **project_data,
            "generation_date": datetime.now(),
            "document_title": "Memorial Descritivo de Instalação Fotovoltaica",
            "document_version": "1.0",
            "responsible_engineer": project_data.get("engineer_name", "A definir"),
            "crea_number": project_data.get("crea_number", "XXXXX-XX"),
        }

        return self.pdf_gen.generate_pdf(
            template_name="memorial.html",
            context=context,
            output_path=output_path,
            stylesheets=["memorial.css"],
        )


class DiagramGenerator:
    """Technical diagram PDF generator."""

    def __init__(self, pdf_generator=None):
        """Initialize diagram generator."""
        self.pdf_gen = pdf_generator or get_pdf_generator()

    def generate_unifilar(
        self, project_data: Dict[str, Any], output_path: Path
    ) -> Path:
        """
        Generate Unifilar Diagram PDF.

        Args:
            project_data: Project data
            output_path: Output PDF path

        Returns:
            Path to generated PDF
        """
        context = {
            **project_data,
            "generation_date": datetime.now(),
            "diagram_type": "Diagrama Unifilar",
        }

        return self.pdf_gen.generate_pdf(
            template_name="diagram_unifilar.html",
            context=context,
            output_path=output_path,
            stylesheets=["diagram.css"],
        )

    def generate_layout(self, project_data: Dict[str, Any], output_path: Path) -> Path:
        """
        Generate Layout Diagram PDF.

        Args:
            project_data: Project data
            output_path: Output PDF path

        Returns:
            Path to generated PDF
        """
        context = {
            **project_data,
            "generation_date": datetime.now(),
            "diagram_type": "Diagrama de Layout",
        }

        return self.pdf_gen.generate_pdf(
            template_name="diagram_layout.html",
            context=context,
            output_path=output_path,
            stylesheets=["diagram.css"],
        )


def get_pdf_generator(templates_dir: Path = TEMPLATES_DIR):
    """
    Factory function to get the appropriate PDF generator.

    Returns WeasyPrint generator if available, otherwise ReportLab generator.

    Args:
        templates_dir: Directory containing Jinja2 templates

    Returns:
        PDF generator instance
    """
    if WEASYPRINT_AVAILABLE:
        logger.info("Using WeasyPrint PDF generator")
        return PDFGenerator(templates_dir)
    else:
        logger.info("WeasyPrint not available, using ReportLab PDF generator")
        return ReportLabPDFGenerator(templates_dir)
