from sqlalchemy.orm import Session
from ..schemas.journey import (
    EconomySimulationRequest,
    EconomySimulationResponse,
    PaybackCalculationRequest,
    PaybackCalculationResponse,
    ProjectValidationRequest,
    ProjectValidationResponse,
    ProjectSubmissionRequest,
    ProjectSubmissionResponse,
    StatusMonitoringRequest,
    StatusMonitoringResponse,
)
from ..validators.inmetro import INMETROValidator
import uuid
from datetime import datetime


class JourneyService:
    def __init__(self, db: Session):
        self.db = db
        self.inmetro_validator = INMETROValidator()

    def simulate_economy(
        self, segment: str, request: EconomySimulationRequest
    ) -> EconomySimulationResponse:
        """Simula economia baseada no segmento e dados fornecidos"""
        # Lógica básica de simulação - pode ser refinada por segmento
        generation_factor = {
            "residential": 0.85,  # Fator de geração para residencial
            "commercial": 0.80,
            "industrial": 0.75,
            "rural": 0.70,
        }.get(segment, 0.80)

        monthly_generation = (
            request.capacity_kw * 30 * generation_factor
        )  # kWh/mês aproximado
        monthly_savings = (
            min(monthly_generation, request.monthly_consumption_kwh) * 0.8
        )  # R$/mês (estimativa)
        annual_savings = monthly_savings * 12
        total_investment = request.capacity_kw * 8000  # R$ 8.000/kW estimado
        payback_years = total_investment / annual_savings if annual_savings > 0 else 0
        roi_percentage = (
            (annual_savings / total_investment) * 100 if total_investment > 0 else 0
        )

        return EconomySimulationResponse(
            monthly_savings=monthly_savings,
            annual_savings=annual_savings,
            payback_years=payback_years,
            total_investment=total_investment,
            roi_percentage=roi_percentage,
        )

    def calculate_payback(
        self, segment: str, request: PaybackCalculationRequest
    ) -> PaybackCalculationResponse:
        """Calcula payback detalhado"""
        # Implementação simplificada - em produção, usar bibliotecas financeiras
        monthly_savings = (
            request.monthly_consumption_kwh * request.electricity_cost_per_kwh * 0.9
        )  # 90% economia
        annual_savings = monthly_savings * 12

        # Projeção de 25 anos
        cash_flow = []
        cumulative = -request.investment_cost
        for year in range(1, 26):
            annual_savings_year = annual_savings * (1 - request.degradation_rate) ** (
                year - 1
            )
            cumulative += annual_savings_year
            cash_flow.append(
                {"year": year, "savings": annual_savings_year, "cumulative": cumulative}
            )
            if cumulative >= 0 and year == 1:
                payback_period = (
                    year - (cumulative - annual_savings_year) / annual_savings_year
                )

        payback_period_years = next(
            (
                cf["year"] - (cf["cumulative"] - cf["savings"]) / cf["savings"]
                for cf in cash_flow
                if cf["cumulative"] >= 0
            ),
            25,
        )

        # NPV e IRR simplificados
        discount_rate = 0.08  # 8%
        npv = (
            sum(cf["savings"] / (1 + discount_rate) ** cf["year"] for cf in cash_flow)
            - request.investment_cost
        )
        irr = 0.10  # Estimativa simplificada

        return PaybackCalculationResponse(
            payback_period_years=payback_period_years,
            net_present_value=npv,
            internal_rate_return=irr,
            cash_flow_projection=cash_flow,
        )

    def validate_project(
        self, segment: str, request: ProjectValidationRequest
    ) -> ProjectValidationResponse:
        """Valida projeto preliminar"""
        errors = []
        warnings = []
        required_docs = ["ART", "Memorial Descritivo", "Diagrama Unifilar"]

        # Validação básica de capacidade por segmento
        capacity_limits = {
            "residential": (2, 15),  # kWp
            "commercial": (10, 500),
            "industrial": (50, 2000),
            "rural": (5, 200),
        }

        min_cap, max_cap = capacity_limits.get(segment, (0, 1000))
        if not (min_cap <= request.capacity_kw <= max_cap):
            errors.append(
                f"Capacidade fora do range típico para {segment}: {min_cap}-{max_cap} kWp"
            )

        # Validação INMETRO dos equipamentos
        for equipment in request.equipment_list:
            if not self.inmetro_validator.validate_equipment(equipment):
                errors.append(
                    f"Equipamento não certificado INMETRO: {equipment.get('modelo', 'N/A')}"
                )

        # Verificações específicas por segmento
        if segment == "industrial" and request.capacity_kw > 500:
            warnings.append(
                "Projetos acima de 500 kWp podem enfrentar restrições GD III"
            )

        if segment == "rural":
            required_docs.append("Declaração de Aptidão ao Pronaf")

        estimated_days = {
            "residential": 15,
            "commercial": 20,
            "industrial": 30,
            "rural": 25,
        }.get(segment, 20)

        return ProjectValidationResponse(
            is_valid=len(errors) == 0,
            validation_errors=errors,
            warnings=warnings,
            estimated_approval_time_days=estimated_days,
            required_documents=required_docs,
        )

    def submit_project(
        self, segment: str, request: ProjectSubmissionRequest
    ) -> ProjectSubmissionResponse:
        """Submete projeto para homologação"""
        project_id = str(uuid.uuid4())

        # Lógica de submissão - em produção, integrar com distribuidoras
        # Por enquanto, simula submissão

        protocol_number = f"2025{project_id[:8].upper()}"

        next_steps = [
            "Aguardar validação inicial",
            "Preparar documentação completa",
            "Agendar vistoria técnica",
        ]

        if request.financing_required:
            next_steps.insert(0, "Processar análise de crédito")

        return ProjectSubmissionResponse(
            project_id=project_id,
            submission_status="submitted",
            protocol_number=protocol_number,
            estimated_completion_days=30,
            next_steps=next_steps,
        )

    def monitor_status(
        self, segment: str, request: StatusMonitoringRequest
    ) -> StatusMonitoringResponse:
        """Monitora status do projeto"""
        # Simulação - em produção, consultar banco de dados
        status_history = [
            {
                "date": "2025-10-01",
                "status": "submitted",
                "description": "Projeto submetido",
            },
            {
                "date": "2025-10-05",
                "status": "under_review",
                "description": "Em análise técnica",
            },
            {
                "date": "2025-10-10",
                "status": "approved",
                "description": "Aprovado para vistoria",
            },
        ]

        current_status = status_history[-1]["status"]
        completion_percentage = 75.0  # Simulado
        issues = [] if current_status == "approved" else ["Aguardando vistoria"]
        next_actions = (
            ["Agendar data de instalação"]
            if current_status == "approved"
            else ["Aguardar contato da distribuidora"]
        )

        return StatusMonitoringResponse(
            project_id=request.project_id,
            current_status=current_status,
            status_history=status_history,
            completion_percentage=completion_percentage,
            issues=issues,
            next_actions=next_actions,
            last_updated=datetime.now(),
        )


class MockINMETROValidator:
    def validate_equipment(self, equipment):
        # Mock validation - always return True for now
        return True
