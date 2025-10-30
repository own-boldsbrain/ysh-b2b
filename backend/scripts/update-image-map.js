#!/usr/bin/env node

/**
 * Script para atualizar product_image_map.json
 * - Escaneia static/products completo
 * - Gera mapeamento normalizado SKU → imagens
 * - Inclui URLs S3 futuras
 * - Mantém estrutura compatível com transformers
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_PATH = path.join(__dirname, "..");
const STATIC_PRODUCTS_PATH = path.join(ROOT_PATH, "static/products");
const OUTPUT_PATH = path.join(STATIC_PRODUCTS_PATH, "product_image_map.json");
const S3_BUCKET = process.env.S3_BUCKET || "ysh-b2b-products";
const S3_REGION = process.env.AWS_REGION || "us-east-1";
const S3_PREFIX = "images/products";

const IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".gif"];

function normalizeKey(filename) {
  return filename
    .replace(/\.(jpg|jpeg|png|webp|gif)$/i, "")
    .replace(/[^a-zA-Z0-9]/g, "")
    .toUpperCase();
}

function scanImagesRecursive(dirPath, basePath = "") {
  const images = [];

  if (!fs.existsSync(dirPath)) {
    return images;
  }

  const entries = fs.readdirSync(dirPath, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    const relativePath = basePath ? `${basePath}/${entry.name}` : entry.name;

    if (entry.isDirectory()) {
      images.push(...scanImagesRecursive(fullPath, relativePath));
    } else if (entry.isFile()) {
      const ext = path.extname(entry.name).toLowerCase();
      if (IMAGE_EXTENSIONS.includes(ext)) {
        const category = basePath.split("/")[0] || "UNCATEGORIZED";

        images.push({
          filename: entry.name,
          path: relativePath,
          category,
          size: fs.statSync(fullPath).size,
        });
      }
    }
  }

  return images;
}

async function updateImageMap() {
  console.log("\n🗺️  ATUALIZAÇÃO DO MAPEAMENTO DE IMAGENS\n");
  console.log("═".repeat(70));

  try {
    // 1. Escanear diretório
    console.log("\n📁 ETAPA 1: Escaneando Imagens\n");

    const allImages = scanImagesRecursive(STATIC_PRODUCTS_PATH);

    console.log(`✓ ${allImages.length} imagens encontradas\n`);

    // 2. Gerar mapeamento
    console.log("🔗 ETAPA 2: Gerando Mapeamento\n");

    const imageMap = {
      images: {},
      metadata: {
        timestamp: new Date().toISOString(),
        total_images: allImages.length,
        s3_bucket: S3_BUCKET,
        s3_region: S3_REGION,
        s3_prefix: S3_PREFIX,
      },
      statistics: {
        by_category: {},
        by_extension: {},
      },
    };

    for (const image of allImages) {
      const key = normalizeKey(image.filename);

      if (!imageMap.images[key]) {
        imageMap.images[key] = [];
      }

      const s3Key = `${S3_PREFIX}/${image.path}`;
      const s3Url = `https://${S3_BUCKET}.s3.${S3_REGION}.amazonaws.com/${s3Key}`;

      imageMap.images[key].push({
        filename: image.filename,
        path: image.path,
        category: image.category,
        local_url: `/static/products/${image.path}`,
        s3_url: s3Url,
        s3_key: s3Key,
        size_bytes: image.size,
      });

      // Estatísticas por categoria
      if (!imageMap.statistics.by_category[image.category]) {
        imageMap.statistics.by_category[image.category] = 0;
      }
      imageMap.statistics.by_category[image.category]++;

      // Estatísticas por extensão
      const ext = path.extname(image.filename).toLowerCase();
      if (!imageMap.statistics.by_extension[ext]) {
        imageMap.statistics.by_extension[ext] = 0;
      }
      imageMap.statistics.by_extension[ext]++;
    }

    console.log(`✓ ${Object.keys(imageMap.images).length} SKUs mapeados\n`);

    // 3. Salvar mapeamento
    console.log("💾 ETAPA 3: Salvando Mapeamento\n");

    fs.writeFileSync(OUTPUT_PATH, JSON.stringify(imageMap, null, 2));

    console.log(`✓ Mapeamento salvo: ${OUTPUT_PATH}\n`);

    // 4. Gerar relatório
    console.log("📊 ETAPA 4: Estatísticas\n");

    console.log(`Imagens por Categoria:`);
    const sortedCategories = Object.entries(imageMap.statistics.by_category).sort(
      ([, a], [, b]) => b - a
    );

    for (const [category, count] of sortedCategories.slice(0, 10)) {
      console.log(`   • ${category}: ${count}`);
    }

    if (sortedCategories.length > 10) {
      console.log(`   ... e mais ${sortedCategories.length - 10} categorias`);
    }

    console.log("\nImagens por Extensão:");
    for (const [ext, count] of Object.entries(imageMap.statistics.by_extension)) {
      console.log(`   • ${ext}: ${count}`);
    }

    console.log("");

    // 5. Resultado final
    console.log("═".repeat(70));
    console.log("\n✅ MAPEAMENTO ATUALIZADO!\n");
    console.log(`📊 Resumo:`);
    console.log(`   • Total de imagens: ${allImages.length}`);
    console.log(`   • SKUs únicos: ${Object.keys(imageMap.images).length}`);
    console.log(`   • Categorias: ${Object.keys(imageMap.statistics.by_category).length}`);
    console.log(`   • Arquivo: product_image_map.json\n`);

    console.log(`🔍 Próximos passos:`);
    console.log(`   1. Upload imagens para S3`);
    console.log(`   2. Upload SKUs para DynamoDB`);
    console.log(`   3. Atualizar transformers para usar mapeamento\n`);

    process.exit(0);
  } catch (error) {
    console.error("\n❌ ERRO NA ATUALIZAÇÃO:\n");
    console.error(error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

updateImageMap().catch(console.error);
