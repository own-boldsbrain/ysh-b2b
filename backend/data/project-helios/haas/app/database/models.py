"""Database models for HaaS Platform."""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    Date,
    Text,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry
from app.database import Base


class Distributor(Base):
    """Database model for distributors."""
    __tablename__ = "distributors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(50))
    service_area: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON
    )  # GeoJSON polygon
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    connection_requests: Mapped[List["ConnectionRequest"]] = relationship(
        "ConnectionRequest", back_populates="distributor"
    )


class User(Base):
    """Database model for users (distributors and admins)."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), default="distributor"
    )  # distributor, admin
    distributor_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("distributors.id"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    distributor: Mapped[Optional[Distributor]] = relationship("Distributor")


class ConnectionRequest(Base):
    """Database model for connection requests."""
    __tablename__ = "connection_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, index=True
    )
    distributor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("distributors.id"), nullable=False, index=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )

    # Connection details
    connection_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # residential, commercial, industrial
    voltage_level: Mapped[str] = mapped_column(String(50), nullable=False)
    power_requirement: Mapped[float] = mapped_column(
        Float, nullable=False
    )  # in kW

    # Location with PostGIS geometry
    location: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON
    )  # GeoJSON point
    location_geom: Mapped[Optional[str]] = mapped_column(
        Geometry('POINT', srid=4326), nullable=True
    )

    # Equipment and documents
    equipment: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        JSON
    )  # INMETRO equipment data
    documents: Mapped[Optional[List[str]]] = mapped_column(
        JSON
    )  # Document URLs/IDs

    # Status and processing
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending, approved, rejected, in_progress, completed
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float)
    estimated_time_days: Mapped[Optional[int]] = mapped_column(Integer)
    requirements: Mapped[Optional[List[str]]] = mapped_column(JSON)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # INMETRO validation results
    inmetro_validation_result: Mapped[Optional[Dict[str, Any]]] = (
        mapped_column(JSON)
    )
    inmetro_valid: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    distributor: Mapped[Distributor] = relationship(
        "Distributor", back_populates="connection_requests"
    )
    user: Mapped[Optional[User]] = relationship("User")


class WebhookConfig(Base):
    """Database model for webhook configurations."""
    __tablename__ = "webhook_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # HMAC secret
    event_types: Mapped[List[str]] = mapped_column(
        JSON, nullable=False
    )  # Events to trigger
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    deliveries: Mapped[List["WebhookDelivery"]] = relationship(
        "WebhookDelivery", back_populates="config"
    )


class WebhookDelivery(Base):
    """Database model for webhook delivery attempts."""
    __tablename__ = "webhook_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    config_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("webhook_configs.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    signature: Mapped[str] = mapped_column(String(255), nullable=False)

    # Delivery status
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )  # pending, delivered, failed, retrying
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)

    # Response details
    response_status: Mapped[Optional[int]] = mapped_column(Integer)
    response_body: Mapped[Optional[str]] = mapped_column(Text)
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    config: Mapped[WebhookConfig] = relationship(
        "WebhookConfig", back_populates="deliveries"
    )


class EquipmentRecord(Base):
    """Database model for INMETRO equipment records."""

    __tablename__ = "equipment_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    categoria: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    fabricante: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    modelo: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    familia: Mapped[Optional[str]] = mapped_column(String(255))

    # Certification info
    normas_ensaios: Mapped[Optional[List[str]]] = mapped_column(JSON)
    ocp: Mapped[Optional[str]] = mapped_column(String(255))
    certificado_numero: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    registro_inmetro: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    laboratorio_ensaio: Mapped[Optional[str]] = mapped_column(String(255))
    data_emissao: Mapped[Optional[date]] = mapped_column(Date)
    data_validade: Mapped[Optional[date]] = mapped_column(Date)

    # Datasheet info
    atributos_tecnicos: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    arquivos_datasheet: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Raw data
    raw_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # Metadata
    fonte: Mapped[str] = mapped_column(String(50), default="INMETRO")
    ultima_atualizacao: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    responsavel: Mapped[Optional[str]] = mapped_column(String(255))
    extra_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def is_valid(self, as_of: Optional[date] = None) -> bool:
        """Check if certification is valid on given date."""
        check_date = as_of or date.today()
        if not self.data_validade:
            return False
        return self.data_validade >= check_date


class DataRecord(Base):
    """Database model for general data provider records."""

    __tablename__ = "data_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    record_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    data_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Metadata
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    record_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # Processing status
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class CrawlerData(Base):
    """Database model for crawler-collected data (ANEEL datasets, etc.)."""

    __tablename__ = "crawler_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # 'aneel', 'bacen', etc.
    dataset_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Metadata
    collection_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    url: Mapped[Optional[str]] = mapped_column(String(500))
    file_path: Mapped[Optional[str]] = mapped_column(
        String(500)
    )  # Local file path if downloaded
    file_size: Mapped[Optional[int]] = mapped_column(Integer)  # Size in bytes

    # Processing status
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, processing, completed, failed
    processing_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text)

    # Data quality
    record_count: Mapped[Optional[int]] = mapped_column(Integer)
    data_quality_score: Mapped[Optional[float]] = mapped_column(Float)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
