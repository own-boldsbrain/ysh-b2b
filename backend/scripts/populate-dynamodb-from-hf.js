#!/usr/bin/env node

/**
 * Script para popular AWS DynamoDB com dados do HuggingFace
 * - Baixa dados do dataset fernando-bold/ysh-solar-products-brazil
 * - Transforma para formato DynamoDB
 * - Faz upload em batch
 */

import AWS from "aws-sdk";
import axios from "axios";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuração AWS
const AWS_REGION = process.env.AWS_REGION || "us-east-1";
const DYNAMODB_TABLE = process.env.DYNAMODB_TABLE || "ysh-products-catalog";

// HuggingFace dataset
const HF_DATASET = "fernando-bold/ysh-solar-products-brazil";
const HF_BASE_URL = `https://huggingface.co/datasets/${HF_DATASET}/resolve/main`;

// Inicializar DynamoDB
const dynamodb = new AWS.DynamoDB.DocumentClient({
  region: AWS_REGION,
});

async function populateDynamoDBFromHF() {
  console.log("\n🚀 POPULAR AWS DYNAMODB COM DADOS DO HUGGINGFACE\n");
  console.log("═".repeat(70));

  try {
    // 1. Verificar credenciais AWS
    console.log("\n🔐 ETAPA 1: Verificando Credenciais AWS\n");

    const sts = new AWS.STS({ region: AWS_REGION });
    const identity = await sts.getCallerIdentity({}).promise();

    console.log(`✓ AWS Account ID: ${identity.Account}`);
    console.log(`✓ Região: ${AWS_REGION}\n`);

    // 2. Verificar tabela DynamoDB
    console.log("📊 ETAPA 2: Verificando Tabela DynamoDB\n");

    const dynamodbClient = new AWS.DynamoDB({ region: AWS_REGION });
    const tableInfo = await dynamodbClient
      .describeTable({ TableName: DYNAMODB_TABLE })
      .promise();

    console.log(`✓ Tabela: ${DYNAMODB_TABLE}`);
    console.log(`✓ Status: ${tableInfo.Table.TableStatus}\n`);

    // 3. Baixar dados do HuggingFace
    console.log("🤗 ETAPA 3: Baixando Dados do HuggingFace\n");

    const dataUrl = `${HF_BASE_URL}/data/unified_products.json`;
    console.log(`Dataset: ${HF_DATASET}`);
    console.log(`URL: ${dataUrl}\n`);

    let products = [];

    try {
      console.log("Baixando unified_products.json...");
      const response = await axios.get(dataUrl, { timeout: 30000 });
      products = Array.isArray(response.data)
        ? response.data
        : response.data.products || [];
      console.log(`✓ ${products.length} produtos baixados\n`);
    } catch (error) {
      console.warn(
        `⚠️  Não foi possível baixar do HuggingFace: ${error.message}`
      );
      console.log("\n📁 Procurando dados locais...\n");

      // Tentar carregar dados locais
      const localPaths = [
        path.join(__dirname, "../data/unified_products.json"),
        path.join(__dirname, "../data/products-inventory/unified_products.json"),
        path.join(
          __dirname,
          "../output/multi-distributor/all-products-2025-10-21T12-28-30-632Z.json"
        ),
      ];

      for (const localPath of localPaths) {
        if (fs.existsSync(localPath)) {
          const data = JSON.parse(fs.readFileSync(localPath, "utf8"));
          products = Array.isArray(data) ? data : data.products || [];
          console.log(`✓ Carregado de: ${path.basename(localPath)}`);
          console.log(`✓ ${products.length} produtos encontrados\n`);
          break;
        }
      }

      if (products.length === 0) {
        throw new Error(
          "Nenhum dado encontrado. Verifique a conexão com HuggingFace ou dados locais."
        );
      }
    }

    // 4. Transformar para formato DynamoDB
    console.log("🔄 ETAPA 4: Transformando para DynamoDB\n");

    const items = products.map((product, index) =>
      transformProductToDynamoDB(product, index)
    );
    console.log(`✓ ${items.length} itens transformados\n`);

    // 5. Upload em batch
    console.log("📤 ETAPA 5: Fazendo Upload em Batch\n");

    let successCount = 0;
    let errorCount = 0;
    const batchSize = 25; // DynamoDB batch write limit
    const totalBatches = Math.ceil(items.length / batchSize);

    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize);
      const batchNumber = Math.floor(i / batchSize) + 1;

      const writeRequests = batch.map((item) => ({
        PutRequest: {
          Item: item,
        },
      }));

      try {
        const params = {
          RequestItems: {
            [DYNAMODB_TABLE]: writeRequests,
          },
        };

        await dynamodb.batchWrite(params).promise();
        successCount += batch.length;

        console.log(
          `   ✓ Batch ${batchNumber}/${totalBatches}: ${successCount}/${items.length} itens enviados`
        );
      } catch (error) {
        console.warn(`   ⚠️  Erro no batch ${batchNumber}: ${error.message}`);
        errorCount += batch.length;
      }
    }

    console.log(`\n✓ Upload concluído: ${successCount}/${items.length}`);
    if (errorCount > 0) {
      console.log(`⚠️  Erros: ${errorCount}\n`);
    } else {
      console.log("");
    }

    // 6. Analisar dados enviados
    console.log("📊 ETAPA 6: Análise dos Dados\n");

    const categories = {};
    const manufacturers = {};
    const distributors = {};

    items.forEach((item) => {
      if (item.category) {
        categories[item.category] = (categories[item.category] || 0) + 1;
      }
      if (item.manufacturer_id) {
        manufacturers[item.manufacturer_id] =
          (manufacturers[item.manufacturer_id] || 0) + 1;
      }
      if (item.distributor) {
        distributors[item.distributor] = (distributors[item.distributor] || 0) + 1;
      }
    });

    console.log("📦 Distribuição por Categoria:");
    Object.entries(categories)
      .sort((a, b) => b[1] - a[1])
      .forEach(([cat, count]) => {
        console.log(`   • ${cat}: ${count} SKUs`);
      });

    console.log("\n🏭 Top 10 Fabricantes:");
    Object.entries(manufacturers)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .forEach(([mfr, count]) => {
        console.log(`   • ${mfr}: ${count} SKUs`);
      });

    console.log("\n🏪 Distribuidores:");
    Object.entries(distributors)
      .sort((a, b) => b[1] - a[1])
      .forEach(([dist, count]) => {
        console.log(`   • ${dist}: ${count} SKUs`);
      });

    console.log("");

    // 7. Salvar relatório
    console.log("💾 ETAPA 7: Salvando Relatório\n");

    const report = {
      timestamp: new Date().toISOString(),
      source: HF_DATASET,
      aws_region: AWS_REGION,
      dynamodb_table: DYNAMODB_TABLE,
      total_products: items.length,
      uploaded_count: successCount,
      error_count: errorCount,
      statistics: {
        categories,
        manufacturers,
        distributors,
      },
      sample_items: items.slice(0, 5),
    };

    const reportPath = path.join(__dirname, "../DYNAMODB_POPULATION_REPORT.json");
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`✓ Relatório: DYNAMODB_POPULATION_REPORT.json\n`);

    // 8. Resultado final
    console.log("═".repeat(70));
    console.log("\n✅ POPULATION CONCLUÍDA!\n");
    console.log(`📊 Estatísticas:`);
    console.log(`   • SKUs Enviados: ${successCount}`);
    console.log(`   • Categorias: ${Object.keys(categories).length}`);
    console.log(`   • Fabricantes: ${Object.keys(manufacturers).length}`);
    console.log(`   • Distribuidores: ${Object.keys(distributors).length}`);
    console.log(`   • Tabela: ${DYNAMODB_TABLE}`);
    console.log(`   • Região: ${AWS_REGION}\n`);

    console.log(`🔍 Próximos Passos:\n`);
    console.log(`   1. Verificar dados no DynamoDB Console`);
    console.log(`   2. Executar: node scripts/fetch-skus-from-dynamodb.js`);
    console.log(`   3. Testar queries por categoria, fabricante, SKU\n`);

    process.exit(errorCount > 0 ? 1 : 0);
  } catch (error) {
    console.error("\n❌ ERRO NO UPLOAD:\n");
    console.error(error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

function transformProductToDynamoDB(product, index) {
  // Gerar SKU único
  const skuCode =
    product.sku ||
    product.sku_code ||
    product.code ||
    `SKU${String(index + 1).padStart(6, "0")}`;

  // Extrair informações
  const name = product.name || product.title || product.product_name || "Produto Sem Nome";
  const category = product.category || product.type || "uncategorized";
  const manufacturer =
    product.manufacturer ||
    product.brand ||
    product.fabricante ||
    "unknown";
  const distributor = product.distributor || product.source || "unknown";
  const price = parseFloat(product.price || product.preco || 0);
  const stock = parseInt(product.stock || product.estoque || 0);

  return {
    sku: skuCode, // Partition key (HASH)
    name: name,
    manufacturer_id: manufacturer.toLowerCase().replace(/\s+/g, "-"),
    manufacturer_name: manufacturer,
    category: category.toLowerCase(),
    distributor: distributor.toLowerCase(),
    price: price,
    stock: stock,
    description: product.description || product.descricao || "",
    specifications: product.specifications || product.specs || {},
    image_url: product.image_url || product.image || "",
    url: product.url || product.link || "",
    created_at: Math.floor(Date.now() / 1000),
    synced_at: null,
    ttl: Math.floor(Date.now() / 1000) + 365 * 24 * 60 * 60, // 1 ano
    source_data: {
      original_id: product.id,
      last_updated: product.updated_at || product.data_atualizacao,
    },
  };
}

// Executar
populateDynamoDBFromHF().catch(console.error);
