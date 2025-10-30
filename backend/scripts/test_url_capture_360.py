"""Teste de Captura End-to-End 360° - URLs de Fabricantes.

Valida todas as URLs coletadas para os 9 fabricantes principais:
- Growatt, Sungrow, Deye, Goodwe, Fronius, Huawei, Enphase, Hoymiles, APsystems

Cobertura:
- URLs oficiais Brasil
- Páginas de produtos por série
- Datasheets de modelos específicos
- Status HTTP e acessibilidade
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("⚠️  requests não instalado. Execute: pip install requests")
    exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class URLTestResult:
    """Resultado de teste de uma URL."""

    url: str
    status_code: int | None = None
    accessible: bool = False
    latency_ms: float = 0.0
    error: str | None = None
    content_type: str | None = None
    redirect_url: str | None = None


@dataclass
class ManufacturerTestReport:
    """Relatório de testes de um fabricante."""

    name: str
    country: str
    total_urls: int = 0
    successful_urls: int = 0
    failed_urls: int = 0
    avg_latency_ms: float = 0.0
    url_results: List[URLTestResult] = field(default_factory=list)


class URLCaptureTester:
    """Tester para validação de URLs de fabricantes."""

    def __init__(self, database_path: str | Path):
        self.database_path = Path(database_path)
        self.session = self._create_session()
        self.results: Dict[str, ManufacturerTestReport] = {}

    def _create_session(self) -> requests.Session:
        """Cria sessão HTTP com retry automático."""
        session = requests.Session()

        # Retry strategy
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Headers
        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            }
        )

        return session

    def load_database(self) -> Dict[str, Any]:
        """Carrega database de URLs."""
        with open(self.database_path, encoding="utf-8") as f:
            return json.load(f)

    def test_url(self, url: str, timeout: int = 10) -> URLTestResult:
        """Testa uma URL individual."""
        result = URLTestResult(url=url)
        start_time = time.time()

        try:
            response = self.session.get(
                url,
                timeout=timeout,
                allow_redirects=True,
            )

            result.status_code = response.status_code
            result.accessible = 200 <= response.status_code < 400
            result.latency_ms = (time.time() - start_time) * 1000
            result.content_type = response.headers.get("Content-Type", "")

            if response.history:
                result.redirect_url = response.url

            logger.info(
                f"✓ {url[:70]:70s} → {response.status_code} "
                f"({result.latency_ms:.0f}ms)"
            )

        except requests.exceptions.Timeout:
            result.error = "Timeout"
            logger.warning(f"⏱ {url[:70]:70s} → Timeout")

        except requests.exceptions.ConnectionError:
            result.error = "Connection Error"
            logger.warning(f"❌ {url[:70]:70s} → Connection Error")

        except requests.exceptions.TooManyRedirects:
            result.error = "Too Many Redirects"
            logger.warning(f"🔄 {url[:70]:70s} → Too Many Redirects")

        except Exception as e:
            result.error = str(e)
            logger.error(f"💥 {url[:70]:70s} → {e}")

        return result

    def extract_urls_from_manufacturer(
        self, manufacturer_data: Dict[str, Any]
    ) -> List[str]:
        """Extrai todas as URLs de um fabricante."""
        urls = []

        # Websites principais
        if "websites" in manufacturer_data:
            urls.extend(manufacturer_data["websites"].values())

        # Product lines
        if "product_lines" in manufacturer_data:
            for line_name, line_data in manufacturer_data["product_lines"].items():
                # URL da linha de produtos
                if "product_page" in line_data:
                    urls.append(line_data["product_page"])

                # Modelos
                if "models" in line_data:
                    for model in line_data["models"]:
                        if "product_page" in model:
                            urls.append(model["product_page"])
                        if "datasheet_url" in model:
                            urls.append(model["datasheet_url"])

        return list(set(urls))  # Remove duplicatas

    def test_manufacturer(
        self, name: str, manufacturer_data: Dict[str, Any]
    ) -> ManufacturerTestReport:
        """Testa todas as URLs de um fabricante."""
        logger.info(f"\n{'='*80}")
        logger.info(f"Testing {name.upper()} {manufacturer_data.get('country', '')}")
        logger.info(f"{'='*80}")

        report = ManufacturerTestReport(
            name=name,
            country=manufacturer_data.get("country", ""),
        )

        urls = self.extract_urls_from_manufacturer(manufacturer_data)
        report.total_urls = len(urls)

        for url in urls:
            result = self.test_url(url)
            report.url_results.append(result)

            if result.accessible:
                report.successful_urls += 1
            else:
                report.failed_urls += 1

            # Rate limiting
            time.sleep(0.5)

        # Calcula latência média
        accessible_results = [r for r in report.url_results if r.accessible]
        if accessible_results:
            report.avg_latency_ms = sum(r.latency_ms for r in accessible_results) / len(
                accessible_results
            )

        return report

    def test_all_manufacturers(self) -> Dict[str, ManufacturerTestReport]:
        """Testa todos os fabricantes."""
        logger.info("🚀 Iniciando Teste de Captura 360° de URLs\n")

        database = self.load_database()
        manufacturers = database.get("manufacturers", {})

        for name, data in manufacturers.items():
            report = self.test_manufacturer(name, data)
            self.results[name] = report

        return self.results

    def generate_summary_report(self) -> Dict[str, Any]:
        """Gera relatório consolidado."""
        total_urls = sum(r.total_urls for r in self.results.values())
        total_successful = sum(r.successful_urls for r in self.results.values())
        total_failed = sum(r.failed_urls for r in self.results.values())

        success_rate = (total_successful / total_urls * 100) if total_urls > 0 else 0

        return {
            "timestamp": datetime.now().isoformat(),
            "total_manufacturers": len(self.results),
            "total_urls_tested": total_urls,
            "successful_urls": total_successful,
            "failed_urls": total_failed,
            "success_rate": f"{success_rate:.1f}%",
            "manufacturers": {
                name: {
                    "country": report.country,
                    "total_urls": report.total_urls,
                    "successful": report.successful_urls,
                    "failed": report.failed_urls,
                    "success_rate": (
                        f"{(report.successful_urls / report.total_urls * 100):.1f}%"
                        if report.total_urls > 0
                        else "0%"
                    ),
                    "avg_latency_ms": f"{report.avg_latency_ms:.0f}",
                }
                for name, report in self.results.items()
            },
        }

    def print_summary(self):
        """Imprime resumo formatado."""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO DE CAPTURA 360° - URLs DE FABRICANTES")
        print("=" * 80)

        for name, report in self.results.items():
            success_rate = (
                (report.successful_urls / report.total_urls * 100)
                if report.total_urls > 0
                else 0
            )

            status_icon = (
                "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
            )

            print(f"\n{status_icon} {report.name.upper()} {report.country}")
            print(f"   URLs Testadas:  {report.total_urls}")
            print(f"   ✓ Sucesso:      {report.successful_urls}")
            print(f"   ✗ Falhas:       {report.failed_urls}")
            print(f"   Taxa:           {success_rate:.1f}%")
            print(f"   Latência Média: {report.avg_latency_ms:.0f}ms")

            # Mostra URLs com falha
            failed_urls = [r for r in report.url_results if not r.accessible]
            if failed_urls:
                print(f"\n   ❌ URLs com Falha:")
                for result in failed_urls[:3]:  # Mostra no máximo 3
                    print(f"      - {result.url[:60]}... → {result.error}")

        # Resumo geral
        total_urls = sum(r.total_urls for r in self.results.values())
        total_successful = sum(r.successful_urls for r in self.results.values())
        overall_success = (total_successful / total_urls * 100) if total_urls > 0 else 0

        print("\n" + "=" * 80)
        print(
            f"🎯 RESULTADO GERAL: {total_successful}/{total_urls} URLs acessíveis ({overall_success:.1f}%)"
        )
        print("=" * 80 + "\n")

    def save_detailed_report(self, output_path: str | Path):
        """Salva relatório detalhado em JSON."""
        output_path = Path(output_path)

        detailed_report = {
            "summary": self.generate_summary_report(),
            "detailed_results": {
                name: {
                    "name": report.name,
                    "country": report.country,
                    "total_urls": report.total_urls,
                    "successful_urls": report.successful_urls,
                    "failed_urls": report.failed_urls,
                    "avg_latency_ms": report.avg_latency_ms,
                    "urls": [
                        {
                            "url": r.url,
                            "status_code": r.status_code,
                            "accessible": r.accessible,
                            "latency_ms": r.latency_ms,
                            "error": r.error,
                            "content_type": r.content_type,
                            "redirect_url": r.redirect_url,
                        }
                        for r in report.url_results
                    ],
                }
                for name, report in self.results.items()
            },
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(detailed_report, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Relatório detalhado salvo em: {output_path}")


def main():
    """Executa teste completo de captura 360°."""
    # Paths
    workspace = Path(__file__).parent.parent
    database_path = workspace / "data" / "manufacturers_urls_database.json"
    output_path = workspace / "data" / "url_capture_360_report.json"

    if not database_path.exists():
        logger.error(f"❌ Database não encontrada: {database_path}")
        return

    # Executa testes
    tester = URLCaptureTester(database_path)
    tester.test_all_manufacturers()

    # Relatórios
    tester.print_summary()
    tester.save_detailed_report(output_path)

    # Validação final
    summary = tester.generate_summary_report()
    success_rate = float(summary["success_rate"].rstrip("%"))

    if success_rate >= 80:
        logger.info("✅ TESTE APROVADO: Taxa de sucesso >= 80%")
    elif success_rate >= 50:
        logger.warning("⚠️  TESTE PARCIAL: Taxa de sucesso entre 50-80%")
    else:
        logger.error("❌ TESTE REPROVADO: Taxa de sucesso < 50%")


if __name__ == "__main__":
    main()
