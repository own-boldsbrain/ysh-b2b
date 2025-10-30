#!/usr/bin/env node
/**
 * Gera tabela comparativa com estratégia de preço dinâmico
 * Analisa markup dinâmico, ajustes, margens e cenários de precificação
 */

import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync, writeFileSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const backendDir = join(__dirname, '..');

console.log('🔍 Carregando dados de precificação dinâmica...\n');

// Carregar dados enriquecidos com estratégia de pricing
const enrichedSkus = JSON.parse(
  readFileSync(join(backendDir, 'enriched-skus-for-dynamodb-images-fixed.json'), 'utf-8')
);

console.log(`✓ Carregados ${enrichedSkus.length} SKUs com precificação dinâmica\n`);

// Processar dados de pricing
const pricingAnalysis = [];

enrichedSkus.forEach(sku => {
  if (!sku.dynamic_markup && !sku.pricing?.dynamic_markup) return;
  
  const dynamicMarkup = sku.dynamic_markup || sku.pricing?.dynamic_markup || {};
  const dynamicAdjustments = sku.dynamic_adjustments || sku.pricing?.dynamic_adjustments || {};
  const channelPricing = sku.channel_pricing || sku.pricing?.channel_pricing || {};
  const psychologicalPricing = sku.psychological_pricing || sku.pricing?.psychological_pricing || {};
  const kpis = sku.kpis || {};
  
  const analysis = {
    sku: sku.sku,
    category: sku.category || 'unknown',
    manufacturer: sku.manufacturer || 'unknown',
    
    // Preços base
    cost_price: sku.cost_price || dynamicMarkup.costPrice || 0,
    final_price: sku.final_price || sku.pricing?.final_price || 0,
    
    // Markup dinâmico
    base_markup: dynamicMarkup.baseMarkup || 0,
    markup_adjustment: dynamicMarkup.adjustment || 0,
    final_markup: dynamicMarkup.finalMarkup || 0,
    selling_price_calculated: dynamicMarkup.sellingPrice || 0,
    
    // Margens
    gross_margin_pct: dynamicMarkup.grossMargin || kpis.gross_margin_percent || 0,
    net_margin_pct: dynamicMarkup.netMargin || kpis.net_margin_percent || 0,
    
    // Cenário e ajustes
    scenario: dynamicMarkup.scenario || 'neutro',
    time_adjustment: dynamicAdjustments.time_adjustment || 0,
    inventory_adjustment: dynamicAdjustments.inventory_adjustment || 0,
    competition_adjustment: dynamicAdjustments.competition_adjustment || 0,
    segment_adjustment: dynamicAdjustments.segment_adjustment || 0,
    urgency_adjustment: dynamicAdjustments.urgency_adjustment || 0,
    total_adjustment: dynamicAdjustments.total_adjustment || 0,
    
    // Canal e descontos
    channel: channelPricing.channel || 'b2c',
    channel_discount: channelPricing.discount || 0,
    channel_price: channelPricing.channelPrice || 0,
    channel_commission: channelPricing.commission || 0,
    
    // Pricing psicológico
    charm_applied: psychologicalPricing.charm_applied || false,
    
    // Score de confiança
    confidence: kpis.confidence || 'low',
    
    // Price score
    price_category: sku.price_score?.category || sku.pricing?.price_score?.category || 'average',
    price_explanation: sku.price_score?.explanation || sku.pricing?.price_score?.explanation || '',
    
    // Imagem
    image_url: sku.image_url || sku.images?.[0] || null
  };
  
  pricingAnalysis.push(analysis);
});

console.log(`📊 Processados ${pricingAnalysis.length} produtos com estratégia de pricing\n`);

