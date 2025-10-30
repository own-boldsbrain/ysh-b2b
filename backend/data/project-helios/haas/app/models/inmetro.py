"""INMETRO validation models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ValidationStatusEnum(str, Enum):
    """Status of validation request."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ValidationError(BaseModel):
    """Validation error detail."""

    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")


class ValidationWarning(BaseModel):
    """Validation warning detail."""

    field: str = Field(..., description="Field with warning")
    message: str = Field(..., description="Warning message")
    code: Optional[str] = Field(None, description="Warning code")


class ValidationStatus(BaseModel):
    """INMETRO validation status."""

    request_id: str = Field(..., description="Unique request ID")
    status: ValidationStatusEnum = Field(..., description="Validation status")

    # Equipment data
    equipment_type: Optional[str] = Field(None, description="Type of equipment")
    model: Optional[str] = Field(None, description="Equipment model")
    manufacturer: Optional[str] = Field(None, description="Manufacturer name")
    certification_number: Optional[str] = Field(
        None, description="INMETRO certification number"
    )

    # Validation results
    valid: bool = Field(False, description="Overall validation result")
    errors: List[ValidationError] = Field(
        default_factory=list, description="Validation errors"
    )
    warnings: List[ValidationWarning] = Field(
        default_factory=list, description="Validation warnings"
    )

    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Request creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    # Additional data
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}
