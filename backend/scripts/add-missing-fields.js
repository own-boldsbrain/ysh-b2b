#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('\n🔧 ADICIONANDO CAMPOS FALTANDO AOS SKUs\n');
console.log('═'.repeat(80) + '\n');

function inferCategoryFromSku(skuString) {
  if (skuString.includes('KIT')) return 'kits';
  if (skuString.includes('INVERSOR')) return 'inversores';
  if (skuString.includes('PAINEL')) return 'paineis';
  if (skuString.includes('BATERIA')) return 'baterias';
  if (skuString.includes('ESTRUTURA')) return 'estrutura';
  return 'componentes';
}

function addMissingFieldsToSku(sku, index, totalSkus) {
  if (!sku.category) {
    sku.category = inferCategoryFromSku(sku.sku);
  }

  if (!sku.price_brl && sku.final_price) {
    sku.price_brl = Math.round(sku.final_price * 100);
  }

  if (!sku.pricing) {
    sku.pricing = {
      cost_price: sku.cost_price,
      price_score: sku.price_score,
      dynamic_markup: sku.dynamic_markup,
      dynamic_adjustments: sku.dynamic_adjustments,
      channel_pricing: sku.channel_pricing,
      final_price: sku.final_price,
      psychological_pricing: sku.psychological_pricing,
      project_splits: sku.project_splits
    };
  }

  if ((index + 1) % 250 === 0) {
    process.stdout.write(`   ✓ ${index + 1}/${totalSkus} SKUs processados\n`);
  }
}

function validateSkuCompleteness(sku) {
  return (
    sku.sku &&
    sku.category &&
    sku.price_brl &&
    sku.pricing?.cost_price &&
    sku.pricing?.final_price &&
    sku.kpis
  );
}

function getMissingFields(sku) {
  return {
    sku: !sku.sku,
    category: !sku.category,
    price_brl: !sku.price_brl,
    pricing: !sku.pricing,
    kpis: !sku.kpis
  };
}

async function enrichMissingSKUData() {
  try {
    const enrichedPath = path.join(__dirname, '../enriched-skus-for-dynamodb.json');

    console.log('📂 Carregando arquivo de SKUs...');
    const enrichedSkus = JSON.parse(fs.readFileSync(enrichedPath, 'utf-8'));
    console.log(`   ✓ Total: ${enrichedSkus.length} SKUs\n`);

    console.log('🔄 ETAPA 1: Adicionando campos faltando...\n');

    let index = 0;
    for (const sku of enrichedSkus) {
      addMissingFieldsToSku(sku, index, enrichedSkus.length);
      index += 1;
    }

    console.log(`\n✅ Campos adicionados aos SKUs`);

    console.log(`\n🔄 ETAPA 2: Validando integridade...\n`);

    const completeSKUs = [];
    const incompleteSKUs = [];

    for (const sku of enrichedSkus) {
      if (validateSkuCompleteness(sku)) {
        completeSKUs.push(sku);
      } else {
        incompleteSKUs.push({
          sku: sku.sku,
          missingFields: getMissingFields(sku)
        });
      }
    }

    console.log(`   ✓ SKUs Completos: ${completeSKUs.length}/${enrichedSkus.length}`);
    console.log(`   ✗ SKUs Incompletos: ${incompleteSKUs.length}/${enrichedSkus.length}`);

    console.log(`\n🔄 ETAPA 3: Salvando resultado...\n`);

    fs.writeFileSync(
      enrichedPath,
      JSON.stringify(completeSKUs, null, 2)
    );
    console.log(`   ✓ Arquivo atualizado: enriched-skus-for-dynamodb.json`);

    console.log('\n' + '═'.repeat(80));
    console.log('📊 RESULTADO FINAL\n');

    const percentage = (completeSKUs.length / enrichedSkus.length * 100).toFixed(2);
    console.log(`✅ SKUs Válidos: ${completeSKUs.length}/${enrichedSkus.length} (${percentage}%)\n`);

    if (incompleteSKUs.length > 0) {
      console.log(`⚠️  ${incompleteSKUs.length} SKUs ainda com problemas:`);
      for (const item of incompleteSKUs.slice(0, 5)) {
        const fields = Object.entries(item.missingFields)
          .filter(([, missing]) => missing)
          .map(([field]) => field);
        console.log(`   • ${item.sku}: faltam ${fields.join(', ')}`);
      }
    } else {
      console.log('✅ TODOS OS SKUs ESTÃO COMPLETOS E VÁLIDOS!');
    }

    console.log('\n' + '═'.repeat(80) + '\n');

    process.exit(incompleteSKUs.length === 0 ? 0 : 1);

  } catch (error) {
    console.error('❌ Erro:', error.message);
    process.exit(1);
  }
}

try {
  await enrichMissingSKUData();
} catch (error) {
  console.error('❌ Erro fatal:', error);
  process.exit(1);
}
