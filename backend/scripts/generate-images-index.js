import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PRODUCT_IMAGE_MAP_PATH = path.join(__dirname, '../static/products/product_image_map.json');
const OUTPUT_JSON_PATH = path.join(__dirname, '../static/products/imgs-index.json');
const OUTPUT_CSV_PATH = path.join(__dirname, '../static/products/imgs-index.csv');

function generateImagesIndex() {
  console.log('\n📸 Gerando índice de imagens do CDN...\n');
  console.log('═'.repeat(70));

  // Ler product_image_map.json
  const productImageMapRaw = JSON.parse(fs.readFileSync(PRODUCT_IMAGE_MAP_PATH, 'utf-8'));
  const productImageMap = productImageMapRaw.images || productImageMapRaw;

  const imagesIndex = [];
  const stats = {
    totalSkus: 0,
    totalImages: 0,
    byCategory: {},
    byManufacturer: {}
  };

  // Processar cada SKU
  for (const [sku, images] of Object.entries(productImageMap)) {
    stats.totalSkus++;

    if (!images || !Array.isArray(images) || images.length === 0) continue;

    images.forEach((image, index) => {
      stats.totalImages++;

      // Extrair fabricante do SKU ou filename
      let manufacturer = 'unknown';
      const skuUpper = sku.toUpperCase();
      
      if (skuUpper.includes('DEYE')) manufacturer = 'DEYE';
      else if (skuUpper.includes('GOODWE')) manufacturer = 'GOODWE';
      else if (skuUpper.includes('HUAWEI')) manufacturer = 'HUAWEI';
      else if (skuUpper.includes('GROWATT')) manufacturer = 'GROWATT';
      else if (skuUpper.includes('ENPHASE')) manufacturer = 'ENPHASE';
      else if (skuUpper.includes('NEOSOLAR')) manufacturer = 'NEOSOLAR';
      else if (skuUpper.includes('FOTUS')) manufacturer = 'FOTUS';
      else if (skuUpper.includes('CANADIAN')) manufacturer = 'CANADIAN SOLAR';
      else if (skuUpper.includes('JINKO')) manufacturer = 'JINKO';
      else if (skuUpper.includes('LONGI')) manufacturer = 'LONGI';
      else if (skuUpper.includes('TRINA')) manufacturer = 'TRINA';
      else if (skuUpper.includes('JA SOLAR')) manufacturer = 'JA SOLAR';
      else if (skuUpper.includes('BYD')) manufacturer = 'BYD';

      const category = image.category || 'uncategorized';

      // Atualizar estatísticas
      stats.byCategory[category] = (stats.byCategory[category] || 0) + 1;
      stats.byManufacturer[manufacturer] = (stats.byManufacturer[manufacturer] || 0) + 1;

      // Adicionar ao índice
      imagesIndex.push({
        sku,
        image_index: index,
        filename: image.filename,
        category,
        manufacturer,
        cdn_url: image.cdn_url,
        size_bytes: image.size_bytes || 0,
        format: path.extname(image.filename).substring(1).toLowerCase()
      });
    });
  }

  // Ordenar por categoria e depois por SKU
  imagesIndex.sort((a, b) => {
    if (a.category !== b.category) return a.category.localeCompare(b.category);
    return a.sku.localeCompare(b.sku);
  });

  // Gerar JSON
  const jsonOutput = {
    generated_at: new Date().toISOString(),
    summary: {
      total_skus: stats.totalSkus,
      total_images: stats.totalImages,
      by_category: stats.byCategory,
      by_manufacturer: stats.byManufacturer
    },
    images: imagesIndex
  };

  fs.writeFileSync(OUTPUT_JSON_PATH, JSON.stringify(jsonOutput, null, 2), 'utf-8');
  console.log(`✅ JSON criado: imgs-index.json (${stats.totalImages} imagens)`);

  // Gerar CSV
  const csvHeaders = 'sku,image_index,filename,category,manufacturer,cdn_url,size_bytes,format\n';
  const csvRows = imagesIndex.map(img => 
    `"${img.sku}",${img.image_index},"${img.filename}","${img.category}","${img.manufacturer}","${img.cdn_url}",${img.size_bytes},"${img.format}"`
  ).join('\n');

  fs.writeFileSync(OUTPUT_CSV_PATH, csvHeaders + csvRows, 'utf-8');
  console.log(`✅ CSV criado: imgs-index.csv (${stats.totalImages} linhas)`);

  console.log('\n' + '═'.repeat(70));
  console.log('\n📊 ESTATÍSTICAS\n');
  console.log(`   Total de SKUs: ${stats.totalSkus}`);
  console.log(`   Total de Imagens: ${stats.totalImages}\n`);

  console.log('📂 Por Categoria:\n');
  Object.entries(stats.byCategory)
    .sort((a, b) => b[1] - a[1])
    .forEach(([cat, count]) => {
      const percentage = ((count / stats.totalImages) * 100).toFixed(1);
      console.log(`   ${cat.padEnd(20)} ${count.toString().padStart(5)} (${percentage}%)`);
    });

  console.log('\n🏭 Por Fabricante:\n');
  Object.entries(stats.byManufacturer)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .forEach(([mfr, count]) => {
      const percentage = ((count / stats.totalImages) * 100).toFixed(1);
      console.log(`   ${mfr.padEnd(20)} ${count.toString().padStart(5)} (${percentage}%)`);
    });

  console.log('\n' + '═'.repeat(70));
  console.log('\n✨ Arquivos gerados:\n');
  console.log(`   📄 ${OUTPUT_JSON_PATH}`);
  console.log(`   📊 ${OUTPUT_CSV_PATH}\n`);
  console.log('═'.repeat(70) + '\n');
}

try {
  generateImagesIndex();
} catch (error) {
  console.error('❌ Erro:', error.message);
  console.error(error.stack);
  process.exit(1);
}
