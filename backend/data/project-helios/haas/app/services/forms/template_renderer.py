"""
Templates HTML para formulários de concessionárias.

Estes templates são usados para renderizar formulários específicos
de cada concessionária com campos e validações apropriadas.
"""

from typing import Dict, Any, List
from pathlib import Path
import jinja2

from ..utility_forms_manager import UtilityForm, FormField, FormAttachment, FieldType


class FormTemplateRenderer:
    """Renderiza templates HTML para formulários de concessionárias."""

    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates"
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)), autoescape=True
        )

    def render_form(self, form: UtilityForm, form_data: Dict[str, Any] = None) -> str:
        """
        Renderiza formulário completo em HTML.

        Args:
            form: Definição do formulário
            form_data: Dados pré-preenchidos (opcional)

        Returns:
            HTML do formulário
        """
        template = self.env.get_template("base_form.html")

        context = {
            "form": form,
            "form_data": form_data or {},
            "field_renderer": self._render_field,
            "attachment_renderer": self._render_attachment,
        }

        return template.render(**context)

    def _render_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo individual do formulário."""
        field_html = ""

        # Label
        field_html += f'<label for="{field.name}" class="form-label">'
        field_html += field.label
        if field.required:
            field_html += ' <span class="text-danger">*</span>'
        field_html += "</label>\n"

        # Campo baseado no tipo
        if field.type == FieldType.TEXT:
            field_html += self._render_text_field(field, value)
        elif field.type == FieldType.NUMBER:
            field_html += self._render_number_field(field, value)
        elif field.type == FieldType.SELECT:
            field_html += self._render_select_field(field, value)
        elif field.type == FieldType.RADIO:
            field_html += self._render_radio_field(field, value)
        elif field.type == FieldType.CHECKBOX:
            field_html += self._render_checkbox_field(field, value)
        elif field.type == FieldType.DATE:
            field_html += self._render_date_field(field, value)
        elif field.type == FieldType.EMAIL:
            field_html += self._render_email_field(field, value)
        elif field.type == FieldType.TEL:
            field_html += self._render_tel_field(field, value)
        elif field.type == FieldType.CPF_CNPJ:
            field_html += self._render_cpf_cnpj_field(field, value)
        elif field.type == FieldType.CEP:
            field_html += self._render_cep_field(field, value)
        elif field.type == FieldType.ADDRESS:
            field_html += self._render_address_field(field, value)
        elif field.type == FieldType.FILE:
            field_html += self._render_file_field(field, value)

        # Help text
        if field.help_text:
            field_html += f'<div class="form-text">{field.help_text}</div>\n'

        return field_html

    def _render_text_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo de texto."""
        attrs = f'id="{field.name}" name="{field.name}" class="form-control"'
        if field.placeholder:
            attrs += f' placeholder="{field.placeholder}"'
        if field.max_length:
            attrs += f' maxlength="{field.max_length}"'
        if field.required:
            attrs += " required"

        return f'<input type="text" {attrs} value="{value or ""}">\n'

    def _render_number_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo numérico."""
        attrs = f'id="{field.name}" name="{field.name}" class="form-control"'
        if field.min_value is not None:
            attrs += f' min="{field.min_value}"'
        if field.max_value is not None:
            attrs += f' max="{field.max_value}"'
        if field.required:
            attrs += " required"

        return f'<input type="number" {attrs} value="{value or ""}" step="0.01">\n'

    def _render_select_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo select."""
        attrs = f'id="{field.name}" name="{field.name}" class="form-select"'
        if field.required:
            attrs += " required"

        html = f"<select {attrs}>\n"
        html += '<option value="">Selecione...</option>\n'

        if field.options:
            for option in field.options:
                selected = " selected" if value == option["value"] else ""
                html += f'<option value="{option["value"]}"{selected}>{option["label"]}</option>\n'

        html += "</select>\n"
        return html

    def _render_radio_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo radio."""
        html = ""
        if field.options:
            for option in field.options:
                checked = " checked" if value == option["value"] else ""
                required = " required" if field.required else ""
                html += f"""
                <div class="form-check">
                    <input class="form-check-input" type="radio" id="{field.name}_{option['value']}"
                           name="{field.name}" value="{option['value']}"{checked}{required}>
                    <label class="form-check-label" for="{field.name}_{option['value']}">
                        {option['label']}
                    </label>
                </div>
                """
        return html

    def _render_checkbox_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo checkbox."""
        checked = " checked" if value else ""
        required = " required" if field.required else ""
        return f"""
        <div class="form-check">
            <input class="form-check-input" type="checkbox" id="{field.name}"
                   name="{field.name}"{checked}{required}>
            <label class="form-check-label" for="{field.name}">
                {field.label}
            </label>
        </div>
        """

    def _render_date_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo de data."""
        attrs = f'id="{field.name}" name="{field.name}" class="form-control"'
        if field.required:
            attrs += " required"

        return f'<input type="date" {attrs} value="{value or ""}">\n'

    def _render_email_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo de email."""
        attrs = f'id="{field.name}" name="{field.name}" class="form-control"'
        if field.required:
            attrs += " required"

        return f'<input type="email" {attrs} value="{value or ""}">\n'

    def _render_tel_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo de telefone."""
        attrs = f'id="{field.name}" name="{field.name}" class="form-control"'
        if field.required:
            attrs += " required"

        return f'<input type="tel" {attrs} value="{value or ""}">\n'

    def _render_cpf_cnpj_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo CPF/CNPJ."""
        attrs = (
            f'id="{field.name}" name="{field.name}" class="form-control cpf-cnpj-mask"'
        )
        if field.required:
            attrs += " required"
        if field.mask:
            attrs += f' data-mask="{field.mask}"'

        return f'<input type="text" {attrs} value="{value or ""}" placeholder="000.000.000-00 ou 00.000.000/0000-00">\n'

    def _render_cep_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo CEP."""
        attrs = f'id="{field.name}" name="{field.name}" class="form-control cep-mask"'
        if field.required:
            attrs += " required"

        return f'<input type="text" {attrs} value="{value or ""}" placeholder="00000-000">\n'

    def _render_address_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo de endereço completo."""
        value = value or {}

        html = """
        <div class="address-fields">
            <div class="row">
                <div class="col-md-8">
                    <label for="{field.name}_logradouro" class="form-label">Logradouro <span class="text-danger">*</span></label>
                    <input type="text" id="{field.name}_logradouro" name="{field.name}[logradouro]"
                           class="form-control" value="{value.get('logradouro', '')}" required>
                </div>
                <div class="col-md-4">
                    <label for="{field.name}_numero" class="form-label">Número <span class="text-danger">*</span></label>
                    <input type="text" id="{field.name}_numero" name="{field.name}[numero]"
                           class="form-control" value="{value.get('numero', '')}" required>
                </div>
            </div>
            <div class="row mt-2">
                <div class="col-md-6">
                    <label for="{field.name}_complemento" class="form-label">Complemento</label>
                    <input type="text" id="{field.name}_complemento" name="{field.name}[complemento]"
                           class="form-control" value="{value.get('complemento', '')}"{complement_required}>
                </div>
                <div class="col-md-6">
                    <label for="{field.name}_bairro" class="form-label">Bairro <span class="text-danger">*</span></label>
                    <input type="text" id="{field.name}_bairro" name="{field.name}[bairro]"
                           class="form-control" value="{value.get('bairro', '')}" required>
                </div>
            </div>
            <div class="row mt-2">
                <div class="col-md-6">
                    <label for="{field.name}_cidade" class="form-label">Cidade <span class="text-danger">*</span></label>
                    <input type="text" id="{field.name}_cidade" name="{field.name}[cidade]"
                           class="form-control" value="{value.get('cidade', '')}" required>
                </div>
                <div class="col-md-3">
                    <label for="{field.name}_estado" class="form-label">Estado <span class="text-danger">*</span></label>
                    <select id="{field.name}_estado" name="{field.name}[estado]" class="form-select" required>
                        <option value="">UF</option>
                        <option value="SP"{"selected_sp"}>SP</option>
                        <option value="MG"{"selected_mg"}>MG</option>
                        <option value="RJ"{"selected_rj"}>RJ</option>
                        <!-- Adicionar outros estados -->
                    </select>
                </div>
                <div class="col-md-3">
                    <label for="{field.name}_cep" class="form-label">CEP <span class="text-danger">*</span></label>
                    <input type="text" id="{field.name}_cep" name="{field.name}[cep]"
                           class="form-control cep-mask" value="{value.get('cep', '')}" placeholder="00000-000" required>
                </div>
            </div>
        </div>
        """

        # Verifica se complemento é obrigatório (CPFL)
        complement_required = (
            " required"
            if field.name == "endereco_instalacao" and "CPFL" in str(field)
            else ""
        )

        # Seleção de estado
        estado = value.get("estado", "")
        selected_sp = " selected" if estado == "SP" else ""
        selected_mg = " selected" if estado == "MG" else ""
        selected_rj = " selected" if estado == "RJ" else ""

        return html.format(
            field=field,
            value=value,
            complement_required=complement_required,
            selected_sp=selected_sp,
            selected_mg=selected_mg,
            selected_rj=selected_rj,
        )

    def _render_file_field(self, field: FormField, value: Any = None) -> str:
        """Renderiza campo de arquivo."""
        attrs = f'id="{field.name}" name="{field.name}" class="form-control"'
        if field.required:
            attrs += " required"

        return f'<input type="file" {attrs}>\n'

    def _render_attachment(self, attachment: FormAttachment) -> str:
        """Renderiza seção de anexo."""
        required = ' <span class="text-danger">*</span>' if attachment.required else ""
        help_text = (
            f'<div class="form-text">{attachment.help_text}</div>'
            if attachment.help_text
            else ""
        )

        return f"""
        <div class="attachment-field mb-3">
            <label for="attachment_{attachment.name}" class="form-label">
                {attachment.label}{required}
            </label>
            <input type="file" id="attachment_{attachment.name}" name="attachments[{attachment.name}]"
                   class="form-control" accept="{','.join(attachment.allowed_types)}"
                   data-max-size="{attachment.max_size_mb * 1024 * 1024}"{' required' if attachment.required else ''}>
            {help_text}
            <div class="file-info mt-1">
                <small class="text-muted">
                    Máximo: {attachment.max_size_mb}MB. Tipos aceitos: {', '.join(attachment.allowed_types)}
                </small>
            </div>
        </div>
        """
