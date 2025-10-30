"""
INMETRO Validator Module

This module provides validation functionality for INMETRO equipment certifications
used in solar energy projects.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class INMETROValidator:
    """
    Validator for INMETRO equipment certifications.

    This class handles validation of equipment certifications against INMETRO
    standards for solar energy projects.
    """

    def __init__(self):
        """Initialize the INMETRO validator."""
        self.logger = logging.getLogger(__name__)

    def validate_equipment(self, equipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate equipment certification data.

        Args:
            equipment_data: Dictionary containing equipment information including
                          certification details, model, manufacturer, etc.

        Returns:
            Dictionary with validation results containing:
            - valid: Boolean indicating if validation passed
            - errors: List of validation errors if any
            - warnings: List of validation warnings if any
        """
        errors = []
        warnings = []

        # Basic validation checks
        required_fields = ["model", "manufacturer", "certification_number"]
        for field in required_fields:
            if field not in equipment_data or not equipment_data[field]:
                errors.append(f"Missing required field: {field}")

        # Certification number format validation
        cert_number = equipment_data.get("certification_number", "")
        if cert_number and not self._is_valid_certification_format(cert_number):
            warnings.append("Certification number format may be invalid")

        # Equipment type validation
        equipment_type = equipment_data.get("type", "")
        if equipment_type and equipment_type not in [
            "inverter",
            "panel",
            "battery",
            "cable",
        ]:
            warnings.append(f"Unknown equipment type: {equipment_type}")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _is_valid_certification_format(self, cert_number: str) -> bool:
        """
        Check if certification number follows expected format.

        Args:
            cert_number: The certification number to validate

        Returns:
            True if format is valid, False otherwise
        """
        # Basic format check - INMETRO certifications typically have specific patterns
        # This is a simplified check - in production this would be more comprehensive
        if not cert_number or len(cert_number) < 5:
            return False

        # Check for common INMETRO patterns
        return any(
            pattern in cert_number.upper() for pattern in ["INMETRO", "CERT", "ISO"]
        )

    def get_certification_requirements(self, equipment_type: str) -> Dict[str, Any]:
        """
        Get certification requirements for a specific equipment type.

        Args:
            equipment_type: Type of equipment (inverter, panel, etc.)

        Returns:
            Dictionary with certification requirements
        """
        requirements = {
            "inverter": {
                "required_certifications": ["INMETRO", "IEC 62109"],
                "efficiency_standard": "IEC 61683",
                "safety_standard": "IEC 62109-1",
            },
            "panel": {
                "required_certifications": ["INMETRO", "IEC 61215", "IEC 61730"],
                "power_tolerance": "±3%",
                "safety_standard": "IEC 61730",
            },
            "battery": {
                "required_certifications": ["INMETRO", "IEC 62619"],
                "capacity_standard": "IEC 61427",
                "safety_standard": "IEC 62133",
            },
            "cable": {
                "required_certifications": ["INMETRO", "NBR 13249"],
                "voltage_rating": "1000V DC",
                "flame_retardant": True,
            },
        }

        return requirements.get(equipment_type, {})
