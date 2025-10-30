/**
 * Invalidate CloudFront Cache
 * Use after updating images in S3 to clear CDN cache
 * 
 * Usage:
 *   node scripts/invalidate-cloudfront-cache.js [path]
 *   
 * Examples:
 *   node scripts/invalidate-cloudfront-cache.js                    # Invalidate all
 *   node scripts/invalidate-cloudfront-cache.js /products/*        # Specific path
 */

import AWS from 'aws-sdk';
import { existsSync, readFileSync } from 'fs';

const cloudfront = new AWS.CloudFront({ region: 'us-east-1' });

async function invalidateCache() {
  try {
    if (!existsSync('cloudfront-distribution-info.json')) {
      console.error('❌ CloudFront distribution não encontrada.');
      console.error('   Execute primeiro: node scripts/create-cloudfront-distribution.js\n');
      process.exit(1);
    }

    const distInfo = JSON.parse(readFileSync('cloudfront-distribution-info.json', 'utf8'));
    const distributionId = distInfo.distributionId;

    // Get path from command line or default to all
    const path = process.argv[2] || '/*';
    const paths = path.split(',').map(p => p.trim());

    console.log('🔄 Invalidando cache do CloudFront...\n');
    console.log(`   Distribution: ${distributionId}`);
    console.log(`   Paths: ${paths.join(', ')}\n`);

    const params = {
      DistributionId: distributionId,
      InvalidationBatch: {
        CallerReference: `invalidation-${Date.now()}`,
        Paths: {
          Quantity: paths.length,
          Items: paths
        }
      }
    };

    const result = await cloudfront.createInvalidation(params).promise();
    const invalidation = result.Invalidation;

    console.log('✅ Invalidação criada com sucesso!\n');
    console.log(`   Invalidation ID: ${invalidation.Id}`);
    console.log(`   Status: ${invalidation.Status}`);
    console.log(`   Criado em: ${invalidation.CreateTime}\n`);

    console.log('⏱️  A invalidação geralmente leva 1-5 minutos.\n');
    console.log('🔍 Verificar status:');
    console.log(`   aws cloudfront get-invalidation --distribution-id ${distributionId} --id ${invalidation.Id}\n`);

  } catch (error) {
    console.error('❌ Erro ao invalidar cache:', error.message);
    
    if (error.code === 'TooManyInvalidationsInProgress') {
      console.error('\n⚠️  Muitas invalidações em progresso. Aguarde alguns minutos.');
    }

    process.exit(1);
  }
}

invalidateCache();
