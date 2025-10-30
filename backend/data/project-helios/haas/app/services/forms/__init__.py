"""
Forms module for utility-specific form management.

This module provides:
- UtilityFormsManager: Core service for managing utility forms
- FormTemplateRenderer: HTML template rendering for forms
- Form definitions and validations for CPFL, Enel, and CEMIG
"""

from ..utility_forms_manager import (
    UtilityFormsManager,
    FormType,
    FormField,
    FormAttachment,
    UtilityForm,
)
from .template_renderer import FormTemplateRenderer

__all__ = [
    "UtilityFormsManager",
    "FormTemplateRenderer",
    "FormType",
    "FormField",
    "FormAttachment",
    "UtilityForm",
]
