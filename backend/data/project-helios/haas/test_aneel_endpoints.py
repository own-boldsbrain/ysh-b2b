"""
Script de teste para os endpoints ANEEL da HaaS API
Testa todos os endpoints implementados em /api/aneel
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
ANEEL_BASE = f"{BASE_URL}/api/aneel"


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


def test_health_check():
    """Testa o endpoint de health check"""
    print("\n🔍 Testando Health Check...")
    response = requests.get(f"{ANEEL_BASE}/health")
    print_response("GET /api/aneel/health", response)
    return response.status_code == 200


def test_sync_endpoint():
    """Testa o endpoint de sincronização"""
    print("\n🔄 Testando Sync ANEEL Data...")

    payload = {"force": False, "datasets": ["gd_projects", "tariff_data"]}

    response = requests.post(f"{ANEEL_BASE}/sync", json=payload)
    print_response("POST /api/aneel/sync", response)
    return response.status_code == 200


def test_query_endpoint():
    """Testa o endpoint de query"""
    print("\n🔎 Testando Query ANEEL Data...")

    payload = {
        "query_type": "gd",
        "filters": {
            "uf": "MG",
            "distribuidora": "CEMIG",
            "potencia_min": 75,
            "potencia_max": 5000,
        },
        "limit": 10,
        "offset": 0,
    }

    response = requests.post(f"{ANEEL_BASE}/query", json=payload)
    print_response("POST /api/aneel/query", response)
    return response.status_code == 200


def test_validate_endpoint():
    """Testa o endpoint de validação de projeto"""
    print("\n✅ Testando Validação de Projeto...")

    payload = {
        "ceg": "MG.GD.CEMIG-D.00012345",
        "distribuidora": "CEMIG",
        "potencia_kw": 150.5,
        "modalidade": "mini",
        "fonte": "fotovoltaica",
        "municipio": "Belo Horizonte",
        "uf": "MG",
    }

    response = requests.post(f"{ANEEL_BASE}/validate", json=payload)
    print_response("POST /api/aneel/validate", response)
    return response.status_code == 200


def test_tariff_calculation():
    """Testa query de cálculo de tarifa"""
    print("\n💰 Testando Cálculo de Tarifa...")

    payload = {
        "query_type": "tariff",
        "filters": {"distribuidora": "CEMIG", "classe": "B1", "consumo_kwh": 500},
        "limit": 1,
        "offset": 0,
    }

    response = requests.post(f"{ANEEL_BASE}/query", json=payload)
    print_response("POST /api/aneel/query (tariff)", response)
    return response.status_code == 200


def test_market_analysis():
    """Testa query de análise de mercado"""
    print("\n📊 Testando Análise de Mercado...")

    payload = {
        "query_type": "market",
        "filters": {"region": "sudeste", "metric": "gd_penetration", "period": "2024"},
        "limit": 10,
        "offset": 0,
    }

    response = requests.post(f"{ANEEL_BASE}/query", json=payload)
    print_response("POST /api/aneel/query (market)", response)
    return response.status_code == 200


def main():
    """Executa todos os testes"""
    print("=" * 80)
    print("🚀 TESTE DOS ENDPOINTS ANEEL - HaaS API")
    print("=" * 80)
    print(f"Base URL: {ANEEL_BASE}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    results = {
        "Health Check": test_health_check(),
        "Sync Data": test_sync_endpoint(),
        "Query GD Projects": test_query_endpoint(),
        "Validate Project": test_validate_endpoint(),
        "Tariff Calculation": test_tariff_calculation(),
        "Market Analysis": test_market_analysis(),
    }

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

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Não foi possível conectar ao servidor.")
        print("Certifique-se de que o servidor está rodando em http://localhost:8000")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        exit(1)
