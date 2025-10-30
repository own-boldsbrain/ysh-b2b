#!/usr/bin/env python3
"""
Verificação de Conexão e Preparação de Upload
Testa conexão e prepara lotes sem fazer upload real
"""
from pathlib import Path
import json
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UploadPreparation:
    """Prepara e valida arquivos para upload"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.batches = []

    def scan_files(self):
        """Varre e organiza arquivos em lotes"""
        logger.info("\n" + "=" * 80)
        logger.info("🔍 ESCANEANDO ARQUIVOS PARA UPLOAD")
        logger.info("=" * 80)

        # Lote 1: JSON Principal
        json_main = self.base_path / "unified_products.json"
        if json_main.exists():
            size_mb = json_main.stat().st_size / (1024 * 1024)
            self.batches.append(
                {
                    "name": "JSON Principal",
                    "files": [json_main],
                    "total_size_mb": size_mb,
                    "destination": "data/",
                }
            )

        # Lote 2: CSVs de Categorias
        csv_dir = self.base_path / "exports" / "csv"
        if csv_dir.exists():
            csv_files = list(csv_dir.glob("*.csv"))
            if csv_files:
                total_size = sum(f.stat().st_size for f in csv_files)
                self.batches.append(
                    {
                        "name": "CSVs por Categoria",
                        "files": csv_files,
                        "total_size_mb": total_size / (1024 * 1024),
                        "destination": "data/csv/categories/",
                    }
                )

        # Lote 3: CSVs Unificados
        unified_dir = self.base_path / "exports" / "unified"
        if unified_dir.exists():
            # Fabricantes
            mfg_files = list(unified_dir.glob("manufacturer_*.csv"))
            if mfg_files:
                total_size = sum(f.stat().st_size for f in mfg_files)
                self.batches.append(
                    {
                        "name": "CSVs de Fabricantes",
                        "files": mfg_files,
                        "total_size_mb": total_size / (1024 * 1024),
                        "destination": "data/csv/manufacturers/",
                    }
                )

            # Categorias Unificadas
            cat_files = list(unified_dir.glob("category_*.csv"))
            if cat_files:
                total_size = sum(f.stat().st_size for f in cat_files)
                self.batches.append(
                    {
                        "name": "CSVs de Categorias Unificadas",
                        "files": cat_files,
                        "total_size_mb": total_size / (1024 * 1024),
                        "destination": "data/csv/unified_categories/",
                    }
                )

            # Análise de Preços
            price_files = [
                unified_dir / "price_comparison_multi_distributor.csv",
                unified_dir / "panel_models_pricing.csv",
            ]
            price_files = [f for f in price_files if f.exists()]
            if price_files:
                total_size = sum(f.stat().st_size for f in price_files)
                self.batches.append(
                    {
                        "name": "CSVs de Análise de Preços",
                        "files": price_files,
                        "total_size_mb": total_size / (1024 * 1024),
                        "destination": "data/csv/price_analysis/",
                    }
                )

            # CSV Mestre
            master = unified_dir / "all_products_unified.csv"
            if master.exists():
                size_mb = master.stat().st_size / (1024 * 1024)
                self.batches.append(
                    {
                        "name": "CSV Mestre Unificado",
                        "files": [master],
                        "total_size_mb": size_mb,
                        "destination": "data/csv/",
                    }
                )

    def display_summary(self):
        """Exibe sumário dos lotes"""
        logger.info("\n" + "=" * 80)
        logger.info("📦 SUMÁRIO DOS LOTES PREPARADOS")
        logger.info("=" * 80)

        total_files = 0
        total_size = 0

        for i, batch in enumerate(self.batches, 1):
            logger.info(f"\n📊 Lote {i}: {batch['name']}")
            logger.info(f"   Destino: {batch['destination']}")
            logger.info(f"   Arquivos: {len(batch['files'])}")
            logger.info(f"   Tamanho: {batch['total_size_mb']:.2f} MB")

            for file in batch["files"]:
                size_kb = file.stat().st_size / 1024
                logger.info(f"      • {file.name} ({size_kb:.2f} KB)")

            total_files += len(batch["files"])
            total_size += batch["total_size_mb"]

        logger.info("\n" + "=" * 80)
        logger.info("📈 TOTAIS")
        logger.info("=" * 80)
        logger.info(f"   Total de lotes: {len(self.batches)}")
        logger.info(f"   Total de arquivos: {total_files}")
        logger.info(f"   Tamanho total: {total_size:.2f} MB")

    def generate_upload_script(self):
        """Gera script bash/powershell de upload manual"""

        # PowerShell script
        ps_script = """# Upload para Hugging Face - PowerShell
# Configure seu token primeiro: $env:HF_TOKEN = 'seu_token'

$REPO_ID = "fernando-bold/ysh-solar-products-brazil"

# Verificar token
if (-not $env:HF_TOKEN) {
    Write-Host "❌ Token não configurado!" -ForegroundColor Red
    Write-Host "Configure com: `$env:HF_TOKEN = 'seu_token'" -ForegroundColor Yellow
    exit 1
}

# Instalar huggingface-cli se necessário
pip install -q huggingface_hub

"""

        for i, batch in enumerate(self.batches, 1):
            ps_script += f"\n# Lote {i}: {batch['name']}\n"
            ps_script += f"Write-Host 'Uploading lote {i}: {batch['name']}' -ForegroundColor Cyan\n"

            for file in batch["files"]:
                rel_path = file.relative_to(self.base_path)
                dest = batch["destination"] + file.name
                ps_script += f"huggingface-cli upload $REPO_ID '{rel_path}' '{dest}' --repo-type dataset\n"

            ps_script += "Start-Sleep -Seconds 1\n"

        ps_script += "\nWrite-Host '✅ Upload concluído!' -ForegroundColor Green\n"

        # Salvar script
        script_path = self.base_path / "upload_manual.ps1"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(ps_script)

        logger.info(f"\n✅ Script PowerShell gerado: {script_path.name}")

    def check_connection(self):
        """Verifica conexão com Hugging Face"""
        try:
            from huggingface_hub import HfApi

            api = HfApi()

            logger.info("\n🔌 Testando conexão com Hugging Face...")

            # Tentar listar repos públicos (não precisa de auth)
            api.list_datasets(limit=1)

            logger.info("✅ Conexão OK!")
            return True

        except Exception as e:
            logger.error(f"❌ Erro de conexão: {e}")
            return False

    def run(self):
        """Executa verificação completa"""
        # Verificar conexão
        connected = self.check_connection()

        # Escanear arquivos
        self.scan_files()

        # Exibir sumário
        self.display_summary()

        # Gerar scripts
        self.generate_upload_script()

        # Instruções finais
        logger.info("\n" + "=" * 80)
        logger.info("📝 PRÓXIMOS PASSOS")
        logger.info("=" * 80)

        if not connected:
            logger.warning("⚠️  Conexão com Hugging Face falhou")
            logger.info("   Verifique sua conexão de internet")

        logger.info("\n1️⃣  Obtenha seu token:")
        logger.info("   https://huggingface.co/settings/tokens")

        logger.info("\n2️⃣  Configure o token:")
        logger.info("   PowerShell: $env:HF_TOKEN = 'seu_token'")
        logger.info("   Bash: export HF_TOKEN='seu_token'")

        logger.info("\n3️⃣  Execute o upload (escolha um):")
        logger.info("   • python upload_to_huggingface.py  (automático)")
        logger.info("   • .\\upload_manual.ps1              (manual, passo a passo)")

        logger.info("\n" + "=" * 80)


def main():
    prep = UploadPreparation()
    prep.run()


if __name__ == "__main__":
    main()
