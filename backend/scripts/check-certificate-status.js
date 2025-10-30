/**
 * Check ACM Certificate Validation Status
 * 
 * Usage:
 *   node scripts/check-certificate-status.js
 */

import AWS from 'aws-sdk';
import { existsSync, readFileSync, writeFileSync } from 'fs';

const acm = new AWS.ACM({ region: 'us-east-1' });

async function checkCertificateStatus() {
  try {
    // Read certificate info
    if (!existsSync('acm-certificate-info.json')) {
      console.error('❌ Arquivo acm-certificate-info.json não encontrado.');
      console.error('   Execute primeiro: node scripts/request-acm-certificate.js\n');
      process.exit(1);
    }

    const certInfo = JSON.parse(readFileSync('acm-certificate-info.json', 'utf8'));
    const certificateArn = certInfo.certificateArn;

    console.log('🔍 Verificando status do certificado...\n');
    console.log(`   ARN: ${certificateArn}\n`);

    const result = await acm.describeCertificate({
      CertificateArn: certificateArn
    }).promise();

    const cert = result.Certificate;

    console.log('📊 STATUS DO CERTIFICADO:\n');
    console.log('=' .repeat(70));
    console.log(`\nStatus: ${cert.Status}`);
    console.log(`Tipo: ${cert.Type}`);
    console.log(`Domínio: ${cert.DomainName}`);
    console.log(`Criado em: ${cert.CreatedAt}`);

    if (cert.Status === 'ISSUED') {
      console.log('\n✅ CERTIFICADO VALIDADO E EMITIDO!\n');
      console.log('   Você pode agora criar a CloudFront distribution.');
      console.log('   Execute: node scripts/create-cloudfront-distribution.js\n');
    } else if (cert.Status === 'PENDING_VALIDATION') {
      console.log('\n⏳ AGUARDANDO VALIDAÇÃO DNS...\n');
      
      console.log('📋 Registros de Validação:\n');
      cert.DomainValidationOptions?.forEach((domain, index) => {
        console.log(`${index + 1}. Domínio: ${domain.DomainName}`);
        console.log(`   Status: ${domain.ValidationStatus}`);
        
        if (domain.ResourceRecord) {
          console.log(`   Tipo: ${domain.ResourceRecord.Type}`);
          console.log(`   Nome: ${domain.ResourceRecord.Name}`);
          console.log(`   Valor: ${domain.ResourceRecord.Value}`);
        }
        console.log('');
      });

      console.log('💡 Certifique-se de que os registros CNAME estão configurados no GoDaddy.');
      console.log('   A validação pode levar 5-30 minutos após adicionar os registros.\n');
    } else {
      console.log(`\n⚠️  Status: ${cert.Status}`);
    }

    console.log('='.repeat(70) + '\n');

    // Update saved info
    certInfo.status = cert.Status;
    certInfo.lastChecked = new Date().toISOString();
    writeFileSync('acm-certificate-info.json', JSON.stringify(certInfo, null, 2));

  } catch (error) {
    console.error('❌ Erro ao verificar certificado:', error.message);
    process.exit(1);
  }
}

checkCertificateStatus();
