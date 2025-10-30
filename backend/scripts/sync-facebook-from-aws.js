#!/usr/bin/env node

/**
 * Script para sincronizar dados de S3 + DynamoDB com Facebook Catalog
 * - Lê SKUs do DynamoDB
 * - Obtém URLs de imagens do S3
 * - Envia para Facebook Catalog via Graph API
 */

import AWS from "aws-sdk";
import axios from "axios";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const dynamodb = new AWS.DynamoDB.DocumentClient({
  region: process.env.AWS_REGION || "us-east-1",
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
});

const s3 = new AWS.S3({
  region: process.env.AWS_REGION || "us-east-1",
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
});

// Configuração do Facebook
const FACEBOOK_TOKEN = process.env.FACEBOOK_TOKEN;
const FACEBOOK_CATALOG_ID = process.env.FACEBOOK_CATALOG_ID;
const FACEBOOK_API_VERSION = "v21.0";

async function loadS3UrlMappings() {
  console.log("\n📥 Carregando URLs de imagens do S3...");

  try {
    const s3Report = JSON.parse(
      fs.readFileSync(path.join(__dirname, "../S3_UPLOAD_REPORT.json"), "utf8")
    );

    const urlMappings = {};
    if (s3Report.image_urls) {
      for (const [imagePath, imageUrl] of Object.entries(
        s3Report.image_urls
      )) {
        const imageName = path.basename(imagePath);
        urlMappings[imageName] = imageUrl;
      }
    }

    console.log(`✓ ${Object.keys(urlMappings).length} URLs carregadas`);
    return urlMappings;
  } catch (error) {
    console.error("❌ Erro ao carregar URLs:", error.message);
    return {};
  }
}

async function loadSkusFromDynamoDB() {
  console.log("\n📦 Carregando SKUs do DynamoDB...");

  try {
    const table = process.env.DYNAMODB_TABLE || "ysh-products-catalog";
    const params = {
      TableName: table,
    };

    const items = [];
    let response;

    do {
      response = await dynamodb.scan(params).promise();
      items.push(...(response.Items || []));
      params.ExclusiveStartKey = response.LastEvaluatedKey;
    } while (response.LastEvaluatedKey);

    console.log(`✓ ${items.length} SKUs carregados do DynamoDB`);
    return items;
  } catch (error) {
    console.error("❌ Erro ao carregar SKUs:", error.message);
    return [];
  }
}

async function transformToFacebookProduct(sku, urlMappings) {
  return {
    title: sku.title || sku.name,
    description: sku.description || "",
    image_url: urlMappings[sku.main_image] || urlMappings[sku.image_file] || "",
    url: sku.url || "",
    price: Math.round(sku.price * 100), // Facebook espera preço em centavos
    currency: sku.currency || "BRL",
    availability: sku.availability || "in stock",
    condition: "new",
    google_product_category: sku.google_product_category || "",
    brand: sku.manufacturer || "YSH",
    sku: sku.sku_code,
    category: sku.category,
    additional_image_urls: sku.additional_images
      ? sku.additional_images
          .split(",")
          .map((img) => urlMappings[img.trim()] || "")
          .filter((url) => url)
      : [],
  };
}

async function syncToFacebook(product) {
  if (!FACEBOOK_TOKEN || !FACEBOOK_CATALOG_ID) {
    throw new Error(
      "FACEBOOK_TOKEN e FACEBOOK_CATALOG_ID são obrigatórios nas variáveis de ambiente"
    );
  }

  const url = `https://graph.facebook.com/${FACEBOOK_API_VERSION}/${FACEBOOK_CATALOG_ID}/products`;

  try {
    const response = await axios.post(url, product, {
      params: {
        access_token: FACEBOOK_TOKEN,
      },
    });

    return {
      success: true,
      facebook_id: response.data.id,
      sku: product.sku,
    };
  } catch (error) {
    console.error(
      `❌ Erro ao sincronizar SKU ${product.sku}:`,
      error.response?.data || error.message
    );
    return {
      success: false,
      sku: product.sku,
      error: error.response?.data || error.message,
    };
  }
}

async function syncCatalogToFacebook() {
  console.log("\n🚀 SINCRONIZAÇÃO AWS → FACEBOOK INICIANDO\n");
  console.log("═".repeat(70) + "\n");

  try {
    // 1. Carregar dados
    const urlMappings = await loadS3UrlMappings();
    const skus = await loadSkusFromDynamoDB();

    if (skus.length === 0) {
      console.error("❌ Nenhum SKU encontrado no DynamoDB");
      process.exit(1);
    }

    console.log(`\n📊 Total de SKUs para sincronizar: ${skus.length}`);

    // 2. Sincronizar em lotes
    const batchSize = 100;
    const results = {
      successful: 0,
      failed: 0,
      total: skus.length,
      timestamp: new Date().toISOString(),
      synced_products: [],
      errors: [],
    };

    for (let i = 0; i < skus.length; i += batchSize) {
      const batch = skus.slice(i, Math.min(i + batchSize, skus.length));
      const batchNumber = Math.floor(i / batchSize) + 1;
      const totalBatches = Math.ceil(skus.length / batchSize);

      console.log(
        `\n📤 Lote ${batchNumber}/${totalBatches} (${batch.length} SKUs)...`
      );

      for (const sku of batch) {
        try {
          const facebookProduct = await transformToFacebookProduct(
            sku,
            urlMappings
          );
          const result = await syncToFacebook(facebookProduct);

          if (result.success) {
            results.successful++;
            results.synced_products.push({
              sku: result.sku,
              facebook_id: result.facebook_id,
            });
            process.stdout.write(".");
          } else {
            results.failed++;
            results.errors.push({
              sku: result.sku,
              error: result.error,
            });
            process.stdout.write("x");
          }
        } catch (error) {
          results.failed++;
          results.errors.push({
            sku: sku.sku_code,
            error: error.message,
          });
          process.stdout.write("x");
        }

        // Respeitar rate limit do Facebook
        await new Promise((resolve) => setTimeout(resolve, 50));
      }

      console.log(`\n✓ Lote ${batchNumber} concluído`);
      console.log(
        `  Sucesso: ${results.successful}, Falhas: ${results.failed}`
      );
    }

    // 3. Gerar relatório
    console.log("\n═".repeat(70));
    console.log("\n📋 RELATÓRIO FINAL DE SINCRONIZAÇÃO\n");

    console.log(`Total de SKUs: ${results.total}`);
    console.log(`✅ Sincronizados: ${results.successful}`);
    console.log(`❌ Falhados: ${results.failed}`);
    console.log(`Taxa de sucesso: ${((results.successful / results.total) * 100).toFixed(1)}%\n`);

    // Salvar relatório
    const reportPath = path.join(
      __dirname,
      "../FACEBOOK_SYNC_FROM_AWS.json"
    );
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
    console.log(`📁 Relatório salvo em: FACEBOOK_SYNC_FROM_AWS.json`);

    if (results.failed > 0) {
      console.log(`\n⚠️  ${results.failed} produtos falharam na sincronização`);
      console.log("Verifique FACEBOOK_SYNC_FROM_AWS.json para detalhes");
    }

    console.log("\n✅ Sincronização concluída!\n");
    process.exit(results.failed > 0 ? 1 : 0);
  } catch (error) {
    console.error("\n❌ ERRO:", error.message);
    process.exit(1);
  }
}

syncCatalogToFacebook().catch(console.error);
