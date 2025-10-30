import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const IMAGE_MAP_PATH = path.join(__dirname, '../static/products/product_image_map.json');
const PRICES_PATH = path.join(__dirname, '../static/products/products-prices-review.json');
const OUTPUT_PATH = path.join(__dirname, '../static/products/products-fully-priced-catalog.json');
const OUTPUT_CSV_PATH = path.join(__dirname, '../static/products/products-fully-priced-catalog.csv');

// Tabela de preços base por categoria e características
const PRICING_RULES = {
  inversores: {
    base: 2500,
    per_kw: 800,
    multipliers: {
      'DEYE': 0.85,
      'GOODWE': 0.90,
      'GROWATT': 0.88,
      'HUAWEI': 1.30,
      'SUNGROW': 1.25,
      'FRONIUS': 1.50,
      'SOLIS': 0.95,
      'SAJ': 0.82,
      'SOFAR': 0.87,
      'FOXESS': 0.92,
      'CANADIAN': 1.10,
      'ENPHASE': 1.20
    }
  },
  modulos: {
    base: 650,
    per_watt: 1.5,
    multipliers: {
      'CANADIAN': 1.15,
      'JINKO': 1.10,
      'TRINA': 1.10,
      'LONGI': 1.12,
      'JA SOLAR': 1.08,
      'RISEN': 0.95,
      'DAH': 1.05
    }
  },
  baterias: {
    base: 4500,
    per_kwh: 2800,
    multipliers: {
      'BYD': 1.20,
      'PYLONTECH': 1.15,
      'DYNESS': 1.10,
      'HUAWEI': 1.25
    }
  },
  estruturas: {
    base: 850,
    per_module: 85,
    multipliers: {
      'K2': 1.15,
      'ROMAGNOLE': 1.10,
      'ALDO': 1.05
    }
  },
  kits: {
    base: 2500,
    per_kwp: 4500, // R$ 4.50 por Wp instalado (médio mercado brasileiro)
    multipliers: {
      'completo': 1.00,
      'hibrido': 1.20,
      'off-grid': 1.50,
      'on-grid': 0.90
    }
  },
  cabos: {
    base: 180,
    per_meter: 12,
    multipliers: {
      '4mm': 0.85,
      '6mm': 1.00,
      '10mm': 1.30
    }
  },
  conectores: {
    base: 45,
    multipliers: {
      'MC4': 1.00,
      'MC5': 1.10
    }
  },
  string_box: {
    base: 850,
    per_string: 120
  },
  default: {
    base: 1200
  }
};

function extractManufacturerFromFilename(filename) {
  const manufacturers = [
    'DEYE', 'GOODWE', 'GROWATT', 'HUAWEI', 'SUNGROW', 'FRONIUS', 
    'SOLIS', 'SAJ', 'SOFAR', 'FOXESS', 'ENPHASE',
    'CANADIAN', 'JINKO', 'TRINA', 'LONGI', 'JA SOLAR', 'RISEN', 'DAH',
    'BYD', 'PYLONTECH', 'DYNESS',
    'K2', 'ROMAGNOLE', 'ALDO'
  ];
  
  const upper = filename.toUpperCase();
  for (const mfr of manufacturers) {
    if (upper.includes(mfr)) return mfr;
  }
  return null;
}

function extractPowerFromFilename(filename) {
  // Padrões: 3000W, 3KW, 3.5KW, 550W, 1704kWp (para kits), etc
  const patterns = [
    /(\d+(?:\.\d+)?)\s*KWP/i,  // KWp para kits (prioridade)
    /(\d+(?:\.\d+)?)\s*KW/i,
    /(\d+(?:\.\d+)?)\s*K(?!G)/i,
    /(\d+)\s*W(?!H)/i
  ];
  
  for (const pattern of patterns) {
    const match = filename.match(pattern);
    if (match) {
      let power = parseFloat(match[1]);
      if (pattern.source.includes('KW') || pattern.source.includes('K(?!')) {
        power *= 1000; // Converter KW para W
      }
      return power;
    }
  }
  return null;
}

function extractCapacityFromFilename(filename) {
  // Para baterias: 5.12KWH, 10KWH, etc
  const match = filename.match(/(\d+(?:\.\d+)?)\s*KWH/i);
  if (match) {
    return parseFloat(match[1]);
  }
  return null;
}

