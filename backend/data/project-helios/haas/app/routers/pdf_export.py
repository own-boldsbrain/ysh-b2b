from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel
from app.services.pdf_export_service import PDFExportService
from app.models.auth import User
from app.auth.dependencies import get_current_user

router = APIRouter()


class PDFExportRequest(BaseModel):
    data: Dict[str, Any]
    template: str = "bacen_report"
    title: str = "Relatório HaaS"


@router.post("/export")
async def export_pdf(
    request: PDFExportRequest,
    # current_user: User = Depends(get_current_user)
):
    """Export data to PDF format."""
    try:
        pdf_service = PDFExportService()
        pdf_bytes = await pdf_service.generate_pdf(
            data=request.data, template=request.template, title=request.title
        )

        return {
            "status": "success",
            "pdf_size": len(pdf_bytes),
            "content_type": "application/pdf",
            "filename": f"{request.title.replace(' ', '_')}.pdf",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.get("/templates")
async def list_templates(
    # current_user: User = Depends(get_current_user)
):
    """List available PDF templates."""
    return {
        "templates": [
            {
                "id": "bacen_report",
                "name": "Relatório BACEN",
                "description": "Relatório de dados econômicos do BACEN",
            },
            {
                "id": "homologation_status",
                "name": "Status de Homologação",
                "description": "Relatório de status de projetos de homologação",
            },
            {
                "id": "compliance_report",
                "name": "Relatório de Conformidade",
                "description": "Relatório de conformidade INMETRO/ANEEL",
            },
        ]
    }
