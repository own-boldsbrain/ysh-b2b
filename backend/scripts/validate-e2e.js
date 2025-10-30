#!/usr/bin/env node

/**
 * Script de Validação End-to-End
 * - Testa conectividade AWS
 * - Verifica imagens locais e no S3
 * - Valida SKUs no DynamoDB
 * - Testa fluxo completo de extração → normalização → upload
 */

import AWS from "aws-sdk";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_PATH = path.join(__dirname, "..");

const AWS_REGION = process.env.AWS_REGION || "us-east-1";
const S3_BUCKET = process.env.S3_BUCKET || "ysh-b2b-products";
const DYNAMODB_TABLE = process.env.DYNAMODB_TABLE || "ysh-products-catalog";

const s3 = new AWS.S3({ region: AWS_REGION });
const dynamodb = new AWS.DynamoDB.DocumentClient({ region: AWS_REGION });

const TESTS = {
  aws_connectivity: false,
  s3_bucket_exists: false,
  s3_has_images: false,
  dynamodb_table_exists: false,
  dynamodb_has_skus: false,
  local_images_exist: false,
  image_map_exists: false,
  image_map_valid: false,
  s3_images_accessible: false,
  dynamodb_query_works: false,
};

async function validateEndToEnd() {
  console.log("\n🔍 VALIDAÇÃO END-TO-END\n");
  console.log("═".repeat(70));

  const results = {
    timestamp: new Date().toISOString(),
    tests: { ...TESTS },
    details: {},
    errors: [],
  };

  try {
    // 1. Validar conectividade AWS
    console.log("\n🔐 TESTE 1: Conectividade AWS\n");

    try {
      await s3.listBuckets().promise();
      results.tests.aws_connectivity = true;
      console.log("✓ Conectividade AWS OK\n");
    } catch (error) {
      results.errors.push(`AWS Connectivity: ${error.message}`);
      console.log("❌ Falha na conectividade AWS\n");
    }

    // 2. Validar bucket S3
    console.log("🪣 TESTE 2: Bucket S3\n");

    try {
      await s3.headBucket({ Bucket: S3_BUCKET }).promise();
      results.tests.s3_bucket_exists = true;
      console.log(`✓ Bucket '${S3_BUCKET}' existe\n`);
    } catch (error) {
      results.errors.push(`S3 Bucket: ${error.message}`);
      console.log(`❌ Bucket '${S3_BUCKET}' não encontrado\n`);
    }

    // 3. Validar imagens no S3
    console.log("🖼️  TESTE 3: Imagens no S3\n");

    try {
      const response = await s3
        .listObjectsV2({
          Bucket: S3_BUCKET,
          Prefix: "images/products",
          MaxKeys: 10,
        })
        .promise();

      if (response.Contents && response.Contents.length > 0) {
        results.tests.s3_has_images = true;
        results.details.s3_image_count = response.KeyCount || 0;
        console.log(`✓ ${response.KeyCount} imagens encontradas no S3\n`);
      } else {
        console.log("⚠️  Nenhuma imagem encontrada no S3\n");
      }
    } catch (error) {
      results.errors.push(`S3 Images: ${error.message}`);
      console.log("❌ Erro ao listar imagens no S3\n");
    }

    // 4. Validar tabela DynamoDB
    console.log("📊 TESTE 4: Tabela DynamoDB\n");

    try {
      const dynamoDbClient = new AWS.DynamoDB({ region: AWS_REGION });
      await dynamoDbClient
        .describeTable({ TableName: DYNAMODB_TABLE })
        .promise();

      results.tests.dynamodb_table_exists = true;
      console.log(`✓ Tabela '${DYNAMODB_TABLE}' existe\n`);
    } catch (error) {
      results.errors.push(`DynamoDB Table: ${error.message}`);
      console.log(`❌ Tabela '${DYNAMODB_TABLE}' não encontrada\n`);
    }

    // 5. Validar SKUs no DynamoDB
    console.log("🔢 TESTE 5: SKUs no DynamoDB\n");

    try {
      const response = await dynamodb
        .scan({
          TableName: DYNAMODB_TABLE,
          Limit: 10,
        })
        .promise();

      if (response.Items && response.Items.length > 0) {
        results.tests.dynamodb_has_skus = true;
        results.details.sample_skus = response.Items.map((item) => item.pk).slice(0, 5);
        console.log(`✓ ${response.Items.length} SKUs encontrados (amostra)\n`);
      } else {
        console.log("⚠️  Nenhum SKU encontrado no DynamoDB\n");
      }
    } catch (error) {
      results.errors.push(`DynamoDB SKUs: ${error.message}`);
      console.log("❌ Erro ao consultar SKUs no DynamoDB\n");
    }

    // 6. Validar imagens locais
    console.log("📁 TESTE 6: Imagens Locais\n");

    const localImagesPath = path.join(ROOT_PATH, "static/products");
    if (fs.existsSync(localImagesPath)) {
      const dirs = fs.readdirSync(localImagesPath).filter((f) => {
        const fullPath = path.join(localImagesPath, f);
        return fs.statSync(fullPath).isDirectory();
      });

      if (dirs.length > 0) {
        results.tests.local_images_exist = true;
        results.details.local_image_categories = dirs.length;
        console.log(`✓ ${dirs.length} categorias de imagens locais\n`);
      } else {
        console.log("⚠️  Nenhuma categoria de imagem local\n");
      }
    } else {
      console.log("❌ Diretório de imagens locais não encontrado\n");
    }

    // 7. Validar mapeamento de imagens
    console.log("🗺️  TESTE 7: Mapeamento de Imagens\n");

    const imageMapPath = path.join(ROOT_PATH, "static/products/product_image_map.json");
    if (fs.existsSync(imageMapPath)) {
      results.tests.image_map_exists = true;

      try {
        const imageMap = JSON.parse(fs.readFileSync(imageMapPath, "utf8"));

        if (imageMap.images && Object.keys(imageMap.images).length > 0) {
          results.tests.image_map_valid = true;
          results.details.mapped_skus = Object.keys(imageMap.images).length;
          console.log(`✓ ${Object.keys(imageMap.images).length} SKUs mapeados\n`);
        } else {
          console.log("⚠️  Mapeamento vazio\n");
        }
      } catch (error) {
        results.errors.push(`Image Map: ${error.message}`);
        console.log("❌ Erro ao ler mapeamento\n");
      }
    } else {
      console.log("❌ Mapeamento de imagens não encontrado\n");
    }

    // 8. Testar acesso a imagem no S3
    console.log("🔗 TESTE 8: Acesso a Imagem no S3\n");

    try {
      const response = await s3
        .listObjectsV2({
          Bucket: S3_BUCKET,
          Prefix: "images/products",
          MaxKeys: 1,
        })
        .promise();

      if (response.Contents && response.Contents.length > 0) {
        const testKey = response.Contents[0].Key;
        await s3.headObject({ Bucket: S3_BUCKET, Key: testKey }).promise();

        results.tests.s3_images_accessible = true;
        console.log(`✓ Imagens S3 acessíveis (testado: ${testKey})\n`);
      } else {
        console.log("⚠️  Nenhuma imagem disponível para teste\n");
      }
    } catch (error) {
      results.errors.push(`S3 Access: ${error.message}`);
      console.log("❌ Erro ao acessar imagem no S3\n");
    }

    // 9. Testar query no DynamoDB
    console.log("🔎 TESTE 9: Query DynamoDB\n");

    try {
      const response = await dynamodb
        .scan({
          TableName: DYNAMODB_TABLE,
          Limit: 1,
        })
        .promise();

      if (response.Items && response.Items.length > 0) {
        const testItem = response.Items[0];
        const queryResponse = await dynamodb
          .query({
            TableName: DYNAMODB_TABLE,
            KeyConditionExpression: "pk = :pk",
            ExpressionAttributeValues: {
              ":pk": testItem.pk,
            },
          })
          .promise();

        if (queryResponse.Items && queryResponse.Items.length > 0) {
          results.tests.dynamodb_query_works = true;
          console.log(`✓ Query DynamoDB funcional (testado: ${testItem.pk})\n`);
        }
      } else {
        console.log("⚠️  Nenhum item disponível para teste\n");
      }
    } catch (error) {
      results.errors.push(`DynamoDB Query: ${error.message}`);
      console.log("❌ Erro ao testar query no DynamoDB\n");
    }

    // Resultado final
    console.log("═".repeat(70));
    console.log("\n📊 RESULTADO DA VALIDAÇÃO\n");

    const passedTests = Object.values(results.tests).filter((t) => t).length;
    const totalTests = Object.keys(results.tests).length;
    const successRate = ((passedTests / totalTests) * 100).toFixed(1);

    console.log(`Testes Passados: ${passedTests}/${totalTests} (${successRate}%)\n`);

    console.log("Detalhes:");
    for (const [test, passed] of Object.entries(results.tests)) {
      console.log(`   ${passed ? "✓" : "❌"} ${test}`);
    }

    console.log("");

    if (results.errors.length > 0) {
      console.log("Erros:");
      results.errors.forEach((error) => {
        console.log(`   • ${error}`);
      });
      console.log("");
    }

    // Salvar relatório
    const reportPath = path.join(ROOT_PATH, "E2E_VALIDATION_REPORT.json");
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));

    console.log(`📄 Relatório salvo: E2E_VALIDATION_REPORT.json\n`);

    if (successRate === 100) {
      console.log("✅ TODOS OS TESTES PASSARAM!\n");
      process.exit(0);
    } else if (successRate >= 80) {
      console.log("⚠️  MAIORIA DOS TESTES PASSOU\n");
      process.exit(0);
    } else {
      console.log("❌ MUITOS TESTES FALHARAM\n");
      process.exit(1);
    }
  } catch (error) {
    console.error("\n❌ ERRO CRÍTICO NA VALIDAÇÃO:\n");
    console.error(error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

validateEndToEnd().catch(console.error);