function extractModuleCountFromFilename(filename) {
  // Padrões: 10MOD, 10 MODULOS, etc
  const patterns = [
    /(\d+)\s*MOD/i,
    /(\d+)\s*PAINEL/i,
    /(\d+)\s*PLACA/i
  ];
  
  for (const pattern of patterns) {
    const match = filename.match(pattern);
    if (match) {
      return parseInt(match[1]);
    }
  }
  return null;
}

function estimatePriceForSKU(sku, imageData) {
  const category = imageData.category || 'default';
  const filename = imageData.filename || '';
  
  const rules = PRICING_RULES[category] || PRICING_RULES.default;
  let price = rules.base;
  
  // Extrair características do nome do arquivo
  const manufacturer = extractManufacturerFromFilename(filename);
  const power = extractPowerFromFilename(filename);
  const capacity = extractCapacityFromFilename(filename);
  const moduleCount = extractModuleCountFromFilename(filename);
  
  // Aplicar regras de precificação
  switch(category) {
    case 'inversores':
      if (power) {
        const kw = power / 1000;
        price = rules.base + (kw * rules.per_kw);
      }
      if (manufacturer && rules.multipliers[manufacturer]) {
        price *= rules.multipliers[manufacturer];
      }
      break;
      
    case 'modulos':
      if (power) {
        price = rules.base + (power * rules.per_watt);
      }
      if (manufacturer && rules.multipliers[manufacturer]) {
        price *= rules.multipliers[manufacturer];
      }
      break;
      
    case 'baterias':
      if (capacity) {
        price = rules.base + (capacity * rules.per_kwh);
      }
      if (manufacturer && rules.multipliers[manufacturer]) {
        price *= rules.multipliers[manufacturer];
      }
      break;
      
    case 'estruturas':
      if (moduleCount) {
        price = rules.base + (moduleCount * rules.per_module);
      }
      if (manufacturer && rules.multipliers[manufacturer]) {
        price *= rules.multipliers[manufacturer];
      }
      break;
      
    case 'kits':
      // Para kits, usar potência em kWp como base principal
      if (power) {
        const kwp = power / 1000;
        price = rules.base + (kwp * rules.per_kwp);
        
        // Aplicar multiplicador por tipo
        const upper = filename.toUpperCase();
        if (upper.includes('OFF-GRID') || upper.includes('OFFGRID')) {
          price *= rules.multipliers['off-grid'];
        } else if (upper.includes('HIBRIDO') || upper.includes('HYBRID')) {
          price *= rules.multipliers['hibrido'];
        } else if (upper.includes('ON-GRID') || upper.includes('ONGRID')) {
          price *= rules.multipliers['on-grid'];
        } else {
          price *= rules.multipliers['completo'];
        }
      } else {
        // Sem potência especificada, usar base
        price = rules.base;
      }
      break;
      
    case 'cabos':
      // Extrair metragem se possível
      const lengthMatch = filename.match(/(\d+)\s*M(?!M)/i);
      if (lengthMatch) {
        const meters = parseInt(lengthMatch[1]);
        price = rules.base + (meters * rules.per_meter);
      }
      
      // Ajustar por bitola
      if (filename.includes('4MM')) price *= rules.multipliers['4mm'];
      else if (filename.includes('6MM')) price *= rules.multipliers['6mm'];
      else if (filename.includes('10MM')) price *= rules.multipliers['10mm'];
      break;
      
    case 'string_box':
      const strings = filename.match(/(\d+)\s*STR/i);
      if (strings) {
        price = rules.base + (parseInt(strings[1]) * rules.per_string);
      }
      break;
  }
  
  // Arredondar para 2 casas decimais
  return Math.round(price * 100) / 100;
}

