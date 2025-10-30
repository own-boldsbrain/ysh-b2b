import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { glob } from 'glob';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const INVENTORY_BASE_PATH = path.join(__dirname, '../data/products-inventory');
const OUTPUT_JSON_PATH = path.join(__dirname, '../static/products/products-prices-review.json');
const OUTPUT_CSV_PATH = path.join(__dirname, '../static/products/products-prices-review.csv');

async function loadPricingData() {
  console.log('\n💰 Carregando dados de preços...\n');
  
  const patterns = [
    `${INVENTORY_BASE_PATH}/**/*.json`
  ];

  const productsWithPrices = [];
  let filesProcessed = 0;
  let totalProducts = 0;

  for (const pattern of patterns) {
    const files = await glob(pattern, { windowsPathsNoEscape: true });
    
    for (const file of files) {
      // Skip arquivos muito grandes ou problemáticos
      if (file.includes('node_modules') || 
          file.includes('backup') ||
          file.includes('neosolar-kits-parsed')) {
        continue;
      }

      try {
        const content = JSON.parse(fs.readFileSync(file, 'utf-8'));
        const products = Array.isArray(content) ? content : [content];
        
        products.forEach(product => {
          totalProducts++;
          
          // Extrair preço de diferentes campos possíveis
          const price = product.price_brl || 
                       product.price || 
                       product.preco || 
                       product.valor ||
                       product.list_price_brl ||
                       product.cost_price_brl ||
                       null;

          if (price && typeof price === 'number' && price > 0) {
            productsWithPrices.push({
              sku: product.sku || product.id || 'N/A',
              title: product.title || product.name || product.model || 'N/A',
              manufacturer: product.manufacturer || product.brand || product.fabricante || 'N/A',
              category: product.category || product.categoria || 'N/A',
              price_brl: price,
              list_price_brl: product.list_price_brl || null,
              cost_price_brl: product.cost_price_brl || null,
              supplier: product.supplier || product.distributor || product.fornecedor || 'N/A',
              model: product.model || product.modelo || null,
              power_w: product.power_w || product.power || product.potencia_w || null,
              source_file: path.basename(file),
              last_updated: product.last_updated || product.data_atualizacao || null
            });
          }
        });
        
        filesProcessed++;
      } catch (error) {
        // Ignorar erros silenciosamente
      }
    }
  }

  console.log(`   ✅ ${filesProcessed} arquivos processados`);
  console.log(`   📦 ${totalProducts} produtos analisados`);
  console.log(`   💰 ${productsWithPrices.length} produtos com preços\n`);
  
  return productsWithPrices;
}

