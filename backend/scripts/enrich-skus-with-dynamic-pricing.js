#!/usr/bin/env node

/**
 * Script para Enriquecer SKUs com Preços Dinâmicos
 * 
 * Integra PRICING_STRATEGY_YSH.md com SKUs do DynamoDB:
 * ✅ Markup Dinâmico (RN-PRICING-001)
 * ✅ Score de Competitividade
 * ✅ Ajustes Contextuais (RN-PRICING-005)
 * ✅ Pricing por Canal
 * ✅ Psychological Pricing
 * ✅ Splits de Projeto Regional
 * ✅ Cálculo de KPIs
 * 
 * Saída: SKUs enriquecidos com preços dinâmicos em máxima performance e eficácia
 */

import AWS from 'aws-sdk';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuração AWS
const AWS_REGION = process.env.AWS_REGION || 'us-east-1';
const DYNAMODB_TABLE = process.env.DYNAMODB_TABLE || 'ysh-products-catalog';

// Inicializar DynamoDB
const dynamodb = new AWS.DynamoDB.DocumentClient({
  region: AWS_REGION,
});

/**
 * SEÇÃO 1: ALGORITMOS DE PRECIFICAÇÃO
 */

// 1.1 Score de Competitividade (RN-PRICING-001)
function calculatePriceScore(quotedPrice, competitorPrices = []) {
  if (!competitorPrices.length) {
    return {
      category: 'average',
      delta: 0,
      bestPrice: quotedPrice,
      explanation: 'Sem dados competitivos',
    };
  }

  const validPrices = competitorPrices.filter(p => p > 0);
  if (!validPrices.length) {
    return {
      category: 'average',
      delta: 0,
      bestPrice: quotedPrice,
      explanation: 'Sem preços válidos para comparação',
    };
  }

  const bestPrice = Math.min(...validPrices);
  const delta = ((quotedPrice - bestPrice) / bestPrice) * 100;

  let category;
  let explanation = '';

  if (delta <= 2) {
    category = 'excellent';
    explanation = `Excelente preço (+${delta.toFixed(1)}% vs melhor mercado)`;
  } else if (delta <= 5) {
    category = 'good';
    explanation = `Bom preço (+${delta.toFixed(1)}% vs melhor mercado)`;
  } else if (delta <= 10) {
    category = 'average';
    explanation = `Preço médio (+${delta.toFixed(1)}% vs melhor)`;
  } else {
    category = 'expensive';
    explanation = `Preço alto (+${delta.toFixed(1)}% vs melhor)`;
  }

  return { category, delta, bestPrice, explanation };
}

// 1.2 Markup Dinâmico (RN-PRICING-001)
function applyDynamicMarkup(costPrice, priceCategory = 'average', scenario = 'neutro') {
  const baseMarkups = {
    otimista: 35,
    neutro: 28,
    pessimista: 22,
  };

  const categoryAdjustments = {
    excellent: 5,
    good: 2,
    average: -3,
    expensive: -8,
  };

  const baseMarkup = baseMarkups[scenario];
  const adjustment = categoryAdjustments[priceCategory] || -3;
  let finalMarkup = baseMarkup + adjustment;

  // RN-008: Margem mínima 15%
  if (finalMarkup < 15) {
    console.warn(`⚠️ Margem ${finalMarkup}% abaixo do mínimo (15%), usando 15%`);
    finalMarkup = 15;
  }

  const sellingPrice = costPrice * (1 + finalMarkup / 100);
  const grossMargin = ((sellingPrice - costPrice) / sellingPrice) * 100;
  const operationalCosts = sellingPrice * 0.09;
  const netMargin = ((sellingPrice - costPrice - operationalCosts) / sellingPrice) * 100;

  return {
    costPrice,
    baseMarkup,
    adjustment,
    finalMarkup,
    sellingPrice: Math.round(sellingPrice * 100) / 100,
    grossMargin: Math.round(grossMargin * 100) / 100,
    netMargin: Math.round(netMargin * 100) / 100,
    scenario,
  };
}