function matchSKUWithPriceData(sku, imageData, pricesData) {
  // Tentar match direto por SKU
  const directMatch = pricesData.products.find(p => p.sku === sku);
  if (directMatch && directMatch.price_brl) {
    return {
      price_brl: directMatch.price_brl,
      list_price_brl: directMatch.list_price_brl,
      cost_price_brl: directMatch.cost_price_brl,
      supplier: directMatch.supplier,
      source: 'direct_match',
      confidence: 1.0
    };
  }
  
  // Tentar match por características (categoria + fabricante + potência)
  const category = imageData.category;
  const filename = imageData.filename || '';
  const manufacturer = extractManufacturerFromFilename(filename);
  const power = extractPowerFromFilename(filename);
  
  if (category && manufacturer) {
    const similarProducts = pricesData.products.filter(p => {
      const pCategory = p.category?.toLowerCase();
      const pMfr = p.manufacturer?.toUpperCase();
      const pPower = p.power_w;
      
      const categoryMatch = pCategory === category.toLowerCase() || 
                          (category === 'inversores' && pCategory === 'inverters');
      const mfrMatch = pMfr === manufacturer;
      
      if (!categoryMatch || !mfrMatch) return false;
      
      // Se temos potência, tentar match próximo (±10%)
      if (power && pPower) {
        const diff = Math.abs(power - pPower) / power;
        return diff < 0.10;
      }
      
      return true;
    });
    
    if (similarProducts.length > 0) {
      // Usar mediana de preços
      const prices = similarProducts
        .map(p => p.price_brl)
        .filter(p => p > 0)
        .sort((a, b) => a - b);
      
      if (prices.length > 0) {
        const medianPrice = prices[Math.floor(prices.length / 2)];
        return {
          price_brl: medianPrice,
          list_price_brl: null,
          cost_price_brl: null,
          supplier: similarProducts[0].supplier,
          source: 'similar_match',
          confidence: 0.7,
          similar_count: prices.length
        };
      }
    }
  }
  
  // Sem match - usar estimativa
  const estimatedPrice = estimatePriceForSKU(sku, imageData);
  return {
    price_brl: estimatedPrice,
    list_price_brl: null,
    cost_price_brl: null,
    supplier: 'Estimated',
    source: 'estimated',
    confidence: 0.4
  };
}

