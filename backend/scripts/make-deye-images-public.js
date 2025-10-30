#!/usr/bin/env node

/**
 * Configurar ACL pública para as imagens DEYE
 */

import AWS from "aws-sdk";

const AWS_REGION = process.env.AWS_REGION || "us-east-1";
const S3_BUCKET = process.env.S3_BUCKET || "ysh-b2b-products";
const S3_PREFIX = "images/products";

const s3 = new AWS.S3({ region: AWS_REGION });

const DEYE_IMAGES = [
  "222132.png",
  "222133.png", 
  "286844.png"
];

async function makePublic() {
  console.log("\n🔓 Tornando imagens DEYE públicas\n");
  
  for (const filename of DEYE_IMAGES) {
    const s3Key = `${S3_PREFIX}/inversores/${filename}`;
    
    try {
      await s3.putObjectAcl({
        Bucket: S3_BUCKET,
        Key: s3Key,
        ACL: 'public-read'
      }).promise();
      
      console.log(`✓ ${filename} agora é público`);
    } catch (error) {
      console.error(`❌ Erro em ${filename}: ${error.message}`);
    }
  }
  
  console.log("\n✅ Concluído\n");
}

makePublic().catch(console.error);
