#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('\n📋 VALIDAÇÃO DE INTEGRIDADE DE SKUs\n');
console.log('═'.repeat(80));

// Campos obrigatórios para SKU válido
const REQUIRED_FIELDS = {
  'core': ['sku', 'category', 'price_brl'],
  'pricing': ['cost_price', 'dynamic_markup', 'final_price', 'kpis'],
  'markup_details': ['baseMarkup', 'finalMarkup', 'sellingPrice', 'grossMargin'],
  'kpis': ['gross_margin_percent', 'net_margin_percent', 'selling_price', 'markup_applied']
};

function validateCoreFields(sku, errors) {
  for (const field of REQUIRED_FIELDS.core) {
    if (!sku[field]) {
      errors.push(`Campo obrigatório ausente: ${field}`);
    }
  }
}

function validatePricingObject(sku, errors) {
  if (typeof sku.pricing !== 'object') {
    errors.push('Objeto pricing inválido ou ausente');
    return false;
  }
  return true;
}

function validateCostPrice(sku, errors) {
  if (!sku.pricing.cost_price || sku.pricing.cost_price <= 0) {
    errors.push('cost_price inválido ou zero');
  }
}

function validateDynamicMarkup(sku, errors, warnings) {
  if (!sku.pricing.dynamic_markup) {
    errors.push('dynamic_markup ausente');
    return;
  }

  const markup = sku.pricing.dynamic_markup;
  
  for (const field of REQUIRED_FIELDS.markup_details) {
    if (markup[field] === undefined || markup[field] === null) {
      errors.push(`dynamic_markup.${field} ausente`);
    }
  }

  if (markup.baseMarkup && markup.baseMarkup < 22) {
    warnings.push(`Markup base baixo: ${markup.baseMarkup}% (mínimo 22%)`);
  }

  if (markup.grossMargin && markup.grossMargin < 20) {
    errors.push(`Margem bruta baixa: ${markup.grossMargin}% (mínimo 20%)`);
  }
}

function validateFinalPrice(sku, errors) {
  if (!sku.pricing.final_price || sku.pricing.final_price <= 0) {
    errors.push('final_price inválido ou zero');
  }
}

function validateKPIs(sku, errors, warnings) {
  if (typeof sku.kpis !== 'object') {
    errors.push('KPIs inválidos ou ausentes');
    return;
  }

  for (const field of REQUIRED_FIELDS.kpis) {
    if (sku.kpis[field] === undefined || sku.kpis[field] === null) {
      errors.push(`kpis.${field} ausente`);
    }
  }

  if (sku.kpis.gross_margin_percent && sku.kpis.gross_margin_percent < 20) {
    errors.push(`Margem bruta em KPI abaixo de 20%: ${sku.kpis.gross_margin_percent}%`);
  }

  if (sku.kpis.net_margin_percent && sku.kpis.net_margin_percent < 11) {
    errors.push(`Margem líquida em KPI abaixo de 11%: ${sku.kpis.net_margin_percent}%`);
  }
}

function validateConsistency(sku, warnings) {
  if (sku.pricing.final_price && sku.kpis?.selling_price) {
    const diff = Math.abs(sku.pricing.final_price - sku.kpis.selling_price);
    if (diff > 1) {
      warnings.push(`Inconsistência de preço: final_price=${sku.pricing.final_price} vs selling_price=${sku.kpis.selling_price}`);
    }
  }
}

function validateOptionalFields(sku, warnings) {
  if (!sku.pricing.psychological_pricing?.charm_applied) {
    warnings.push('Psychological pricing não aplicado');
  }

  if (!sku.pricing.channel_pricing?.channel) {
    warnings.push('Channel pricing incompleto');
  }

  if (!sku.pricing.project_splits) {
    warnings.push('Project splits ausentes');
  }
}

function getSeverity(errors, warnings) {
  if (errors.length > 0) return 'ERROR';
  if (warnings.length > 0) return 'WARNING';
  return 'OK';
}

function validateSKU(sku) {
  const errors = [];
  const warnings = [];

  validateCoreFields(sku, errors);

  if (!validatePricingObject(sku, errors)) {
    return { valid: false, errors, warnings };
  }

  validateCostPrice(sku, errors);
  validateDynamicMarkup(sku, errors, warnings);
  validateFinalPrice(sku, errors);
  validateKPIs(sku, errors, warnings);
  validateConsistency(sku, warnings);
  validateOptionalFields(sku, warnings);

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    severity: getSeverity(errors, warnings)
  };
}

async function validateCatalog() {
  const reportPath = path.join(__dirname, '../ENRICHED_SKUS_DYNAMIC_PRICING_REPORT.json');
  const uploadPath = path.join(__dirname, '../enriched-skus-for-dynamodb.json');

  if (!fs.existsSync(reportPath)) {
    console.error('❌ Arquivo ENRICHED_SKUS_DYNAMIC_PRICING_REPORT.json não encontrado');
    process.exit(1);
  }

  console.log('📂 Carregando SKUs enriquecidos...\n');

  try {
    // Carregar SKUs para upload
    const uploadData = JSON.parse(fs.readFileSync(uploadPath, 'utf-8'));

    const totalSkus = uploadData.length;
    let validSkus = 0;
    let skusWithErrors = 0;
    let skusWithWarnings = 0;
    const invalidSkus = [];
    const warningSkus = [];

    console.log(`🔍 Validando ${totalSkus} SKUs...\n`);

    // Validar cada SKU
    await processSkusInBatches(uploadData, {
      onSKUValidated: (i, sku, validation) => {
        if (!validation.valid) {
          skusWithErrors++;
          invalidSkus.push({
            index: i,
            sku: sku.sku,
            errors: validation.errors
          });
        } else if (validation.warnings.length > 0) {
          skusWithWarnings++;
          warningSkus.push({
            index: i,
            sku: sku.sku,
            warnings: validation.warnings
          });
        } else {
          validSkus++;
        }
      },
      onProgress: (i) => {
        if ((i + 1) % 250 === 0) {
          process.stdout.write(`   ✓ ${i + 1}/${totalSkus} processados\n`);
        }
      }
    });

    printValidationResults(totalSkus, validSkus, skusWithErrors, skusWithWarnings, invalidSkus, warningSkus);
    
    const validationReport = generateValidationReport(totalSkus, validSkus, skusWithErrors, skusWithWarnings, invalidSkus, warningSkus);
    saveValidationReport(validationReport);

    process.exit(skusWithErrors === 0 ? 0 : 1);

  } catch (error) {
    console.error('❌ Erro ao validar SKUs:', error.message);
    process.exit(1);
  }
}