async function generatePriceReview() {
  console.log('\n💰 Gerando revisão de preços...\n');
  console.log('═'.repeat(70));

  const productsWithPrices = await loadPricingData();

  const stats = {
    totalWithPrices: productsWithPrices.length,
    byCategory: {},
    byManufacturer: {},
    bySupplier: {},
    priceRanges: {
      under_1000: 0,
      '1000_5000': 0,
      '5000_10000': 0,
      '10000_20000': 0,
      '20000_50000': 0,
      over_50000: 0
    }
  };

  let totalPrice = 0;
  let minPrice = Infinity;
  let maxPrice = 0;

  productsWithPrices.forEach(product => {
    const price = product.price_brl;
    totalPrice += price;
    minPrice = Math.min(minPrice, price);
    maxPrice = Math.max(maxPrice, price);

    // Por categoria
    const cat = product.category || 'uncategorized';
    stats.byCategory[cat] = (stats.byCategory[cat] || 0) + 1;

    // Por fabricante
    const mfr = product.manufacturer || 'unknown';
    stats.byManufacturer[mfr] = (stats.byManufacturer[mfr] || 0) + 1;

    // Por fornecedor
    const sup = product.supplier || 'unknown';
    stats.bySupplier[sup] = (stats.bySupplier[sup] || 0) + 1;

    // Por faixa de preço
    if (price < 1000) stats.priceRanges.under_1000++;
    else if (price < 5000) stats.priceRanges['1000_5000']++;
    else if (price < 10000) stats.priceRanges['5000_10000']++;
    else if (price < 20000) stats.priceRanges['10000_20000']++;
    else if (price < 50000) stats.priceRanges['20000_50000']++;
    else stats.priceRanges.over_50000++;
  });

  const avgPrice = totalPrice / productsWithPrices.length;

  // Ordenar por preço
  productsWithPrices.sort((a, b) => b.price_brl - a.price_brl);

  // Gerar JSON
  const jsonOutput = {
    generated_at: new Date().toISOString(),
    summary: {
      total_products_with_prices: stats.totalWithPrices,
      price_statistics: {
        min_price_brl: minPrice,
        max_price_brl: maxPrice,
        avg_price_brl: Math.round(avgPrice * 100) / 100,
        total_value_brl: Math.round(totalPrice * 100) / 100
      },
      by_category: stats.byCategory,
      by_manufacturer: stats.byManufacturer,
      by_supplier: stats.bySupplier,
      by_price_range: stats.priceRanges
    },
    products: productsWithPrices
  };

  fs.writeFileSync(OUTPUT_JSON_PATH, JSON.stringify(jsonOutput, null, 2), 'utf-8');
  console.log(`✅ JSON criado: products-prices-review.json (${stats.totalWithPrices} produtos)`);

  // Gerar CSV
  const csvHeaders = 'sku,title,manufacturer,category,price_brl,list_price_brl,cost_price_brl,supplier,model,power_w,source_file\n';
  const csvRows = productsWithPrices.map(p => 
    `"${p.sku}","${p.title}","${p.manufacturer}","${p.category}",${p.price_brl},${p.list_price_brl || ''},${p.cost_price_brl || ''},"${p.supplier}","${p.model || ''}",${p.power_w || ''},"${p.source_file}"`
  ).join('\n');

  fs.writeFileSync(OUTPUT_CSV_PATH, csvHeaders + csvRows, 'utf-8');
  console.log(`✅ CSV criado: products-prices-review.csv (${stats.totalWithPrices} linhas)`);

  console.log('\n' + '═'.repeat(70));
  console.log('\n📊 ANÁLISE DE PREÇOS\n');
  console.log(`   Total com preços: ${stats.totalWithPrices}`);
  console.log(`   💵 Menor preço: R$ ${minPrice.toFixed(2)}`);
  console.log(`   💰 Maior preço: R$ ${maxPrice.toFixed(2)}`);
  console.log(`   📊 Preço médio: R$ ${avgPrice.toFixed(2)}`);
  console.log(`   💎 Valor total: R$ ${totalPrice.toLocaleString('pt-BR', {minimumFractionDigits: 2})}\n`);

  console.log('📂 Por Categoria (Top 10):\n');
  Object.entries(stats.byCategory)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .forEach(([cat, count]) => {
      console.log(`   ${cat.padEnd(25)} ${count.toString().padStart(4)} produtos`);
    });

  console.log('\n🏭 Por Fabricante (Top 10):\n');
  Object.entries(stats.byManufacturer)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .forEach(([mfr, count]) => {
      console.log(`   ${mfr.padEnd(25)} ${count.toString().padStart(4)} produtos`);
    });

  console.log('\n🏪 Por Fornecedor:\n');
  Object.entries(stats.bySupplier)
    .sort((a, b) => b[1] - a[1])
    .forEach(([sup, count]) => {
      console.log(`   ${sup.padEnd(25)} ${count.toString().padStart(4)} produtos`);
    });

  console.log('\n💵 Faixas de Preço:\n');
  console.log(`   Até R$ 1.000............ ${stats.priceRanges.under_1000} produtos`);
  console.log(`   R$ 1.000 - R$ 5.000..... ${stats.priceRanges['1000_5000']} produtos`);
  console.log(`   R$ 5.000 - R$ 10.000.... ${stats.priceRanges['5000_10000']} produtos`);
  console.log(`   R$ 10.000 - R$ 20.000... ${stats.priceRanges['10000_20000']} produtos`);
  console.log(`   R$ 20.000 - R$ 50.000... ${stats.priceRanges['20000_50000']} produtos`);
  console.log(`   Acima de R$ 50.000...... ${stats.priceRanges.over_50000} produtos`);

  console.log('\n' + '═'.repeat(70));
  console.log('\n🔝 TOP 10 MAIS CAROS:\n');
  productsWithPrices.slice(0, 10).forEach((p, i) => {
    console.log(`   ${(i+1).toString().padStart(2)}. R$ ${p.price_brl.toLocaleString('pt-BR', {minimumFractionDigits: 2}).padStart(12)} - ${p.title.substring(0, 45)}`);
    console.log(`       ${p.manufacturer} | ${p.category} | ${p.supplier}`);
  });

  console.log('\n' + '═'.repeat(70));
  console.log('\n🔽 TOP 10 MAIS BARATOS:\n');
  productsWithPrices.slice(-10).reverse().forEach((p, i) => {
    console.log(`   ${(i+1).toString().padStart(2)}. R$ ${p.price_brl.toLocaleString('pt-BR', {minimumFractionDigits: 2}).padStart(12)} - ${p.title.substring(0, 45)}`);
    console.log(`       ${p.manufacturer} | ${p.category} | ${p.supplier}`);
  });

  console.log('\n' + '═'.repeat(70));
  console.log('\n✨ Arquivos gerados:\n');
  console.log(`   📄 ${OUTPUT_JSON_PATH}`);
  console.log(`   📊 ${OUTPUT_CSV_PATH}\n`);
  console.log('═'.repeat(70) + '\n');
}

try {
  await generatePriceReview();
} catch (error) {
  console.error('❌ Erro:', error.message);
  console.error(error.stack);
  process.exit(1);
}
