#!/usr/bin/env node

/**
 * Pipeline Integrado de Imagens
 * - Integra extração de fabricantes + distribuidores
 * - Sistema de fallback hierárquico
 * - Padronização completa de nomenclatura
 * - Prioriza qualidade e fonte oficial
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import {
  extractManufacturerImages,
  ProductInfo,
  ImageResult,
} from "./extract-manufacturer-images.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_PATH = path.join(__dirname, "..");
const INVENTORY_PATH = path.join(ROOT_PATH, "data/products-inventory");
const OUTPUT_DIR = path.join(ROOT_PATH, "static/products-unified");

interface InventoryProduct {
  sku?: string;
  SKU?: string;
  codigo?: string;
  fabricante?: string;
  manufacturer?: string;
  marca?: string;
  modelo?: string;
  model?: string;
  potencia?: string;
  power?: string;
  categoria?: string;
  category?: string;
  tipo?: string;
  type?: string;
  image?: string;
  image_url?: string;
  imagem?: string;
}

function normalizeManufacturerName(name: string): string {
  const mapping: Record<string, string> = {
    "longi solar": "LONGI",
    longi: "LONGI",
    growatt: "GROWATT",
    sungrow: "SUNGROW",
    risen: "RISEN",
    "risen energy": "RISEN",
    jinko: "JINKO",
    jinkosolar: "JINKO",
    trina: "TRINA",
    "trina solar": "TRINA",
    "canadian solar": "CANADIAN-SOLAR",
    canadian: "CANADIAN-SOLAR",
    byd: "BYD",
    fronius: "FRONIUS",
    deye: "DEYE",
    solis: "SOLIS",
    huawei: "HUAWEI",
    pylontech: "PYLONTECH",
    dyness: "DYNESS",
    enphase: "ENPHASE",
    fortlev: "FORTLEV",
  };

  const normalized = name.toLowerCase().trim();
  return mapping[normalized] || name.toUpperCase();
}

function extractPowerFromString(str: string): string | undefined {
  const patterns = [
    /(\d+\.?\d*)\s*kW/i,
    /(\d+\.?\d*)\s*W/i,
    /(\d+)\s*Wp/i,
    /-(\d+)W/,
    /-(\d+)kW/,
  ];

  for (const pattern of patterns) {
    const match = str.match(pattern);
    if (match) {
      return match[1];
    }
  }

  return undefined;
}

function categorizeProduct(product: InventoryProduct): string {
  const type = (
    product.tipo ||
    product.type ||
    product.categoria ||
    product.category ||
    ""
  ).toLowerCase();

  if (type.includes("painel") || type.includes("panel") || type.includes("módulo")) {
    return "panels";
  }

  if (
    type.includes("inversor") ||
    type.includes("inverter") ||
    type.includes("microinversor")
  ) {
    return "inverters";
  }

  if (type.includes("bateria") || type.includes("battery")) {
    return "batteries";
  }

  if (type.includes("kit")) {
    return "kits";
  }

  if (type.includes("estrutura") || type.includes("structure")) {
    return "structures";
  }

  if (type.includes("cabo") || type.includes("cable")) {
    return "cables";
  }

  return "others";
}

function scanInventoryProducts(): ProductInfo[] {
  console.log("\n📦 Escaneando Inventários\n");

  const products: ProductInfo[] = [];
  const seenSkus = new Set<string>();

  function scanDir(dirPath: string, depth = 0) {
    if (depth > 4 || !fs.existsSync(dirPath)) return;

    const entries = fs.readdirSync(dirPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry.name);

      if (entry.isDirectory()) {
        scanDir(fullPath, depth + 1);
      } else if (
        entry.isFile() &&
        entry.name.endsWith(".json") &&
        !entry.name.includes("schema") &&
        !entry.name.includes("report")
      ) {
        try {
          const data = JSON.parse(fs.readFileSync(fullPath, "utf8"));

          const extractProducts = (obj: any): InventoryProduct[] => {
            if (Array.isArray(obj)) {
              return obj.flatMap(extractProducts);
            }

            if (obj && typeof obj === "object") {
              if (obj.sku || obj.SKU || obj.codigo) {
                return [obj as InventoryProduct];
              }

              if (obj.products || obj.items) {
                return extractProducts(obj.products || obj.items);
              }

              return Object.values(obj).flatMap(extractProducts);
            }

            return [];
          };

          const foundProducts = extractProducts(data);

          for (const prod of foundProducts) {
            const sku = prod.sku || prod.SKU || prod.codigo;
            if (!sku || seenSkus.has(sku)) continue;

            seenSkus.add(sku);

            const manufacturer =
              prod.fabricante || prod.manufacturer || prod.marca || "UNKNOWN";

            const normalizedManufacturer = normalizeManufacturerName(manufacturer);

            products.push({
              sku,
              manufacturer: normalizedManufacturer,
              model: prod.modelo || prod.model,
              power:
                prod.potencia ||
                prod.power ||
                extractPowerFromString(sku) ||
                extractPowerFromString(prod.modelo || prod.model || ""),
              category: categorizeProduct(prod),
              distributor_url: prod.image || prod.image_url || prod.imagem,
            });
          }
        } catch (error) {
          // Ignorar arquivos inválidos
        }
      }
    }
  }

  scanDir(INVENTORY_PATH);

  console.log(`✓ ${products.length} produtos encontrados\n`);

  return products;
}

async function runUnifiedPipeline() {
  console.log("\n🔄 PIPELINE UNIFICADO DE IMAGENS\n");
  console.log("═".repeat(70));

  try {
    // 1. Escanear inventários
    console.log("\n📋 ETAPA 1: Coleta de Produtos\n");

    const products = scanInventoryProducts();

    // Agrupar por fabricante
    const byManufacturer: Record<string, ProductInfo[]> = {};

    for (const product of products) {
      if (!byManufacturer[product.manufacturer]) {
        byManufacturer[product.manufacturer] = [];
      }
      byManufacturer[product.manufacturer].push(product);
    }

    console.log(`Produtos por Fabricante:`);
    const sorted = Object.entries(byManufacturer).sort((a, b) => b[1].length - a[1].length);

    for (const [mfr, prods] of sorted.slice(0, 10)) {
      console.log(`   • ${mfr}: ${prods.length}`);
    }

    if (sorted.length > 10) {
      console.log(`   ... e mais ${sorted.length - 10} fabricantes`);
    }

    console.log("");

    // 2. Extrair imagens de fabricantes
    console.log("\n🏭 ETAPA 2: Extração de Fabricantes\n");

    const results = await extractManufacturerImages(products);

    // 3. Gerar estrutura unificada
    console.log("\n📁 ETAPA 3: Estrutura Unificada\n");

    if (!fs.existsSync(OUTPUT_DIR)) {
      fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    const unifiedMap: Record<string, any> = {
      metadata: {
        timestamp: new Date().toISOString(),
        total_products: products.length,
        source_priority: ["official", "cdn", "distributor", "placeholder"],
      },
      images: {},
      statistics: {
        by_manufacturer: {},
        by_category: {},
        by_source: {
          official: 0,
          cdn: 0,
          distributor: 0,
          placeholder: 0,
        },
      },
    };

    for (const result of results) {
      const key = `${result.product.manufacturer}-${result.product.sku}`.toUpperCase();

      unifiedMap.images[key] = {
        sku: result.product.sku,
        manufacturer: result.product.manufacturer,
        model: result.product.model,
        power: result.product.power,
        category: result.product.category,
        source: result.source,
        url: result.url,
        local_path: result.local_path
          ? path.relative(ROOT_PATH, result.local_path)
          : null,
        success: result.success,
      };

      // Estatísticas
      unifiedMap.statistics.by_source[result.source]++;

      if (!unifiedMap.statistics.by_manufacturer[result.product.manufacturer]) {
        unifiedMap.statistics.by_manufacturer[result.product.manufacturer] = 0;
      }
      unifiedMap.statistics.by_manufacturer[result.product.manufacturer]++;

      if (!unifiedMap.statistics.by_category[result.product.category || "unknown"]) {
        unifiedMap.statistics.by_category[result.product.category || "unknown"] = 0;
      }
      unifiedMap.statistics.by_category[result.product.category || "unknown"]++;
    }

    // Salvar mapeamento unificado
    const mapPath = path.join(OUTPUT_DIR, "unified-image-map.json");
    fs.writeFileSync(mapPath, JSON.stringify(unifiedMap, null, 2));

    console.log(`✓ Mapeamento unificado salvo: ${mapPath}\n`);

    // 4. Resultado final
    console.log("═".repeat(70));
    console.log("\n✅ PIPELINE UNIFICADO CONCLUÍDO!\n");

    console.log(`📊 Resumo:`);
    console.log(`   • Total de produtos: ${products.length}`);
    console.log(
      `   • Imagens oficiais: ${unifiedMap.statistics.by_source.official}`
    );
    console.log(`   • CDN: ${unifiedMap.statistics.by_source.cdn}`);
    console.log(
      `   • Distribuidores: ${unifiedMap.statistics.by_source.distributor}`
    );
    console.log(
      `   • Placeholders: ${unifiedMap.statistics.by_source.placeholder}\n`
    );

    const officialRate =
      ((unifiedMap.statistics.by_source.official +
        unifiedMap.statistics.by_source.cdn) /
        products.length) *
      100;

    console.log(`🎯 Taxa de Fontes Oficiais: ${officialRate.toFixed(1)}%\n`);

    process.exit(0);
  } catch (error) {
    console.error("\n❌ ERRO NO PIPELINE:\n");
    console.error(error instanceof Error ? error.message : String(error));
    console.error(error instanceof Error ? error.stack : "");
    process.exit(1);
  }
}

runUnifiedPipeline().catch(console.error);
