import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { glob } from 'glob';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PRODUCT_IMAGE_MAP_PATH = path.join(__dirname, '../static/products/product_image_map.json');
const INVENTORY_BASE_PATH = path.join(__dirname, '../data/products-inventory');
const OUTPUT_JSON_PATH = path.join(__dirname, '../static/products/products-detailed-catalog.json');
const OUTPUT_CSV_PATH = path.join(__dirname, '../static/products/products-detailed-catalog.csv');

async function loadInventoryFiles() {
  console.log('\n📦 Carregando arquivos de inventário...\n');
  
  const patterns = [
    `${INVENTORY_BASE_PATH}/examples/**/*.json`,
    `${INVENTORY_BASE_PATH}/distributors/**/*.json`,
    `${INVENTORY_BASE_PATH}/exports/**/*.json`
  ];

  const allProducts = [];
  let filesLoaded = 0;

  for (const pattern of patterns) {
    const files = await glob(pattern, { windowsPathsNoEscape: true });
    
    for (const file of files) {
      try {
        const content = JSON.parse(fs.readFileSync(file, 'utf-8'));
        const products = Array.isArray(content) ? content : [content];
        
        products.forEach(product => {
          if (product.sku) {
            allProducts.push({
              ...product,
              source_file: path.basename(file)
            });
          }
        });
        
        filesLoaded++;
      } catch (error) {
        console.log(`   ⚠️  Ignorando ${path.basename(file)}: ${error.message}`);
      }
    }
  }

  console.log(`   ✅ ${filesLoaded} arquivos carregados`);
  console.log(`   📦 ${allProducts.length} produtos encontrados\n`);
  
  return allProducts;
}

