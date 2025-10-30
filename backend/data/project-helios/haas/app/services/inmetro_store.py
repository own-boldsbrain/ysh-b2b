"""INMETRO validation storage using Redis cache."""

import json
import logging
from typing import Optional
from app.services.redis_service import redis_service
from app.models.inmetro import ValidationStatus

logger = logging.getLogger(__name__)


class InmetroValidationStore:
    """
    Redis-backed storage for INMETRO validation requests.

    Keys: validation:{request_id}
    TTL: 86400s (24 hours) for completed validations
    """

    KEY_PREFIX = "validation"
    COMPLETED_TTL = 86400  # 24 hours
    IN_PROGRESS_TTL = 3600  # 1 hour

    @classmethod
    def _build_key(cls, request_id: str) -> str:
        """Build Redis key for validation request."""
        return f"{cls.KEY_PREFIX}:{request_id}"

    @classmethod
    def save(cls, request_id: str, status: ValidationStatus) -> bool:
        """
        Save validation status to Redis.

        Args:
            request_id: Unique validation request ID
            status: ValidationStatus object

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            key = cls._build_key(request_id)
            value = status.model_dump_json()

            # Set TTL based on status
            ttl = (
                cls.COMPLETED_TTL
                if status.status in ["completed", "failed"]
                else cls.IN_PROGRESS_TTL
            )

            success = redis_service.set(key, value, expires_in=ttl)
            if success:
                logger.info("Saved validation %s with TTL %ds", request_id, ttl)
            return success
        except Exception as exc:
            logger.error("Failed to save validation %s: %s", request_id, exc)
            return False

    @classmethod
    def get(cls, request_id: str) -> Optional[ValidationStatus]:
        """
        Get validation status from Redis.

        Args:
            request_id: Validation request ID

        Returns:
            ValidationStatus object or None if not found
        """
        try:
            key = cls._build_key(request_id)
            value = redis_service.get(key)

            if value is None:
                logger.debug("Validation %s not found in cache", request_id)
                return None

            # Parse JSON to ValidationStatus
            data = json.loads(value)
            return ValidationStatus(**data)
        except Exception as exc:
            logger.error("Failed to get validation %s: %s", request_id, exc)
            return None

    @classmethod
    def delete(cls, request_id: str) -> bool:
        """
        Delete validation from Redis.

        Args:
            request_id: Validation request ID

        Returns:
            True if deleted, False otherwise
        """
        try:
            key = cls._build_key(request_id)
            success = redis_service.delete(key)
            if success:
                logger.info("Deleted validation %s", request_id)
            return success
        except Exception as exc:
            logger.error("Failed to delete validation %s: %s", request_id, exc)
            return False

    @classmethod
    def exists(cls, request_id: str) -> bool:
        """
        Check if validation exists in Redis.

        Args:
            request_id: Validation request ID

        Returns:
            True if exists, False otherwise
        """
        key = cls._build_key(request_id)
        return redis_service.exists(key)
