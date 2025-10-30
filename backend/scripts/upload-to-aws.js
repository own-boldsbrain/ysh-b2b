#!/usr/bin/env node

/**
 * Script maestro para upload completo em AWS
 * - Verifica credenciais
 * - Faz upload de imagens em S3
 * - Faz upload de SKUs em DynamoDB
 * - Gera sincronização para Facebook
 */

import { spawn } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function runCommand(command, args, env = {}) {
  return new Promise((resolve, reject) => {
    const process = spawn(command, args, {
      stdio: "inherit",
      env: { ...process.env, ...env },
    });

    process.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command failed with code ${code}`));
      }
    });
  });
}

async function executeAWSUpload() {
  console.log("\n🚀 UPLOAD COMPLETO PARA AWS - INICIALIZANDO\n");
  console.log("═".repeat(70));

  try {
    // 1. Verificar credenciais
    console.log("\n🔐 ETAPA 0: Verificando Credenciais AWS\n");

    const requiredEnvs = [
      "AWS_ACCESS_KEY_ID",
      "AWS_SECRET_ACCESS_KEY",
      "AWS_REGION",
    ];

    for (const env of requiredEnvs) {
      if (!process.env[env]) {
        console.error(`❌ Variável ${env} não configurada`);
        console.log("\nConfigure as variáveis de ambiente:");
        console.log("  export AWS_ACCESS_KEY_ID=your_key");
        console.log("  export AWS_SECRET_ACCESS_KEY=your_secret");
        console.log("  export AWS_REGION=us-east-1");
        process.exit(1);
      }
    }

    console.log("✓ AWS_REGION:", process.env.AWS_REGION);
    console.log("✓ S3_BUCKET:", process.env.S3_BUCKET || "ysh-b2b-products");
    console.log(
      "✓ DYNAMODB_TABLE:",
      process.env.DYNAMODB_TABLE || "ysh-products-catalog"
    );
    console.log("✓ Credenciais: Configuradas\n");

    // 2. Upload de imagens
    console.log("═".repeat(70));
    console.log("\n📸 ETAPA 1: UPLOAD DE IMAGENS PARA S3\n");

    try {
      await runCommand("node", ["scripts/upload-images-s3.js"], {
        AWS_REGION: process.env.AWS_REGION,
        AWS_ACCESS_KEY_ID: process.env.AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY: process.env.AWS_SECRET_ACCESS_KEY,
        S3_BUCKET: process.env.S3_BUCKET,
      });
      console.log("✅ Upload de imagens concluído\n");
    } catch (error) {
      console.error("❌ Erro no upload de imagens:", error.message);
      process.exit(1);
    }

    // 3. Upload de SKUs
    console.log("═".repeat(70));
    console.log("\n📦 ETAPA 2: UPLOAD DE SKUs PARA DYNAMODB\n");

    try {
      await runCommand("node", ["scripts/upload-skus-dynamodb.js"], {
        AWS_REGION: process.env.AWS_REGION,
        AWS_ACCESS_KEY_ID: process.env.AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY: process.env.AWS_SECRET_ACCESS_KEY,
        DYNAMODB_TABLE: process.env.DYNAMODB_TABLE,
      });
      console.log("✅ Upload de SKUs concluído\n");
    } catch (error) {
      console.error("❌ Erro no upload de SKUs:", error.message);
      process.exit(1);
    }

    // 4. Gerar relatório final
    console.log("═".repeat(70));
    console.log("\n📋 ETAPA 3: RELATÓRIO FINAL\n");

    const s3Report = JSON.parse(
      fs.readFileSync(path.join(__dirname, "../S3_UPLOAD_REPORT.json"), "utf8")
    );
    const dynamodbReport = JSON.parse(
      fs.readFileSync(
        path.join(__dirname, "../DYNAMODB_UPLOAD_REPORT.json"),
        "utf8"
      )
    );

    const finalReport = {
      timestamp: new Date().toISOString(),
      status: "COMPLETED",
      aws_region: process.env.AWS_REGION,
      s3: {
        bucket: s3Report.s3_bucket,
        images_uploaded: s3Report.uploaded_count,
        errors: s3Report.error_count,
      },
      dynamodb: {
        table: dynamodbReport.dynamodb_table,
        skus_uploaded: dynamodbReport.uploaded_count,
        errors: dynamodbReport.error_count,
      },
      next_steps: [
        "Verificar S3 bucket no AWS Console",
        "Verificar tabela DynamoDB no AWS Console",
        "Sincronizar com Facebook Catalog",
        "Testar Instagram Shopping e WhatsApp",
      ],
    };

    const finalReportPath = path.join(__dirname, "../AWS_UPLOAD_COMPLETE.json");
    fs.writeFileSync(finalReportPath, JSON.stringify(finalReport, null, 2));

    console.log("✅ Relatório Final:\n");
    console.log(`   S3 Bucket: ${s3Report.s3_bucket}`);
    console.log(`   Imagens: ${s3Report.uploaded_count} enviadas`);
    console.log(`\n   DynamoDB Table: ${dynamodbReport.dynamodb_table}`);
    console.log(`   SKUs: ${dynamodbReport.uploaded_count} enviados`);
    console.log(`\n   Status: COMPLETO ✅`);
    console.log(`   Relatório: AWS_UPLOAD_COMPLETE.json\n`);

    // 5. Resumo e próximos passos
    console.log("═".repeat(70));
    console.log("\n🎉 UPLOAD PARA AWS CONCLUÍDO COM SUCESSO!\n");

    console.log("📊 RESUMO:\n");
    console.log(`   • ${s3Report.uploaded_count} imagens no S3`);
    console.log(`   • ${dynamodbReport.uploaded_count} SKUs no DynamoDB`);
    console.log(`   • Região: ${process.env.AWS_REGION}`);
    console.log(`   • Tempo: ${new Date().toLocaleString("pt-BR")}\n`);

    console.log("🚀 PRÓXIMOS PASSOS:\n");
    console.log("1. Verificar AWS Console:");
    console.log(`   • S3: https://s3.console.aws.amazon.com/s3/buckets/${s3Report.s3_bucket}`);
    console.log(
      `   • DynamoDB: https://console.aws.amazon.com/dynamodbv2/home#tables`
    );
    console.log("\n2. Sincronizar com Facebook:");
    console.log("   node scripts/sync-facebook-from-aws.js");
    console.log("\n3. Validar em plataformas Meta\n");

    process.exit(0);
  } catch (error) {
    console.error("\n❌ ERRO:", error.message);
    process.exit(1);
  }
}

executeAWSUpload().catch(console.error);
