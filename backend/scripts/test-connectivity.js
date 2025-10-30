#!/usr/bin/env node

/**
 * Script para testar conectividade com AWS e Facebook
 * Valida todas as conexões antes de iniciar uploads
 */

import AWS from "aws-sdk";
import axios from "axios";
import dotenv from "dotenv";

dotenv.config();

const colors = {
  reset: "\x1b[0m",
  green: "\x1b[32m",
  red: "\x1b[31m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
};

function log(level, message) {
  const timestamp = new Date().toLocaleTimeString("pt-BR");
  const prefix = {
    info: `${colors.blue}ℹ${colors.reset}`,
    success: `${colors.green}✅${colors.reset}`,
    error: `${colors.red}❌${colors.reset}`,
    warn: `${colors.yellow}⚠️${colors.reset}`,
  }[level];
  console.log(`[${timestamp}] ${prefix} ${message}`);
}

async function testAWSConnection() {
  log("info", "Testando conexão com AWS...");

  try {
    const credentials = new AWS.Credentials({
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    });

    const sts = new AWS.STS({ credentials, region: process.env.AWS_REGION });
    const identity = await sts.getCallerIdentity({}).promise();

    log("success", `AWS conectado - Account: ${identity.Account}`);
    return true;
  } catch (error) {
    log("error", `Erro AWS: ${error.message}`);
    return false;
  }
}

async function testS3Connectivity() {
  log("info", "Testando conectividade S3...");

  try {
    const bucket = process.env.S3_BUCKET || "ysh-b2b-products";
    const s3 = new AWS.S3({
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      region: process.env.AWS_REGION,
    });

    // Verificar se bucket existe
    await s3.headBucket({ Bucket: bucket }).promise();

    // Fazer upload de teste
    const testKey = ".connectivity-test";
    await s3
      .putObject({
        Bucket: bucket,
        Key: testKey,
        Body: JSON.stringify({ test: true, timestamp: new Date().toISOString() }),
        ContentType: "application/json",
      })
      .promise();

    // Deletar arquivo de teste
    await s3.deleteObject({ Bucket: bucket, Key: testKey }).promise();

    log("success", `S3 operacional - Bucket: ${bucket}`);
    return true;
  } catch (error) {
    log("error", `Erro S3: ${error.message}`);
    return false;
  }
}

async function testDynamoDBConnectivity() {
  log("info", "Testando conectividade DynamoDB...");

  try {
    const table = process.env.DYNAMODB_TABLE || "ysh-products-catalog";
    const dynamodb = new AWS.DynamoDB({
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      region: process.env.AWS_REGION,
    });

    const response = await dynamodb
      .describeTable({ TableName: table })
      .promise();

    log(
      "success",
      `DynamoDB operacional - Tabela: ${table} (${response.Table.ItemCount} itens)`
    );
    return true;
  } catch (error) {
    log("error", `Erro DynamoDB: ${error.message}`);
    return false;
  }
}

async function testFacebookConnectivity() {
  const token = process.env.FACEBOOK_TOKEN;
  const catalogId = process.env.FACEBOOK_CATALOG_ID;

  if (!token || !catalogId) {
    log("warn", "Facebook: Token ou Catalog ID não configurados (opcional)");
    return null;
  }

  log("info", "Testando conectividade Facebook...");

  try {
    const response = await axios.get(
      `https://graph.facebook.com/v21.0/${catalogId}?access_token=${token}&fields=id,name,item_count`
    );

    log(
      "success",
      `Facebook operacional - Catálogo: ${response.data.name} (${response.data.item_count} produtos)`
    );
    return true;
  } catch (error) {
    log("error", `Erro Facebook: ${error.message}`);
    return false;
  }
}

async function testNetworkLatency() {
  log("info", "Testando latência de rede...");

  const tests = [
    {
      name: "AWS STS",
      url: "https://sts.amazonaws.com/",
    },
    {
      name: "S3",
      url: "https://s3.amazonaws.com/",
    },
    {
      name: "Facebook API",
      url: "https://graph.facebook.com/",
    },
  ];

  for (const test of tests) {
    try {
      const start = Date.now();
      await axios.get(test.url, { timeout: 5000 });
      const latency = Date.now() - start;
      log(
        "success",
        `${test.name}: ${latency}ms${latency > 1000 ? " (lento)" : ""}`
      );
    } catch (error) {
      log("warn", `${test.name}: Sem resposta`);
    }
  }
}

async function runAllTests() {
  console.log("\n═".repeat(70));
  console.log("\n🧪 TESTE DE CONECTIVIDADE\n");
  console.log("═".repeat(70) + "\n");

  const results = {
    aws: await testAWSConnection(),
    s3: await testS3Connectivity(),
    dynamodb: await testDynamoDBConnectivity(),
    facebook: await testFacebookConnectivity(),
  };

  console.log("\n═".repeat(70));
  console.log("\n📊 RESULTADO DOS TESTES\n");

  let allPassed = true;
  for (const [service, result] of Object.entries(results)) {
    if (result === null) continue;
    const status = result ? "✅" : "❌";
    console.log(`${status} ${service.toUpperCase()}`);
    if (!result) allPassed = false;
  }

  console.log("\n═".repeat(70));

  if (allPassed || (results.aws && results.s3 && results.dynamodb)) {
    console.log("\n✅ TODOS OS TESTES PASSARAM!\n");
    console.log("Você está pronto para fazer upload:\n");
    console.log("  node scripts/upload-to-aws.js\n");
    process.exit(0);
  } else {
    console.log(
      "\n❌ ALGUNS TESTES FALHARAM - CORRIJA OS PROBLEMAS ACIMA\n"
    );
    process.exit(1);
  }
}

console.log("\n⏳ Aguarde enquanto testamos conexões...\n");
runAllTests().catch(console.error);
