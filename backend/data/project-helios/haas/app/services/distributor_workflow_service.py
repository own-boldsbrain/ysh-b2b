from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import asyncio
from sqlalchemy.orm import Session
from app.database.models import Distributor as DBDistributor, ConnectionRequest as DBConnectionRequest
from app.models.distributors import Distributor, ConnectionRequest, ConnectionResponse


class DistributorWorkflowService:
    """Service to handle distributor connection request workflows."""

    def __init__(self):
        pass

    def validate_request(self, request: ConnectionRequest) -> Dict[str, Any]:
        """Validate connection request data."""
        errors = []

        if request.power_requirement <= 0:
            errors.append("Power requirement must be greater than 0")

        if not request.location:
            errors.append("Location information is required")

        connection_types = ["residential", "commercial", "industrial"]
        if request.connection_type not in connection_types:
            errors.append(f"Invalid connection type. Must be one of: {', '.join(connection_types)}")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def process_inmetro_validation(self, request: ConnectionRequest) -> Optional[Dict[str, Any]]:
        """Process INMETRO validation if equipment data is provided."""
        if not request.equipment:
            return None

        try:
            from app.services.inmetro_validation_service import inmetro_validator
            validation_result = inmetro_validator.validate_equipment_batch(
                request.equipment, request
            )
            return validation_result
        except Exception as e:
            # Log validation error but allow request to proceed
            print(f"INMETRO validation error: {e}")
            return None

    def calculate_costs_and_requirements(self, distributor: Distributor, request: ConnectionRequest, inmetro_valid: bool) -> Dict[str, Any]:
        """Calculate estimated costs and requirements based on distributor and request."""
        # Simulate different processing times and costs based on distributor
        if distributor.code == "CPFL":
            estimated_cost = request.power_requirement * 150  # R$ 150/kW
            estimated_days = 15
        elif distributor.code == "ENEL_SP":
            estimated_cost = request.power_requirement * 180  # R$ 180/kW
            estimated_days = 20
        elif distributor.code == "CEMIG":
            estimated_cost = request.power_requirement * 140  # R$ 140/kW
            estimated_days = 18
        else:
            estimated_cost = request.power_requirement * 160  # Default
            estimated_days = 21

        # Basic validation requirements
        requirements = [
            "Comprovante de propriedade ou contrato de locação",
            "Projeto elétrico aprovado",
            "ART do responsável técnico",
            "Comprovante de pagamento da taxa de ligação"
        ]

        # Add INMETRO-specific requirements if equipment was validated and valid
        if inmetro_valid:
            requirements.extend([
                "Certificado INMETRO válido para todos os equipamentos",
                "Laudo de ensaio dos equipamentos",
                "Comprovante de conformidade com Portaria 140/2022"
            ])

        return {
            "estimated_cost": estimated_cost,
            "estimated_time_days": estimated_days,
            "requirements": requirements
        }

    def create_connection_response(self, request_id: str, status: str, cost_info: Dict[str, Any], rejection_reason: Optional[str] = None) -> ConnectionResponse:
        """Create a ConnectionResponse object."""
        return ConnectionResponse(
            request_id=request_id,
            status=status,
            estimated_cost=cost_info.get("estimated_cost"),
            estimated_time_days=cost_info.get("estimated_time_days"),
            requirements=cost_info.get("requirements", []),
            rejection_reason=rejection_reason,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def save_to_database(self, db: Session, distributor_id: int, request: ConnectionRequest, response: ConnectionResponse, inmetro_result: Optional[Dict[str, Any]], user_id: Optional[int] = None) -> DBConnectionRequest:
        """Save the connection request to the database."""
        db_connection_request = DBConnectionRequest(
            request_id=response.request_id,
            distributor_id=distributor_id,
            user_id=user_id,
            connection_type=request.connection_type,
            voltage_level=request.voltage_level,
            power_requirement=request.power_requirement,
            location=request.location,
            equipment=request.equipment,
            documents=request.documents,
            status=response.status,
            estimated_cost=response.estimated_cost,
            estimated_time_days=response.estimated_time_days,
            requirements=response.requirements,
            rejection_reason=response.rejection_reason,
            inmetro_validation_result=inmetro_result,
            inmetro_valid=inmetro_result["valid"] if inmetro_result else False
        )

        db.add(db_connection_request)
        db.commit()
        db.refresh(db_connection_request)
        return db_connection_request

    async def trigger_webhooks(self, event_type: str, request_id: str, distributor_id: int, connection_request: Dict[str, Any], status_change: Dict[str, Any]):
        """Trigger webhook events asynchronously."""
        try:
            from app.services.webhook_service import trigger_webhook_event
            await trigger_webhook_event(
                event_type=event_type,
                request_id=request_id,
                distributor_id=distributor_id,
                connection_request=connection_request,
                status_change=status_change
            )
        except Exception as e:
            # Log webhook error but don't fail the request
            print(f"Webhook trigger failed: {e}")

    async def execute_workflow(self, db: Session, distributor_id: int, request: ConnectionRequest, user_id: Optional[int] = None) -> ConnectionResponse:
        """Execute the complete distributor connection workflow."""
        # Get distributor
        from app.services.distributor_service import get_distributor_by_id
        distributor = get_distributor_by_id(db, distributor_id)
        if not distributor:
            raise ValueError(f"Distributor with ID {distributor_id} not found")

        # Step 1: Validate request
        validation = self.validate_request(request)
        if not validation["valid"]:
            # Return rejected response with validation errors
            cost_info = {"estimated_cost": None, "estimated_time_days": None, "requirements": []}
            response = self.create_connection_response(
                str(uuid.uuid4()), "rejected", cost_info,
                rejection_reason=f"Validation failed: {', '.join(validation['errors'])}"
            )
            return response

        # Step 2: Process INMETRO validation
        inmetro_result = self.process_inmetro_validation(request)
        if inmetro_result and not inmetro_result["valid"]:
            # INMETRO validation failed
            cost_info = {"estimated_cost": None, "estimated_time_days": None, "requirements": []}
            rejection_reason = (
                "INMETRO validation failed: " +
                "; ".join([
                    f"Equipment {r['equipment_index']}: {', '.join(r.get('errors', []))}"
                    for r in inmetro_result["results"]
                    if not r["valid"]
                ])
            )
            response = self.create_connection_response(str(uuid.uuid4()), "rejected", cost_info, rejection_reason)
            return response

        # Step 3: Calculate costs and requirements
        inmetro_valid = inmetro_result["valid"] if inmetro_result else False
        cost_info = self.calculate_costs_and_requirements(distributor, request, inmetro_valid)

        # Step 4: Create response
        request_id = str(uuid.uuid4())
        response = self.create_connection_response(request_id, "pending", cost_info)

        # Step 5: Save to database
        self.save_to_database(db, distributor_id, request, response, inmetro_result, user_id)

        # Step 6: Trigger webhooks asynchronously
        status_change = {
            "status": "pending",
            "message": "Connection request submitted",
            "inmetro_validation": inmetro_result
        }
        asyncio.create_task(
            self.trigger_webhooks(
                "connection_submitted", request_id, distributor_id,
                request.dict(), status_change
            )
        )

        return response