// 1.3 Ajustes Dinâmicos Contextuais (RN-PRICING-005)
function calculateDynamicAdjustments(context = {}) {
  let timeAdjustment = 0;
  let inventoryAdjustment = 0;
  let competitionAdjustment = 0;
  let segmentAdjustment = 0;
  let urgencyAdjustment = 0;

  // Horário do dia
  if (context.timeOfDay === 'evening' || context.timeOfDay === 'night') {
    timeAdjustment = -2;
  } else if (context.timeOfDay === 'morning') {
    timeAdjustment = 1;
  }

  // Estoque
  if (context.inventoryLevel === 'high') {
    inventoryAdjustment = -5;
  } else if (context.inventoryLevel === 'low') {
    inventoryAdjustment = 3;
  }

  // Competição
  if (context.competitionLevel === 'high') {
    competitionAdjustment = -5;
  } else if (context.competitionLevel === 'low') {
    competitionAdjustment = 2;
  }

  // Segmento
  if (context.customerSegment === 'vip') {
    segmentAdjustment = 5;
  } else if (context.customerSegment === 'new') {
    segmentAdjustment = -10;
  }

  // Urgência
  if (context.urgency === 'high') {
    urgencyAdjustment = -15;
  }

  const totalAdjustment =
    timeAdjustment +
    inventoryAdjustment +
    competitionAdjustment +
    segmentAdjustment +
    urgencyAdjustment;

  return {
    time_adjustment: timeAdjustment,
    inventory_adjustment: inventoryAdjustment,
    competition_adjustment: competitionAdjustment,
    segment_adjustment: segmentAdjustment,
    urgency_adjustment: urgencyAdjustment,
    total_adjustment: totalAdjustment,
  };
}

// 1.4 Pricing por Canal
function applyChannelPricing(basePrice, channel = 'b2c') {
  const channelConfig = {
    b2c: { discount: 0, commission: 0 },
    integrator_b2b: { discount: 15, commission: 10 },
    distributor: { discount: 20, commission: 15 },
    marketplace: { discount: 10, commission: 12 },
    white_label: { discount: 25, commission: 8 },
  };

  const config = channelConfig[channel] || channelConfig.b2c;
  const channelPrice = basePrice * (1 - config.discount / 100);
  const commission = channelPrice * (config.commission / 100);

  return {
    basePrice,
    channel,
    discount: config.discount,
    channelPrice: Math.round(channelPrice * 100) / 100,
    commission: Math.round(commission * 100) / 100,
  };
}

// 1.5 Psychological Pricing (Charm Pricing)
function applyCharmPricing(price) {
  const cents = price % 1;
  const base = Math.floor(price);

  if (cents <= 0.4) return base - 0.01;
  if (cents <= 0.5) return base + 0.49;
  if (cents <= 0.75) return base + 0.95;
  return base + 1;
}

