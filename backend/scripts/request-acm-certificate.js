/**
 * Request SSL/TLS Certificate from AWS Certificate Manager (ACM)
 * For domain: cdn.yellosolarhub.com
 * 
 * Prerequisites:
 * - AWS credentials configured
 * - Domain ownership (will need to validate via DNS)
 * 
 * Usage:
 *   node scripts/request-acm-certificate.js
 */

import AWS from 'aws-sdk';
import { writeFileSync } from 'fs';

// ACM must be in us-east-1 for CloudFront
const acm = new AWS.ACM({ region: 'us-east-1' });

const DOMAIN = 'yellosolarhub.com';
const REGION = 'us-east-1';

async function requestCertificate() {
  console.log('🔐 Solicitando certificado SSL/TLS no ACM...\n');
  console.log(`   Domínio: ${DOMAIN}`);
  console.log(`   Região: ${REGION} (obrigatório para CloudFront)\n`);

  try {
    const params = {
      DomainName: DOMAIN,
      ValidationMethod: 'DNS',
      SubjectAlternativeNames: [
        DOMAIN,
        `*.${DOMAIN}` // wildcard for subdomains
      ],
      Tags: [
        {
          Key: 'Project',
          Value: 'YSH-B2B'
        },
        {
          Key: 'Purpose',
          Value: 'CloudFront-S3-Images'
        },
        {
          Key: 'Environment',
          Value: 'Production'
        }
      ]
    };

    const result = await acm.requestCertificate(params).promise();
    
    console.log('✅ Certificado solicitado com sucesso!\n');
    console.log(`   Certificate ARN: ${result.CertificateArn}\n`);

    // Wait a moment for AWS to generate validation records
    console.log('⏳ Aguardando geração dos registros de validação DNS...\n');
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Get validation details
    const certDetails = await acm.describeCertificate({
      CertificateArn: result.CertificateArn
    }).promise();

    console.log('📋 REGISTROS DNS PARA VALIDAÇÃO:\n');
    console.log('=' .repeat(70));
    
    if (certDetails.Certificate.DomainValidationOptions) {
      certDetails.Certificate.DomainValidationOptions.forEach((domain, index) => {
        console.log(`\n${index + 1}. Domínio: ${domain.DomainName}`);
        
        if (domain.ResourceRecord) {
          console.log(`   Tipo: ${domain.ResourceRecord.Type}`);
          console.log(`   Nome: ${domain.ResourceRecord.Name}`);
          console.log(`   Valor: ${domain.ResourceRecord.Value}`);
        } else {
          console.log('   ⏳ Registros ainda sendo gerados... Execute novamente em 30 segundos.');
        }
      });
    }

    console.log('\n' + '='.repeat(70));
    console.log('\n📌 INSTRUÇÕES:\n');
    console.log('1. Acesse o painel DNS do GoDaddy');
    console.log('2. Adicione os registros CNAME de validação acima');
    console.log('3. Aguarde 5-30 minutos para validação automática');
    console.log('4. Execute: node scripts/check-certificate-status.js');
    console.log('\n💾 Salve o Certificate ARN:\n');
    console.log(`   ${result.CertificateArn}\n`);

    // Save to file for next steps
    const output = {
      certificateArn: result.CertificateArn,
      domain: DOMAIN,
      status: certDetails.Certificate.Status,
      requestedAt: new Date().toISOString(),
      validationRecords: certDetails.Certificate.DomainValidationOptions?.map(d => ({
        domain: d.DomainName,
        type: d.ResourceRecord?.Type,
        name: d.ResourceRecord?.Name,
        value: d.ResourceRecord?.Value
      }))
    };

    writeFileSync(
      'acm-certificate-info.json',
      JSON.stringify(output, null, 2)
    );

    console.log('✅ Informações salvas em: acm-certificate-info.json\n');

  } catch (error) {
    console.error('❌ Erro ao solicitar certificado:', error.message);
    
    if (error.code === 'LimitExceededException') {
      console.error('\n⚠️  Limite de certificados atingido. Aguarde ou delete certificados não utilizados.');
    }
    
    if (error.code === 'InvalidParameterException') {
      console.error('\n⚠️  Parâmetro inválido. Verifique o formato do domínio.');
    }

    process.exit(1);
  }
}

requestCertificate();
