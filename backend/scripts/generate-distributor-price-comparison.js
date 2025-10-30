#!/usr/bin/env node
/**
 * Gera tabela comparativa de preços por distribuidor
 * Analisa múltiplas fontes de dados para identificar variações de preço
 */

import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync, writeFileSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const backendDir = join(__dirname, '..');

console.log('🔍 Carregando dados de catálogos...\n');

// Carregar múltiplas fontes de dados
const enrichedSkus = JSON.parse(
  readFileSync(join(backendDir, 'enriched-skus-for-dynamodb-images-fixed.json'), 'utf-8')
);

const detailedCatalog = JSON.parse(
  readFileSync(join(backendDir, 'static', 'products', 'products-detailed-catalog.json'), 'utf-8')
);

const pricedCatalog = JSON.parse(
  readFileSync(join(backendDir, 'static', 'products', 'products-fully-priced-catalog.json'), 'utf-8')
);

console.log(`✓ Carregados ${enrichedSkus.length} SKUs enriquecidos`);
console.log(`✓ Carregados ${detailedCatalog.products.length} produtos detalhados`);
console.log(`✓ Carregados ${pricedCatalog.products.length} produtos com preço\n`);

// Mapear produtos por SKU
const skuMap = new Map();

// Adicionar dados enriquecidos (fonte primária)
enrichedSkus.forEach(sku => {
  if (!skuMap.has(sku.sku)) {
    skuMap.set(sku.sku, {
      sku: sku.sku,
      category: sku.category || 'unknown',
      manufacturer: sku.manufacturer || 'unknown',
      image_url: sku.image_url || sku.images?.[0] || null,
      prices: [],
      stats: {
        min: null,
        max: null,
        avg: null,
        variation_pct: 0
      }
    });
  }
  
  const product = skuMap.get(sku.sku);
  
  // Adicionar preço de custo (source: internal)
  if (sku.cost_price && sku.cost_price > 0) {
    product.prices.push({
      source: 'internal_cost',
      distributor: 'YSH Internal',
      price: sku.cost_price,
      type: 'cost'
    });
  }
  
  // Adicionar preço final (source: internal_pricing)
  if (sku.final_price && sku.final_price > 0) {
    product.prices.push({
      source: 'internal_pricing',
      distributor: 'YSH B2C',
      price: sku.final_price,
      type: 'final'
    });
  }
  
  // Adicionar preço do pricing object se diferente
  if (sku.pricing?.final_price && sku.pricing.final_price !== sku.final_price) {
    product.prices.push({
      source: 'pricing_engine',
      distributor: 'YSH Pricing',
      price: sku.pricing.final_price,
      type: 'calculated'
    });
  }
});

// Adicionar dados do catálogo detalhado
detailedCatalog.products.forEach(prod => {
  if (!prod.sku) return;
  
  if (!skuMap.has(prod.sku)) {
    skuMap.set(prod.sku, {
      sku: prod.sku,
      category: prod.category || 'unknown',
      manufacturer: prod.manufacturer || 'unknown',
      image_url: prod.image_url || null,
      prices: [],
      stats: {
        min: null,
        max: null,
        avg: null,
        variation_pct: 0
      }
    });
  }
  
  const product = skuMap.get(prod.sku);
  
  // Adicionar preços se existirem
  if (prod.price_brl && prod.price_brl > 0) {
    product.prices.push({
      source: 'detailed_catalog',
      distributor: prod.supplier || 'Catalog',
      price: prod.price_brl / 100, // converter centavos para reais
      type: 'catalog'
    });
  }
  
  if (prod.list_price_brl && prod.list_price_brl > 0) {
    product.prices.push({
      source: 'list_price',
      distributor: 'List Price',
      price: prod.list_price_brl / 100,
      type: 'list'
    });
  }
  
  if (prod.cost_price_brl && prod.cost_price_brl > 0) {
    product.prices.push({
      source: 'catalog_cost',
      distributor: prod.supplier || 'Supplier',
      price: prod.cost_price_brl / 100,
      type: 'cost'
    });
  }
});

// Adicionar dados do catálogo precificado
pricedCatalog.products.forEach(prod => {
  if (!prod.sku) return;
  
  if (!skuMap.has(prod.sku)) {
    skuMap.set(prod.sku, {
      sku: prod.sku,
      category: prod.category || 'unknown',
      manufacturer: prod.manufacturer || 'unknown',
      image_url: prod.image_url || null,
      prices: [],
      stats: {
        min: null,
        max: null,
        avg: null,
        variation_pct: 0
      }
    });
  }
  
  const product = skuMap.get(prod.sku);
  
  if (prod.price_brl && prod.price_brl > 0) {
    // Converter centavos para reais se necessário
    const price = prod.price_brl > 100000 ? prod.price_brl / 100 : prod.price_brl;
    
    product.prices.push({
      source: 'priced_catalog',
      distributor: prod.supplier || 'Estimated',
      price: price,
      type: prod.source === 'estimated' ? 'estimated' : 'catalog',
      confidence: prod.confidence || null
    });
  }
});

console.log(`📊 Processando ${skuMap.size} produtos únicos...\n`);

