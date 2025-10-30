"""
Módulo de Scraping de Imagens

Responsável por buscar e extrair URLs de imagens de packshots oficiais
dos sites dos fabricantes, conforme o "Plano Comandante A".
"""

import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from config import HTTP_HEADERS, REQUEST_TIMEOUT, REQUESTS_PER_SECOND_PER_DOMAIN
from agent_manager import AgentManager


class ImageScraper:
    def __init__(self):
        self.agent_manager = AgentManager()
        self.session = requests.Session()
        self.session.headers.update(HTTP_HEADERS)
        self.domain_last_request = {}

        # Mapeamento da Onda 1: SKU -> URLs (principal e adicionais)
        self.wave1_targets = {
            "PNL-JINKO-TGR-585W-NTYPE": {
                "type": "pdf",
                "primary": "https://www.jinkosolar.com/2023/PDF/20231211.pdf",
                "additional": [],
            },
            "PNL-TRINA-VERTEX-670W-MONO": {
                "type": "pdf",
                "primary": "https://static.trinasolar.com/sites/default/files/Datasheet_Vertex_DEG21C.20_670W_EN_2022_A.pdf",
                "additional": [],
            },
            "PNL-JA-JAM72-550W-PERC": {
                "type": "pdf",
                "primary": "https://www.jasolar.com/uploadfile/2021/0706/20210706053524693.pdf",
                "additional": [
                    "https://www.jasolar.com/uploadfile/2024/0112/20240112033948512.pdf",
                    "https://www.jasolar.com/uploadfile/fujian/2024/0801/fa0ee8eb0311a64.pdf",
                ],
            },
            "PNL-LONGI-HMO6-665W-BF": {
                "type": "pdf",
                "primary": "https://static.longi.com/LR_7_72_HVH_655_670_M_30_30_and_15_Scientist_BGV_02_20241118_EN_Draft_9293e45f42.pdf",
                "additional": [
                    "https://static.longi.com/LR_7_72_HVDF_640_665_M_30_30_and_15_Frame_Guardian_Anti_Dust_BGV_02_20250528_EN_3dffc216b7.pdf"
                ],
            },
            "PNL-CANA-CS7N-550W-BF": {
                "type": "pdf",
                "primary": "https://static.csisolar.com/wp-content/uploads/sites/3/2024/03/29101600/CS-Datasheet-TOPBiHiKu7-TOPCon_CS7N-TB-AG_v1.61_F43M_J5_NA.pdf",
                "additional": [
                    "https://static.csisolar.com/wp-content/uploads/2020/10/06153525/CS-Datasheet-BiHiKu7_CS7N-MB-AG_v2.4_EN.pdf",
                    "https://static.csisolar.com/wp-content/uploads/sites/2/2020/10/07063301/CS-Datasheet-HiKu7_CS7N-MS_v2.4_AU.pdf",
                ],
            },
            "INV-DEYE-SUN-8K-SG04LP3-EU": {
                "type": "direct",
                "primary": "https://www.deyeinverter.com/wp-content/uploads/2025/01/16/sg02lp2-us-am-01.png",
                "additional": [
                    "https://www.deyeinverter.com/wp-content/uploads/2025/01/16/sg02lp2-us-am-02.png"
                ],
            },
        }

    def _get_search_urls(self, sku_info):
        """Gera URLs de busca no Google para encontrar a página do produto."""
        manufacturer = sku_info.get("manufacturer", "").lower()
        query = sku_info.get("search_query", "")

        # Mapeamento de domínios oficiais para garantir a busca no lugar certo
        domains = {
            "canadian": "csisolar.com",
            "jinko": "jinkosolar.com",
            "longi": "longi.com",
            "trina": "trinasolar.com",
            "ja": "jasolar.com",
            "growatt": "growatt.com",
            "deye": "deyeinverter.com",
            "solis": "solisinverters.com",
            "goodwe": "goodwe.com",
            "fronius": "fronius.com",
        }
        domain = domains.get(manufacturer, f"{manufacturer}.com")

        # Retorna uma URL de busca do Google que restringe ao domínio oficial
        return [
            f"https://www.google.com/search?q=site:{domain}+{query.replace(' ', '+')}"
        ]

    def _rate_limit(self, url):
        """Garante que não façamos requisições demais para o mesmo domínio."""
        domain = urlparse(url).netloc
        last_req_time = self.domain_last_request.get(domain, 0)
        elapsed = time.time() - last_req_time

        wait_time = (1 / REQUESTS_PER_SECOND_PER_DOMAIN) - elapsed
        if wait_time > 0:
            time.sleep(wait_time)

        self.domain_last_request[domain] = time.time()

    def find_images(self, sku_info):
        """
        Orquestra a busca por imagens para um determinado SKU.
        Para SKUs da Onda 1, usa o mapeamento direto.
        Para outros SKUs, usa agentes de IA para buscar.
        """
        sku = sku_info.get("original_sku")

        # Verifica se o SKU está na Onda 1
        if sku in self.wave1_targets:
            target = self.wave1_targets[sku]
            results = []

            # Adiciona a URL principal
            results.append(
                {"url": target["primary"], "type": target["type"], "is_primary": True}
            )

            # Adiciona URLs adicionais
            for add_url in target.get("additional", []):
                results.append(
                    {"url": add_url, "type": target["type"], "is_primary": False}
                )

            print(f"✅ SKU {sku} encontrado na Onda 1: {len(results)} URL(s)")
            return results

        # Para outros SKUs (placeholder para futuro)
        print(
            f"ℹ️  SKU {sku} não está na Onda 1. Busca automática ainda não implementada."
        )
        return []

    def download_file(self, url, output_path):
        """
        Baixa um arquivo (imagem ou PDF) de uma URL.
        """
        try:
            self._rate_limit(url)
            print(f"⬇️  Baixando: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT, stream=True)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"✅ Arquivo baixado: {output_path}")
            return True
        except requests.RequestException as e:
            print(f"❌ Erro ao baixar {url}: {e}")
            return False


if __name__ == "__main__":
    from sku_parser import parse_sku

    scraper = ImageScraper()
    test_sku = "PNL-JINKO-TGR-585W-NTYPE"
    sku_data = parse_sku(test_sku)

    images = scraper.find_images(sku_data)
    print(f"\nImagens/PDFs encontrados para {test_sku}:")
    for item in images:
        status = "Primary" if item["is_primary"] else "Additional"
        print(f"- [{item['type'].upper()}] {item['url']} ({status})")
