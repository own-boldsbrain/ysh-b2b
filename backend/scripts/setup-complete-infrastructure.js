/**
 * Complete Infrastructure Setup Script
 * Runs all steps automatically once certificate is validated
 * 
 * Usage:
 *   node scripts/setup-complete-infrastructure.js
 */

import AWS from 'aws-sdk';
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const cloudfront = new AWS.CloudFront({ region: 'us-east-1' });
const acm = new AWS.ACM({ region: 'us-east-1' });

const BUCKET_NAME = 'ysh-b2b-products';
const DOMAIN = 'cdn.yellosolarhub.com';

async function setupInfrastructure() {
  console.log('🚀 YSH B2B - Complete Infrastructure Setup\n');
  console.log('=' .repeat(70) + '\n');

  try {
    // Step 1: Check certificate
    console.log('📋 PASSO 1: Verificando certificado ACM...\n');
    
    if (!existsSync('acm-certificate-info.json')) {
      console.error('❌ Certificado não encontrado. Execute: node scripts/request-acm-certificate.js');
      process.exit(1);
    }

    const certInfo = JSON.parse(readFileSync('acm-certificate-info.json', 'utf8'));
    
    const certResult = await acm.describeCertificate({
      CertificateArn: certInfo.certificateArn
    }).promise();

    const certStatus = certResult.Certificate.Status;
    
    if (certStatus !== 'ISSUED') {
      console.error(`❌ Certificado não validado (Status: ${certStatus})`);
      console.error('   Aguarde a validação DNS ou execute: node scripts/monitor-certificate-validation.js\n');
      process.exit(1);
    }

    console.log('✅ Certificado validado!\n');
    console.log(`   ARN: ${certInfo.certificateArn}`);
    console.log(`   Domínio: ${DOMAIN}\n`);

    // Step 2: Create CloudFront Distribution
    console.log('=' .repeat(70));
    console.log('\n📋 PASSO 2: Criando CloudFront Distribution...\n');

    // Check if distribution already exists
    if (existsSync('cloudfront-distribution-info.json')) {
      const existingDist = JSON.parse(readFileSync('cloudfront-distribution-info.json', 'utf8'));
      console.log('⚠️  Distribution já existe:');
      console.log(`   ID: ${existingDist.distributionId}`);
      console.log(`   Domain: ${existingDist.domainName}`);
      console.log(`   Status: ${existingDist.status}\n`);
      
      const response = await new Promise((resolve) => {
        const readline = require('readline').createInterface({
          input: process.stdin,
          output: process.stdout
        });
        readline.question('   Usar distribution existente? (s/n): ', (answer) => {
          readline.close();
          resolve(answer.toLowerCase() === 's');
        });
      });

      if (!response) {
        console.log('\n   Criando nova distribution...\n');
      } else {
        console.log('\n✅ Usando distribution existente\n');
        printFinalInstructions(existingDist);
        return;
      }
    }

    // Create distribution
    const s3 = new AWS.S3({ region: 'us-east-1' });
    const bucketLocation = await s3.getBucketLocation({ Bucket: BUCKET_NAME }).promise();
    const bucketRegion = bucketLocation.LocationConstraint || 'us-east-1';
    const originDomain = `${BUCKET_NAME}.s3.${bucketRegion}.amazonaws.com`;

    const distributionParams = {
      DistributionConfig: {
        CallerReference: `ysh-b2b-${Date.now()}`,
        Comment: 'YSH B2B Product Images - Auto Setup',
        Enabled: true,
        Origins: {
          Quantity: 1,
          Items: [{
            Id: 'S3-ysh-b2b-products',
            DomainName: originDomain,
            OriginPath: '/images',
            S3OriginConfig: { OriginAccessIdentity: '' },
            ConnectionAttempts: 3,
            ConnectionTimeout: 10,
            OriginShield: { Enabled: false }
          }]
        },
        DefaultCacheBehavior: {
          TargetOriginId: 'S3-ysh-b2b-products',
          ViewerProtocolPolicy: 'redirect-to-https',
          AllowedMethods: {
            Quantity: 2,
            Items: ['GET', 'HEAD'],
            CachedMethods: { Quantity: 2, Items: ['GET', 'HEAD'] }
          },
          Compress: true,
          ForwardedValues: {
            QueryString: false,
            Cookies: { Forward: 'none' },
            Headers: { Quantity: 0, Items: [] }
          },
          MinTTL: 0,
          DefaultTTL: 86400,
          MaxTTL: 31536000,
          TrustedSigners: { Enabled: false, Quantity: 0 },
          TrustedKeyGroups: { Enabled: false, Quantity: 0 }
        },
        Aliases: { Quantity: 1, Items: [DOMAIN] },
        ViewerCertificate: {
          ACMCertificateArn: certInfo.certificateArn,
          SSLSupportMethod: 'sni-only',
          MinimumProtocolVersion: 'TLSv1.2_2021',
          Certificate: certInfo.certificateArn,
          CertificateSource: 'acm'
        },
        PriceClass: 'PriceClass_100',
        CustomErrorResponses: {
          Quantity: 1,
          Items: [{ ErrorCode: 403, ErrorCachingMinTTL: 300 }]
        },
        Logging: { Enabled: false, IncludeCookies: false, Bucket: '', Prefix: '' },
        HttpVersion: 'http2and3',
        IsIPV6Enabled: true,
        Restrictions: {
          GeoRestriction: { RestrictionType: 'none', Quantity: 0 }
        }
      }
    };

    const distResult = await cloudfront.createDistribution(distributionParams).promise();
    const distribution = distResult.Distribution;

    console.log('✅ CloudFront Distribution criada!\n');
    console.log(`   ID: ${distribution.Id}`);
    console.log(`   Domain: ${distribution.DomainName}`);
    console.log(`   Status: ${distribution.Status}\n`);

    const distInfo = {
      distributionId: distribution.Id,
      domainName: distribution.DomainName,
      arn: distribution.ARN,
      status: distribution.Status,
      aliases: [DOMAIN],
      certificateArn: certInfo.certificateArn,
      createdAt: new Date().toISOString(),
      dnsRecords: {
        type: 'CNAME',
        name: 'images',
        value: distribution.DomainName,
        ttl: 3600
      }
    };

    writeFileSync('cloudfront-distribution-info.json', JSON.stringify(distInfo, null, 2));

    // Step 3: Print instructions
    printFinalInstructions(distInfo);

  } catch (error) {
    console.error('\n❌ Erro:', error.message);
    
    if (error.code === 'CNAMEAlreadyExists') {
      console.error('\n⚠️  Domínio já associado a outra distribution.');
      console.error('   Liste: aws cloudfront list-distributions');
    }
    
    process.exit(1);
  }
}