// Calcular estatísticas por produto
const productsWithMultiplePrices = [];

skuMap.forEach((product, sku) => {
  if (product.prices.length === 0) return;
  
  // Remover duplicatas (mesmo price + distributor)
  const uniquePrices = [];
  const seen = new Set();
  
  product.prices.forEach(p => {
    const key = `${p.distributor}-${p.price.toFixed(2)}`;
    if (!seen.has(key)) {
      seen.add(key);
      uniquePrices.push(p);
    }
  });
  
  product.prices = uniquePrices;
  
  // Calcular estatísticas
  const prices = product.prices.map(p => p.price);
  product.stats.min = Math.min(...prices);
  product.stats.max = Math.max(...prices);
  product.stats.avg = prices.reduce((a, b) => a + b, 0) / prices.length;
  
  if (product.stats.max > 0) {
    product.stats.variation_pct = ((product.stats.max - product.stats.min) / product.stats.min) * 100;
  }
  
  // Adicionar ranking de preços
  product.prices.sort((a, b) => a.price - b.price);
  product.prices.forEach((p, idx) => {
    p.rank = idx + 1;
    p.is_best = idx === 0;
    p.is_worst = idx === product.prices.length - 1;
    p.diff_from_best_pct = product.stats.min > 0 
      ? ((p.price - product.stats.min) / product.stats.min) * 100 
      : 0;
  });
  
  if (product.prices.length >= 2) {
    productsWithMultiplePrices.push(product);
  }
});

// Ordenar por maior variação de preço
productsWithMultiplePrices.sort((a, b) => b.stats.variation_pct - a.stats.variation_pct);

console.log(`✅ Encontrados ${productsWithMultiplePrices.length} produtos com múltiplas ofertas\n`);

// Gerar tabela CSV
const csvRows = [
  'SKU,Categoria,Fabricante,Num_Ofertas,Melhor_Preco,Pior_Preco,Preco_Medio,Variacao_%,Distribuidores'
];

productsWithMultiplePrices.forEach(product => {
  const distributors = product.prices.map(p => `${p.distributor}:R$${p.price.toFixed(2)}`).join('; ');
  
  csvRows.push([
    product.sku,
    product.category,
    product.manufacturer,
    product.prices.length,
    product.stats.min.toFixed(2),
    product.stats.max.toFixed(2),
    product.stats.avg.toFixed(2),
    product.stats.variation_pct.toFixed(2),
    `"${distributors}"`
  ].join(','));
});

// Salvar CSV
const csvPath = join(backendDir, 'distributor-price-comparison.csv');
writeFileSync(csvPath, csvRows.join('\n'), 'utf-8');
console.log(`📄 CSV gerado: ${csvPath}`);

// Gerar JSON detalhado
const jsonPath = join(backendDir, 'distributor-price-comparison.json');
const report = {
  generated_at: new Date().toISOString(),
  summary: {
    total_products: skuMap.size,
    products_with_multiple_prices: productsWithMultiplePrices.length,
    avg_offers_per_product: productsWithMultiplePrices.length > 0
      ? (productsWithMultiplePrices.reduce((sum, p) => sum + p.prices.length, 0) / productsWithMultiplePrices.length).toFixed(2)
      : 0,
    avg_price_variation_pct: productsWithMultiplePrices.length > 0
      ? (productsWithMultiplePrices.reduce((sum, p) => sum + p.stats.variation_pct, 0) / productsWithMultiplePrices.length).toFixed(2)
      : 0
  },
  products: productsWithMultiplePrices.slice(0, 100) // Top 100 por variação
};

writeFileSync(jsonPath, JSON.stringify(report, null, 2), 'utf-8');
console.log(`📄 JSON gerado: ${jsonPath}\n`);

// Exibir resumo
console.log('📊 RESUMO:\n');
console.log(`   Total de produtos: ${skuMap.size}`);
console.log(`   Com múltiplas ofertas: ${productsWithMultiplePrices.length} (${(productsWithMultiplePrices.length / skuMap.size * 100).toFixed(1)}%)`);
console.log(`   Média de ofertas/produto: ${report.summary.avg_offers_per_product}`);
console.log(`   Variação média de preços: ${report.summary.avg_price_variation_pct}%\n`);

// Exibir top 10 com maior variação
console.log('🏆 TOP 10 PRODUTOS COM MAIOR VARIAÇÃO DE PREÇO:\n');
productsWithMultiplePrices.slice(0, 10).forEach((p, idx) => {
  console.log(`${idx + 1}. ${p.sku}`);
  console.log(`   Categoria: ${p.category} | Ofertas: ${p.prices.length}`);
  console.log(`   Melhor: R$ ${p.stats.min.toFixed(2)} | Pior: R$ ${p.stats.max.toFixed(2)} | Variação: ${p.stats.variation_pct.toFixed(1)}%`);
  
  p.prices.forEach(price => {
    const indicator = price.is_best ? '🟢' : (price.is_worst ? '🔴' : '⚪');
    console.log(`   ${indicator} ${price.distributor}: R$ ${price.price.toFixed(2)} (+${price.diff_from_best_pct.toFixed(1)}%)`);
  });
  console.log('');
});

console.log('✅ Análise concluída!');
