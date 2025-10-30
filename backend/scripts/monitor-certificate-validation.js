/**
 * Monitor ACM Certificate Validation
 * Checks every 30 seconds until certificate is validated
 * 
 * Usage:
 *   node scripts/monitor-certificate-validation.js
 */

import AWS from 'aws-sdk';
import { existsSync, readFileSync, writeFileSync } from 'fs';

const acm = new AWS.ACM({ region: 'us-east-1' });
const CHECK_INTERVAL = 30000; // 30 seconds
const MAX_CHECKS = 60; // 30 minutes total

async function monitorValidation() {
  try {
    if (!existsSync('acm-certificate-info.json')) {
      console.error('❌ Arquivo acm-certificate-info.json não encontrado.');
      process.exit(1);
    }

    const certInfo = JSON.parse(readFileSync('acm-certificate-info.json', 'utf8'));
    const certificateArn = certInfo.certificateArn;

    console.log('🔄 Monitorando validação do certificado...\n');
    console.log(`   Intervalo: ${CHECK_INTERVAL / 1000}s`);
    console.log(`   Timeout: ${(MAX_CHECKS * CHECK_INTERVAL) / 60000} minutos\n`);
    console.log('=' .repeat(70) + '\n');

    let checks = 0;

    const checkStatus = async () => {
      checks++;
      const timestamp = new Date().toLocaleTimeString('pt-BR');

      try {
        const result = await acm.describeCertificate({
          CertificateArn: certificateArn
        }).promise();

        const cert = result.Certificate;
        const status = cert.Status;

        console.log(`[${timestamp}] Check ${checks}/${MAX_CHECKS} - Status: ${status}`);

        if (status === 'ISSUED') {
          console.log('\n' + '='.repeat(70));
          console.log('\n🎉 CERTIFICADO VALIDADO COM SUCESSO!\n');
          console.log(`   ARN: ${certificateArn}`);
          console.log(`   Domínio: ${cert.DomainName}`);
          console.log(`   Emitido em: ${cert.IssuedAt}\n`);
          console.log('✅ Próximo passo: Criar CloudFront Distribution\n');
          console.log('   Execute: node scripts/create-cloudfront-distribution.js\n');
          console.log('='.repeat(70) + '\n');

          // Update saved info
          certInfo.status = status;
          certInfo.issuedAt = cert.IssuedAt;
          certInfo.lastChecked = new Date().toISOString();
          writeFileSync('acm-certificate-info.json', JSON.stringify(certInfo, null, 2));

          process.exit(0);
        } else if (status === 'FAILED' || status === 'VALIDATION_TIMED_OUT') {
          console.error(`\n❌ Validação falhou: ${status}`);
          console.error('   Verifique os registros DNS no GoDaddy.\n');
          process.exit(1);
        }

        if (checks >= MAX_CHECKS) {
          console.warn('\n⚠️  Timeout atingido. Execute novamente ou verifique manualmente:\n');
          console.warn('   node scripts/check-certificate-status.js\n');
          process.exit(0);
        }

        // Schedule next check
        setTimeout(checkStatus, CHECK_INTERVAL);

      } catch (error) {
        console.error(`\n❌ Erro ao verificar status: ${error.message}`);
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

monitorValidation();
