#!/usr/bin/env node

/**
 * Configurar política de bucket S3 para permitir leitura pública de imagens
 */

import AWS from "aws-sdk";

const AWS_REGION = process.env.AWS_REGION || "us-east-1";
const S3_BUCKET = process.env.S3_BUCKET || "ysh-b2b-products";

const s3 = new AWS.S3({ region: AWS_REGION });

const bucketPolicy = {
  Version: "2012-10-17",
  Statement: [
    {
      Sid: "PublicReadGetObject",
      Effect: "Allow",
      Principal: "*",
      Action: "s3:GetObject",
      Resource: `arn:aws:s3:::${S3_BUCKET}/images/products/*`
    }
  ]
};

async function setBucketPolicy() {
  console.log("\n🔧 Configurando política de bucket S3\n");
  console.log(`Bucket: ${S3_BUCKET}`);
  console.log(`Região: ${AWS_REGION}\n`);
  
  try {
    // Verificar configuração atual de Block Public Access
    const blockConfig = await s3.getPublicAccessBlock({ Bucket: S3_BUCKET }).promise();
    
    console.log("📋 Configuração atual Block Public Access:");
    console.log(JSON.stringify(blockConfig.PublicAccessBlockConfiguration, null, 2));
    console.log("");
    
    if (blockConfig.PublicAccessBlockConfiguration.BlockPublicPolicy) {
      console.log("⚠️  BlockPublicPolicy está ativado. Desativando...\n");
      
      await s3.putPublicAccessBlock({
        Bucket: S3_BUCKET,
        PublicAccessBlockConfiguration: {
          BlockPublicAcls: true,  // Manter bloqueio de ACLs
          IgnorePublicAcls: true,  // Manter ignorar ACLs públicas
          BlockPublicPolicy: false, // Permitir políticas públicas
          RestrictPublicBuckets: false // Permitir acesso público via política
        }
      }).promise();
      
      console.log("✓ Block Public Access atualizado\n");
    }
    
    // Aplicar política do bucket
    await s3.putBucketPolicy({
      Bucket: S3_BUCKET,
      Policy: JSON.stringify(bucketPolicy)
    }).promise();
    
    console.log("✅ Política de bucket aplicada com sucesso!\n");
    console.log("📋 Política aplicada:");
    console.log(JSON.stringify(bucketPolicy, null, 2));
    console.log("\n🔗 As imagens em /images/products/* agora são públicas\n");
    
  } catch (error) {
    console.error("❌ Erro ao configurar política:", error.message);
    
    if (error.code === 'AccessDenied') {
      console.error("\n⚠️  Sem permissões suficientes. Verifique IAM policies.\n");
    }
    
    process.exit(1);
  }
}

setBucketPolicy().catch(console.error);