async function ensureAllSKUsPriced() {
  console.log('\n💰 GARANTINDO PRECIFICAÇÃO COMPLETA\n');
  console.log('═'.repeat(70));
  
  // Carregar dados
  console.log('\n📂 Carregando dados...\n');
  const imageMap = JSON.parse(fs.readFileSync(IMAGE_MAP_PATH, 'utf-8'));
  const pricesData = JSON.parse(fs.readFileSync(PRICES_PATH, 'utf-8'));
  
  const allSKUs = Object.keys(imageMap.images);
  console.log(`   ✅ ${allSKUs.length} SKUs no catálogo`);
  console.log(`   ✅ ${pricesData.products.length} produtos com preços conhecidos\n`);
  
  // Processar cada SKU
  console.log('⚙️  Processando precificação...\n');
  const pricedCatalog = [];
  const stats = {
    direct_match: 0,
    similar_match: 0,
    estimated: 0,
    by_category: {},
    by_confidence: {
      high: 0,    // confidence >= 0.8
      medium: 0,  // 0.5 <= confidence < 0.8
      low: 0      // confidence < 0.5
    }
  };
  
  for (const sku of allSKUs) {
    const imageData = imageMap.images[sku][0]; // Pegar primeira imagem
    const pricingInfo = matchSKUWithPriceData(sku, imageData, pricesData);
    
    const product = {
      sku,
      category: imageData.category,
      filename: imageData.filename,
      image_url: imageData.cdn_url,
      manufacturer: extractManufacturerFromFilename(imageData.filename),
      power_w: extractPowerFromFilename(imageData.filename),
      capacity_kwh: extractCapacityFromFilename(imageData.filename),
      ...pricingInfo
    };
    
    pricedCatalog.push(product);
    
    // Atualizar estatísticas
    stats[pricingInfo.source]++;
    
    const cat = imageData.category || 'uncategorized';
    stats.by_category[cat] = (stats.by_category[cat] || 0) + 1;
    
    if (pricingInfo.confidence >= 0.8) stats.by_confidence.high++;
    else if (pricingInfo.confidence >= 0.5) stats.by_confidence.medium++;
    else stats.by_confidence.low++;
  }
  
  // Calcular estatísticas de preços
  const prices = pricedCatalog.map(p => p.price_brl);
  const totalValue = prices.reduce((sum, p) => sum + p, 0);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const avgPrice = totalValue / prices.length;
  
  // Ordenar por preço (decrescente)
  pricedCatalog.sort((a, b) => b.price_brl - a.price_brl);
  
  // Gerar JSON
  const output = {
    generated_at: new Date().toISOString(),
    summary: {
      total_skus: allSKUs.length,
      pricing_coverage: '100%',
      pricing_methods: {
        direct_match: stats.direct_match,
        similar_match: stats.similar_match,
        estimated: stats.estimated
      },
      confidence_distribution: stats.by_confidence,
      price_statistics: {
        min_price_brl: minPrice,
        max_price_brl: maxPrice,
        avg_price_brl: Math.round(avgPrice * 100) / 100,
        total_value_brl: Math.round(totalValue * 100) / 100
      },
      by_category: stats.by_category
    },
    products: pricedCatalog
  };
  
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(output, null, 2), 'utf-8');
  console.log(`✅ JSON criado: products-fully-priced-catalog.json (${allSKUs.length} SKUs)`);
  
  // Gerar CSV
  const csvHeaders = 'sku,category,manufacturer,power_w,capacity_kwh,price_brl,list_price_brl,cost_price_brl,supplier,source,confidence,image_url\n';
  const csvRows = pricedCatalog.map(p => 
    `"${p.sku}","${p.category || ''}","${p.manufacturer || ''}",${p.power_w || ''},${p.capacity_kwh || ''},${p.price_brl},${p.list_price_brl || ''},${p.cost_price_brl || ''},"${p.supplier}","${p.source}",${p.confidence},"${p.image_url}"`
  ).join('\n');
  
  fs.writeFileSync(OUTPUT_CSV_PATH, csvHeaders + csvRows, 'utf-8');
  console.log(`✅ CSV criado: products-fully-priced-catalog.csv (${allSKUs.length} linhas)`);
  
  // Relatório
  console.log('\n' + '═'.repeat(70));
  console.log('\n📊 RELATÓRIO DE PRECIFICAÇÃO\n');
  console.log(`   Total de SKUs: ${allSKUs.length}`);
  console.log(`   ✅ Cobertura: 100%\n`);
  
  console.log('🎯 Métodos de Precificação:\n');
  console.log(`   🎯 Match Direto.......... ${stats.direct_match.toString().padStart(4)} SKUs (${(stats.direct_match/allSKUs.length*100).toFixed(1)}%)`);
  console.log(`   🔍 Match Similar......... ${stats.similar_match.toString().padStart(4)} SKUs (${(stats.similar_match/allSKUs.length*100).toFixed(1)}%)`);
  console.log(`   📐 Estimado.............. ${stats.estimated.toString().padStart(4)} SKUs (${(stats.estimated/allSKUs.length*100).toFixed(1)}%)\n`);
  
  console.log('📊 Confiança da Precificação:\n');
  console.log(`   🟢 Alta (≥80%)........... ${stats.by_confidence.high.toString().padStart(4)} SKUs (${(stats.by_confidence.high/allSKUs.length*100).toFixed(1)}%)`);
  console.log(`   🟡 Média (50-80%)........ ${stats.by_confidence.medium.toString().padStart(4)} SKUs (${(stats.by_confidence.medium/allSKUs.length*100).toFixed(1)}%)`);
  console.log(`   🟠 Baixa (<50%).......... ${stats.by_confidence.low.toString().padStart(4)} SKUs (${(stats.by_confidence.low/allSKUs.length*100).toFixed(1)}%)\n`);
  
  console.log('💰 Estatísticas de Preços:\n');
  console.log(`   💵 Menor preço: R$ ${minPrice.toFixed(2)}`);
  console.log(`   💰 Maior preço: R$ ${maxPrice.toFixed(2)}`);
  console.log(`   📊 Preço médio: R$ ${avgPrice.toFixed(2)}`);
  console.log(`   💎 Valor total: R$ ${totalValue.toLocaleString('pt-BR', {minimumFractionDigits: 2})}\n`);
  
  console.log('📂 Por Categoria:\n');
  Object.entries(stats.by_category)
    .sort((a, b) => b[1] - a[1])
    .forEach(([cat, count]) => {
      const pct = (count/allSKUs.length*100).toFixed(1);
      console.log(`   ${cat.padEnd(25)} ${count.toString().padStart(4)} SKUs (${pct}%)`);
    });
  
  console.log('\n' + '═'.repeat(70));
  console.log('\n🔝 TOP 10 MAIS CAROS:\n');
  pricedCatalog.slice(0, 10).forEach((p, i) => {
    console.log(`   ${(i+1).toString().padStart(2)}. R$ ${p.price_brl.toLocaleString('pt-BR', {minimumFractionDigits: 2}).padStart(12)} - ${p.filename.substring(0, 45)}`);
    console.log(`       ${p.manufacturer || 'N/A'} | ${p.category} | ${p.source} (${(p.confidence*100).toFixed(0)}% confiança)`);
  });
  
  console.log('\n' + '═'.repeat(70));
  console.log('\n✨ Arquivos gerados:\n');
  console.log(`   📄 ${OUTPUT_PATH}`);
  console.log(`   📊 ${OUTPUT_CSV_PATH}\n`);
  console.log('═'.repeat(70) + '\n');
}

try {
  await ensureAllSKUsPriced();
} catch (error) {
  console.error('❌ Erro:', error.message);
  console.error(error.stack);
  process.exit(1);
}
