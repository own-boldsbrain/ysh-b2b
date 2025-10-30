/**
 * Update Image URLs in Database/JSON
 * Replaces S3 direct URLs with CloudFront URLs
 * 
 * Usage:
 *   node scripts/update-image-urls-to-cloudfront.js
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';

const S3_BUCKET_URL = 'https://ysh-b2b-products.s3.us-east-1.amazonaws.com/images';
const CLOUDFRONT_DOMAIN = 'cdn.yellosolarhub.com';

async function updateImageUrls() {
  console.log('🔄 Atualizando URLs de imagens para CloudFront...\n');

  try {
    // Check if CloudFront is configured
    const cfInfoPath = 'cloudfront-distribution-info.json';
    if (!existsSync(cfInfoPath)) {
      console.error('❌ CloudFront não configurado.');
      console.error('   Execute: node scripts/create-cloudfront-distribution.js\n');
      process.exit(1);
    }

    const distInfo = JSON.parse(readFileSync(cfInfoPath, 'utf8'));
    const cloudfrontUrl = `https://${CLOUDFRONT_DOMAIN}`;

    console.log(`   De:   ${S3_BUCKET_URL}`);
    console.log(`   Para: ${cloudfrontUrl}\n`);
    console.log('=' .repeat(70) + '\n');

    // Update product_image_map.json (in static/products/)
    const productMapPath = join('static', 'products', 'product_image_map.json');
    if (existsSync(productMapPath)) {
      console.log('📋 Atualizando product_image_map.json...');
      
      const imageMap = JSON.parse(readFileSync(productMapPath, 'utf8'));
      let updated = 0;

      // Handle nested structure { images: { sku: [images...] } }
      if (imageMap.images) {
        Object.keys(imageMap.images).forEach(sku => {
          imageMap.images[sku].forEach(img => {
            if (img.s3_url && img.s3_url.includes(S3_BUCKET_URL)) {
              img.s3_url = img.s3_url.replace(S3_BUCKET_URL, cloudfrontUrl);
              img.cdn_url = img.s3_url; // Add CDN URL field
              updated++;
            }
          });
        });
      }

      writeFileSync(productMapPath, JSON.stringify(imageMap, null, 2));
      console.log(`   ✅ ${updated} URLs atualizadas\n`);
    }

    // Update unified-image-map.json (if exists)
    const unifiedMapPath = 'unified-image-map.json';
    if (existsSync(unifiedMapPath)) {
      console.log('📋 Atualizando unified-image-map.json...');
      
      const unifiedMap = JSON.parse(readFileSync(unifiedMapPath, 'utf8'));
      let updated = 0;

      Object.keys(unifiedMap).forEach(sku => {
        const item = unifiedMap[sku];
        if (item.s3_url && item.s3_url.includes(S3_BUCKET_URL)) {
          item.s3_url = item.s3_url.replace(S3_BUCKET_URL, cloudfrontUrl);
          item.cdn_url = item.s3_url;
          updated++;
        }
      });

      writeFileSync(unifiedMapPath, JSON.stringify(unifiedMap, null, 2));
      console.log(`   ✅ ${updated} URLs atualizadas\n`);
    }

    // Create backup of original S3 URLs
    const backup = {
      s3BucketUrl: S3_BUCKET_URL,
      cloudfrontUrl: cloudfrontUrl,
      updatedAt: new Date().toISOString(),
      note: 'Backup of URL migration. S3 URLs still work as fallback.'
    };

    writeFileSync('url-migration-backup.json', JSON.stringify(backup, null, 2));

    console.log('=' .repeat(70));
    console.log('\n✅ URLs atualizadas com sucesso!\n');
    console.log('📝 Benefícios do CloudFront:\n');
    console.log('   • ⚡ Latência reduzida (CDN global)');
    console.log('   • 💰 Custos menores (cache)');
    console.log('   • 🔒 HTTPS com certificado customizado');
    console.log('   • 🌐 Domínio personalizado\n');
    console.log('🔄 URLs S3 diretas continuam funcionando como fallback.\n');
    console.log('=' .repeat(70) + '\n');

  } catch (error) {
    console.error('❌ Erro ao atualizar URLs:', error.message);
    process.exit(1);
  }
}

updateImageUrls();
