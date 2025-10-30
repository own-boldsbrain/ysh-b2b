#!/usr/bin/env python3
"""Upload de produtos únicos consolidados para o AWS DynamoDB.

Este script cria (se necessário) uma tabela otimizada para leitura com GSIs
por fabricante e tipo de equipamento e grava os produtos consolidados com
metadados completos de pricing e imagens. Pensado para lotes pequenos de
produtos únicos de alta qualidade.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable, TypeAlias

import boto3  # type: ignore[import]
from botocore.exceptions import ClientError  # type: ignore[import]


# Diretórios
ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT_DIR / "unique-products-consolidated.json"
REPORT_FILE = ROOT_DIR / "UNIQUE_PRODUCTS_DYNAMODB_REPORT.json"

# Configurações DynamoDB
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
TABLE_NAME = os.getenv("UNIQUE_PRODUCTS_TABLE", "ysh-unique-products")
GSI_MANUFACTURER = "GSI_MANUFACTURER"
GSI_EQUIPMENT = "GSI_EQUIPMENT_TYPE"

# Tipos auxiliares
JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | dict[str, "JSONValue"] | list["JSONValue"]
DynamoScalar: TypeAlias = str | Decimal | bool
DynamoValue: TypeAlias = (
    DynamoScalar | list["DynamoValue"] | dict[str, "DynamoValue"]
)

# Helpers numéricos
TWOPLACES = Decimal("0.01")


def to_decimal(value: float | int | str) -> Decimal:
    """Converte valores numéricos para Decimal com duas casas."""

    return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def normalize_manufacturer(name: str | None) -> str:
    if not name:
        return "UNKNOWN"
    return name.strip().strip(":").upper()


def normalize_equipment_type(value: str | None) -> str:
    if not value:
        return "unknown"
    return value.strip().lower().replace(" ", "_")


def normalize_image_url(url: str) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if url.startswith("/"):
        return "https://cdn.yellosolarhub.com" + url
    return url


def remove_none(value: Any) -> Any:  # noqa: ANN401
    """Remove valores None de estruturas aninhadas."""

    if isinstance(value, dict):
        cleaned: dict[str, Any] = {}
        for key, val in value.items():
            converted = remove_none(val)
            if converted is not None:
                cleaned[key] = converted
        return cleaned
    if isinstance(value, list):
        cleaned_list = [remove_none(item) for item in value]
        return [item for item in cleaned_list if item is not None]
    return value


def convert_numeric(value: Any) -> Any:  # noqa: ANN401
    """Converte floats recursivamente em Decimal aceito pelo DynamoDB."""

    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return to_decimal(value)
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, (str, bool)):
        return value
    if isinstance(value, list):
        return _convert_list(value)
    if isinstance(value, dict):
        return _convert_dict(value)
    return value


def _convert_list(values: list[Any]) -> list[Any]:  # noqa: ANN401
    result: list[Any] = []
    for item in values:
        converted = convert_numeric(item)
        if converted is not None:
            result.append(converted)
    return result


def _convert_dict(values: dict[str, Any]) -> dict[str, Any]:  # noqa: ANN401
    result: dict[str, Any] = {}
    for key, val in values.items():
        converted = convert_numeric(val)
        if converted is not None:
            result[key] = converted
    return result


def compute_price_stats(prices: Iterable[float]) -> dict[str, Decimal]:
    values = [to_decimal(p) for p in prices if p is not None]
    if not values:
        return {}

    sorted_vals = sorted(values)
    min_price = sorted_vals[0]
    max_price = sorted_vals[-1]
    count = len(sorted_vals)
    total = sum(sorted_vals, Decimal("0"))
    avg_price = (
        total / Decimal(count)
    ).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    mid = len(sorted_vals) // 2
    if len(sorted_vals) % 2 == 1:
        median_price = sorted_vals[mid]
    else:
        median_price = (
            (sorted_vals[mid - 1] + sorted_vals[mid]) / Decimal(2)
        ).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    return {
        "min": min_price,
        "max": max_price,
        "avg": avg_price,
        "median": median_price,
        "latest": sorted_vals[-1],
    }


def load_products() -> list[dict[str, Any]]:
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo de origem não encontrado: {SOURCE_FILE}"
        )

    with SOURCE_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise TypeError(
            "O arquivo de origem deve conter uma lista de produtos"
        )

    return data


def build_distributor_summary(
    raw_distributors: dict[str, Any]
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for name, payload in raw_distributors.items():
        prices = payload.get("prices") or []
        price_stats = compute_price_stats(prices)
        source_files = payload.get("source_files", []) or []
        if not isinstance(source_files, list):
            source_files = [source_files]
        summary[name] = {
            "offer_count": int(payload.get("count", len(prices))),
            "price_stats": price_stats,
            "source_files": source_files[:10],
        }
    return summary


def build_media_payload(media: dict[str, Any]) -> dict[str, Any]:
    primary = media.get("primary_image")
    image_sources = media.get("image_sources") or []
    normalized_images = [
        normalize_image_url(str(url))
        for url in image_sources
        if isinstance(url, str)
    ]

    return {
        "primary_image": normalize_image_url(primary) if primary else None,
        "image_count": media.get("image_count", len(normalized_images)),
        "images": normalized_images[:100],
        "all_images": normalized_images,
    }


def transform_product(product: dict[str, Any]) -> dict[str, Any]:
    manufacturer_label = str(product.get("manufacturer") or "UNKNOWN")
    manufacturer_normalized = normalize_manufacturer(manufacturer_label)
    equipment_type = normalize_equipment_type(product.get("equipment_type"))

    specs = product.get("specs", {})
    pricing = product.get("pricing", {})
    price_range = pricing.get("price_range_brl", {})

    tag_candidates = {
        manufacturer_normalized,
        manufacturer_label,
        equipment_type,
        f"{(specs.get('power_kwp') or 0):.2f}kwp",
    }

    keyword_candidates = {
        manufacturer_normalized,
        manufacturer_label,
        product.get("name", ""),
        product.get("description", {}).get("primary", ""),
    }

    transformed: dict[str, Any] = {
        "sku": product["sku"],
        "name": product.get("name"),
        "manufacturer": manufacturer_normalized,
        "manufacturer_label": manufacturer_label,
        "equipment_type": equipment_type,
        "equipment_type_label": product.get("equipment_type"),
        "power_kwp": specs.get("power_kwp"),
        "voltage_v": specs.get("voltage_v"),
        "price_min": price_range.get("min"),
        "price_max": price_range.get("max"),
        "price_avg": price_range.get("avg"),
        "distributor_count": pricing.get("distributor_count"),
        "total_offers": pricing.get("total_offers"),
        "description_primary": product.get("description", {}).get("primary"),
        "description_technical": product.get("description", {}).get(
            "technical_summary"
        ),
        "components": product.get("components"),
        "specs": specs,
        "distributors_summary": build_distributor_summary(
            product.get("distributors", {})
        ),
        "pricing_metadata": {
            "price_range_brl": price_range,
        },
        "media": build_media_payload(product.get("media", {})),
        "tags": [
            tag.strip().lower()
            for tag in tag_candidates
            if isinstance(tag, str) and tag.strip()
        ],
        "search_keywords": [
            keyword.strip()
            for keyword in keyword_candidates
            if isinstance(keyword, str) and keyword.strip()
        ],
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "data_version": "unique-products/v1",
    }

    # Limitar keywords a strings não vazias
    transformed["search_keywords"] = [
        kw.strip()
        for kw in transformed["search_keywords"]
        if isinstance(kw, str) and kw.strip()
    ]

    transformed["tags"] = [
        tag.strip().lower()
        for tag in transformed.get("tags", [])
        if isinstance(tag, str) and tag.strip()
    ]

    transformed = convert_numeric(transformed)
    transformed = remove_none(transformed)
    return transformed


def ensure_table(dynamodb_resource) -> Any:
    table = dynamodb_resource.Table(TABLE_NAME)
    try:
        table.load()
        print(f"✅ Tabela existente encontrada: {TABLE_NAME}")
        return table
    except ClientError as error:
        if error.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    print(f"🆕 Criando tabela DynamoDB: {TABLE_NAME}")
    table = dynamodb_resource.create_table(
        TableName=TABLE_NAME,
        AttributeDefinitions=[
            {"AttributeName": "sku", "AttributeType": "S"},
            {"AttributeName": "manufacturer", "AttributeType": "S"},
            {"AttributeName": "equipment_type", "AttributeType": "S"},
        ],
        KeySchema=[{"AttributeName": "sku", "KeyType": "HASH"}],
        GlobalSecondaryIndexes=[
            {
                "IndexName": GSI_MANUFACTURER,
                "KeySchema": [
                    {"AttributeName": "manufacturer", "KeyType": "HASH"},
                    {"AttributeName": "sku", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": GSI_EQUIPMENT,
                "KeySchema": [
                    {"AttributeName": "equipment_type", "KeyType": "HASH"},
                    {"AttributeName": "sku", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        BillingMode="PAY_PER_REQUEST",
        Tags=[
            {"Key": "project", "Value": "ysh-b2b"},
            {"Key": "dataset", "Value": "unique-products"},
        ],
    )

    table.wait_until_exists()
    print("✅ Tabela criada e pronta para uso")
    return table


@dataclass
class UploadReport:
    total_products: int
    uploaded: int
    aws_region: str
    table_name: str
    failed: int
    manufacturer_breakdown: dict[str, int]
    equipment_breakdown: dict[str, int]


def generate_report(
    items: list[dict[str, Any]], uploaded: int, failed: int
) -> UploadReport:
    manufacturer_counts: dict[str, int] = {}
    equipment_counts: dict[str, int] = {}
    for item in items:
        manufacturer = item.get("manufacturer", "UNKNOWN")
        equipment = item.get("equipment_type", "unknown")
        manufacturer_counts[manufacturer] = (
            manufacturer_counts.get(manufacturer, 0) + 1
        )
        equipment_counts[equipment] = (
            equipment_counts.get(equipment, 0) + 1
        )

    return UploadReport(
        total_products=len(items),
        uploaded=uploaded,
        failed=failed,
        aws_region=AWS_REGION,
        table_name=TABLE_NAME,
        manufacturer_breakdown=manufacturer_counts,
        equipment_breakdown=equipment_counts,
    )


def save_report(
    report: UploadReport, sample_items: list[dict[str, Any]]
) -> None:
    def _json_safe(value: Any) -> Any:
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, dict):
            return {key: _json_safe(val) for key, val in value.items()}
        if isinstance(value, list):
            return [_json_safe(item) for item in value]
        return value

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "aws_region": report.aws_region,
        "table_name": report.table_name,
        "total_products": report.total_products,
        "uploaded": report.uploaded,
        "failed": report.failed,
        "manufacturer_breakdown": report.manufacturer_breakdown,
        "equipment_breakdown": report.equipment_breakdown,
        "sample_items": sample_items[:3],
    }

    safe_payload = _json_safe(payload)

    REPORT_FILE.write_text(
        json.dumps(safe_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"💾 Relatório salvo em {REPORT_FILE.name}")


def main() -> None:
    print("🚀 Upload de produtos únicos para DynamoDB")
    print("=" * 72)

    products = load_products()
    transformed_items = [transform_product(product) for product in products]

    print(f"• Produtos carregados: {len(transformed_items)}")

    session = boto3.Session(region_name=AWS_REGION)
    dynamodb = session.resource("dynamodb")
    table = ensure_table(dynamodb)

    uploaded = 0
    failed = 0
    with table.batch_writer(overwrite_by_pkeys=["sku"]) as batch:
        for item in transformed_items:
            try:
                batch.put_item(Item=item)
                uploaded += 1
            except ClientError as error:
                failed += 1
                print(f"⚠️  Falha ao enviar {item['sku']}: {error}")

    print("=" * 72)
    print(f"✅ Upload concluído: {uploaded} itens")
    if failed:
        print(f"⚠️  Falhas: {failed}")

    report = generate_report(transformed_items, uploaded, failed)
    save_report(report, transformed_items)


if __name__ == "__main__":
    main()
