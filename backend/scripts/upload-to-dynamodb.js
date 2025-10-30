#!/usr/bin/env node

/**
 * Script para upload de SKUs para DynamoDB
 * - Lê todos os inventários normalizados
 * - Enriquece com URLs de imagens
 * - Upload em batch para DynamoDB
 * - Mantém índices para busca eficiente
 */

import AWS from "aws-sdk";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_PATH = path.join(__dirname, "..");
const INVENTORY_PATH = path.join(ROOT_PATH, "data/products-inventory");
const IMAGE_MAP_PATH = path.join(ROOT_PATH, "static/products/product_image_map.json");

const AWS_REGION = process.env.AWS_REGION || "us-east-1";
const DYNAMODB_TABLE = process.env.DYNAMODB_TABLE || "ysh-products-catalog";

const dynamodb = new AWS.DynamoDB.DocumentClient({
  region: AWS_REGION,
});

const BATCH_SIZE = 25; // DynamoDB BatchWriteItem limit

function normalizeKey(str) {
  if (!str) return "";
  return str
    .toString()
    .replace(/[^a-zA-Z0-9]/g, "")
    .toUpperCase();
}

function findImageForSku(sku, imageMap) {
  if (!imageMap || !imageMap.images) return null;

  const normalizedSku = normalizeKey(sku);

  // Busca direta
  if (imageMap.images[normalizedSku]) {
    return imageMap.images[normalizedSku][0];
  }

  // Busca parcial
  for (const [key, images] of Object.entries(imageMap.images)) {
    if (key.includes(normalizedSku) || normalizedSku.includes(key)) {
      return images[0];
    }
  }

  return null;
}

function scanInventoryFiles(dirPath, depth = 0) {
  const files = [];

  if (depth > 4 || !fs.existsSync(dirPath)) {
    return files;
  }

  const entries = fs.readdirSync(dirPath, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);

    if (entry.isDirectory()) {
      files.push(...scanInventoryFiles(fullPath, depth + 1));
    } else if (
      entry.isFile() &&
      entry.name.endsWith(".json") &&
      !entry.name.includes("schema") &&
      !entry.name.includes("report") &&
      !entry.name.includes("map")
    ) {
      files.push(fullPath);
    }
  }

  return files;
}

function extractProducts(data) {
  const products = [];

  if (Array.isArray(data)) {
    return data;
  }

  if (data.products && Array.isArray(data.products)) {
    return data.products;
  }

  if (data.items && Array.isArray(data.items)) {
    return data.items;
  }

  // Busca profunda
  const searchDeep = (obj) => {
    if (Array.isArray(obj)) {
      obj.forEach(searchDeep);
    } else if (obj && typeof obj === "object") {
      if (obj.sku || obj.SKU || obj.codigo) {
        products.push(obj);
      }
      Object.values(obj).forEach(searchDeep);
    }
  };

  searchDeep(data);

  return products;
}

