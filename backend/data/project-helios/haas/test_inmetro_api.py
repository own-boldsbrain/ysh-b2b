"""Script de teste para endpoints INMETRO - Issue #2"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
# Token mock para desenvolvimento
HEADERS = {"Authorization": "Bearer test-token-dev"}


def test_health():
    """Testa health check da API."""
    print("\n🔍 Testando /health...")
    response = requests.get("http://localhost:8000/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


def test_manufacturers():
    """Testa GET /inmetro/manufacturers."""
    print("\n🔍 Testando GET /api/inmetro/manufacturers...")
    url = f"{BASE_URL}/inmetro/manufacturers"
    response = requests.get(url, headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        manufacturers = response.json()
        print(f"✅ {len(manufacturers)} fabricantes encontrados:")
        for mfr in manufacturers[:5]:
            print(f"  - {mfr}")
    else:
        print(f"❌ Erro: {response.text}")


def test_models():
    """Testa GET /inmetro/models/{manufacturer}."""
    print("\n🔍 Testando GET /api/inmetro/models/Fronius...")
    url = f"{BASE_URL}/inmetro/models/Fronius"
    response = requests.get(url, headers=HEADERS)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        models = response.json()
        print(f"✅ {len(models)} modelos encontrados:")
        for model in models:
            print(f"  - {model}")
    else:
        print(f"❌ Erro: {response.text}")


def test_validate_equipment():
    """Testa POST /inmetro/validate."""
    print("\n🔍 Testando POST /api/inmetro/validate...")
    url = f"{BASE_URL}/inmetro/validate"
    payload = {
        "categoria": "inversores",
        "fabricante": "Fronius",
        "modelo": "Primo 8.2-1",
        "registry_id": "TEST-2025-001",
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    print(f"Status: {response.status_code}")

    if response.status_code == 202:
        data = response.json()
        print("✅ Validação iniciada:")
        print(f"  Request ID: {data['request_id']}")
        print(f"  Status: {data['status']}")
        print(f"  Mensagem: {data['message']}")
        return data["request_id"]
    else:
        print(f"❌ Erro: {response.text}")
        return None


def test_get_status(request_id: str):
    """Testa GET /inmetro/status/{request_id}."""
    import time

    print(f"\n🔍 Testando GET /api/inmetro/status/{request_id}...")
    url = f"{BASE_URL}/inmetro/status/{request_id}"

    # Aguardar processamento (máx 10s)
    for i in range(10):
        time.sleep(1)
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            data = response.json()
            status = data["status"]
            print(f"  [{i+1}s] Status: {status}")

            if status in ["completed", "failed"]:
                print("\n✅ Validação finalizada:")
                print(f"  Valid: {data.get('valid', False)}")
                print(f"  Certificado: {data.get('certification_number', 'N/A')}")
                print(f"  Mensagem: {data.get('message', '')}")
                break
        else:
            print(f"❌ Erro: {response.text}")
            break


def test_search():
    """Testa GET /inmetro/search."""
    print("\n🔍 Testando GET /api/inmetro/search?query=Fronius...")
    url = f"{BASE_URL}/inmetro/search"
    params = {"query": "Fronius", "page": 1, "page_size": 10}

    response = requests.get(url, params=params, headers=HEADERS)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['total']} resultados encontrados:")
        for result in data["results"]:
            print(
                f"  - {result['manufacturer']} {result['model']} "
                f"({result['certificate_number']})"
            )
    else:
        print(f"❌ Erro: {response.text}")


def test_batch():
    """Testa POST /inmetro/batch."""
    print("\n🔍 Testando POST /api/inmetro/batch...")
    url = f"{BASE_URL}/inmetro/batch"
    payload = {
        "equipments": [
            {
                "categoria": "inversores",
                "fabricante": "Fronius",
                "modelo": "Primo 8.2-1",
            },
            {
                "categoria": "modulos",
                "fabricante": "Canadian Solar",
                "modelo": "CS3W-450MS",
            },
        ]
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    print(f"Status: {response.status_code}")

    if response.status_code == 202:
        data = response.json()
        print(f"✅ {data.get('message', 'Lote agendado')}:")
        for idx, req_id in data.items():
            if idx != "message":
                print(f"  [{idx}] Request ID: {req_id}")
    else:
        print(f"❌ Erro: {response.text}")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTES DE INTEGRAÇÃO - INMETRO API (Issue #2)")
    print("=" * 60)

    try:
        # 1. Health check
        test_health()

        # 2. Listar fabricantes
        test_manufacturers()

        # 3. Listar modelos
        test_models()

        # 4. Buscar equipamentos
        test_search()

        # 5. Validar equipamento individual
        request_id = test_validate_equipment()
        if request_id:
            test_get_status(request_id)

        # 6. Validação em lote
        test_batch()

        print("\n" + "=" * 60)
        print("✅ TESTES CONCLUÍDOS")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Servidor não está rodando em http://localhost:8000")
        print("Execute: cd haas && python run.py")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
