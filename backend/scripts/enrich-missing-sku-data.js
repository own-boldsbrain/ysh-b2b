#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('\n🔧 CORREÇÃO E ENRIQUECIMENTO DE SKUs INCOMPLETOS\n');
console.log('═'.repeat(80));

function createCatalogMap(catalog) {
  const catalogMap = {};
  for (const product of catalog) {
    if (product.sku) {
      catalogMap[product.sku] = product;
    }
  }
  return catalogMap;
}

function addMissingCatalogFields(sku, catalogProduct) {
  if (!catalogProduct) return;
  
  const fields = ['category', 'price_brl', 'filename', 'image_url', 'manufacturer', 'power_w', 'capacity_kwh', 'supplier'];
  for (const field of fields) {
    if (!sku[field] && catalogProduct[field]) {
      sku[field] = catalogProduct[field];
    }
  }
}

function addKPIsIfMissing(sku) {
  if (!sku.kpis && sku.dynamic_markup) {
    sku.kpis = {
      gross_margin_percent: sku.dynamic_markup.grossMargin,
      net_margin_percent: sku.dynamic_markup.netMargin,
      selling_price: sku.final_price,
      markup_applied: sku.dynamic_markup.finalMarkup,
      adjustments_applied: sku.dynamic_adjustments?.total_adjustment || 0,
      confidence: 'high'
    };
  }
}

function addPricingIfMissing(sku) {
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
}

function isSkuComplete(sku) {
  return (
    sku.sku &&
    sku.category &&
    sku.price_brl &&
    sku.pricing?.cost_price &&
    sku.pricing?.final_price &&
    sku.kpis
  );
}

function enrichSkusWithCatalog(enrichedSkus, catalogMap) {
  for (let i = 0; i < enrichedSkus.length; i++) {
    const sku = enrichedSkus[i];
    const catalogProduct = catalogMap[sku.sku];

    addMissingCatalogFields(sku, catalogProduct);
    addKPIsIfMissing(sku);
    addPricingIfMissing(sku);

    if ((i + 1) % 250 === 0) {
      process.stdout.write(`   ✓ ${i + 1}/${enrichedSkus.length} SKUs processados\n`);
    }
  }
}

function filterCompleteSkus(enrichedSkus) {
  const completeSKUs = [];
  const incompleteSKUs = [];

  for (const sku of enrichedSkus) {
    if (isSkuComplete(sku)) {
      completeSKUs.push(sku);
    } else {
      incompleteSKUs.push({
        sku: sku.sku,
        missingFields: {
          sku: !sku.sku,
          category: !sku.category,
          price_brl: !sku.price_brl,
          pricing: !sku.pricing,
          kpis: !sku.kpis
        }
      });
    }
  }

  return { completeSKUs, incompleteSKUs };
}

function getMissingFieldsCounts(incompleteSKUs) {
  const missingCounts = {};
  for (const item of incompleteSKUs) {
    for (const [field, missing] of Object.entries(item.missingFields)) {
      if (missing) {
        missingCounts[field] = (missingCounts[field] || 0) + 1;
      }
    }
  }
  return missingCounts;
}

function printFinalResults(completeSKUs, incompleteSKUs, enrichedSkus) {
  console.log('\n' + '═'.repeat(80));
  console.log('📊 RESULTADO FINAL\n');

  console.log('✅ ESTATÍSTICAS:');
  const completePercentage = (completeSKUs.length / enrichedSkus.length * 100).toFixed(2);
  const incompletePercentage = (incompleteSKUs.length / enrichedSkus.length * 100).toFixed(2);
  console.log(`   • SKUs Completos: ${completeSKUs.length}/${enrichedSkus.length} (${completePercentage}%)`);
  console.log(`   • SKUs Incompletos: ${incompleteSKUs.length}/${enrichedSkus.length} (${incompletePercentage}%)`);

  if (incompleteSKUs.length > 0) {
    console.log(`\n⚠️  PROBLEMAS DETECTADOS:`);
    
    const missingCounts = getMissingFieldsCounts(incompleteSKUs);
    for (const [field, count] of Object.entries(missingCounts)) {
      console.log(`   • ${field}: ${count} SKUs`);
    }

    console.log(`\n📄 Primeiros 5 SKUs incompletos:`);
    for (const item of incompleteSKUs.slice(0, 5)) {
      console.log(`   • ${item.sku}`);
    }
  } else {
    console.log('\n✅ TODOS OS SKUs ESTÃO COMPLETOS E VÁLIDOS!');
  }

  console.log('\n' + '═'.repeat(80) + '\n');
}

async function enrichMissingSKUData() {
  try {
    // Carregar dados
    const catalogPath = path.join(__dirname, '../products-fully-priced-catalog.json');
    const enrichedPath = path.join(__dirname, '../enriched-skus-for-dynamodb.json');

    if (!fs.existsSync(catalogPath)) {
      console.error('❌ Catálogo não encontrado');
      process.exit(1);
    }

    console.log('📂 Carregando arquivos...');

    const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf-8'));
    const enrichedSkus = JSON.parse(fs.readFileSync(enrichedPath, 'utf-8'));

    console.log(`   ✓ Catálogo: ${catalog.length} produtos`);
    console.log(`   ✓ SKUs Enriquecidos: ${enrichedSkus.length} SKUs`);

    const catalogMap = createCatalogMap(catalog);

    console.log(`\n� ETAPA 1: Mesclando dados do catálogo...\n`);
    enrichSkusWithCatalog(enrichedSkus, catalogMap);

    console.log(`\n🔄 ETAPA 2: Filtrando SKUs completos...\n`);
    const { completeSKUs, incompleteSKUs } = filterCompleteSkus(enrichedSkus);
    console.log(`   ✓ SKUs Completos: ${completeSKUs.length}`);
    console.log(`   ✗ SKUs Incompletos: ${incompleteSKUs.length}`);

    console.log(`\n🔄 ETAPA 3: Salvando dados corrigidos...\n`);

    fs.writeFileSync(
      path.join(__dirname, '../enriched-skus-for-dynamodb-fixed.json'),
      JSON.stringify(completeSKUs, null, 2)
    );
    console.log(`   ✓ Arquivo: enriched-skus-for-dynamodb-fixed.json (${completeSKUs.length} SKUs)`);

    if (incompleteSKUs.length > 0) {
      fs.writeFileSync(
        path.join(__dirname, '../incomplete-skus-report.json'),
        JSON.stringify({
          timestamp: new Date().toISOString(),
          total_incomplete: incompleteSKUs.length,
          incomplete_skus: incompleteSKUs.slice(0, 50)
        }, null, 2)
      );
      console.log(`   ✓ Relatório: incomplete-skus-report.json (${incompleteSKUs.length} SKUs)`);
    }

    printFinalResults(completeSKUs, incompleteSKUs, enrichedSkus);

    process.exit(incompleteSKUs.length === 0 ? 0 : 1);

  } catch (error) {
    console.error('❌ Erro:', error.message);
    process.exit(1);
  }
}

// Executar
try {
  await enrichMissingSKUData();
} catch (error) {
  console.error('❌ Erro fatal:', error);
  process.exit(1);
}
