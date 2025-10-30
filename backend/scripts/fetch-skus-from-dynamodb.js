#!/usr/bin/env node

/**
 * Script para recuperar SKUs do AWS DynamoDB
 * - Lista todos os SKUs disponíveis na tabela
 * - Permite filtrar por categoria, fabricante
 * - Exporta para JSON
 */

import AWS from "aws-sdk";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuração AWS
const AWS_REGION = process.env.AWS_REGION || "us-east-1";
const DYNAMODB_TABLE = process.env.DYNAMODB_TABLE || "ysh-products-catalog";

// Inicializar DynamoDB
const dynamodb = new AWS.DynamoDB.DocumentClient({
  region: AWS_REGION,
});

async function fetchSKUsFromDynamoDB() {
  console.log("\n🔍 RECUPERANDO SKUs DO AWS DYNAMODB\n");
  console.log("═".repeat(70));

  try {
    // 1. Verificar credenciais AWS
    console.log("\n🔐 ETAPA 1: Verificando Credenciais AWS\n");
    
    const sts = new AWS.STS({ region: AWS_REGION });
    const identity = await sts.getCallerIdentity({}).promise();
    
    console.log(`✓ AWS Account ID: ${identity.Account}`);
    console.log(`✓ ARN: ${identity.Arn}`);
    console.log(`✓ Região: ${AWS_REGION}\n`);

    // 2. Verificar tabela DynamoDB
    console.log("📊 ETAPA 2: Verificando Tabela DynamoDB\n");

    const dynamodbClient = new AWS.DynamoDB({ region: AWS_REGION });
    const tableInfo = await dynamodbClient
      .describeTable({ TableName: DYNAMODB_TABLE })
      .promise();

    console.log(`✓ Tabela: ${DYNAMODB_TABLE}`);
    console.log(`✓ Status: ${tableInfo.Table.TableStatus}`);
    console.log(`✓ Item Count: ${tableInfo.Table.ItemCount || 0}`);
    console.log(
      `✓ Tamanho: ${(tableInfo.Table.TableSizeBytes / 1024 / 1024).toFixed(2)} MB\n`
    );

    // 3. Escanear todos os SKUs
    console.log("📥 ETAPA 3: Escaneando SKUs\n");

    let allItems = [];
    let lastEvaluatedKey = null;
    let scanCount = 0;

    do {
      scanCount++;
      const params = {
        TableName: DYNAMODB_TABLE,
        ExclusiveStartKey: lastEvaluatedKey,
        Limit: 100, // Processar em lotes
      };

      const result = await dynamodb.scan(params).promise();
      allItems = allItems.concat(result.Items);
      lastEvaluatedKey = result.LastEvaluatedKey;

      console.log(
        `   ✓ Scan ${scanCount}: ${result.Items.length} itens (Total: ${allItems.length})`
      );
    } while (lastEvaluatedKey);

    console.log(`\n✓ Total de SKUs recuperados: ${allItems.length}\n`);

    // 4. Analisar dados
    console.log("📊 ETAPA 4: Análise dos Dados\n");

    const categories = {};
    const manufacturers = {};
    const priceRanges = {
      "0-1000": 0,
      "1000-5000": 0,
      "5000-10000": 0,
      "10000+": 0,
    };

    allItems.forEach((item) => {
      // Contar por categoria
      if (item.category) {
        categories[item.category] = (categories[item.category] || 0) + 1;
      }

      // Contar por fabricante
      if (item.manufacturer_id) {
        manufacturers[item.manufacturer_id] =
          (manufacturers[item.manufacturer_id] || 0) + 1;
      }

      // Agrupar por faixa de preço
      if (item.price) {
        if (item.price < 1000) priceRanges["0-1000"]++;
        else if (item.price < 5000) priceRanges["1000-5000"]++;
        else if (item.price < 10000) priceRanges["5000-10000"]++;
        else priceRanges["10000+"]++;
      }
    });

    console.log("📦 Distribuição por Categoria:");
    Object.entries(categories)
      .sort((a, b) => b[1] - a[1])
      .forEach(([cat, count]) => {
        console.log(`   • ${cat}: ${count} SKUs`);
      });

    console.log("\n🏭 Distribuição por Fabricante:");
    Object.entries(manufacturers)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10) // Top 10
      .forEach(([mfr, count]) => {
        console.log(`   • ${mfr}: ${count} SKUs`);
      });

    console.log("\n💰 Distribuição por Faixa de Preço:");
    Object.entries(priceRanges).forEach(([range, count]) => {
      console.log(`   • R$ ${range}: ${count} SKUs`);
    });

    console.log("");

    // 5. Gerar relatório
    console.log("💾 ETAPA 5: Gerando Relatório\n");

    const report = {
      timestamp: new Date().toISOString(),
      aws_region: AWS_REGION,
      dynamodb_table: DYNAMODB_TABLE,
      total_skus: allItems.length,
      scan_count: scanCount,
      statistics: {
        categories,
        manufacturers,
        price_ranges: priceRanges,
      },
      sample_skus: allItems.slice(0, 5).map((item) => ({
        pk: item.pk,
        sk: item.sk,
        sku_code: item.sku_code,
        name: item.name,
        category: item.category,
        manufacturer_id: item.manufacturer_id,
        price: item.price,
        stock: item.stock,
      })),
      all_skus: allItems,
    };

    // Salvar relatório completo
    const reportPath = path.join(__dirname, "../DYNAMODB_SKUS_REPORT.json");
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`✓ Relatório completo: DYNAMODB_SKUS_REPORT.json`);

    // Salvar apenas lista de SKUs
    const skusListPath = path.join(__dirname, "../DYNAMODB_SKUS_LIST.json");
    const skusList = allItems.map((item) => ({
      sku_code: item.sku_code,
      name: item.name,
      category: item.category,
      manufacturer: item.manufacturer_id,
      price: item.price,
      stock: item.stock,
    }));
    fs.writeFileSync(skusListPath, JSON.stringify(skusList, null, 2));
    console.log(`✓ Lista de SKUs: DYNAMODB_SKUS_LIST.json\n`);

    // 6. Resultado final
    console.log("═".repeat(70));
    console.log("\n✅ RECUPERAÇÃO CONCLUÍDA!\n");
    console.log(`📊 Estatísticas:`);
    console.log(`   • Total de SKUs: ${allItems.length}`);
    console.log(`   • Categorias: ${Object.keys(categories).length}`);
    console.log(`   • Fabricantes: ${Object.keys(manufacturers).length}`);
    console.log(`   • Tabela: ${DYNAMODB_TABLE}`);
    console.log(`   • Região: ${AWS_REGION}\n`);

    console.log(`📁 Arquivos Gerados:\n`);
    console.log(`   • DYNAMODB_SKUS_REPORT.json - Relatório completo`);
    console.log(`   • DYNAMODB_SKUS_LIST.json - Lista simplificada\n`);

    return report;
  } catch (error) {
    console.error("\n❌ ERRO NA RECUPERAÇÃO:\n");
    console.error(error.message);

    if (error.code === "ResourceNotFoundException") {
      console.error(`\n⚠️  A tabela "${DYNAMODB_TABLE}" não existe.`);
      console.error(`   Verifique se o nome da tabela está correto.\n`);
    } else if (
      error.code === "CredentialsError" ||
      error.code === "SignatureDoesNotMatch"
    ) {
      console.error("\n⚠️  Problema com credenciais AWS.");
      console.error("   Verifique suas credenciais em ~/.aws/credentials\n");
    }

    process.exit(1);
  }
}

// Executar
fetchSKUsFromDynamoDB().catch(console.error);
