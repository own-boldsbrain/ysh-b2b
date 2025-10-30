/**
 * Sync Manufacturer Images to CDN
 * Synchronizes official manufacturer images with SKUs and uploads to S3/CDN
 * 
 * Usage:
 *   node scripts/sync-manufacturer-images-to-cdn.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import AWS from 'aws-sdk';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const s3 = new AWS.S3({ region: 'us-east-1' });
const BUCKET_NAME = 'ysh-b2b-products';
const CLOUDFRONT_DOMAIN = 'https://cdn.yellosolarhub.com';

// Image source directory
const SOURCE_DIR = path.join(__dirname, '..', 'static', 'products', 'inversores');
const OFFICIAL_DIR = path.join(__dirname, '..', 'static', 'products-official');

// Manufacturer patterns
const MANUFACTURER_PATTERNS = {
  DEYE: /^DEYE-(.+)_image\.(webp|jpg|jpeg|png)$/i,
  GOODWE: /^GOODWE-(.+)_image\.(webp|jpg|jpeg|png)$/i,
  ENPHASE: /^ENPHASE-(.+)_IMAGE_PRODUCT_\d+\.(webp|jpg|jpeg|png)$/i,
  GROWATT: /^GROWATT-(.+)_IMAGE_PRODUCT_\d+\.(webp|jpg|jpeg|png)$/i,
  HUAWEI: /^HUAWEI-(.+)_IMAGE_PRODUCT_\d+\.(webp|jpg|jpeg|png)$/i
};

function sanitizeFilename(str) {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

async function uploadToS3(localPath, s3Key, contentType) {
  const fileContent = fs.readFileSync(localPath);
  
  const params = {
    Bucket: BUCKET_NAME,
    Key: s3Key,
    Body: fileContent,
    ContentType: contentType
  };

  await s3.putObject(params).promise();
  return `${CLOUDFRONT_DOMAIN}/${s3Key.replace('images/', '')}`;
}

function getContentType(ext) {
  const types = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp'
  };
  return types[ext.toLowerCase()] || 'application/octet-stream';
}

async function syncImages() {
  console.log('🔄 Sincronizando imagens de fabricantes com CDN...\n');
  
  if (!fs.existsSync(SOURCE_DIR)) {
    console.error(`❌ Diretório não encontrado: ${SOURCE_DIR}`);
    process.exit(1);
  }

  const files = fs.readdirSync(SOURCE_DIR);
  const results = {
    total: 0,
    uploaded: 0,
    skipped: 0,
    errors: 0,
    byManufacturer: {}
  };

  for (const file of files) {
    results.total++;

    // Check if matches any manufacturer pattern
    let manufacturer = null;
    let modelName = null;

    for (const [mfr, regex] of Object.entries(MANUFACTURER_PATTERNS)) {
      const match = file.match(regex);
      if (match) {
        manufacturer = mfr;
        modelName = match[1];
        break;
      }
    }

    if (!manufacturer) {
      // Skip generic IMAGE_PRODUCT files
      if (file.startsWith('IMAGE_PRODUCT_')) {
        results.skipped++;
        continue;
      }
      
      results.skipped++;
      continue;
    }

    console.log(`📦 ${manufacturer}: ${modelName}`);
    
    try {
      // Create official directory structure
      const mfrDir = path.join(OFFICIAL_DIR, manufacturer.toLowerCase(), 'inversores');
      if (!fs.existsSync(mfrDir)) {
        fs.mkdirSync(mfrDir, { recursive: true });
      }

      // Generate clean filename
      const ext = path.extname(file);
      const cleanModel = sanitizeFilename(modelName);
      const officialFilename = `${cleanModel}${ext}`;
      const officialPath = path.join(mfrDir, officialFilename);

      // Copy to official directory
      const sourcePath = path.join(SOURCE_DIR, file);
      fs.copyFileSync(sourcePath, officialPath);
      console.log(`   ✅ Copiado: ${path.relative(process.cwd(), officialPath)}`);

      // Upload to S3
      const s3Key = `images/products/inversores/${manufacturer.toLowerCase()}-${cleanModel}${ext}`;
      const contentType = getContentType(ext);
      const cdnUrl = await uploadToS3(officialPath, s3Key, contentType);
      
      console.log(`   🌐 CDN: ${cdnUrl}\n`);

      results.uploaded++;
      
      // Track by manufacturer
      if (!results.byManufacturer[manufacturer]) {
        results.byManufacturer[manufacturer] = 0;
      }
      results.byManufacturer[manufacturer]++;

    } catch (error) {
      console.error(`   ❌ Erro: ${error.message}\n`);
      results.errors++;
    }
  }

  // Summary
  console.log('='.repeat(70));
  console.log('\n📊 RESUMO DA SINCRONIZAÇÃO\n');
  console.log(`   Total de arquivos: ${results.total}`);
  console.log(`   ✅ Uploaded: ${results.uploaded}`);
  console.log(`   ⏭️  Skipped: ${results.skipped}`);
  console.log(`   ❌ Errors: ${results.errors}\n`);

  console.log('📦 Por Fabricante:\n');
  Object.entries(results.byManufacturer)
    .sort(([,a], [,b]) => b - a)
    .forEach(([mfr, count]) => {
      console.log(`   ${mfr}: ${count} imagens`);
    });

  console.log('\n' + '='.repeat(70));
  
  if (results.uploaded > 0) {
    console.log('\n✨ Próximo passo: Invalidar cache do CloudFront');
    console.log('   npm run aws:invalidate-cache\n');
  }
}

syncImages().catch(error => {
  console.error('\n❌ Erro fatal:', error);
  process.exit(1);
});
