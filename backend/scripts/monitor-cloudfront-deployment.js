/**
 * Monitor CloudFront Deployment
 * Checks deployment status every minute until complete
 * 
 * Usage:
 *   node scripts/monitor-cloudfront-deployment.js
 */

import AWS from 'aws-sdk';
import { existsSync, readFileSync, writeFileSync } from 'fs';

const cloudfront = new AWS.CloudFront({ region: 'us-east-1' });
const CHECK_INTERVAL = 60000; // 1 minute
const MAX_CHECKS = 45; // 45 minutes

async function monitorDeployment() {
  try {
    if (!existsSync('cloudfront-distribution-info.json')) {
      console.error('❌ CloudFront distribution não encontrada.');
      process.exit(1);
    }

    const distInfo = JSON.parse(readFileSync('cloudfront-distribution-info.json', 'utf8'));
    const distributionId = distInfo.distributionId;

    console.log('🔄 Monitorando deployment do CloudFront...\n');
    console.log(`   Distribution ID: ${distributionId}`);
    console.log(`   Custom Domain: ${distInfo.aliases[0]}`);
    console.log(`   Intervalo: ${CHECK_INTERVAL / 1000}s`);
    console.log(`   Timeout: ${(MAX_CHECKS * CHECK_INTERVAL) / 60000} minutos\n`);
    console.log('=' .repeat(70) + '\n');

    let checks = 0;

    const checkStatus = async () => {
      checks++;
      const timestamp = new Date().toLocaleTimeString('pt-BR');

      try {
        const result = await cloudfront.getDistribution({ Id: distributionId }).promise();
        const distribution = result.Distribution;
        const status = distribution.Status;

        console.log(`[${timestamp}] Check ${checks}/${MAX_CHECKS} - Status: ${status}`);

        if (status === 'Deployed') {
          console.log('\n' + '='.repeat(70));
          console.log('\n🎉 CLOUDFRONT DEPLOYMENT CONCLUÍDO!\n');
          console.log(`   Distribution: ${distributionId}`);
          console.log(`   CloudFront URL: https://${distribution.DomainName}`);
          console.log(`   Custom Domain: https://${distInfo.aliases[0]}\n`);
          
          console.log('📋 PRÓXIMOS PASSOS:\n');
          console.log('1. Aguarde propagação DNS (5-30 minutos)');
          console.log('2. Teste acesso:');
          console.log(`   https://${distInfo.aliases[0]}/products/inversores/286844.png\n`);
          console.log('3. Atualize URLs no banco/JSON:');
          console.log('   npm run aws:update-urls\n');
          console.log('='.repeat(70) + '\n');

          // Update saved info
          distInfo.status = status;
          distInfo.deployedAt = new Date().toISOString();
          writeFileSync('cloudfront-distribution-info.json', JSON.stringify(distInfo, null, 2));

          process.exit(0);
        }

        if (checks >= MAX_CHECKS) {
          console.warn('\n⚠️  Timeout atingido. Execute novamente:\n');
          console.warn('   npm run aws:check-cloudfront\n');
          process.exit(0);
        }

        // Schedule next check
        setTimeout(checkStatus, CHECK_INTERVAL);

      } catch (error) {
        console.error(`\n❌ Erro: ${error.message}`);
        process.exit(1);
      }
    };

    // Start monitoring
    await checkStatus();

  } catch (error) {
    console.error('❌ Erro:', error.message);
    process.exit(1);
  }
}

monitorDeployment();