function printFinalInstructions(distInfo) {
  console.log('=' .repeat(70));
  console.log('\n🎯 PRÓXIMOS PASSOS - Configuração GoDaddy DNS\n');
  console.log('=' .repeat(70) + '\n');
  
  console.log('📋 ADICIONE ESTE REGISTRO CNAME NO GODADDY:\n');
  console.log('   Tipo:  CNAME');
  console.log('   Nome:  images');
  console.log(`   Valor: ${distInfo.dnsRecords.value}`);
  console.log('   TTL:   3600 (1 hora)\n');
  
  console.log('=' .repeat(70) + '\n');
  console.log('⏱️  AGUARDE:\n');
  console.log('   • CloudFront Deployment: 15-30 minutos');
  console.log('   • DNS Propagation: 5-30 minutos\n');
  
  console.log('✅ TESTE (após deployment e DNS):\n');
  console.log(`   https://${DOMAIN}/products/inversores/286844.png\n`);
  
  console.log('🔍 MONITORAR DEPLOYMENT:\n');
  console.log('   node scripts/check-cloudfront-status.js\n');
  
  console.log('=' .repeat(70) + '\n');
  
  // Save instructions to file
  const instructions = `# Instruções Finais - CloudFront + GoDaddy DNS

## ☁️ CloudFront Distribution

- **Distribution ID:** ${distInfo.distributionId}
- **CloudFront Domain:** ${distInfo.dnsRecords.value}
- **Custom Domain:** ${DOMAIN}
- **Status:** ${distInfo.status}

## 🌐 Configuração DNS no GoDaddy

Adicione o seguinte registro CNAME:

\`\`\`
Tipo:  CNAME
Nome:  images
Valor: ${distInfo.dnsRecords.value}
TTL:   3600
\`\`\`

## ⏱️ Tempo de Propagação

- CloudFront Deployment: 15-30 minutos
- DNS Propagation: 5-30 minutos

## ✅ URLs de Teste

Após deployment e propagação DNS:

- https://${DOMAIN}/products/inversores/286844.png
- https://${DOMAIN}/products/inversores/222132.png
- https://${DOMAIN}/products/inversores/222133.png

## 🔍 Verificar Status

\`\`\`bash
# Status da distribution
node scripts/check-cloudfront-status.js

# Testar DNS
nslookup ${DOMAIN}

# Testar acesso
Invoke-WebRequest -Uri "https://${DOMAIN}/products/inversores/286844.png" -Method Head
\`\`\`

---
Gerado em: ${new Date().toISOString()}
`;

  writeFileSync('FINAL_SETUP_INSTRUCTIONS.md', instructions);
  console.log('📄 Instruções salvas em: FINAL_SETUP_INSTRUCTIONS.md\n');
}

setupInfrastructure();