// Análise por cenário
const scenarioStats = {};
pricingAnalysis.forEach(p => {
  if (!scenarioStats[p.scenario]) {
    scenarioStats[p.scenario] = {
      count: 0,
      avg_markup: 0,
      avg_gross_margin: 0,
      avg_net_margin: 0,
      total_markup: 0,
      total_gross: 0,
      total_net: 0
    };
  }
  
  const stats = scenarioStats[p.scenario];
  stats.count++;
  stats.total_markup += p.final_markup;
  stats.total_gross += p.gross_margin_pct;
  stats.total_net += p.net_margin_pct;
});

Object.keys(scenarioStats).forEach(scenario => {
  const stats = scenarioStats[scenario];
  stats.avg_markup = (stats.total_markup / stats.count).toFixed(2);
  stats.avg_gross_margin = (stats.total_gross / stats.count).toFixed(2);
  stats.avg_net_margin = (stats.total_net / stats.count).toFixed(2);
});

// Análise por categoria de preço
const priceCategories = {};
pricingAnalysis.forEach(p => {
  if (!priceCategories[p.price_category]) {
    priceCategories[p.price_category] = { count: 0, products: [] };
  }
  priceCategories[p.price_category].count++;
  priceCategories[p.price_category].products.push(p.sku);
});

// Ordenar por maior margem líquida
pricingAnalysis.sort((a, b) => b.net_margin_pct - a.net_margin_pct);

// Gerar CSV detalhado
const csvRows = [
  'SKU,Categoria,Custo,Preco_Final,Markup_Base_%,Ajuste_%,Markup_Final_%,Margem_Bruta_%,Margem_Liquida_%,Cenario,Canal,Desconto_Canal,Charm_Pricing,Confianca,Ajuste_Tempo,Ajuste_Estoque,Ajuste_Competicao,Ajuste_Segmento,Ajuste_Urgencia,Total_Ajustes'
];

pricingAnalysis.forEach(p => {
  csvRows.push([
    p.sku,
    p.category,
    p.cost_price.toFixed(2),
    p.final_price.toFixed(2),
    p.base_markup,
    p.markup_adjustment,
    p.final_markup,
    p.gross_margin_pct,
    p.net_margin_pct,
    p.scenario,
    p.channel,
    p.channel_discount,
    p.charm_applied ? 'Sim' : 'Não',
    p.confidence,
    p.time_adjustment,
    p.inventory_adjustment,
    p.competition_adjustment,
    p.segment_adjustment,
    p.urgency_adjustment,
    p.total_adjustment
  ].join(','));
});

// Salvar CSV
const csvPath = join(backendDir, 'dynamic-pricing-analysis.csv');
writeFileSync(csvPath, csvRows.join('\n'), 'utf-8');
console.log(`📄 CSV gerado: ${csvPath}`);

// Gerar JSON com análises
const jsonReport = {
  generated_at: new Date().toISOString(),
  summary: {
    total_products: pricingAnalysis.length,
    avg_final_markup: (pricingAnalysis.reduce((sum, p) => sum + p.final_markup, 0) / pricingAnalysis.length).toFixed(2),
    avg_gross_margin: (pricingAnalysis.reduce((sum, p) => sum + p.gross_margin_pct, 0) / pricingAnalysis.length).toFixed(2),
    avg_net_margin: (pricingAnalysis.reduce((sum, p) => sum + p.net_margin_pct, 0) / pricingAnalysis.length).toFixed(2),
    with_charm_pricing: pricingAnalysis.filter(p => p.charm_applied).length,
    with_adjustments: pricingAnalysis.filter(p => p.total_adjustment !== 0).length
  },
  scenario_analysis: scenarioStats,
  price_category_distribution: priceCategories,
  top_margin_products: pricingAnalysis.slice(0, 50),
  low_margin_products: pricingAnalysis.slice(-20)
};

const jsonPath = join(backendDir, 'dynamic-pricing-analysis.json');
writeFileSync(jsonPath, JSON.stringify(jsonReport, null, 2), 'utf-8');
console.log(`📄 JSON gerado: ${jsonPath}\n`);

