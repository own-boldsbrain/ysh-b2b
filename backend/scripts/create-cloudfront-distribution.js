/**
 * Create CloudFront Distribution for S3 Static Images
 * 
 * Prerequisites:
 * - ACM certificate validated (check with check-certificate-status.js)
 * - S3 bucket configured (ysh-b2b-products)
 * 
 * Usage:
 *   node scripts/create-cloudfront-distribution.js
 */

import AWS from 'aws-sdk';
import { existsSync, readFileSync, writeFileSync } from 'fs';

const cloudfront = new AWS.CloudFront({ region: 'us-east-1' });
const s3 = new AWS.S3({ region: 'us-east-1' });

const BUCKET_NAME = 'ysh-b2b-products';
const DOMAIN = 'cdn.yellosolarhub.com';

async function createDistribution() {
  try {
    // Check certificate
    if (!existsSync('acm-certificate-info.json')) {
      console.error('❌ Certificado não encontrado.');
      console.error('   Execute primeiro: node scripts/request-acm-certificate.js\n');
      process.exit(1);
    }

    const certInfo = JSON.parse(readFileSync('acm-certificate-info.json', 'utf8'));
    
    if (certInfo.status !== 'ISSUED') {
      console.error(`❌ Certificado ainda não validado (Status: ${certInfo.status})`);
      console.error('   Execute: node scripts/check-certificate-status.js');
      console.error('   Aguarde a validação DNS antes de criar a CloudFront distribution.\n');
      process.exit(1);
    }

    console.log('☁️  Criando CloudFront Distribution...\n');
    console.log(`   Bucket: ${BUCKET_NAME}`);
    console.log(`   Domínio: ${DOMAIN}`);
    console.log(`   Certificado: ${certInfo.certificateArn}\n`);

    // Get bucket region
    const bucketLocation = await s3.getBucketLocation({ Bucket: BUCKET_NAME }).promise();
    const bucketRegion = bucketLocation.LocationConstraint || 'us-east-1';
    const originDomain = `${BUCKET_NAME}.s3.${bucketRegion}.amazonaws.com`;

    const params = {
      DistributionConfig: {
        CallerReference: `ysh-b2b-${Date.now()}`,
        Comment: 'YSH B2B Product Images Distribution',
        Enabled: true,
        
        // S3 Origin
        Origins: {
          Quantity: 1,
          Items: [
            {
              Id: 'S3-ysh-b2b-products',
              DomainName: originDomain,
              OriginPath: '/images',
              CustomHeaders: {
                Quantity: 0,
                Items: []
              },
              S3OriginConfig: {
                OriginAccessIdentity: '' // Using bucket policy for public access
              },
              ConnectionAttempts: 3,
              ConnectionTimeout: 10,
              OriginShield: {
                Enabled: false
              }
            }
          ]
        },

        // Default Cache Behavior
        DefaultCacheBehavior: {
          TargetOriginId: 'S3-ysh-b2b-products',
          ViewerProtocolPolicy: 'redirect-to-https',
          AllowedMethods: {
            Quantity: 2,
            Items: ['GET', 'HEAD'],
            CachedMethods: {
              Quantity: 2,
              Items: ['GET', 'HEAD']
            }
          },
          Compress: true,
          ForwardedValues: {
            QueryString: false,
            Cookies: {
              Forward: 'none'
            },
            Headers: {
              Quantity: 0,
              Items: []
            }
          },
          MinTTL: 0,
          DefaultTTL: 86400, // 1 day
          MaxTTL: 31536000, // 1 year
          TrustedSigners: {
            Enabled: false,
            Quantity: 0,
            Items: []
          },
          TrustedKeyGroups: {
            Enabled: false,
            Quantity: 0,
            Items: []
          }
        },

        // Custom Domain
        Aliases: {
          Quantity: 1,
          Items: [DOMAIN]
        },

        // SSL Certificate
        ViewerCertificate: {
          ACMCertificateArn: certInfo.certificateArn,
          SSLSupportMethod: 'sni-only',
          MinimumProtocolVersion: 'TLSv1.2_2021',
          Certificate: certInfo.certificateArn,
          CertificateSource: 'acm'
        },

        // Price Class
        PriceClass: 'PriceClass_100', // US, Canada, Europe

        // Error Pages
        CustomErrorResponses: {
          Quantity: 1,
          Items: [
            {
              ErrorCode: 403,
              ResponsePagePath: '',
              ResponseCode: '',
              ErrorCachingMinTTL: 300
            }
          ]
        },

        // Logging (optional)
        Logging: {
          Enabled: false,
          IncludeCookies: false,
          Bucket: '',
          Prefix: ''
        },

        // Web ACL (optional)
        WebACLId: '',

        // HTTP Version
        HttpVersion: 'http2and3',

        // IPv6
        IsIPV6Enabled: true,

        // Restrictions
        Restrictions: {
          GeoRestriction: {
            RestrictionType: 'none',
            Quantity: 0,
            Items: []
          }
        }
      }
    };

    console.log('⏳ Criando distribution (pode levar alguns minutos)...\n');
    
    const result = await cloudfront.createDistribution(params).promise();
    const distribution = result.Distribution;

    console.log('✅ CloudFront Distribution criada com sucesso!\n');
    console.log('=' .repeat(70));
    console.log(`\nDistribution ID: ${distribution.Id}`);
    console.log(`Domain Name: ${distribution.DomainName}`);
    console.log(`Status: ${distribution.Status}`);
    console.log(`ARN: ${distribution.ARN}`);

    console.log('\n' + '='.repeat(70));
    console.log('\n📋 PRÓXIMOS PASSOS:\n');
    console.log('1. Aguarde o deployment da distribution (Status: InProgress → Deployed)');
    console.log('   Isso pode levar 15-30 minutos.');
    console.log('   Execute: node scripts/check-cloudfront-status.js\n');
    console.log('2. Configure o DNS no GoDaddy:\n');
    console.log(`   Tipo: CNAME`);
    console.log(`   Nome: images (ou images.yellosolar.com.br)`);
    console.log(`   Valor: ${distribution.DomainName}`);
    console.log(`   TTL: 3600 (1 hora)\n`);
    console.log('3. Aguarde propagação DNS (5-30 minutos)');
    console.log('4. Teste: https://images.yellosolar.com.br/products/inversores/286844.png\n');

    // Save distribution info
    const output = {
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

    writeFileSync(
      'cloudfront-distribution-info.json',
      JSON.stringify(output, null, 2)
    );

    console.log('✅ Informações salvas em: cloudfront-distribution-info.json\n');

  } catch (error) {
    console.error('❌ Erro ao criar CloudFront distribution:', error.message);
    
    if (error.code === 'CNAMEAlreadyExists') {
      console.error('\n⚠️  O domínio já está associado a outra distribution.');
      console.error('   Liste as distributions: aws cloudfront list-distributions');
    }

    if (error.code === 'InvalidViewerCertificate') {
      console.error('\n⚠️  Certificado inválido ou não validado.');
      console.error('   Verifique: node scripts/check-certificate-status.js');
    }

    process.exit(1);
  }
}

createDistribution();