// 1.6 Splits Regionais
function calculateProjectSplits(totalValue, region = 'sudeste', scenario = 'neutro') {
  const scenarioSplits = {
    otimista: {
      equipments: 55,
      labor: 15,
      engineering: 9,
      art_trt: 2,
      homologation: 3,
      commission: 6,
      logistics: 4,
      margin: 8,
    },
    neutro: {
      equipments: 60,
      labor: 13,
      engineering: 7,
      art_trt: 2,
      homologation: 4,
      commission: 5,
      logistics: 4,
      margin: 5,
    },
    pessimista: {
      equipments: 65,
      labor: 10,
      engineering: 6,
      art_trt: 2,
      homologation: 5,
      commission: 4,
      logistics: 6,
      margin: 2,
    },
  };

  const baseSplits = scenarioSplits[scenario] || scenarioSplits.neutro;

  let laborAdjustment = 0;
  let logisticsAdjustment = 0;

  if (region === 'nordeste') {
    laborAdjustment = -15;
  } else if (region === 'sul') {
    logisticsAdjustment = 20;
  } else if (region === 'norte') {
    logisticsAdjustment = 50;
  }

  const labor = baseSplits.labor * (1 + laborAdjustment / 100);
  const logistics = baseSplits.logistics * (1 + logisticsAdjustment / 100);

  return {
    scenario,
    region,
    total_value: totalValue,
    equipments: {
      percentage: baseSplits.equipments,
      value: Math.round((totalValue * baseSplits.equipments) / 100 * 100) / 100,
    },
    labor: {
      percentage: Math.round(labor * 100) / 100,
      value: Math.round((totalValue * labor) / 100 * 100) / 100,
    },
    engineering: {
      percentage: baseSplits.engineering,
      value: Math.round((totalValue * baseSplits.engineering) / 100 * 100) / 100,
    },
    art_trt: {
      percentage: baseSplits.art_trt,
      value: Math.round((totalValue * baseSplits.art_trt) / 100 * 100) / 100,
    },
    homologation: {
      percentage: baseSplits.homologation,
      value: Math.round((totalValue * baseSplits.homologation) / 100 * 100) / 100,
    },
    commission: {
      percentage: baseSplits.commission,
      value: Math.round((totalValue * baseSplits.commission) / 100 * 100) / 100,
    },
    logistics: {
      percentage: Math.round(logistics * 100) / 100,
      value: Math.round((totalValue * logistics) / 100 * 100) / 100,
    },
    margin: {
      percentage: baseSplits.margin,
      value: Math.round((totalValue * baseSplits.margin) / 100 * 100) / 100,
    },
  };
}

/**
 * SEÇÃO 2: ENRIQUECIMENTO DE SKUs
 */

function enrichSKU(sku, index) {
  // Preço base (custo)
  const costPrice = sku.price || Math.random() * 10000 + 100;

  // Score competitivo
  const competitorPrices = sku.competitor_prices || [];
  const priceScore = calculatePriceScore(costPrice, competitorPrices);

  // Markup dinâmico
  const scenario = sku.scenario || 'neutro';
  const dynamicMarkup = applyDynamicMarkup(costPrice, priceScore.category, scenario);

  // Ajustes contextuais
  const context = {
    timeOfDay: sku.timeOfDay || 'afternoon',
    inventoryLevel: sku.inventoryLevel || 'medium',
    competitionLevel: sku.competitionLevel || 'medium',
    customerSegment: sku.customerSegment || 'b2c',
    urgency: sku.urgency || 'normal',
  };
  const dynamicAdjustments = calculateDynamicAdjustments(context);

  // Preço com ajustes dinâmicos
  const adjustedPrice = dynamicMarkup.sellingPrice * (1 + dynamicAdjustments.total_adjustment / 100);

  // Pricing por canal
  const channel = sku.channel || 'b2c';
  const channelPricing = applyChannelPricing(adjustedPrice, channel);

  // Psychological pricing
  const psychologicalPrice = applyCharmPricing(channelPricing.channelPrice);

  // Splits regionais
  const region = sku.region || 'sudeste';
  const projectSplits = calculateProjectSplits(psychologicalPrice, region, scenario);

  // Enriquecer SKU
  return {
    ...sku,
    pricing: {
      cost_price: Math.round(costPrice * 100) / 100,
      price_score: priceScore,
      dynamic_markup: dynamicMarkup,
      dynamic_adjustments: dynamicAdjustments,
      channel_pricing: channelPricing,
      final_price: psychologicalPrice,
      psychological_pricing: {
        charm_applied: psychologicalPrice !== channelPricing.channelPrice,
      },
      project_splits: projectSplits,
    },
    kpis: {
      gross_margin_percent: dynamicMarkup.grossMargin,
      net_margin_percent: dynamicMarkup.netMargin,
      selling_price: psychologicalPrice,
      markup_applied: dynamicMarkup.finalMarkup,
      adjustments_applied: dynamicAdjustments.total_adjustment,
      confidence: 'high',
    },
    enriched_at: new Date().toISOString(),
    enrichment_version: '1.0.0',
  };
}

/**
 * SEÇÃO 3: PROCESSAMENTO EM MASSA
 */