async function generateDetailedCatalog() {
  console.log('\n🔧 Gerando catálogo detalhado de produtos...\n');
  console.log('═'.repeat(70));

  // Carregar product_image_map.json
  const productImageMapRaw = JSON.parse(fs.readFileSync(PRODUCT_IMAGE_MAP_PATH, 'utf-8'));
  const productImageMap = productImageMapRaw.images || productImageMapRaw;

  // Carregar inventário de produtos
  const inventoryProducts = await loadInventoryFiles();
  
  // Criar mapa de inventário por SKU
  const inventoryMap = {};
  inventoryProducts.forEach(product => {
    const sku = product.sku.toUpperCase().replace(/[^A-Z0-9]/g, '');
    inventoryMap[sku] = product;
  });

  const detailedCatalog = [];
  const stats = {
    totalSkus: 0,
    withInventoryData: 0,
    withoutInventoryData: 0,
    withImages: 0,
    withPricing: 0,
    byCategory: {},
    byManufacturer: {}
  };

  // Processar cada SKU do product_image_map
  for (const [sku, images] of Object.entries(productImageMap)) {
    stats.totalSkus++;

    // Tentar múltiplas estratégias de matching
    const normalizedSku = sku.toUpperCase().replace(/[^A-Z0-9]/g, '');
    let inventoryData = inventoryMap[normalizedSku] || 
                       inventoryMap[sku] || 
                       inventoryMap[sku.toUpperCase()] || {};
    
    const hasInventoryData = Object.keys(inventoryData).length > 1; // Mais que apenas source_file

    if (hasInventoryData) {
      stats.withInventoryData++;
    } else {
      stats.withoutInventoryData++;
    }

    const imageData = (images && Array.isArray(images) && images.length > 0) ? images[0] : {};
    const hasImages = !!imageData.cdn_url;
    
    if (hasImages) stats.withImages++;
    if (inventoryData.price_brl || inventoryData.price) stats.withPricing++;

    const category = imageData.category || inventoryData.category || 'uncategorized';
    const manufacturer = inventoryData.manufacturer || 
                        inventoryData.brand || 
                        (sku.includes('DEYE') ? 'DEYE' : 
                         sku.includes('GOODWE') ? 'GOODWE' :
                         sku.includes('HUAWEI') ? 'HUAWEI' :
                         sku.includes('GROWATT') ? 'GROWATT' :
                         sku.includes('ENPHASE') ? 'ENPHASE' :
                         sku.includes('NEOSOLAR') ? 'NEOSOLAR' :
                         sku.includes('FOTUS') ? 'FOTUS' : 'unknown');

    stats.byCategory[category] = (stats.byCategory[category] || 0) + 1;
    stats.byManufacturer[manufacturer] = (stats.byManufacturer[manufacturer] || 0) + 1;

    // Compilar dados completos do produto
    const productDetail = {
      // Identificação
      sku: sku,
      manufacturer: manufacturer,
      model: inventoryData.model || inventoryData.name || null,
      title: inventoryData.title || inventoryData.name || null,
      description: inventoryData.description || null,
      category: category,
      
      // Imagens
      image_url: imageData.cdn_url || null,
      image_count: (images && Array.isArray(images)) ? images.length : 0,
      all_image_urls: (images && Array.isArray(images)) ? images.map(img => img.cdn_url) : [],
      
      // Preços
      price_brl: inventoryData.price_brl || inventoryData.price || null,
      list_price_brl: inventoryData.list_price_brl || inventoryData.list_price || null,
      cost_price_brl: inventoryData.cost_price_brl || inventoryData.cost_price || null,
      
      // Especificações técnicas (para inversores)
      power_w: inventoryData.power_w || inventoryData.power || inventoryData.potencia_w || null,
      voltage_v: inventoryData.voltage_v || inventoryData.voltage || inventoryData.tensao_v || null,
      efficiency_percent: inventoryData.efficiency_percent || inventoryData.efficiency || null,
      
      // Especificações técnicas (para painéis)
      capacity_w: inventoryData.capacity_w || inventoryData.potencia || null,
      cell_type: inventoryData.cell_type || inventoryData.tecnologia || null,
      
      // Especificações técnicas (para baterias)
      capacity_kwh: inventoryData.capacity_kwh || inventoryData.capacidade_kwh || null,
      technology: inventoryData.technology || inventoryData.tecnologia || null,
      cycle_life: inventoryData.cycle_life || inventoryData.ciclos || null,
      
      // Dimensões e peso
      weight_kg: inventoryData.weight_kg || inventoryData.peso_kg || null,
      dimensions_mm: inventoryData.dimensions_mm || inventoryData.dimensoes || null,
      
      // Certificações e garantia
      certifications: inventoryData.certifications || inventoryData.certificacoes || [],
      warranty_years: inventoryData.warranty_years || inventoryData.garantia_anos || null,
      
      // Metadados
      in_stock: inventoryData.in_stock !== undefined ? inventoryData.in_stock : null,
      stock_quantity: inventoryData.stock_quantity || inventoryData.estoque || null,
      supplier: inventoryData.supplier || inventoryData.fornecedor || null,
      source_file: inventoryData.source_file || null,
      has_complete_data: hasInventoryData,
      last_updated: inventoryData.last_updated || inventoryData.data_atualizacao || null
    };

    detailedCatalog.push(productDetail);
  }

  // Ordenar por categoria e depois por SKU
  detailedCatalog.sort((a, b) => {
    if (a.category !== b.category) return a.category.localeCompare(b.category);
    return a.sku.localeCompare(b.sku);
  });

  // Gerar JSON
  const jsonOutput = {
    generated_at: new Date().toISOString(),
    summary: {
      total_products: stats.totalSkus,
      with_inventory_data: stats.withInventoryData,
      without_inventory_data: stats.withoutInventoryData,
      with_images: stats.withImages,
      with_pricing: stats.withPricing,
      coverage_percent: {
        inventory: ((stats.withInventoryData / stats.totalSkus) * 100).toFixed(1),
        images: ((stats.withImages / stats.totalSkus) * 100).toFixed(1),
        pricing: ((stats.withPricing / stats.totalSkus) * 100).toFixed(1)
      },
      by_category: stats.byCategory,
      by_manufacturer: stats.byManufacturer
    },
    products: detailedCatalog
  };

  fs.writeFileSync(OUTPUT_JSON_PATH, JSON.stringify(jsonOutput, null, 2), 'utf-8');
  console.log(`✅ JSON criado: products-detailed-catalog.json (${stats.totalSkus} produtos)`);

  // Gerar CSV
  const csvHeaders = 'sku,manufacturer,model,title,category,image_url,price_brl,power_w,capacity_w,capacity_kwh,voltage_v,weight_kg,warranty_years,in_stock,has_complete_data,source_file\n';
  const csvRows = detailedCatalog.map(p => 
    `"${p.sku}","${p.manufacturer}","${p.model || ''}","${p.title || ''}","${p.category}","${p.image_url || ''}",${p.price_brl || ''},${p.power_w || ''},${p.capacity_w || ''},${p.capacity_kwh || ''},${p.voltage_v || ''},${p.weight_kg || ''},${p.warranty_years || ''},${p.in_stock !== null ? p.in_stock : ''},${p.has_complete_data},"${p.source_file || ''}"`
  ).join('\n');

  fs.writeFileSync(OUTPUT_CSV_PATH, csvHeaders + csvRows, 'utf-8');
  console.log(`✅ CSV criado: products-detailed-catalog.csv (${stats.totalSkus} linhas)`);

  console.log('\n' + '═'.repeat(70));
  console.log('\n📊 ESTATÍSTICAS DO CATÁLOGO\n');
  console.log(`   Total de Produtos: ${stats.totalSkus}`);
  console.log(`   ✅ Com dados de inventário: ${stats.withInventoryData} (${jsonOutput.summary.coverage_percent.inventory}%)`);
  console.log(`   📸 Com imagens: ${stats.withImages} (${jsonOutput.summary.coverage_percent.images}%)`);
  console.log(`   💰 Com preços: ${stats.withPricing} (${jsonOutput.summary.coverage_percent.pricing}%)`);
  console.log(`   ⚠️  Sem dados completos: ${stats.withoutInventoryData}\n`);

  console.log('📂 Por Categoria (Top 10):\n');
  Object.entries(stats.byCategory)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .forEach(([cat, count]) => {
      const percentage = ((count / stats.totalSkus) * 100).toFixed(1);
      console.log(`   ${cat.padEnd(25)} ${count.toString().padStart(4)} (${percentage}%)`);
    });

  console.log('\n🏭 Por Fabricante (Top 10):\n');
  Object.entries(stats.byManufacturer)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .forEach(([mfr, count]) => {
      const percentage = ((count / stats.totalSkus) * 100).toFixed(1);
      console.log(`   ${mfr.padEnd(25)} ${count.toString().padStart(4)} (${percentage}%)`);
    });

  console.log('\n' + '═'.repeat(70));
  console.log('\n✨ Arquivos gerados:\n');
  console.log(`   📄 ${OUTPUT_JSON_PATH}`);
  console.log(`   📊 ${OUTPUT_CSV_PATH}\n`);
  console.log('═'.repeat(70) + '\n');
}

try {
  await generateDetailedCatalog();
} catch (error) {
  console.error('❌ Erro:', error.message);
  console.error(error.stack);
  process.exit(1);
}