// Exibir resumo
console.log('📊 RESUMO DA ESTRATÉGIA DE PRECIFICAÇÃO DINÂMICA:\n');
console.log(`   Total de produtos: ${pricingAnalysis.length}`);
console.log(`   Markup médio final: ${jsonReport.summary.avg_final_markup}%`);
console.log(`   Margem bruta média: ${jsonReport.summary.avg_gross_margin}%`);
console.log(`   Margem líquida média: ${jsonReport.summary.avg_net_margin}%`);
console.log(`   Produtos com charm pricing: ${jsonReport.summary.with_charm_pricing} (${(jsonReport.summary.with_charm_pricing / pricingAnalysis.length * 100).toFixed(1)}%)`);
console.log(`   Produtos com ajustes: ${jsonReport.summary.with_adjustments} (${(jsonReport.summary.with_adjustments / pricingAnalysis.length * 100).toFixed(1)}%)\n`);

// Análise por cenário
console.log('🎯 ANÁLISE POR CENÁRIO DE PRECIFICAÇÃO:\n');
Object.keys(scenarioStats).sort().forEach(scenario => {
  const stats = scenarioStats[scenario];
  console.log(`   ${scenario.toUpperCase()}:`);
  console.log(`      Produtos: ${stats.count}`);
  console.log(`      Markup médio: ${stats.avg_markup}%`);
  console.log(`      Margem bruta média: ${stats.avg_gross_margin}%`);
  console.log(`      Margem líquida média: ${stats.avg_net_margin}%\n`);
});

// Top 10 produtos com maior margem líquida
console.log('🏆 TOP 10 PRODUTOS COM MAIOR MARGEM LÍQUIDA:\n');
pricingAnalysis.slice(0, 10).forEach((p, idx) => {
  console.log(`${idx + 1}. ${p.sku}`);
  console.log(`   Categoria: ${p.category} | Cenário: ${p.scenario}`);
  console.log(`   Custo: R$ ${p.cost_price.toFixed(2)} → Preço: R$ ${p.final_price.toFixed(2)}`);
  console.log(`   Markup: ${p.base_markup}% (ajuste ${p.markup_adjustment}%) = ${p.final_markup}%`);
  console.log(`   Margem Bruta: ${p.gross_margin_pct}% | Margem Líquida: ${p.net_margin_pct}%`);
  
  const adjustments = [];
  if (p.time_adjustment) adjustments.push(`Tempo:${p.time_adjustment}`);
  if (p.inventory_adjustment) adjustments.push(`Estoque:${p.inventory_adjustment}`);
  if (p.competition_adjustment) adjustments.push(`Competição:${p.competition_adjustment}`);
  if (p.segment_adjustment) adjustments.push(`Segmento:${p.segment_adjustment}`);
  if (p.urgency_adjustment) adjustments.push(`Urgência:${p.urgency_adjustment}`);
  
  if (adjustments.length > 0) {
    console.log(`   Ajustes: ${adjustments.join(', ')}`);
  }
  console.log('');
});

// Produtos com ajustes aplicados
const withAdjustments = pricingAnalysis.filter(p => p.total_adjustment !== 0);
if (withAdjustments.length > 0) {
  console.log(`\n⚙️  PRODUTOS COM AJUSTES DINÂMICOS: ${withAdjustments.length}\n`);
  
  // Estatísticas de ajustes
  const adjustmentTypes = {
    time: withAdjustments.filter(p => p.time_adjustment !== 0).length,
    inventory: withAdjustments.filter(p => p.inventory_adjustment !== 0).length,
    competition: withAdjustments.filter(p => p.competition_adjustment !== 0).length,
    segment: withAdjustments.filter(p => p.segment_adjustment !== 0).length,
    urgency: withAdjustments.filter(p => p.urgency_adjustment !== 0).length
  };
  
  console.log('   Tipos de ajuste aplicados:');
  Object.entries(adjustmentTypes).forEach(([type, count]) => {
    if (count > 0) {
      console.log(`      ${type}: ${count} produtos`);
    }
  });
}

console.log('\n✅ Análise de precificação dinâmica concluída!');