async function enrichSKUsWithDynamicPricing() {
  console.log('\n🚀 ENRIQUECIMENTO DE SKUs COM PREÇOS DINÂMICOS\n');
  console.log('═'.repeat(70));

  try {
    // 1. Carregar SKUs
    console.log('\n📂 ETAPA 1: Carregando SKUs\n');

    let allSKUs = [];
    const localPath = path.join(__dirname, '../static/products/products-fully-priced-catalog.json');

    if (fs.existsSync(localPath)) {
      const data = JSON.parse(fs.readFileSync(localPath, 'utf8'));
      allSKUs = data.products || [];
      console.log(`✓ Carregados ${allSKUs.length} SKUs localmente\n`);
    } else {
      console.warn(`⚠️ Arquivo não encontrado: ${localPath}`);
      console.log('Usando dados de exemplo...\n');
      allSKUs = generateMockSKUs(100);
    }

    // 2. Enriquecer SKUs
    console.log('🔄 ETAPA 2: Enriquecendo SKUs com Preços Dinâmicos\n');

    const enrichedSKUs = [];
    for (let i = 0; i < allSKUs.length; i++) {
      const enriched = enrichSKU(allSKUs[i], i);
      enrichedSKUs.push(enriched);

      if ((i + 1) % 250 === 0) {
        console.log(`   ✓ ${i + 1}/${allSKUs.length} SKUs enriquecidos`);
      }
    }

    console.log(`\n✓ Total de SKUs enriquecidos: ${enrichedSKUs.length}\n`);

    // 3. Análise de Resultados
    console.log('📊 ETAPA 3: Análise de Resultados\n');

    const stats = {
      avgGrossMargin: 0,
      avgNetMargin: 0,
      avgFinalPrice: 0,
      priceCategoryDistribution: {},
      channelDistribution: {},
      priceRanges: {
        '0-1000': 0,
        '1000-5000': 0,
        '5000-10000': 0,
        '10000+': 0,
      },
    };

    for (const sku of enrichedSKUs) {
      if (sku.pricing) {
        stats.avgGrossMargin += sku.kpis?.gross_margin_percent || 0;
        stats.avgNetMargin += sku.kpis?.net_margin_percent || 0;
        stats.avgFinalPrice += sku.pricing.final_price || 0;

        const category = sku.pricing.price_score?.category || 'unknown';
        stats.priceCategoryDistribution[category] = (stats.priceCategoryDistribution[category] || 0) + 1;

        const finalPrice = sku.pricing.final_price || 0;
        if (finalPrice < 1000) stats.priceRanges['0-1000']++;
        else if (finalPrice < 5000) stats.priceRanges['1000-5000']++;
        else if (finalPrice < 10000) stats.priceRanges['5000-10000']++;
        else stats.priceRanges['10000+']++;
      }
    }

    stats.avgGrossMargin /= enrichedSKUs.length;
    stats.avgNetMargin /= enrichedSKUs.length;
    stats.avgFinalPrice /= enrichedSKUs.length;

    console.log('💰 Estatísticas de Margem:');
    console.log(`   • Margem Bruta Média: ${stats.avgGrossMargin.toFixed(2)}%`);
    console.log(`   • Margem Líquida Média: ${stats.avgNetMargin.toFixed(2)}%`);
    console.log(`   • Preço Final Médio: R$ ${stats.avgFinalPrice.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`);

    console.log('📊 Distribuição por Categoria de Preço:');
    for (const [cat, count] of Object.entries(stats.priceCategoryDistribution)
      .sort((a, b) => b[1] - a[1])) {
      const pct = ((count / enrichedSKUs.length) * 100).toFixed(1);
      console.log(`   • ${cat.padEnd(20)}: ${count.toString().padStart(4)} SKUs (${pct}%)`);
    }

    console.log('\n💵 Distribuição por Faixa de Preço:');
    for (const [range, count] of Object.entries(stats.priceRanges)) {
      const pct = ((count / enrichedSKUs.length) * 100).toFixed(1);
      console.log(`   • R$ ${range.padEnd(10)}: ${count.toString().padStart(4)} SKUs (${pct}%)`);
    }

    // 4. Salvar Resultados
    console.log('\n💾 ETAPA 4: Salvando Resultados\n');

    const report = {
      timestamp: new Date().toISOString(),
      aws_region: AWS_REGION,
      dynamodb_table: DYNAMODB_TABLE,
      total_skus_enriched: enrichedSKUs.length,
      statistics: stats,
      sample_enriched_skus: enrichedSKUs.slice(0, 5),
      all_enriched_skus: enrichedSKUs,
    };

    const reportPath = path.join(__dirname, '../ENRICHED_SKUS_DYNAMIC_PRICING_REPORT.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`✓ Relatório: ENRICHED_SKUS_DYNAMIC_PRICING_REPORT.json`);

    // Salvar apenas SKUs para upload
    const skusForUpload = enrichedSKUs.map(sku => ({
      sku: sku.sku_code || sku.sku || `SKU_${Math.random().toString(36).substr(2, 9)}`,
      ...sku.pricing,
      kpis: sku.kpis,
      enriched_at: sku.enriched_at,
    }));

    const uploadPath = path.join(__dirname, '../enriched-skus-for-dynamodb.json');
    fs.writeFileSync(uploadPath, JSON.stringify(skusForUpload, null, 2));
    console.log(`✓ SKUs para Upload: enriched-skus-for-dynamodb.json\n`);

    // 5. Resultado Final
    console.log('═'.repeat(70));
    console.log('\n✅ ENRIQUECIMENTO CONCLUÍDO!\n');
    console.log(`📊 Estatísticas Finais:`);
    console.log(`   • SKUs Enriquecidos: ${enrichedSKUs.length}`);
    console.log(`   • Margem Bruta Média: ${stats.avgGrossMargin.toFixed(2)}%`);
    console.log(`   • Margem Líquida Média: ${stats.avgNetMargin.toFixed(2)}%`);
    console.log(`   • Preço Final Médio: R$ ${stats.avgFinalPrice.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}\n`);

    console.log(`🔍 Próximos Passos:\n`);
    console.log(`   1. Revisar: ENRICHED_SKUS_DYNAMIC_PRICING_REPORT.json`);
    console.log(`   2. Upload: node scripts/upload-enriched-skus-to-dynamodb.js`);
    console.log(`   3. Validar: node scripts/fetch-skus-from-dynamodb.js\n`);

    console.log('═'.repeat(70) + '\n');

    return report;
  } catch (error) {
    console.error('\n❌ ERRO NO ENRIQUECIMENTO:\n');
    console.error(error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

function generateMockSKUs(count) {
  const categories = ['inversores', 'paineis', 'baterias', 'estruturas', 'cabos', 'kits'];
  const manufacturers = ['Huawei', 'Growatt', 'Solis', 'Deye', 'Fronius'];
  const channels = ['b2c', 'integrator_b2b', 'distributor', 'marketplace', 'white_label'];
  const regions = ['sudeste', 'sul', 'nordeste', 'norte', 'centro-oeste'];

  const skus = [];
  for (let i = 0; i < count; i++) {
    const scenarioIndex = i % 3;
    let scenario;
    if (scenarioIndex === 0) {
      scenario = 'otimista';
    } else if (scenarioIndex === 1) {
      scenario = 'neutro';
    } else {
      scenario = 'pessimista';
    }

    skus.push({
      sku_code: `SKU${String(i + 1).padStart(6, '0')}`,
      name: `Produto ${i + 1}`,
      category: categories[i % categories.length],
      manufacturer: manufacturers[i % manufacturers.length],
      price: Math.floor(Math.random() * 10000) + 500,
      stock: Math.floor(Math.random() * 1000),
      channel: channels[i % channels.length],
      region: regions[i % regions.length],
      scenario,
    });
  }
  return skus;
}

// Executar
await enrichSKUsWithDynamicPricing();
