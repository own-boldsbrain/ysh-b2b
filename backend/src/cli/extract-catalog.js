#!/usr/bin/env node

/**
 * Extract Catalog CLI
 * Trigger workflow manual de extração de catálogo
 */

const args = process.argv.slice(2);
const distributorFlag = args.findIndex(arg => arg === '--distributor');
const distributor = distributorFlag !== -1 ? args[distributorFlag + 1] : null;

if (!distributor) {
  console.error('❌ Erro: --distributor é obrigatório');
  console.log('\nUso: npm run workflow:extract -- --distributor <nome>');
  console.log('\nDistribuidores disponíveis:');
  console.log('  - fortlev');
  console.log('  - neosolar');
  console.log('  - solfacil');
  console.log('  - fotus');
  console.log('  - odex');
  console.log('  - edeltec');
  console.log('  - dynamis');
  process.exit(1);
}

const VALID_DISTRIBUTORS = [
  'fortlev',
  'neosolar',
  'solfacil',
  'fotus',
  'odex',
  'edeltec',
  'dynamis',
];

if (!VALID_DISTRIBUTORS.includes(distributor)) {
  console.error(`❌ Erro: Distribuidor inválido "${distributor}"`);
  console.log('\nDistribuidores válidos:', VALID_DISTRIBUTORS.join(', '));
  process.exit(1);
}

console.log(`🚀 Iniciando extração de catálogo: ${distributor}`);
console.log('⏳ Aguarde...\n');

// Simulated workflow trigger - in production, call Temporal client
setTimeout(() => {
  const workflowId = `catalog-extraction-${distributor}-${Date.now()}`;
  console.log('✅ Workflow iniciado com sucesso!');
  console.log(`\n📋 Workflow ID: ${workflowId}`);
  console.log(`\n🔍 Acompanhe em: http://localhost:8080/namespaces/default/workflows/${workflowId}`);
  console.log('\n📊 Ver status: npm run workflow:status -- --workflow-id ' + workflowId);
}, 1000);
