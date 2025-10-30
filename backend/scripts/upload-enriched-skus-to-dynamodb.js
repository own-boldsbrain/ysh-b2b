#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import AWS from 'aws-sdk';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configurar AWS SDK
const dynamodb = new AWS.DynamoDB.DocumentClient({
  region: process.env.AWS_REGION || 'us-east-1',
  maxRetries: 5,
  httpOptions: { timeout: 30000 }
});

const TABLE_NAME = process.env.DYNAMODB_TABLE_NAME || 'ysh-products-catalog';

console.log('\n📊 UPLOAD DE SKUs ENRIQUECIDOS PARA DYNAMODB\n');
console.log('═'.repeat(70));

// Parse CLI arguments
const args = process.argv.slice(2);
let customFilePath = null;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--file' && args[i + 1]) {
    customFilePath = args[i + 1];
    break;
  }
}

// Carregar SKUs enriquecidos
const enrichedSkusPath = customFilePath 
  ? (path.isAbsolute(customFilePath) ? customFilePath : path.join(__dirname, '..', customFilePath))
  : path.join(__dirname, '../enriched-skus-for-dynamodb.json');

if (!fs.existsSync(enrichedSkusPath)) {
  console.error('❌ Arquivo não encontrado:', enrichedSkusPath);
  process.exit(1);
}

const enrichedSkus = JSON.parse(fs.readFileSync(enrichedSkusPath, 'utf-8'));
console.log(`📄 Usando arquivo: ${enrichedSkusPath}`);

console.log(`\n📁 Carregados ${enrichedSkus.length} SKUs enriquecidos`);
console.log(`📍 Tabela DynamoDB: ${TABLE_NAME}`);
console.log(`🔧 Região AWS: ${process.env.AWS_REGION || 'us-east-1'}`);

// Função para fazer batch write com retry
async function batchWriteItems(items, batchSize = 25) {
  const batches = [];
  for (let i = 0; i < items.length; i += batchSize) {
    batches.push(items.slice(i, i + batchSize));
  }

  let successCount = 0;
  let errorCount = 0;
  const errors = [];

  for (let batchIndex = 0; batchIndex < batches.length; batchIndex++) {
    const batch = batches[batchIndex];
    const requests = batch.map(item => ({
      PutRequest: {
        Item: item
      }
    }));

    let retries = 0;
    let success = false;

    while (retries < 3 && !success) {
      try {
        const params = {
          RequestItems: {
            [TABLE_NAME]: requests
          }
        };

        await dynamodb.batchWrite(params).promise();
        successCount += batch.length;
        success = true;

        const progress = Math.round((batchIndex + 1) / batches.length * 100);
        process.stdout.write(`\r✅ Progresso: ${batchIndex + 1}/${batches.length} batches (${progress}%) - ${successCount}/${enrichedSkus.length} SKUs`);
      } catch (error) {
        retries++;
        if (retries < 3) {
          console.log(`\n⚠️  Erro na tentativa ${retries}, aguardando...`);
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, retries) * 1000));
        } else {
          errorCount += batch.length;
          errors.push({
            batch: batchIndex,
            error: error.message,
            itemCount: batch.length
          });
        }
      }
    }
  }

  return { successCount, errorCount, errors };
}

// Executar upload
async function uploadToDynamoDB() {
  try {
    console.log('\n🔄 ETAPA 1: Testando Conexão com DynamoDB');
    
    // Testar conexão
    const testParams = {
      TableName: TABLE_NAME,
      Limit: 1
    };

    await dynamodb.scan(testParams).promise();
    console.log('✅ Conexão com DynamoDB estabelecida com sucesso');

    console.log('\n🔄 ETAPA 2: Executando Batch Write');
    const result = await batchWriteItems(enrichedSkus);

    console.log('\n\n✅ UPLOAD CONCLUÍDO!');
    console.log('\n📊 Estatísticas de Upload:');
    console.log(`   ✓ SKUs Importados com Sucesso: ${result.successCount}`);
    console.log(`   ✗ SKUs com Erro: ${result.errorCount}`);

    if (result.errors.length > 0) {
      console.log('\n⚠️  Erros Detectados:');
      for (const err of result.errors) {
        console.log(`   • Batch ${err.batch}: ${err.error} (${err.itemCount} itens)`);
      }
    }

    console.log('\n🎯 Próximos Passos:');
    console.log('   1. Validar: node scripts/fetch-skus-from-dynamodb.js');
    console.log('   2. Consultar: aws dynamodb scan --table-name ysh-products-catalog --limit 5');
    console.log('   3. Monitorar: Verificar CloudWatch Logs');

  } catch (error) {
    console.error('\n❌ Erro ao fazer upload:', error.message);
    if (error.code === 'ResourceNotFoundException') {
      console.error('   A tabela DynamoDB não existe. Execute primeiro:');
      console.error('   aws dynamodb create-table --table-name ysh-products-catalog ...');
    }
    process.exit(1);
  }

  console.log('\n' + '═'.repeat(70) + '\n');
}

// Executar
try {
  await uploadToDynamoDB();
} catch (error) {
  console.error('❌ Erro fatal:', error);
  process.exit(1);
}
