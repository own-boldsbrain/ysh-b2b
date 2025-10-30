"""
Testes básicos para o Utility Forms Manager.

Executar com: python -m pytest haas/tests/test_forms_manager.py -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app.services.forms import UtilityFormsManager, FormType


class TestUtilityFormsManager:

    def setup_method(self):
        """Setup para cada teste."""
        self.forms_manager = UtilityFormsManager()

    def test_get_available_forms_cpfl(self):
        """Testa obtenção de formulários disponíveis para CPFL."""
        forms = self.forms_manager.get_available_forms("CPFL")
        assert FormType.SOLICITACAO_ACESSO in forms

    def test_get_available_forms_enel(self):
        """Testa obtenção de formulários disponíveis para Enel."""
        forms = self.forms_manager.get_available_forms("ENEL")
        assert FormType.SOLICITACAO_ACESSO in forms

    def test_get_available_forms_cemig(self):
        """Testa obtenção de formulários disponíveis para CEMIG."""
        forms = self.forms_manager.get_available_forms("CEMIG")
        assert FormType.SOLICITACAO_ACESSO in forms

    def test_get_form_cpfl(self):
        """Testa obtenção de formulário específico CPFL."""
        form = self.forms_manager.get_form("CPFL", FormType.SOLICITACAO_ACESSO)
        assert form is not None
        assert form.utility_code == "CPFL"
        assert form.title == "Solicitação de Acesso - CPFL Paulista"
        assert len(form.fields) > 0
        assert len(form.attachments) > 0

    def test_get_form_invalid_utility(self):
        """Testa formulário para concessionária inválida."""
        form = self.forms_manager.get_form("INVALID", FormType.SOLICITACAO_ACESSO)
        assert form is None

    def test_validate_form_data_valid_cpfl(self):
        """Testa validação de dados válidos para CPFL."""
        form_data = {
            "nome_solicitante": "João Silva",
            "cpf_cnpj": "123.456.789-00",
            "numero_cliente": "12345678",
            "endereco_instalacao": {
                "logradouro": "Rua das Flores",
                "numero": "123",
                "complemento": "Apto 45",  # CPFL requer complemento
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01234-567",
            },
            "potencia_instalada_kw": 3000,
            "tipo_geracao": "solar_fotovoltaica",
            "modalidade_compensacao": "mesma_unidade",
        }

        result = self.forms_manager.validate_form_data(
            "CPFL", FormType.SOLICITACAO_ACESSO, form_data
        )
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_form_data_missing_required_cpfl(self):
        """Testa validação com campos obrigatórios faltando para CPFL."""
        form_data = {
            "nome_solicitante": "João Silva"
            # Faltando CPF, endereço, etc.
        }

        result = self.forms_manager.validate_form_data(
            "CPFL", FormType.SOLICITACAO_ACESSO, form_data
        )
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any("obrigatório" in error.lower() for error in result["errors"])

    def test_validate_form_data_cpfl_complement_required(self):
        """Testa que CPFL requer complemento do endereço."""
        form_data = {
            "nome_solicitante": "João Silva",
            "cpf_cnpj": "123.456.789-00",
            "numero_cliente": "12345678",
            "endereco_instalacao": {
                "logradouro": "Rua das Flores",
                "numero": "123",
                # complemento faltando - obrigatório para CPFL
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01234-567",
            },
            "potencia_instalada_kw": 3000,
            "tipo_geracao": "solar_fotovoltaica",
            "modalidade_compensacao": "mesma_unidade",
        }

        result = self.forms_manager.validate_form_data(
            "CPFL", FormType.SOLICITACAO_ACESSO, form_data
        )
        assert result["valid"] is False
        assert any("complemento" in error.lower() for error in result["errors"])

    def test_validate_form_data_cemig_min_power(self):
        """Testa potência mínima para CEMIG."""
        form_data = {
            "nome_solicitante": "João Silva",
            "cpf_cnpj": "123.456.789-00",
            "numero_cliente": "12345678",
            "endereco_instalacao": {
                "logradouro": "Rua das Flores",
                "numero": "123",
                "bairro": "Centro",
                "cidade": "Belo Horizonte",
                "estado": "MG",
                "cep": "01234-567",
            },
            "potencia_instalada_kw": 5,  # Abaixo do mínimo de 10 kW
            "fonte_energia": "solar",
            "modalidade_compensacao": "mesma_unidade",
        }

        result = self.forms_manager.validate_form_data(
            "CEMIG", FormType.SOLICITACAO_ACESSO, form_data
        )
        assert result["valid"] is False
        assert any(
            "mínima" in error.lower() and "10 kw" in error.lower()
            for error in result["errors"]
        )

    def test_validate_cpf_valid(self):
        """Testa validação de CPF válido."""
        # CPF válido de exemplo
        cpf = "12345678909"  # Este é um CPF válido para teste
        assert self.forms_manager._validate_cpf(cpf) is True

    def test_validate_cpf_invalid(self):
        """Testa validação de CPF inválido."""
        cpf = "11111111111"  # CPF inválido (todos dígitos iguais)
        assert self.forms_manager._validate_cpf(cpf) is False

    def test_validate_cnpj_valid(self):
        """Testa validação de CNPJ válido."""
        # CNPJ válido de exemplo
        cnpj = "12345678000195"  # Este é um CNPJ válido para teste
        assert self.forms_manager._validate_cnpj(cnpj) is True

    def test_validate_cep_valid(self):
        """Testa validação de CEP válido."""
        cep = "01234567"
        assert self.forms_manager._validate_cep(cep) is True

    def test_validate_cep_invalid(self):
        """Testa validação de CEP inválido."""
        cep = "123456"  # Muito curto
        assert self.forms_manager._validate_cep(cep) is False


if __name__ == "__main__":
    # Executa testes manualmente
    test_instance = TestUtilityFormsManager()
    test_instance.setup_method()

    print("Executando testes do Forms Manager...")

    try:
        test_instance.test_get_available_forms_cpfl()
        print("✓ Teste CPFL forms OK")

        test_instance.test_get_form_cpfl()
        print("✓ Teste get form CPFL OK")

        test_instance.test_validate_form_data_valid_cpfl()
        print("✓ Teste validação CPFL válida OK")

        test_instance.test_validate_cpf_valid()
        print("✓ Teste CPF válido OK")

        print("\nTodos os testes passaram!")

    except Exception as e:
        print(f"✗ Erro no teste: {e}")
        import traceback

        traceback.print_exc()
