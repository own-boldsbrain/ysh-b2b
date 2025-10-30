"""
Utility Forms Manager - Gerencia formulários específicos de concessionárias

Implementa mapeamentos completos para CPFL, Enel SP e CEMIG,
com validações de campos, templates e regras de negócio.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class FormType(str, Enum):
    """Tipos de formulários por concessionária."""

    SOLICITACAO_ACESSO = "solicitacao_acesso"
    COMPLEMENTACAO_INFORMACOES = "complementacao_informacoes"
    SOLICITACAO_VISTORIA = "solicitacao_vistoria"
    ALTERACAO_PROJETO = "alteracao_projeto"


class FieldType(str, Enum):
    """Tipos de campos de formulário."""

    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DATE = "date"
    EMAIL = "email"
    TEL = "tel"
    CPF_CNPJ = "cpf_cnpj"
    CEP = "cep"
    ADDRESS = "address"
    FILE = "file"


@dataclass
class FormField:
    """Definição de campo de formulário."""

    name: str
    label: str
    type: FieldType
    required: bool = False
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None
    options: Optional[List[Dict[str, str]]] = None  # Para select/radio
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    mask: Optional[str] = None  # Para formatação (ex: CPF)
    depends_on: Optional[str] = None  # Campo dependente


@dataclass
class FormAttachment:
    """Definição de anexo obrigatório."""

    name: str
    label: str
    required: bool = True
    max_size_mb: int = 5
    allowed_types: List[str] = field(default_factory=lambda: ["application/pdf"])
    help_text: Optional[str] = None


@dataclass
class UtilityForm:
    """Definição completa de formulário de concessionária."""

    utility_code: str
    form_type: FormType
    title: str
    description: str
    url: str
    method: str = "POST"
    enctype: str = "multipart/form-data"
    fields: List[FormField] = field(default_factory=list)
    attachments: List[FormAttachment] = field(default_factory=list)
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    quirks: Dict[str, Any] = field(default_factory=dict)  # Particularidades específicas


class UtilityFormsManager:
    """Gerenciador de formulários de concessionárias."""

    def __init__(self):
        self.forms: Dict[str, Dict[FormType, UtilityForm]] = {}
        self._load_forms()

    def _load_forms(self):
        """Carrega definições de formulários."""
        self.forms = {
            "CPFL": self._get_cpfl_forms(),
            "ENEL": self._get_enel_forms(),
            "CEMIG": self._get_cemig_forms(),
        }

    def get_form(self, utility_code: str, form_type: FormType) -> Optional[UtilityForm]:
        """Retorna formulário específico."""
        utility_forms = self.forms.get(utility_code.upper())
        if utility_forms:
            return utility_forms.get(form_type)
        return None

    def get_available_forms(self, utility_code: str) -> List[FormType]:
        """Retorna tipos de formulários disponíveis para uma concessionária."""
        utility_forms = self.forms.get(utility_code.upper())
        return list(utility_forms.keys()) if utility_forms else []

    def validate_form_data(
        self, utility_code: str, form_type: FormType, form_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valida dados de formulário contra regras da concessionária.

        Returns:
            Dict com 'valid': bool, 'errors': List[str], 'warnings': List[str]
        """
        form = self.get_form(utility_code, form_type)
        if not form:
            return {
                "valid": False,
                "errors": [
                    f"Formulário {form_type} não encontrado para {utility_code}"
                ],
                "warnings": [],
            }

        errors = []
        warnings = []

        # Valida campos obrigatórios
        for field in form.fields:
            if field.required:
                value = form_data.get(field.name)
                if value is None or (isinstance(value, str) and not value.strip()):
                    errors.append(f"Campo obrigatório: {field.label}")

        # Validações específicas por campo
        for field in form.fields:
            value = form_data.get(field.name)
            if value is not None:
                field_errors = self._validate_field(field, value)
                errors.extend(field_errors)

        # Validações de negócio específicas da concessionária
        business_errors = self._validate_business_rules(
            utility_code, form_type, form_data
        )
        errors.extend(business_errors)

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def _validate_field(self, field: FormField, value: Any) -> List[str]:
        """Valida valor de campo individual."""
        errors = []

        if field.type == FieldType.NUMBER:
            try:
                num_value = float(value)
                if field.min_value is not None and num_value < field.min_value:
                    errors.append(f"{field.label}: valor mínimo é {field.min_value}")
                if field.max_value is not None and num_value > field.max_value:
                    errors.append(f"{field.label}: valor máximo é {field.max_value}")
            except (ValueError, TypeError):
                errors.append(f"{field.label}: deve ser um número válido")

        elif field.type == FieldType.TEXT and field.max_length:
            if len(str(value)) > field.max_length:
                errors.append(f"{field.label}: máximo {field.max_length} caracteres")

        elif field.type == FieldType.EMAIL:
            import re

            if not re.match(r"[^@]+@[^@]+\.[^@]+", str(value)):
                errors.append(f"{field.label}: email inválido")

        elif field.type == FieldType.CPF_CNPJ:
            if not self._validate_cpf_cnpj(str(value)):
                errors.append(f"{field.label}: CPF/CNPJ inválido")

        elif field.type == FieldType.CEP:
            if not self._validate_cep(str(value)):
                errors.append(f"{field.label}: CEP inválido")

        return errors

    def _validate_business_rules(
        self, utility_code: str, form_type: FormType, form_data: Dict[str, Any]
    ) -> List[str]:
        """Valida regras de negócio específicas da concessionária."""
        errors = []

        if utility_code.upper() == "CPFL":
            errors.extend(self._validate_cpfl_rules(form_type, form_data))
        elif utility_code.upper() == "ENEL":
            errors.extend(self._validate_enel_rules(form_type, form_data))
        elif utility_code.upper() == "CEMIG":
            errors.extend(self._validate_cemig_rules(form_type, form_data))

        return errors

    def _validate_cpfl_rules(
        self, form_type: FormType, form_data: Dict[str, Any]
    ) -> List[str]:
        """Regras específicas CPFL."""
        errors = []

        if form_type == FormType.SOLICITACAO_ACESSO:
            potencia = form_data.get("potencia_instalada_kw")
            if potencia and potencia > 5000:
                errors.append("CPFL: Potência máxima permitida é 5 MW (5000 kW)")

            # CPFL requer complemento de endereço
            endereco = form_data.get("endereco_instalacao", {})
            if not endereco.get("complemento"):
                errors.append("CPFL: Complemento do endereço é obrigatório")

        return errors

    def _validate_enel_rules(
        self, form_type: FormType, form_data: Dict[str, Any]
    ) -> List[str]:
        """Regras específicas Enel."""
        errors = []

        if form_type == FormType.SOLICITACAO_ACESSO:
            modalidade = form_data.get("modalidade_compensacao")
            if modalidade == "autoconsumo_remoto":
                errors.append("Enel: Autoconsumo remoto não disponível nesta região")

        return errors

    def _validate_cemig_rules(
        self, form_type: FormType, form_data: Dict[str, Any]
    ) -> List[str]:
        """Regras específicas CEMIG."""
        errors = []

        if form_type == FormType.SOLICITACAO_ACESSO:
            potencia = form_data.get("potencia_instalada_kw")
            if potencia and potencia < 10:
                errors.append("CEMIG: Potência mínima para GD é 10 kW")

        return errors

    def _validate_cpf_cnpj(self, value: str) -> bool:
        """Valida CPF ou CNPJ."""
        # Remove caracteres não numéricos
        value = "".join(filter(str.isdigit, value))

        if len(value) == 11:  # CPF
            return self._validate_cpf(value)
        elif len(value) == 14:  # CNPJ
            return self._validate_cnpj(value)
        return False

    def _validate_cpf(self, cpf: str) -> bool:
        """Valida CPF."""
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        def calc_digit(cpf_slice: str, factor: int) -> int:
            total = sum(
                int(digit) * factor
                for digit, factor in zip(cpf_slice, range(factor, 1, -1))
            )
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder

        return calc_digit(cpf[:9], 10) == int(cpf[9]) and calc_digit(
            cpf[:10], 11
        ) == int(cpf[10])

    def _validate_cnpj(self, cnpj: str) -> bool:
        """Valida CNPJ."""
        if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
            return False

        def calc_digit(cnpj_slice: str, factor: int) -> int:
            total = sum(
                int(digit) * factor
                for digit, factor in zip(cnpj_slice, range(factor, 1, -1))
            )
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder

        return calc_digit(cnpj[:12], 5) == int(cnpj[12]) and calc_digit(
            cnpj[:13], 6
        ) == int(cnpj[13])

    def _validate_cep(self, cep: str) -> bool:
        """Valida CEP brasileiro."""
        cep = "".join(filter(str.isdigit, cep))
        return len(cep) == 8

    # ========================================
    # DEFINIÇÕES DE FORMULÁRIOS POR CONCESSIONÁRIA
    # ========================================

    def _get_cpfl_forms(self) -> Dict[FormType, UtilityForm]:
        """Formulários CPFL Paulista."""
        return {
            FormType.SOLICITACAO_ACESSO: UtilityForm(
                utility_code="CPFL",
                form_type=FormType.SOLICITACAO_ACESSO,
                title="Solicitação de Acesso - CPFL Paulista",
                description="Formulário para solicitação de acesso à rede de distribuição",
                url="https://servicosonline.cpfl.com.br/agencia-webapp/solicitar-acesso",
                fields=[
                    FormField(
                        name="nome_solicitante",
                        label="Nome do Solicitante",
                        type=FieldType.TEXT,
                        required=True,
                        max_length=100,
                    ),
                    FormField(
                        name="cpf_cnpj",
                        label="CPF/CNPJ",
                        type=FieldType.CPF_CNPJ,
                        required=True,
                        mask="999.999.999-99",
                    ),
                    FormField(
                        name="numero_cliente",
                        label="Número do Cliente",
                        type=FieldType.TEXT,
                        required=True,
                        max_length=10,
                        help_text="Número da conta de energia",
                    ),
                    FormField(
                        name="endereco_instalacao",
                        label="Endereço de Instalação",
                        type=FieldType.ADDRESS,
                        required=True,
                    ),
                    FormField(
                        name="potencia_instalada_kw",
                        label="Potência Instalada (kW)",
                        type=FieldType.NUMBER,
                        required=True,
                        min_value=0,
                        max_value=5000,
                        help_text="Potência total do sistema fotovoltaico",
                    ),
                    FormField(
                        name="tipo_geracao",
                        label="Tipo de Geração",
                        type=FieldType.SELECT,
                        required=True,
                        options=[
                            {
                                "value": "solar_fotovoltaica",
                                "label": "Solar Fotovoltaica",
                            },
                            {"value": "eolica", "label": "Eólica"},
                            {"value": "hibrida", "label": "Híbrida"},
                        ],
                    ),
                    FormField(
                        name="modalidade_compensacao",
                        label="Modalidade de Compensação",
                        type=FieldType.SELECT,
                        required=True,
                        options=[
                            {
                                "value": "mesma_unidade",
                                "label": "Mesma Unidade Consumidora",
                            },
                            {
                                "value": "empreendimento_multiplo",
                                "label": "Empreendimento Múltiplo",
                            },
                            {
                                "value": "geracao_compartilhada",
                                "label": "Geração Compartilhada",
                            },
                        ],
                    ),
                ],
                attachments=[
                    FormAttachment(
                        name="art_engenheiro",
                        label="ART do Engenheiro Responsável",
                        required=True,
                        max_size_mb=5,
                        help_text="Anotação de Responsabilidade Técnica",
                    ),
                    FormAttachment(
                        name="diagrama_unifilar",
                        label="Diagrama Unifilar",
                        required=True,
                        max_size_mb=10,
                        help_text="Diagrama elétrico do sistema",
                    ),
                    FormAttachment(
                        name="memorial_descritivo",
                        label="Memorial Descritivo",
                        required=True,
                        max_size_mb=10,
                    ),
                ],
                validation_rules={
                    "max_power_kw": 5000,
                    "min_power_kw": 0,
                    "require_address_complement": True,
                },
                quirks={
                    "cpf_format": "sem_pontuacao",
                    "power_unit": "kW",
                    "require_complement": True,
                },
            )
        }

    def _get_enel_forms(self) -> Dict[FormType, UtilityForm]:
        """Formulários Enel."""
        return {
            FormType.SOLICITACAO_ACESSO: UtilityForm(
                utility_code="ENEL",
                form_type=FormType.SOLICITACAO_ACESSO,
                title="Solicitação de Acesso - Enel",
                description="Formulário para solicitação de acesso à rede de distribuição",
                url="https://www.enel.com.br/pt-br/clientes/solicitar-acesso.html",
                fields=[
                    FormField(
                        name="nome_solicitante",
                        label="Nome do Solicitante",
                        type=FieldType.TEXT,
                        required=True,
                        max_length=100,
                    ),
                    FormField(
                        name="cpf_cnpj",
                        label="CPF/CNPJ",
                        type=FieldType.CPF_CNPJ,
                        required=True,
                    ),
                    FormField(
                        name="numero_instalacao",
                        label="Número da Instalação",
                        type=FieldType.TEXT,
                        required=True,
                        max_length=12,
                        help_text="Número da unidade consumidora",
                    ),
                    FormField(
                        name="endereco_instalacao",
                        label="Endereço de Instalação",
                        type=FieldType.ADDRESS,
                        required=True,
                    ),
                    FormField(
                        name="potencia_instalada_kw",
                        label="Potência Instalada (kW)",
                        type=FieldType.NUMBER,
                        required=True,
                        min_value=0,
                        max_value=5000,
                    ),
                    FormField(
                        name="tipo_sistema",
                        label="Tipo de Sistema",
                        type=FieldType.SELECT,
                        required=True,
                        options=[
                            {"value": "fotovoltaico", "label": "Fotovoltaico"},
                            {"value": "eolico", "label": "Eólico"},
                        ],
                    ),
                    FormField(
                        name="modalidade_compensacao",
                        label="Modalidade de Compensação",
                        type=FieldType.SELECT,
                        required=True,
                        options=[
                            {"value": "mesma_unidade", "label": "Mesma Unidade"},
                            {
                                "value": "empreendimento_multiplo",
                                "label": "Empreendimento Múltiplo",
                            },
                            {
                                "value": "geracao_compartilhada",
                                "label": "Geração Compartilhada",
                            },
                            {
                                "value": "autoconsumo_remoto",
                                "label": "Autoconsumo Remoto",
                            },
                        ],
                    ),
                ],
                attachments=[
                    FormAttachment(
                        name="art_engenheiro",
                        label="ART do Engenheiro",
                        required=True,
                        max_size_mb=5,
                    ),
                    FormAttachment(
                        name="diagrama_unifilar",
                        label="Diagrama Unifilar",
                        required=True,
                        max_size_mb=10,
                    ),
                    FormAttachment(
                        name="memorial_descritivo",
                        label="Memorial Descritivo",
                        required=True,
                        max_size_mb=10,
                    ),
                    FormAttachment(
                        name="certificado_inmetro",
                        label="Certificado INMETRO",
                        required=True,
                        max_size_mb=5,
                    ),
                ],
                validation_rules={
                    "max_power_kw": 5000,
                    "min_power_kw": 0,
                    "remote_self_consumption_available": False,
                },
                quirks={
                    "installation_number_field": "numero_instalacao",
                    "require_inmetro_cert": True,
                },
            )
        }

    def _get_cemig_forms(self) -> Dict[FormType, UtilityForm]:
        """Formulários CEMIG."""
        return {
            FormType.SOLICITACAO_ACESSO: UtilityForm(
                utility_code="CEMIG",
                form_type=FormType.SOLICITACAO_ACESSO,
                title="Solicitação de Acesso - CEMIG",
                description="Formulário para solicitação de acesso à rede de distribuição",
                url="https://www.cemig.com.br/atendimento/geracao-distribuida/",
                fields=[
                    FormField(
                        name="nome_solicitante",
                        label="Nome do Solicitante",
                        type=FieldType.TEXT,
                        required=True,
                        max_length=100,
                    ),
                    FormField(
                        name="cpf_cnpj",
                        label="CPF/CNPJ",
                        type=FieldType.CPF_CNPJ,
                        required=True,
                    ),
                    FormField(
                        name="numero_cliente",
                        label="Número do Cliente",
                        type=FieldType.TEXT,
                        required=True,
                        max_length=10,
                    ),
                    FormField(
                        name="endereco_instalacao",
                        label="Endereço de Instalação",
                        type=FieldType.ADDRESS,
                        required=True,
                    ),
                    FormField(
                        name="potencia_instalada_kw",
                        label="Potência Instalada (kW)",
                        type=FieldType.NUMBER,
                        required=True,
                        min_value=10,  # CEMIG tem mínimo de 10 kW
                        max_value=5000,
                    ),
                    FormField(
                        name="fonte_energia",
                        label="Fonte de Energia",
                        type=FieldType.SELECT,
                        required=True,
                        options=[
                            {"value": "solar", "label": "Solar"},
                            {"value": "eolica", "label": "Eólica"},
                            {"value": "biomassa", "label": "Biomassa"},
                        ],
                    ),
                    FormField(
                        name="modalidade_compensacao",
                        label="Modalidade de Compensação",
                        type=FieldType.SELECT,
                        required=True,
                        options=[
                            {
                                "value": "mesma_unidade",
                                "label": "Mesma Unidade Consumidora",
                            },
                            {
                                "value": "empreendimento_multiplo",
                                "label": "Empreendimento Múltiplo",
                            },
                            {
                                "value": "geracao_compartilhada",
                                "label": "Geração Compartilhada",
                            },
                        ],
                    ),
                ],
                attachments=[
                    FormAttachment(
                        name="art_engenheiro",
                        label="ART do Engenheiro",
                        required=True,
                        max_size_mb=5,
                    ),
                    FormAttachment(
                        name="diagrama_unifilar",
                        label="Diagrama Unifilar",
                        required=True,
                        max_size_mb=10,
                    ),
                    FormAttachment(
                        name="memorial_descritivo",
                        label="Memorial Descritivo",
                        required=True,
                        max_size_mb=10,
                    ),
                    FormAttachment(
                        name="laudo_tecnico",
                        label="Laudo Técnico",
                        required=True,
                        max_size_mb=10,
                        help_text="Laudo técnico assinado por profissional habilitado",
                    ),
                ],
                validation_rules={
                    "max_power_kw": 5000,
                    "min_power_kw": 10,  # Mínimo específico CEMIG
                    "require_technical_report": True,
                },
                quirks={
                    "min_power_kw": 10,
                    "require_technical_report": True,
                    "address_format": "detalhado",
                },
            )
        }
