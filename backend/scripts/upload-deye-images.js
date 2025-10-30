#!/usr/bin/env node

/**
 * Upload apenas das 3 imagens DEYE para S3
 */

import AWS from "aws-sdk";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const AWS_REGION = process.env.AWS_REGION || "us-east-1";
const S3_BUCKET = process.env.S3_BUCKET || "ysh-b2b-products";
const S3_PREFIX = "images/products";

const s3 = new AWS.S3({ region: AWS_REGION });

const DEYE_IMAGES = [
  "222132.png",
  "222133.png",
  "286844.png"
];

async function uploadDeyeImages() {
  console.log("\n🔧 Upload DEYE Images para S3\n");
  
  const inversoresPath = path.join(__dirname, "../static/products/inversores");
  
  for (const filename of DEYE_IMAGES) {
    const filePath = path.join(inversoresPath, filename);
    
    if (!fs.existsSync(filePath)) {
      console.log(`❌ ${filename} não encontrado`);
      continue;
    }
    
    const fileContent = fs.readFileSync(filePath);
    const s3Key = `${S3_PREFIX}/inversores/${filename}`;
    
    try {
      await s3.putObject({
        Bucket: S3_BUCKET,
        Key: s3Key,
        Body: fileContent,
        ContentType: "image/png",
      }).promise();
      
      const url = `https://${S3_BUCKET}.s3.${AWS_REGION}.amazonaws.com/${s3Key}`;
      console.log(`✓ ${filename} → ${url}`);
    } catch (error) {
      console.error(`❌ Erro ao enviar ${filename}: ${error.message}`);
    }
  }
  
  console.log("\n✅ Upload concluído\n");
}

uploadDeyeImages().catch(console.error);
