/**
 * Check CloudFront Distribution Status
 * 
 * Usage:
 *   node scripts/check-cloudfront-status.js
 */

import AWS from 'aws-sdk';
import { existsSync, readFileSync, writeFileSync } from 'fs';

const cloudfront = new AWS.CloudFront({ region: 'us-east-1' });

async function checkDistributionStatus() {
  try {
    if (!existsSync('cloudfront-distribution-info.json')) {
      console.error('❌ Arquivo cloudfront-distribution-info.json não encontrado.');
      console.error('   Execute primeiro: node scripts/create-cloudfront-distribution.js\n');
      process.exit(1);
    }

    const distInfo = JSON.parse(readFileSync('cloudfront-distribution-info.json', 'utf8'));
    const distributionId = distInfo.distributionId;

    console.log('🔍 Verificando status da CloudFront distribution...\n');
    console.log(`   Distribution ID: ${distributionId}\n`);

    const result = await cloudfront.getDistribution({ Id: distributionId }).promise();
    const distribution = result.Distribution;

    console.log('📊 STATUS DA DISTRIBUTION:\n');
    console.log('=' .repeat(70));
    console.log(`\nStatus: ${distribution.Status}`);
    console.log(`Domain Name: ${distribution.DomainName}`);
    console.log(`Enabled: ${distribution.DistributionConfig.Enabled}`);
    console.log(`Aliases: ${distribution.DistributionConfig.Aliases.Items.join(', ')}`);
    console.log(`Price Class: ${distribution.DistributionConfig.PriceClass}`);

    if (distribution.Status === 'Deployed') {
      console.log('\n✅ DISTRIBUTION IMPLANTADA COM SUCESSO!\n');
      console.log('📋 Configure agora o DNS no GoDaddy:\n');
      console.log('   Tipo: CNAME');
      console.log(`   Nome: ${distInfo.dnsRecords.name}`);
      console.log(`   Valor: ${distInfo.dnsRecords.value}`);
      console.log(`   TTL: ${distInfo.dnsRecords.ttl}\n`);
      console.log('🔗 URL de teste (após configurar DNS):');
      console.log(`   https://${distribution.DistributionConfig.Aliases.Items[0]}/products/inversores/286844.png\n`);
    } else if (distribution.Status === 'InProgress') {
      console.log('\n⏳ DEPLOYMENT EM ANDAMENTO...\n');
      console.log('   Aguarde alguns minutos e execute novamente este script.');
      console.log('   O deployment geralmente leva 15-30 minutos.\n');
    } else {
      console.log(`\n⚠️  Status: ${distribution.Status}\n`);
    }

    console.log('='.repeat(70) + '\n');

    // Update saved info
    distInfo.status = distribution.Status;
    distInfo.lastChecked = new Date().toISOString();
    writeFileSync('cloudfront-distribution-info.json', JSON.stringify(distInfo, null, 2));

  } catch (error) {
    console.error('❌ Erro ao verificar distribution:', error.message);
    process.exit(1);
  }
}

checkDistributionStatus();