async function processSkusInBatches(uploadData, callbacks) {
  for (let i = 0; i < uploadData.length; i++) {
    const sku = uploadData[i];
    const validation = validateSKU(sku);
    callbacks.onSKUValidated(i, sku, validation);
    callbacks.onProgress(i);
  }
}

function printValidationResults(totalSkus, validSkus, skusWithErrors, skusWithWarnings, invalidSkus, warningSkus) {
  console.log('\n' + '═'.repeat(80));
  console.log('📊 RESULTADO DA VALIDAÇÃO\n');

  console.log('✅ ESTATÍSTICAS:');
  console.log(`   • SKUs Válidos: ${validSkus}/${totalSkus} (${(validSkus / totalSkus * 100).toFixed(2)}%)`);
  console.log(`   • SKUs com Avisos: ${skusWithWarnings}/${totalSkus} (${(skusWithWarnings / totalSkus * 100).toFixed(2)}%)`);
  console.log(`   • SKUs com Erros: ${skusWithErrors}/${totalSkus} (${(skusWithErrors / totalSkus * 100).toFixed(2)}%)`);

  printErrorDetails(invalidSkus);
  printWarningDetails(warningSkus);
  printFinalStatus(totalSkus, validSkus, skusWithErrors, skusWithWarnings);
}

function printErrorDetails(invalidSkus) {
  if (invalidSkus.length === 0) return;

  console.log(`\n❌ SKUs COM ERROS (${invalidSkus.length}):\n`);
  
  for (const item of invalidSkus.slice(0, 10)) {
    console.log(`   SKU #${item.index}: ${item.sku}`);
    for (const error of item.errors) {
      console.log(`      • ${error}`);
    }
  }

  if (invalidSkus.length > 10) {
    console.log(`\n   ... e mais ${invalidSkus.length - 10} SKUs com erros`);
  }
}

function printWarningDetails(warningSkus) {
  if (warningSkus.length === 0) return;

  if (warningSkus.length <= 5) {
    console.log(`\n⚠️  SKUs COM AVISOS (${warningSkus.length}):\n`);
    
    for (const item of warningSkus) {
      console.log(`   SKU #${item.index}: ${item.sku}`);
      for (const warning of item.warnings) {
        console.log(`      • ${warning}`);
      }
    }
  } else {
    console.log(`\n⚠️  ${warningSkus.length} SKUs com avisos (resumo omitido)`);
  }
}

function printFinalStatus(totalSkus, validSkus, skusWithErrors, skusWithWarnings) {
  console.log('\n' + '═'.repeat(80));

  if (skusWithErrors === 0) {
    console.log('\n✅ VALIDAÇÃO CONCLUÍDA COM SUCESSO!');
    console.log(`\n   ✓ Todos os ${totalSkus} SKUs estão completos e válidos`);
    console.log(`   ✓ Taxa de sucesso: 100%`);
    console.log(`   ✓ Avisos: ${skusWithWarnings} (não-críticos)`);
  } else {
    console.log('\n❌ VALIDAÇÃO CONCLUÍDA COM FALHAS!');
    console.log(`\n   ✗ ${skusWithErrors} SKUs com erros críticos`);
    console.log(`   ✗ Taxa de sucesso: ${(validSkus / totalSkus * 100).toFixed(2)}%`);
    console.log(`\n   ⚠️  Ação recomendada: Remediar SKUs inválidos antes de publicar`);
  }

  console.log(`\n📄 Relatório detalhado salvo em: SKU_VALIDATION_REPORT.json`);
  console.log('\n' + '═'.repeat(80) + '\n');
}

function generateValidationReport(totalSkus, validSkus, skusWithErrors, skusWithWarnings, invalidSkus, warningSkus) {
  return {
    timestamp: new Date().toISOString(),
    total_skus: totalSkus,
    valid_skus: validSkus,
    skus_with_warnings: skusWithWarnings,
    skus_with_errors: skusWithErrors,
    success_rate: (validSkus / totalSkus * 100).toFixed(2),
    validation_status: skusWithErrors === 0 ? 'PASSED' : 'FAILED',
    error_summary: {
      count: invalidSkus.length,
      samples: invalidSkus.slice(0, 10)
    },
    warning_summary: {
      count: warningSkus.length,
      samples: warningSkus.slice(0, 5)
    }
  };
}

function saveValidationReport(validationReport) {
  fs.writeFileSync(
    path.join(__dirname, '../SKU_VALIDATION_REPORT.json'),
    JSON.stringify(validationReport, null, 2)
  );
}

// Executar validação
try {
  await validateCatalog();
} catch (error) {
  console.error('❌ Erro fatal:', error);
  process.exit(1);
}
