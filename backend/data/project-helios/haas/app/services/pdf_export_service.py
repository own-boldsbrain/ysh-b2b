import io
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime

class PDFExportService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom styles for the PDF."""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )

        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.darkblue
        )

        self.normal_style = self.styles['Normal']

    async def generate_pdf(
        self,
        data: Dict[str, Any],
        template: str = "bacen_report",
        title: str = "Relatório HaaS"
    ) -> bytes:
        """Generate PDF from data using specified template."""
        buffer = io.BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build content based on template
        content = []

        # Add title
        content.append(Paragraph(title, self.title_style))
        content.append(Spacer(1, 12))

        # Add generation timestamp
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        content.append(Paragraph(f"Gerado em: {timestamp}", self.normal_style))
        content.append(Spacer(1, 20))

        # Generate content based on template
        if template == "bacen_report":
            content.extend(self._generate_bacen_report(data))
        elif template == "homologation_status":
            content.extend(self._generate_homologation_report(data))
        elif template == "compliance_report":
            content.extend(self._generate_compliance_report(data))
        else:
            content.extend(self._generate_generic_report(data))

        # Build PDF
        doc.build(content)
        buffer.seek(0)
        return buffer.getvalue()

    def _generate_bacen_report(self, data: Dict[str, Any]) -> list:
        """Generate BACEN economic data report."""
        content = []

        content.append(Paragraph("Dados Econômicos - BACEN", self.section_style))
        content.append(Spacer(1, 12))

        # Create table data
        table_data = [
            ["Indicador", "Valor", "Data", "Variação"]
        ]

        if "selic_rate" in data:
            table_data.append([
                "Taxa SELIC",
                f"{data.get('selic_rate', 'N/A')}%",
                data.get('date', 'N/A'),
                self._calculate_variation(data, 'selic')
            ])

        if "cdi_rate" in data:
            table_data.append([
                "Taxa CDI",
                f"{data.get('cdi_rate', 'N/A')}%",
                data.get('date', 'N/A'),
                self._calculate_variation(data, 'cdi')
            ])

        if "spread" in data:
            table_data.append([
                "Spread SELIC-CDI",
                f"{data.get('spread', 'N/A')} p.p.",
                data.get('date', 'N/A'),
                "N/A"
            ])

        # Create table
        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        content.append(table)
        content.append(Spacer(1, 20))

        # Add analysis
        if "change_significant" in data and data["change_significant"]:
            content.append(Paragraph(
                "⚠️ Mudanças significativas detectadas nas taxas de juros.",
                self.normal_style
            ))

        return content

    def _generate_homologation_report(self, data: Dict[str, Any]) -> list:
        """Generate homologation status report."""
        content = []

        content.append(Paragraph("Status de Homologação", self.section_style))
        content.append(Spacer(1, 12))

        # Summary statistics
        total_projects = data.get('total_projects', 0)
        approved = data.get('approved', 0)
        rejected = data.get('rejected', 0)
        pending = data.get('pending', 0)

        content.append(Paragraph(f"Total de Projetos: {total_projects}", self.normal_style))
        content.append(Paragraph(f"Aprovados: {approved}", self.normal_style))
        content.append(Paragraph(f"Rejeitados: {rejected}", self.normal_style))
        content.append(Paragraph(f"Pendentes: {pending}", self.normal_style))
        content.append(Spacer(1, 20))

        # Projects table
        if "projects" in data:
            table_data = [
                ["ID do Projeto", "Cliente", "Status", "Distribuidora", "Data de Submissão"]
            ]

            for project in data["projects"][:20]:  # Limit to 20 projects
                table_data.append([
                    project.get('id', 'N/A'),
                    project.get('client_name', 'N/A'),
                    project.get('status', 'N/A'),
                    project.get('distributor', 'N/A'),
                    project.get('submitted_date', 'N/A')
                ])

            table = Table(table_data, colWidths=[1*inch, 1.5*inch, 1*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            content.append(table)

        return content

    def _generate_compliance_report(self, data: Dict[str, Any]) -> list:
        """Generate compliance monitoring report."""
        content = []

        content.append(Paragraph("Relatório de Conformidade INMETRO/ANEEL", self.section_style))
        content.append(Spacer(1, 12))

        # Compliance issues
        if "compliance_issues" in data:
            content.append(Paragraph("Problemas de Conformidade:", self.section_style))
            content.append(Spacer(1, 6))

            for issue in data["compliance_issues"][:10]:  # Limit to 10 issues
                severity = "🔴 CRÍTICO" if issue.get('severity') == 'high' else "🟡 MÉDIO"
                content.append(Paragraph(
                    f"{severity}: {issue.get('issue', 'N/A')} (Equipamento: {issue.get('model', 'N/A')})",
                    self.normal_style
                ))
                content.append(Spacer(1, 6))

        # Regulatory updates
        if "regulation_updates" in data:
            content.append(Paragraph("Atualizações Regulatórias:", self.section_style))
            content.append(Spacer(1, 6))

            for update in data["regulation_updates"][:5]:  # Limit to 5 updates
                content.append(Paragraph(
                    f"{update.get('title', 'N/A')} - {update.get('publication_date', 'N/A')}",
                    self.normal_style
                ))
                content.append(Spacer(1, 6))

        return content

    def _generate_generic_report(self, data: Dict[str, Any]) -> list:
        """Generate generic report from data."""
        content = []

        content.append(Paragraph("Relatório de Dados", self.section_style))
        content.append(Spacer(1, 12))

        # Convert data to formatted text
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                content.append(Paragraph(f"{key}:", self.normal_style))
                content.append(Paragraph(str(value), self.normal_style))
            else:
                content.append(Paragraph(f"{key}: {value}", self.normal_style))
            content.append(Spacer(1, 6))

        return content

    def _calculate_variation(self, data: Dict[str, Any], indicator: str) -> str:
        """Calculate variation for economic indicators."""
        # This would typically compare with historical data
        # For now, return placeholder
        return "N/A"