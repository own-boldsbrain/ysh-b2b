#!/usr/bin/env node

/**
 * Script para analisar e normalizar dados antes do upload
 * - Analisa SKUs no CSV
 * - Analisa imagens disponíveis
 * - Verifica correspondência entre SKUs e imagens
 * - Gera relatório de normalização
 * - Cria mapeamento otimizado
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { parse } from "csv-parse/sync";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Paths
const CSV_PATH = path.join(
  __dirname,
  "../data/products-inventory/exports/csv/all_products.csv"
);
const IMAGES_BASE_PATH = path.join(__dirname, "../static/products");

// Extensões de imagem válidas
const IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".gif"];

// Funções auxiliares
function normalizeFilename(filename) {
  return filename
    .toLowerCase()
    .replace(/[^\w\d.-]/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_|_$/g, "");
}

function extractSKUFromFilename(filename) {
  // Padrões comuns de SKU em nomes de arquivo
  const patterns = [
    /sku_(\d+)/, // sku_123456
    /IMAGE_PRODUCT_(\d+)/, // IMAGE_PRODUCT_600123
    /^(\d{5,})/, // 123456.jpg
    /NEO-(\d+)/, // NEO-21742
    /fortlev_kit_(\d+)/, // fortlev_kit_001
  ];

  const basename = path.basename(filename, path.extname(filename));

  for (const pattern of patterns) {
    const match = basename.match(pattern);
    if (match) return match[1];
  }

  return null;
}

function categorizeImage(filename, filepath) {
  const lowerName = filename.toLowerCase();

  if (lowerName.includes("inverter") || lowerName.includes("inv")) {
    return "inverters";
  } else if (lowerName.includes("panel") || lowerName.includes("painel")) {
    return "panels";
  } else if (lowerName.includes("kit")) {
    return "kits";
  } else if (lowerName.includes("charger") || lowerName.includes("controller")) {
    return "chargers";
  } else if (lowerName.includes("cable") || lowerName.includes("station")) {
    return "accessories";
  }

  // Tentar inferir da estrutura de diretório
  const parts = filepath.split(path.sep);
  const categoryIndex = parts.findIndex((p) => p === "products");

  if (categoryIndex >= 0 && parts[categoryIndex + 1]) {
    return parts[categoryIndex + 1];
  }

  return "other";
}

async function analyzeCSV() {
  console.log("📊 Analisando CSV de produtos...\n");

  if (!fs.existsSync(CSV_PATH)) {
    throw new Error(`CSV não encontrado: ${CSV_PATH}`);
  }

  const csvContent = fs.readFileSync(CSV_PATH, "utf-8");
  const records = parse(csvContent, {
    columns: true,
    skip_empty_lines: true,
  });

  console.log(`✓ ${records.length} produtos encontrados no CSV\n`);

  // Análise de estrutura
  const analysis = {
    total: records.length,
    byDistributor: {},
    byCategory: {},
    withImages: 0,
    withoutImages: 0,
    imageUrls: [],
    uniqueIds: new Set(),
  };

  for (const record of records) {
    const distributor = record.distributor || "unknown";
    const category = record.category || "unknown";

    analysis.byDistributor[distributor] =
      (analysis.byDistributor[distributor] || 0) + 1;
    analysis.byCategory[category] = (analysis.byCategory[category] || 0) + 1;

    if (record.id) {
      analysis.uniqueIds.add(record.id);
    }

    if (record.image_url || record.panel_image || record.inverter_image) {
      analysis.withImages++;
      if (record.image_url) analysis.imageUrls.push(record.image_url);
      if (record.panel_image) analysis.imageUrls.push(record.panel_image);
      if (record.inverter_image) analysis.imageUrls.push(record.inverter_image);
    } else {
      analysis.withoutImages++;
    }
  }

  console.log("📈 Análise de SKUs:");
  console.log(`   • Total de produtos: ${analysis.total}`);
  console.log(`   • IDs únicos: ${analysis.uniqueIds.size}`);
  console.log(`   • Com imagens: ${analysis.withImages}`);
  console.log(`   • Sem imagens: ${analysis.withoutImages}`);
  console.log(`   • URLs de imagens: ${analysis.imageUrls.length}\n`);

  console.log("📦 Por distribuidor:");
  Object.entries(analysis.byDistributor)
    .sort((a, b) => b[1] - a[1])
    .forEach(([dist, count]) => {
      console.log(`   • ${dist}: ${count}`);
    });

  console.log("\n📂 Por categoria:");
  Object.entries(analysis.byCategory)
    .sort((a, b) => b[1] - a[1])
    .forEach(([cat, count]) => {
      console.log(`   • ${cat}: ${count}`);
    });

  return { records, analysis };
}

async function analyzeImages() {
  console.log("\n🖼️  Analisando imagens disponíveis...\n");

  if (!fs.existsSync(IMAGES_BASE_PATH)) {
    console.warn(`⚠️  Diretório de imagens não encontrado: ${IMAGES_BASE_PATH}`);
    return { images: [], analysis: {} };
  }

  const images = [];
  const analysis = {
    total: 0,
    byCategory: {},
    byExtension: {},
    withSKU: 0,
    withoutSKU: 0,
    skuMapping: {},
  };

  function scanDirectory(dir, relPath = "") {
    const entries = fs.readdirSync(dir);

    for (const entry of entries) {
      const fullPath = path.join(dir, entry);
      const relativePath = path.join(relPath, entry);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory()) {
        scanDirectory(fullPath, relativePath);
      } else if (stat.isFile()) {
        const ext = path.extname(entry).toLowerCase();
        if (!IMAGE_EXTENSIONS.includes(ext)) continue;

        const category = categorizeImage(entry, fullPath);
        const sku = extractSKUFromFilename(entry);

        const imageInfo = {
          filename: entry,
          path: fullPath,
          relativePath,
          size: stat.size,
          extension: ext,
          category,
          sku,
        };

        images.push(imageInfo);
        analysis.total++;

        analysis.byCategory[category] = (analysis.byCategory[category] || 0) + 1;
        analysis.byExtension[ext] = (analysis.byExtension[ext] || 0) + 1;

        if (sku) {
          analysis.withSKU++;
          if (!analysis.skuMapping[sku]) {
            analysis.skuMapping[sku] = [];
          }
          analysis.skuMapping[sku].push(imageInfo);
        } else {
          analysis.withoutSKU++;
        }
      }
    }
  }

  scanDirectory(IMAGES_BASE_PATH);

  console.log("📈 Análise de imagens:");
  console.log(`   • Total de imagens: ${analysis.total}`);
  console.log(`   • Com SKU identificado: ${analysis.withSKU}`);
  console.log(`   • Sem SKU identificado: ${analysis.withoutSKU}`);
  console.log(
    `   • SKUs únicos: ${Object.keys(analysis.skuMapping).length}\n`
  );

  console.log("📂 Por categoria:");
  Object.entries(analysis.byCategory)
    .sort((a, b) => b[1] - a[1])
    .forEach(([cat, count]) => {
      console.log(`   • ${cat}: ${count}`);
    });

  console.log("\n📄 Por extensão:");
  Object.entries(analysis.byExtension)
    .sort((a, b) => b[1] - a[1])
    .forEach(([ext, count]) => {
      console.log(`   • ${ext}: ${count}`);
    });

  return { images, analysis };
}

async function generateNormalizationPlan(csvData, imageData) {
  console.log("\n🔄 Gerando plano de normalização...\n");

  const plan = {
    timestamp: new Date().toISOString(),
    csv: csvData.analysis,
    images: imageData.analysis,
    matching: {
      matched: 0,
      unmatched_products: 0,
      unmatched_images: 0,
    },
    recommendations: [],
    mapping: {},
  };

  // Encontrar correspondências entre produtos e imagens
  const productIds = new Set(
    csvData.records.map((r) => r.id).filter((id) => id)
  );
  const imageSKUs = new Set(Object.keys(imageData.analysis.skuMapping));

  // Produtos com imagens correspondentes
  for (const id of productIds) {
    if (imageSKUs.has(id)) {
      plan.matching.matched++;
      plan.mapping[id] = imageData.analysis.skuMapping[id];
    } else {
      plan.matching.unmatched_products++;
    }
  }

  // Imagens sem produtos correspondentes
  plan.matching.unmatched_images =
    imageSKUs.size - plan.matching.matched;

  console.log("🔗 Correspondências:");
  console.log(`   • Produtos com imagens: ${plan.matching.matched}`);
  console.log(
    `   • Produtos sem imagens: ${plan.matching.unmatched_products}`
  );
  console.log(
    `   • Imagens sem produtos: ${plan.matching.unmatched_images}\n`
  );

  // Gerar recomendações
  if (plan.matching.unmatched_products > 0) {
    plan.recommendations.push({
      type: "warning",
      message: `${plan.matching.unmatched_products} produtos não têm imagens correspondentes`,
      action:
        "Considere baixar imagens dos URLs externos ou usar imagens placeholder",
    });
  }

  if (plan.matching.unmatched_images > 0) {
    plan.recommendations.push({
      type: "info",
      message: `${plan.matching.unmatched_images} imagens não têm produtos correspondentes`,
      action: "Verifique se os SKUs estão corretos ou se há produtos faltando",
    });
  }

  if (imageData.analysis.withoutSKU > 0) {
    plan.recommendations.push({
      type: "warning",
      message: `${imageData.analysis.withoutSKU} imagens não têm SKU identificável no nome`,
      action:
        "Renomear arquivos seguindo padrão: sku_{ID}_{description}.{ext}",
    });
  }

  const matchRate = (
    (plan.matching.matched / productIds.size) *
    100
  ).toFixed(2);
  plan.recommendations.push({
    type: "success",
    message: `Taxa de correspondência: ${matchRate}%`,
    action:
      matchRate < 80
        ? "Melhorar normalização de nomes de arquivos"
        : "Boa cobertura de imagens",
  });

  console.log("💡 Recomendações:");
  plan.recommendations.forEach((rec, i) => {
    const icon =
      rec.type === "success" ? "✅" : rec.type === "warning" ? "⚠️ " : "ℹ️ ";
    console.log(`   ${icon} ${rec.message}`);
    console.log(`      → ${rec.action}`);
  });

  return plan;
}

async function saveReport(plan) {
  const reportPath = path.join(__dirname, "../NORMALIZATION_REPORT.json");
  fs.writeFileSync(reportPath, JSON.stringify(plan, null, 2));

  console.log(`\n💾 Relatório salvo: ${reportPath}`);
}

async function main() {
  console.log("\n═".repeat(70));
  console.log("🔍 ANÁLISE E NORMALIZAÇÃO DE DADOS - YSH B2B");
  console.log("═".repeat(70) + "\n");

  try {
    const csvData = await analyzeCSV();
    const imageData = await analyzeImages();
    const plan = await generateNormalizationPlan(csvData, imageData);
    await saveReport(plan);

    console.log("\n═".repeat(70));
    console.log("✅ ANÁLISE CONCLUÍDA COM SUCESSO!");
    console.log("═".repeat(70) + "\n");

    process.exit(0);
  } catch (error) {
    console.error("\n❌ Erro durante análise:", error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

main();