async function uploadSkusToDynamoDB() {
  console.log("\n📤 UPLOAD DE SKUs PARA DYNAMODB\n");
  console.log("═".repeat(70));

  try {
    // 1. Verificar credenciais
    console.log("\n🔐 ETAPA 1: Verificando Configuração\n");

    if (!process.env.AWS_ACCESS_KEY_ID || !process.env.AWS_SECRET_ACCESS_KEY) {
      console.error("❌ Credenciais AWS não configuradas");
      process.exit(1);
    }

    console.log(`✓ AWS_REGION: ${AWS_REGION}`);
    console.log(`✓ DYNAMODB_TABLE: ${DYNAMODB_TABLE}\n`);

    // 2. Carregar mapeamento de imagens
    console.log("🗺️  ETAPA 2: Carregando Mapeamento de Imagens\n");

    let imageMap = null;
    if (fs.existsSync(IMAGE_MAP_PATH)) {
      imageMap = JSON.parse(fs.readFileSync(IMAGE_MAP_PATH, "utf8"));
      console.log(`✓ Mapeamento carregado: ${Object.keys(imageMap.images).length} SKUs\n`);
    } else {
      console.log("⚠️  Mapeamento não encontrado, imagens não serão linkadas\n");
    }

    // 3. Escanear inventários
    console.log("📁 ETAPA 3: Escaneando Inventários\n");

    const inventoryFiles = scanInventoryFiles(INVENTORY_PATH);
    console.log(`✓ ${inventoryFiles.length} arquivos encontrados\n`);

    // 4. Processar produtos
    console.log("🔄 ETAPA 4: Processando Produtos\n");

    const allProducts = [];
    const skuSet = new Set();
    let duplicates = 0;

    for (const filePath of inventoryFiles) {
      try {
        const data = JSON.parse(fs.readFileSync(filePath, "utf8"));
        const products = extractProducts(data);

        for (const product of products) {
          const sku = product.sku || product.SKU || product.codigo;

          if (!sku) continue;

          const normalizedSku = normalizeKey(sku);

          if (skuSet.has(normalizedSku)) {
            duplicates++;
            continue;
          }

          skuSet.add(normalizedSku);

          // Enriquecer com imagem
          const imageData = findImageForSku(sku, imageMap);

          const enrichedProduct = {
            ...product,
            sku_normalized: normalizedSku,
            image_url: imageData?.s3_url || null,
            image_local: imageData?.local_url || null,
            image_category: imageData?.category || null,
            source_file: path.relative(ROOT_PATH, filePath),
            updated_at: new Date().toISOString(),
          };

          allProducts.push(enrichedProduct);
        }
      } catch (error) {
        console.warn(`⚠️  Erro ao processar ${path.basename(filePath)}: ${error.message}`);
      }
    }

    console.log(`✓ ${allProducts.length} produtos únicos processados`);
    console.log(`✓ ${duplicates} duplicatas removidas\n`);

    // 5. Upload para DynamoDB em batches
    console.log("📤 ETAPA 5: Upload para DynamoDB\n");

    let uploadedCount = 0;
    let errorCount = 0;

    for (let i = 0; i < allProducts.length; i += BATCH_SIZE) {
      const batch = allProducts.slice(i, i + BATCH_SIZE);

      const putRequests = batch.map((product) => ({
        PutRequest: {
          Item: {
            pk: `SKU#${product.sku_normalized}`,
            sk: "METADATA",
            ...product,
          },
        },
      }));

      try {
        await dynamodb
          .batchWrite({
            RequestItems: {
              [DYNAMODB_TABLE]: putRequests,
            },
          })
          .promise();

        uploadedCount += batch.length;

        if (uploadedCount % 100 === 0 || uploadedCount === allProducts.length) {
          console.log(`   ✓ ${uploadedCount}/${allProducts.length} produtos enviados`);
        }
      } catch (error) {
        console.warn(`   ⚠️  Erro no batch ${i}: ${error.message}`);
        errorCount += batch.length;
      }
    }

    console.log(`\n✓ Upload concluído: ${uploadedCount} sucesso, ${errorCount} falhas\n`);

    // 6. Salvar relatório
    console.log("💾 ETAPA 6: Gerando Relatório\n");

    const report = {
      timestamp: new Date().toISOString(),
      dynamodb_table: DYNAMODB_TABLE,
      aws_region: AWS_REGION,
      statistics: {
        total_files: inventoryFiles.length,
        total_products: allProducts.length,
        duplicates_removed: duplicates,
        uploaded: uploadedCount,
        errors: errorCount,
        with_images: allProducts.filter((p) => p.image_url).length,
      },
      sample_products: allProducts.slice(0, 5).map((p) => ({
        sku: p.sku,
        sku_normalized: p.sku_normalized,
        image_url: p.image_url,
        source: p.source_file,
      })),
    };

    const reportPath = path.join(ROOT_PATH, "DYNAMODB_UPLOAD_REPORT.json");
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    console.log("✓ Relatório salvo: DYNAMODB_UPLOAD_REPORT.json\n");

    // 7. Resultado final
    console.log("═".repeat(70));
    console.log("\n✅ UPLOAD PARA DYNAMODB CONCLUÍDO!\n");
    console.log(`📊 Estatísticas:`);
    console.log(`   • Produtos: ${allProducts.length}`);
    console.log(`   • Enviados: ${uploadedCount}`);
    console.log(`   • Erros: ${errorCount}`);
    console.log(`   • Com imagens: ${allProducts.filter((p) => p.image_url).length}`);
    console.log(`   • Tabela: ${DYNAMODB_TABLE}\n`);

    process.exit(errorCount > 0 ? 1 : 0);
  } catch (error) {
    console.error("\n❌ ERRO NO UPLOAD:\n");
    console.error(error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

uploadSkusToDynamoDB().catch(console.error);
