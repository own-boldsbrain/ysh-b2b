#!/usr/bin/env node

/**
 * Script para upload de imagens para AWS S3
 * - Localiza todas as imagens em static/products
 * - Faz upload em batch para S3
 * - Gera URLs públicas
 * - Atualiza product_image_map.json com URLs do S3
 */

import AWS from "aws-sdk";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuração AWS
const AWS_REGION = process.env.AWS_REGION || "us-east-1";
const S3_BUCKET = process.env.S3_BUCKET || "ysh-b2b-products";
const S3_PREFIX = "images/products";

// Inicializar S3
const s3 = new AWS.S3({
  region: AWS_REGION,
});

const STATIC_PRODUCTS_PATH = path.join(__dirname, "../static/products");
const IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".gif"];

async function uploadImagesToS3() {
  console.log("\n🚀 UPLOAD DE IMAGENS PARA AWS S3\n");
  console.log("═".repeat(70));

  try {
    // 1. Verificar credenciais AWS
    console.log("\n🔐 ETAPA 1: Verificando Credenciais AWS\n");

    if (!process.env.AWS_ACCESS_KEY_ID || !process.env.AWS_SECRET_ACCESS_KEY) {
      console.error(
        "❌ Credenciais AWS não configuradas em variáveis de ambiente"
      );
      console.log(
        "   Configure: AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY\n"
      );
      process.exit(1);
    }

    console.log("✓ AWS_REGION:", AWS_REGION);
    console.log("✓ S3_BUCKET:", S3_BUCKET);
    console.log("✓ S3_PREFIX:", S3_PREFIX);
    console.log("✓ Credenciais: Configuradas\n");

    // 2. Verificar se bucket existe
    console.log("🪣 ETAPA 2: Verificando Bucket S3\n");

    try {
      await s3.headBucket({ Bucket: S3_BUCKET }).promise();
      console.log(`✓ Bucket '${S3_BUCKET}' existe e é acessível\n`);
    } catch (error) {
      if (error.code === "NotFound") {
        console.log(
          `⚠️  Bucket '${S3_BUCKET}' não existe. Criando...\n`
        );
        await s3
          .createBucket({ Bucket: S3_BUCKET })
          .promise();
        console.log(`✓ Bucket criado: ${S3_BUCKET}\n`);
      } else {
        throw error;
      }
    }

    // 3. Descobrir imagens
    console.log("📁 ETAPA 3: Descobrindo Imagens\n");

    const categories = fs
      .readdirSync(STATIC_PRODUCTS_PATH)
      .filter((f) => {
        const fullPath = path.join(STATIC_PRODUCTS_PATH, f);
        return fs.statSync(fullPath).isDirectory();
      });

    let totalImages = 0;
    const imagesToUpload = [];

    for (const category of categories) {
      const categoryPath = path.join(STATIC_PRODUCTS_PATH, category);
      const files = fs.readdirSync(categoryPath);

      for (const file of files) {
        const ext = path.extname(file).toLowerCase();
        if (!IMAGE_EXTENSIONS.includes(ext)) continue;

        const filePath = path.join(categoryPath, file);
        imagesToUpload.push({
          category,
          file,
          path: filePath,
          size: fs.statSync(filePath).size,
        });
        totalImages++;
      }
    }

    console.log(`✓ ${totalImages} imagens encontradas\n`);

    // 4. Fazer upload em batch
    console.log("📤 ETAPA 4: Fazendo Upload para S3\n");

    let uploadedCount = 0;
    let errorCount = 0;
    const s3Urls = {};
    const errors = [];

    for (const image of imagesToUpload) {
      const s3Key = `${S3_PREFIX}/${image.category}/${image.file}`;
      
      try {
        const fileContent = fs.readFileSync(image.path);

        await s3
          .putObject({
            Bucket: S3_BUCKET,
            Key: s3Key,
            Body: fileContent,
            ContentType: getMimeType(image.file),
          })
          .promise();

        const s3Url = `https://${S3_BUCKET}.s3.${AWS_REGION}.amazonaws.com/${s3Key}`;
        s3Urls[`${image.category}/${image.file}`] = s3Url;

        uploadedCount++;

        if (uploadedCount % 50 === 0) {
          console.log(`   ✓ ${uploadedCount}/${totalImages} imagens enviadas`);
        }
      } catch (error) {
        console.warn(`   ⚠️  Erro ao enviar ${image.file}: ${error.message}`);
        errors.push({ file: image.file, error: error.message });
        errorCount++;
        
        if (errorCount > 10) {
          console.error(`\n❌ Muitos erros detectados (${errorCount}). Abortando upload.`);
          throw new Error(`Upload abortado após ${errorCount} erros`);
        }
      }
    }

    console.log(`\n✓ Upload concluído: ${uploadedCount}/${totalImages}`);
    if (errorCount > 0) {
      console.log(`⚠️  Erros: ${errorCount}\n`);
    } else {
      console.log("");
    }

    // 5. Salvar relatório
    console.log("💾 ETAPA 5: Salvando Relatório\n");

    const report = {
      timestamp: new Date().toISOString(),
      aws_region: AWS_REGION,
      s3_bucket: S3_BUCKET,
      s3_prefix: S3_PREFIX,
      total_images: totalImages,
      uploaded_count: uploadedCount,
      error_count: errorCount,
      errors: errors,
      s3_urls: s3Urls,
      next_steps: [
        "Atualizar product_image_map.json com URLs do S3",
        "Fazer upload dos SKUs para DynamoDB",
        "Atualizar transformers para usar URLs do S3",
      ],
    };

    const reportPath = path.join(__dirname, "../S3_UPLOAD_REPORT.json");
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    console.log("✓ Relatório salvo: S3_UPLOAD_REPORT.json\n");

    // 6. Resultado final
    console.log("═".repeat(70));
    console.log("\n✅ UPLOAD PARA S3 CONCLUÍDO!\n");
    console.log(`📊 Estatísticas:`);
    console.log(`   • Imagens: ${totalImages}`);
    console.log(`   • Enviadas: ${uploadedCount}`);
    console.log(`   • Erros: ${errorCount}`);
    console.log(`   • Bucket: ${S3_BUCKET}`);
    console.log(`   • Região: ${AWS_REGION}\n`);

    console.log(
      `🔗 URLs Públicas: https://${S3_BUCKET}.s3.${AWS_REGION}.amazonaws.com/${S3_PREFIX}/{categoria}/{arquivo}\n`
    );

    process.exit(errorCount > 0 ? 1 : 0);
  } catch (error) {
    console.error("\n❌ ERRO NO UPLOAD:\n");
    console.error(error.message);
    process.exit(1);
  }
}

// Helper para MIME types
function getMimeType(filename) {
  const ext = path.extname(filename).toLowerCase();
  const mimeTypes = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
  };
  return mimeTypes[ext] || "application/octet-stream";
}

uploadImagesToS3().catch(console.error);
