#!/usr/bin/env node
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, BatchWriteCommand } from '@aws-sdk/lib-dynamodb';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('\n📤 UPLOAD DE SKUs ENRIQUECIDOS PARA DYNAMODB\n');
console.log('═'.repeat(80) + '\n');

const client = new DynamoDBClient({ region: 'us-east-1' });
const docClient = DynamoDBDocumentClient.from(client);

const tableName = 'skus-catalog';
const batchSize = 25; // DynamoDB batch max

async function uploadSkusToDynamoDB() {
  try {
    const enrichedPath = path.join(__dirname, '../enriched-skus-for-dynamodb.json');
    
    console.log('📂 Carregando SKUs enriquecidos...');
    const skus = JSON.parse(fs.readFileSync(enrichedPath, 'utf-8'));
    console.log(`   ✓ Total: ${skus.length} SKUs para upload\n`);

    console.log('📤 ETAPA 1: Upload em lotes de 25...\n');

    let uploaded = 0;
    let failed = 0;
    const failedSkus = [];

    for (let i = 0; i < skus.length; i += batchSize) {
      const batch = skus.slice(i, i + batchSize);
      const requests = batch.map(sku => ({
        PutRequest: {
          Item: {
            pk: `SKU#${sku.sku}`,
            sk: 'METADATA',
            sku: sku.sku,
            category: sku.category,
            price_brl: sku.price_brl,
            cost_price: sku.cost_price,
            final_price: sku.final_price,
            pricing: sku.pricing,
            kpis: sku.kpis,
            dynamic_markup: sku.dynamic_markup,
            channel_pricing: sku.channel_pricing,
            enriched_at: sku.enriched_at,
            updated_at: new Date().toISOString(),
            ttl: Math.floor(Date.now() / 1000) + (90 * 24 * 60 * 60) // 90 dias
          }
        }
      }));

      try {
        await docClient.send(new BatchWriteCommand({
          RequestItems: {
            [tableName]: requests
          }
        }));
        uploaded += batch.length;
      } catch (error) {
        console.error(`   ❌ Erro no lote ${Math.floor(i / batchSize) + 1}: ${error.message}`);
        failed += batch.length;
        for (const sku of batch) {
          failedSkus.push(sku.sku);
        }
      }

      const progress = Math.min(i + batchSize, skus.length);
      if ((i + batchSize) % 250 === 0 || progress === skus.length) {
        process.stdout.write(`   ✓ ${progress}/${skus.length} SKUs enviados\n`);
      }
    }

    console.log(`\n✅ Upload Concluído:`);
    console.log(`   • Enviados: ${uploaded}/${skus.length}`);
    console.log(`   • Falhados: ${failed}/${skus.length}`);

    if (failed > 0) {
      console.log(`\n⚠️  SKUs com falha (primeiros 10):`);
      for (const sku of failedSkus.slice(0, 10)) {
        console.log(`   • ${sku}`);
      }
    }

    console.log('\n' + '═'.repeat(80));
    console.log('📊 RESULTADO FINAL\n');

    const percentage = ((uploaded / skus.length) * 100).toFixed(2);
    console.log(`✅ Taxa de Sucesso: ${percentage}%`);
    console.log(`📊 SKUs no DynamoDB: ${uploaded} registros\n`);

    if (failed === 0) {
      console.log('✅ TODOS OS SKUs FORAM ENVIADOS COM SUCESSO!');
    }

    console.log('═'.repeat(80) + '\n');

    process.exit(failed === 0 ? 0 : 1);

  } catch (error) {
    console.error('❌ Erro:', error.message);
    process.exit(1);
  }
}

// Executar
try {
  await uploadSkusToDynamoDB();
} catch (error) {
  console.error('❌ Erro fatal:', error);
  process.exit(1);
}
