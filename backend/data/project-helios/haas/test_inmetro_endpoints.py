"""
Script de teste para os endpoints INMETRO da HaaS API
Testa 5 endpoints principais: validate, status, certificate, search, batch
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
INMETRO_BASE = f"{BASE_URL}/api/inmetro"

# Token de autenticação (usando token mock para testes)
# Em produção, usar login real
HEADERS = {
    "Authorization": "Bearer mock_token_for_testing"
}


def print_response(endpoint: str, response: requests.Response):
    """Imprime a resposta formatada"""
    print(f"\n{'='*80}")
    print(f"Endpoint: {endpoint}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print(f"{'='*80}\n")


def test_validate_equipment():
    """Testa POST /inmetro/validate"""
    print("\n🔍 Testando POST /inmetro/validate...")

    payload = {
        "categoria": "inversores",
        "fabricante": "Fronius",
        "modelo": "Primo 8.2-1",
        "registry_id": "INV-2024-00123"
    }

    try:
        response = requests.post(
            f"{INMETRO_BASE}/validate",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        print_response("POST /api/inmetro/validate", response)
        
        if response.status_code == 202:
            data = response.json()
            return data.get("request_id")
        return None
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None


def test_get_status(request_id: str):
    """Testa GET /inmetro/status/{request_id}"""
    print(f"\n🔎 Testando GET /inmetro/status/{request_id}...")

    try:
        response = requests.get(
            f"{INMETRO_BASE}/status/{request_id}",
            headers=HEADERS,
            timeout=10
        )
        print_response(f"GET /api/inmetro/status/{request_id}", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def test_get_certificate():
    """Testa GET /inmetro/certificate/{certificate_number}"""
    print("\n📜 Testando GET /inmetro/certificate/BRA-123456...")

    try:
        response = requests.get(
            f"{INMETRO_BASE}/certificate/BRA-123456",
            headers=HEADERS,
            timeout=10
        )
        print_response("GET /api/inmetro/certificate/BRA-123456", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def test_search_equipment():
    """Testa GET /inmetro/search"""
    print("\n🔍 Testando GET /inmetro/search?query=Fronius...")

    try:
        response = requests.get(
            f"{INMETRO_BASE}/search",
            params={
                "query": "Fronius",
                "category": "inversores",
                "page": 1,
                "page_size": 10
            },
            headers=HEADERS,
            timeout=10
        )
        print_response("GET /api/inmetro/search", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def test_batch_validation():
    """Testa POST /inmetro/batch"""
    print("\n📦 Testando POST /inmetro/batch...")

    payload = {
        "equipments": [
            {
                "categoria": "inversores",
                "fabricante": "Fronius",
                "modelo": "Primo 8.2-1"
            },
            {
                "categoria": "modulos",
                "fabricante": "Canadian Solar",
                "modelo": "CS3W-450MS"
            },
            {
                "categoria": "inversores",
                "fabricante": "WEG",
                "modelo": "SIW300H"
            }
        ]
    }

    try:
        response = requests.post(
            f"{INMETRO_BASE}/batch",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        print_response("POST /api/inmetro/batch", response)
        
        if response.status_code == 202:
            data = response.json()
            # Retornar os request_ids
            return [v for k, v in data.items() if k.isdigit()]
        return []
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return []


def test_health_check():
    """Testa endpoint de saúde geral"""
    print("\n❤️ Testando GET /health...")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print_response("GET /health", response)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("=" * 80)
    print("🚀 TESTE DOS ENDPOINTS INMETRO - HaaS API")
    print("=" * 80)
    print(f"Base URL: {INMETRO_BASE}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("\n⚠️ NOTA: Testes usam autenticação mock. Em produção, use login real.\n")

    results = {}

    # 1. Health Check (baseline)
    results["Health Check"] = test_health_check()

    # 2. Validar equipamento individual
    request_id = test_validate_equipment()
    if request_id:
        results["POST /validate"] = True
        
        # Aguardar processamento (background task)
        print("\n⏳ Aguardando 3 segundos para processamento em background...")
        time.sleep(3)
        
        # 3. Consultar status da validação
        results["GET /status"] = test_get_status(request_id)
    else:
        results["POST /validate"] = False
        results["GET /status"] = False

    # 4. Buscar certificado
    results["GET /certificate"] = test_get_certificate()

    # 5. Buscar equipamentos
    results["GET /search"] = test_search_equipment()

    # 6. Validação em lote
    batch_ids = test_batch_validation()
    results["POST /batch"] = len(batch_ids) > 0
    
    if batch_ids:
        print(f"\n✅ Batch gerou {len(batch_ids)} requisições: {batch_ids[:3]}...")

    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO DOS TESTES")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASSOU" if passed_test else "❌ FALHOU"
        print(f"{status} - {test_name}")

    print(f"\n{passed}/{total} testes passaram ({(passed/total)*100:.1f}%)")
    print("=" * 80)

    # Status final
    if passed == total:
        print("\n🎉 SUCESSO! Todos os endpoints INMETRO estão funcionando!")
        return 0
    elif passed > 0:
        print(f"\n⚠️ PARCIAL: {passed}/{total} endpoints funcionando.")
        print("Verifique os logs acima para detalhes dos erros.")
        return 1
    else:
        print("\n❌ FALHA: Nenhum endpoint INMETRO funcionando.")
        print("Verifique se o servidor está rodando e configurado corretamente.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar ao servidor.")
        print("Certifique-se de que o servidor está rodando em http://localhost:8000")
        exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Testes interrompidos pelo usuário.")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
