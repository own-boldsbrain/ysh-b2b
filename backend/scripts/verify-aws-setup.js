#!/usr/bin/env node

/**
 * Script de verificação pré-upload para AWS
 * Valida credenciais, arquivos e configurações
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import AWS from "aws-sdk";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function checkEnvironmentVariables() {
  console.log("\n🔐 VERIFICANDO VARIÁVEIS DE AMBIENTE\n");
  const required = {
    AWS_ACCESS_KEY_ID: "Chave de acesso AWS",
    AWS_SECRET_ACCESS_KEY: "Chave secreta AWS",
    AWS_REGION: "Região AWS",
  };

  const optional = {
    FACEBOOK_TOKEN: "Token Facebook (para sincronização)",
    FACEBOOK_CATALOG_ID: "ID Catálogo Facebook (para sincronização)",
    S3_BUCKET: `Bucket S3 (padrão: ysh-b2b-products)`,
    DYNAMODB_TABLE: `Tabela DynamoDB (padrão: ysh-products-catalog)`,
  };

  let allValid = true;

  for (const [key, description] of Object.entries(required)) {
    if (process.env[key]) {
      console.log(`✅ ${key}: Configurado`);
    } else {
      console.log(`❌ ${key}: FALTANDO (${description})`);
      allValid = false;
    }
  }

  console.log("\n📋 Variáveis Opcionais:\n");
  for (const [key, description] of Object.entries(optional)) {
    if (process.env[key]) {
      console.log(`✅ ${key}: Configurado`);
    } else {
      console.log(`⚠️  ${key}: Não configurado (${description})`);
    }
  }

  return allValid;
}

async function checkAWSCredentials() {
  console.log("\n🌐 VALIDANDO CREDENCIAIS AWS\n");

  try {
    const credentials = new AWS.Credentials({
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    });

    const sts = new AWS.STS({ credentials, region: process.env.AWS_REGION });
    const identity = await sts.getCallerIdentity({}).promise();

    console.log(`✅ AWS Account ID: ${identity.Account}`);
    console.log(`✅ AWS User ARN: ${identity.Arn}`);
    console.log(`✅ Region: ${process.env.AWS_REGION}`);

    return true;
  } catch (error) {
    console.error(`❌ Erro ao validar credenciais AWS: ${error.message}`);
    return false;
  }
}

async function checkS3Bucket() {
  console.log("\n📦 VERIFICANDO S3 BUCKET\n");

  try {
    const bucket = process.env.S3_BUCKET || "ysh-b2b-products";
    const s3 = new AWS.S3({
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      region: process.env.AWS_REGION,
    });

    const headBucket = await s3.headBucket({ Bucket: bucket }).promise();
    console.log(`✅ Bucket S3 existe: ${bucket}`);

    // Contar objetos
    const listObjects = await s3
      .listObjectsV2({ Bucket: bucket })
      .promise();
    console.log(`   Objetos no bucket: ${listObjects.Contents?.length || 0}`);

    return true;
  } catch (error) {
    if (error.code === "NoSuchBucket") {
      console.log(`⚠️  Bucket não existe: ${process.env.S3_BUCKET || "ysh-b2b-products"}`);
      console.log("   Criando novo bucket...\n");
      return await createS3Bucket();
    } else {
      console.error(`❌ Erro ao verificar S3: ${error.message}`);
      return false;
    }
  }
}

async function createS3Bucket() {
  try {
    const bucket = process.env.S3_BUCKET || "ysh-b2b-products";
    const s3 = new AWS.S3({
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      region: process.env.AWS_REGION,
    });

    const region = process.env.AWS_REGION || "us-east-1";

    const params = {
      Bucket: bucket,
      ...(region !== "us-east-1" && {
        CreateBucketConfiguration: { LocationConstraint: region },
      }),
    };

    await s3.createBucket(params).promise();
    console.log(`✅ Bucket criado: ${bucket}`);

    // Ativar acesso público
    await s3
      .putBucketPolicy({
        Bucket: bucket,
        Policy: JSON.stringify({
          Version: "2012-10-17",
          Statement: [
            {
              Effect: "Allow",
              Principal: "*",
              Action: "s3:GetObject",
              Resource: `arn:aws:s3:::${bucket}/*`,
            },
          ],
        }),
      })
      .promise();

    console.log(`✅ Política de acesso público ativada\n`);
    return true;
  } catch (error) {
    console.error(`❌ Erro ao criar bucket: ${error.message}`);
    return false;
  }
}

async function checkDynamoDBTable() {
  console.log("\n🗄️  VERIFICANDO DYNAMODB TABLE\n");

  try {
    const table = process.env.DYNAMODB_TABLE || "ysh-products-catalog";
    const dynamodb = new AWS.DynamoDB({
      accessKeyId: process.env.AWS_ACCESS_KEY_ID,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
      region: process.env.AWS_REGION,
    });

    const describeTable = await dynamodb
      .describeTable({ TableName: table })
      .promise();

    console.log(`✅ Tabela DynamoDB existe: ${table}`);
    console.log(`   Status: ${describeTable.Table.TableStatus}`);
    console.log(`   Itens: ${describeTable.Table.ItemCount}`);

    return true;
  } catch (error) {
    if (error.code === "ResourceNotFoundException") {
      console.log(`⚠️  Tabela não existe: ${process.env.DYNAMODB_TABLE || "ysh-products-catalog"}`);
      console.log("   Use CloudFormation para criar: aws-cloudformation/main-stack-simple.yml\n");
      return false;
    } else {
      console.error(`❌ Erro ao verificar DynamoDB: ${error.message}`);
      return false;
    }
  }
}

async function checkLocalFiles() {
  console.log("\n📁 VERIFICANDO ARQUIVOS LOCAIS\n");

  const requiredDirectories = [
    "static/products",
    "scripts",
  ];

  const requiredFiles = [
    "package.json",
    "scripts/upload-images-s3.js",
    "scripts/upload-skus-dynamodb.js",
    "scripts/upload-to-aws.js",
  ];

  let allValid = true;

  for (const dir of requiredDirectories) {
    const fullPath = path.join(__dirname, "..", dir);
    if (fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()) {
      console.log(`✅ Diretório existe: ${dir}`);
    } else {
      console.log(`❌ Diretório faltando: ${dir}`);
      allValid = false;
    }
  }

  for (const file of requiredFiles) {
    const fullPath = path.join(__dirname, "..", file);
    if (fs.existsSync(fullPath)) {
      console.log(`✅ Arquivo existe: ${file}`);
    } else {
      console.log(`❌ Arquivo faltando: ${file}`);
      allValid = false;
    }
  }

  return allValid;
}

async function checkImageDirectory() {
  console.log("\n📸 VERIFICANDO IMAGENS\n");

  try {
    const imgDir = path.join(__dirname, "..", "static", "products");

    if (!fs.existsSync(imgDir)) {
      console.log(`❌ Diretório static/products não encontrado`);
      return false;
    }

    let imageCount = 0;
    let categories = new Set();

    const countImages = (dir) => {
      const files = fs.readdirSync(dir);
      for (const file of files) {
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
          categories.add(file);
          countImages(fullPath);
        } else if ([".jpg", ".jpeg", ".png", ".webp", ".gif"].includes(path.extname(file).toLowerCase())) {
          imageCount++;
        }
      }
    };

    countImages(imgDir);

    console.log(`✅ Total de imagens: ${imageCount}`);
    console.log(`✅ Categorias: ${categories.size}`);
    console.log(`   ${Array.from(categories).join(", ")}\n`);

    return imageCount > 0;
  } catch (error) {
    console.error(`❌ Erro ao verificar imagens: ${error.message}`);
    return false;
  }
}

async function runAllChecks() {
  console.log("═".repeat(70));
  console.log("\n🔍 VERIFICAÇÃO PRÉ-UPLOAD AWS\n");
  console.log("═".repeat(70));

  const checks = {
    "Variáveis de Ambiente": await checkEnvironmentVariables(),
    "Credenciais AWS": await checkAWSCredentials(),
    "S3 Bucket": await checkS3Bucket(),
    "DynamoDB Table": await checkDynamoDBTable(),
    "Arquivos Locais": await checkLocalFiles(),
    "Diretório de Imagens": await checkImageDirectory(),
  };

  console.log("\n═".repeat(70));
  console.log("\n📊 RESUMO DAS VERIFICAÇÕES\n");

  let allPassed = true;
  for (const [check, result] of Object.entries(checks)) {
    const status = result ? "✅" : "❌";
    console.log(`${status} ${check}`);
    if (!result) allPassed = false;
  }

  console.log("\n═".repeat(70));

  if (allPassed) {
    console.log("\n✅ TUDO PRONTO PARA UPLOAD!\n");
    console.log("Próximo comando:\n");
    console.log("  node scripts/upload-to-aws.js\n");
    process.exit(0);
  } else {
    console.log("\n❌ AJUSTE OS ERROS ACIMA ANTES DE CONTINUAR\n");
    process.exit(1);
  }
}

runAllChecks().catch(console.error);
