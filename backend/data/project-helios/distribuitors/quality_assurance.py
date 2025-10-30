"""
ANEEL Distribuidoras - Quality Assurance System
================================================
Valida completude, consistência e acurácia dos dados capturados
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class DataQualityValidator:
    """Valida qualidade dos dados extraídos"""

    # Estados válidos do Brasil
    VALID_STATES = {
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    }

    # Thresholds de qualidade
    MIN_MUNICIPIOS = 1
    MAX_MUNICIPIOS_PLAUSIVEL = 1000  # Maior distribuidora
    MIN_CONFIDENCE = 0.5
    MIN_AREA_KM2 = 10  # Cooperativa pequena
    MAX_AREA_KM2 = 1000000  # Área do Brasil ~8.5M km²

    def __init__(self):
        self.validation_results = []
        self.quality_scores = []

    def validate_record(self, record: Dict) -> Dict:
        """
        Valida um registro individual

        Returns:
            Dict com resultado da validação
        """
        validations = {
            "cnpj": record.get("cnpj"),
            "sigla": record.get("sigla"),
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "errors": [],
            "warnings": [],
            "quality_score": 0.0,
            "status": "UNKNOWN",
        }

        # Check 1: Estados válidos
        estados = record.get("estados", [])
        if estados:
            valid_estados = all(e in self.VALID_STATES for e in estados)
            validations["checks"]["estados_validos"] = valid_estados

            if not valid_estados:
                invalid = [e for e in estados if e not in self.VALID_STATES]
                validations["errors"].append(f"Estados inválidos: {invalid}")
        else:
            validations["checks"]["estados_validos"] = False
            validations["warnings"].append("Nenhum estado informado")

        # Check 2: Total de municípios plausível
        total_mun = record.get("total_municipios", 0)
        validations["checks"]["municipios_plausivel"] = (
            self.MIN_MUNICIPIOS <= total_mun <= self.MAX_MUNICIPIOS_PLAUSIVEL
        )

        if total_mun == 0:
            validations["warnings"].append("Total de municípios não informado")
        elif total_mun > self.MAX_MUNICIPIOS_PLAUSIVEL:
            validations["errors"].append(
                f"Total de municípios implausível: {total_mun}"
            )

        # Check 3: Área de concessão plausível
        area = record.get("area_concessao_km2")
        if area:
            validations["checks"]["area_plausivel"] = (
                self.MIN_AREA_KM2 <= area <= self.MAX_AREA_KM2
            )

            if area > self.MAX_AREA_KM2:
                validations["errors"].append(
                    f"Área de concessão implausível: {area} km²"
                )
        else:
            validations["checks"]["area_plausivel"] = None
            validations["warnings"].append("Área de concessão não informada")

        # Check 4: Confidence score
        confidence = record.get("confidence_score", 0.0)
        validations["checks"]["confidence_adequada"] = confidence >= self.MIN_CONFIDENCE

        if confidence < self.MIN_CONFIDENCE:
            validations["warnings"].append(
                f"Baixa confiança na extração: {confidence:.2f}"
            )

        # Check 5: Coordenadas geográficas
        has_coords = all(
            record.get(k) is not None for k in ["lat_centro", "lng_centro"]
        )
        validations["checks"]["coordenadas_presentes"] = has_coords

        if not has_coords:
            validations["warnings"].append("Coordenadas não calculadas")

        # Check 6: Consistência estados vs municípios
        if estados and total_mun > 0:
            # Heurística: se tem muitos estados, deve ter muitos municípios
            expected_min = len(estados) * 10  # ~10 municípios por estado

            if total_mun < expected_min:
                validations["warnings"].append(
                    f"Poucos municípios para {len(estados)} estado(s): "
                    f"{total_mun} (esperado >={expected_min})"
                )

        # Calcular quality score (0-100)
        checks_passed = sum(1 for v in validations["checks"].values() if v is True)
        total_checks = sum(1 for v in validations["checks"].values() if v is not None)

        if total_checks > 0:
            base_score = (checks_passed / total_checks) * 100

            # Penalizar por erros e warnings
            penalty = len(validations["errors"]) * 20
            penalty += len(validations["warnings"]) * 5

            validations["quality_score"] = max(0, base_score - penalty)

        # Determinar status final
        if validations["quality_score"] >= 80:
            validations["status"] = "EXCELENTE"
        elif validations["quality_score"] >= 60:
            validations["status"] = "BOM"
        elif validations["quality_score"] >= 40:
            validations["status"] = "REGULAR"
        elif validations["quality_score"] >= 20:
            validations["status"] = "RUIM"
        else:
            validations["status"] = "CRÍTICO"

        self.validation_results.append(validations)
        self.quality_scores.append(validations["quality_score"])

        return validations

    def validate_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valida dataset completo"""
        print("\n🔍 Validando qualidade dos dados...")

        for idx, row in df.iterrows():
            record = row.to_dict()
            self.validate_record(record)

        # Criar DataFrame de resultados
        df_validations = pd.DataFrame(self.validation_results)

        return df_validations

    def generate_quality_report(self) -> Dict:
        """Gera relatório de qualidade"""

        if not self.quality_scores:
            return {"status": "NO_DATA", "message": "Nenhum dado validado"}

        total = len(self.quality_scores)

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_records": total,
            "quality_metrics": {
                "score_medio": sum(self.quality_scores) / total,
                "score_minimo": min(self.quality_scores),
                "score_maximo": max(self.quality_scores),
            },
            "status_distribution": {},
            "top_issues": self._get_top_issues(),
            "recommendations": self._generate_recommendations(),
        }

        # Distribuição por status
        for result in self.validation_results:
            status = result["status"]
            report["status_distribution"][status] = (
                report["status_distribution"].get(status, 0) + 1
            )

        return report

    def _get_top_issues(self) -> List[Dict]:
        """Identifica principais problemas"""
        error_counts = {}
        warning_counts = {}

        for result in self.validation_results:
            for error in result["errors"]:
                error_counts[error] = error_counts.get(error, 0) + 1

            for warning in result["warnings"]:
                warning_counts[warning] = warning_counts.get(warning, 0) + 1

        top_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        top_warnings = sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]

        return {
            "top_errors": [{"issue": k, "count": v} for k, v in top_errors],
            "top_warnings": [{"issue": k, "count": v} for k, v in top_warnings],
        }

    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas nos problemas encontrados"""
        recommendations = []

        avg_score = sum(self.quality_scores) / len(self.quality_scores)

        if avg_score < 50:
            recommendations.append(
                "Score médio baixo (<50). Considere re-executar a extração "
                "com prompts LLM mais específicos."
            )

        # Contar problemas comuns
        no_estados = sum(
            1 for r in self.validation_results if not r["checks"].get("estados_validos")
        )

        if no_estados > len(self.validation_results) * 0.3:
            recommendations.append(
                f"{no_estados} registros sem estados válidos (>30%). "
                "Verifique mapeamento de estados no extrator."
            )

        no_coords = sum(
            1
            for r in self.validation_results
            if not r["checks"].get("coordenadas_presentes")
        )

        if no_coords > 0:
            recommendations.append(
                f"{no_coords} registros sem coordenadas. "
                "Execute cálculo de coordenadas geográficas."
            )

        return recommendations


def generate_markdown_report(
    df: pd.DataFrame, validations: pd.DataFrame, quality_report: Dict, output_path: Path
):
    """Gera relatório markdown completo"""

    md = []
    md.append("# 📊 Relatório de Qualidade - Extração Territorial ANEEL")
    md.append("")
    md.append(f"**Data**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    md.append(f"**Total de Registros**: {len(df)}")
    md.append("")
    md.append("---")
    md.append("")

    # Métricas de Qualidade
    md.append("## 🎯 Métricas de Qualidade")
    md.append("")

    metrics = quality_report["quality_metrics"]
    md.append(f"- **Score Médio**: {metrics['score_medio']:.1f}/100")
    md.append(f"- **Score Mínimo**: {metrics['score_minimo']:.1f}/100")
    md.append(f"- **Score Máximo**: {metrics['score_maximo']:.1f}/100")
    md.append("")

    # Distribuição por Status
    md.append("## 📈 Distribuição por Status")
    md.append("")
    md.append("| Status | Quantidade | Percentual |")
    md.append("|--------|------------|------------|")

    total = quality_report["total_records"]
    for status, count in quality_report["status_distribution"].items():
        pct = (count / total) * 100
        md.append(f"| {status} | {count} | {pct:.1f}% |")

    md.append("")

    # Principais Problemas
    md.append("## ⚠️ Principais Problemas")
    md.append("")

    top_issues = quality_report["top_issues"]

    if top_issues["top_errors"]:
        md.append("### Erros Críticos")
        md.append("")
        for issue in top_issues["top_errors"]:
            md.append(f"- **{issue['issue']}**: {issue['count']} ocorrências")
        md.append("")

    if top_issues["top_warnings"]:
        md.append("### Avisos")
        md.append("")
        for issue in top_issues["top_warnings"]:
            md.append(f"- {issue['issue']}: {issue['count']} ocorrências")
        md.append("")

    # Recomendações
    md.append("## 💡 Recomendações")
    md.append("")

    for rec in quality_report["recommendations"]:
        md.append(f"1. {rec}")

    md.append("")
    md.append("---")
    md.append("")

    # Top 10 Melhores
    md.append("## ✅ Top 10 Distribuidoras (Melhor Qualidade)")
    md.append("")
    md.append("| Posição | Sigla | Razão Social | Score | Status |")
    md.append("|---------|-------|--------------|-------|--------|")

    top_10 = validations.nlargest(10, "quality_score")
    for idx, (_, row) in enumerate(top_10.iterrows(), 1):
        md.append(
            f"| {idx} | {row['sigla']} | "
            f"{df[df['CNPJ'] == row['cnpj']]['Razão Social'].iloc[0][:40]} | "
            f"{row['quality_score']:.1f} | {row['status']} |"
        )

    md.append("")

    # Bottom 10
    md.append("## ❌ Bottom 10 Distribuidoras (Requer Atenção)")
    md.append("")
    md.append("| Posição | Sigla | Razão Social | Score | Status |")
    md.append("|---------|-------|--------------|-------|--------|")

    bottom_10 = validations.nsmallest(10, "quality_score")
    for idx, (_, row) in enumerate(bottom_10.iterrows(), 1):
        md.append(
            f"| {idx} | {row['sigla']} | "
            f"{df[df['CNPJ'] == row['cnpj']]['Razão Social'].iloc[0][:40]} | "
            f"{row['quality_score']:.1f} | {row['status']} |"
        )

    md.append("")
    md.append("---")
    md.append("")
    md.append("*Relatório gerado automaticamente pelo sistema YSH B2B*")

    # Salvar
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"✅ Relatório salvo: {output_path}")


if __name__ == "__main__":
    # Exemplo de uso
    print("=" * 70)
    print("ANEEL DISTRIBUIDORAS - QUALITY ASSURANCE")
    print("=" * 70)
    print()

    # Carregar dados
    base_dir = Path(__file__).parent
    input_file = base_dir / "aneel_distribuidoras_360_territorial_enriched.csv"

    if not input_file.exists():
        print(f"❌ Arquivo não encontrado: {input_file}")
        print("Execute primeiro: python aneel_territorial_extractor.py")
        exit(1)

    df = pd.read_csv(input_file, sep=";")
    print(f"📂 {len(df)} registros carregados")
    print()

    # Validar
    validator = DataQualityValidator()
    df_validations = validator.validate_dataset(df)

    # Gerar relatório de qualidade
    quality_report = validator.generate_quality_report()

    print("\n📊 RESUMO DE QUALIDADE:")
    print(f"Score médio: {quality_report['quality_metrics']['score_medio']:.1f}/100")
    print(f"Distribuição por status:")
    for status, count in quality_report["status_distribution"].items():
        pct = (count / quality_report["total_records"]) * 100
        print(f"  - {status}: {count} ({pct:.1f}%)")
    print()

    # Salvar validações
    validations_file = base_dir / "aneel_distribuidoras_validations.csv"
    df_validations.to_csv(validations_file, sep=";", index=False)
    print(f"✅ Validações salvas: {validations_file}")

    # Salvar relatório JSON
    report_json = base_dir / "quality_report.json"
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(quality_report, f, ensure_ascii=False, indent=2)
    print(f"✅ Relatório JSON salvo: {report_json}")

    # Gerar relatório markdown
    report_md = base_dir / "QUALITY_REPORT.md"
    generate_markdown_report(df, df_validations, quality_report, report_md)

    print("\n✅ QA CONCLUÍDO")
