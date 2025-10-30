import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PRODUCT_IMAGE_MAP_PATH = path.join(__dirname, '../static/products/product_image_map.json');
const OUTPUT_JSON_PATH = path.join(__dirname, '../static/products/sku-images-sync.json');
const OUTPUT_CSV_PATH = path.join(__dirname, '../static/products/sku-images-sync.csv');

function generateSkuSyncReport() {
  console.log('\n🔗 Gerando relatório de sincronização SKU → URLs...\n');
  console.log('═'.repeat(70));

  // Ler product_image_map.json
  const productImageMapRaw = JSON.parse(fs.readFileSync(PRODUCT_IMAGE_MAP_PATH, 'utf-8'));
  const productImageMap = productImageMapRaw.images || productImageMapRaw;

  const skuSyncData = [];
  const stats = {
    totalSkus: 0,
    skusWithImages: 0,
    skusWithoutImages: 0,
    totalUrls: 0,
    skusWithMultipleImages: 0,
    byCategory: {},
    byImageCount: {}
  };

  // Processar cada SKU
  for (const [sku, images] of Object.entries(productImageMap)) {
    stats.totalSkus++;

    if (!images || !Array.isArray(images) || images.length === 0) {
      stats.skusWithoutImages++;
      skuSyncData.push({
        sku,
        has_images: false,
        image_count: 0,
        primary_url: null,
        all_urls: [],
        categories: [],
        total_size_bytes: 0
      });
      continue;
    }

    stats.skusWithImages++;
    stats.totalUrls += images.length;

    if (images.length > 1) {
      stats.skusWithMultipleImages++;
    }

    // Extrair informações do SKU
    const categories = [...new Set(images.map(img => img.category || 'uncategorized'))];
    const allUrls = images.map(img => img.cdn_url);
    const totalSize = images.reduce((sum, img) => sum + (img.size_bytes || 0), 0);

    // Atualizar estatísticas por categoria
    categories.forEach(cat => {
      stats.byCategory[cat] = (stats.byCategory[cat] || 0) + 1;
    });

    // Atualizar estatísticas por número de imagens
    const imageCount = images.length;
    stats.byImageCount[imageCount] = (stats.byImageCount[imageCount] || 0) + 1;

    // Adicionar ao relatório
    skuSyncData.push({
      sku,
      has_images: true,
      image_count: imageCount,
      primary_url: allUrls[0],
      all_urls: allUrls,
      categories: categories,
      total_size_bytes: totalSize,
      formats: [...new Set(images.map(img => path.extname(img.filename).substring(1).toLowerCase()))]
    });
  }

  // Ordenar por SKU
  skuSyncData.sort((a, b) => a.sku.localeCompare(b.sku));

  // Gerar JSON
  const jsonOutput = {
    generated_at: new Date().toISOString(),
    summary: {
      total_skus: stats.totalSkus,
      skus_with_images: stats.skusWithImages,
      skus_without_images: stats.skusWithoutImages,
      total_image_urls: stats.totalUrls,
      skus_with_multiple_images: stats.skusWithMultipleImages,
      avg_images_per_sku: (stats.totalUrls / stats.skusWithImages).toFixed(2),
      by_category: stats.byCategory,
      by_image_count: stats.byImageCount
    },
    skus: skuSyncData
  };

  fs.writeFileSync(OUTPUT_JSON_PATH, JSON.stringify(jsonOutput, null, 2), 'utf-8');
  console.log(`✅ JSON criado: sku-images-sync.json (${stats.totalSkus} SKUs)`);

  // Gerar CSV
  const csvHeaders = 'sku,has_images,image_count,primary_url,all_urls,categories,total_size_bytes,formats\n';
  const csvRows = skuSyncData.map(item => {
    const allUrlsStr = item.all_urls.join('|');
    const categoriesStr = item.categories.join('|');
    const formatsStr = (item.formats || []).join('|');
    return `"${item.sku}",${item.has_images},${item.image_count},"${item.primary_url || ''}","${allUrlsStr}","${categoriesStr}",${item.total_size_bytes},"${formatsStr}"`;
  }).join('\n');

  fs.writeFileSync(OUTPUT_CSV_PATH, csvHeaders + csvRows, 'utf-8');
  console.log(`✅ CSV criado: sku-images-sync.csv (${stats.totalSkus} linhas)`);

  console.log('\n' + '═'.repeat(70));
  console.log('\n📊 ESTATÍSTICAS DE SINCRONIZAÇÃO\n');
  console.log(`   Total de SKUs: ${stats.totalSkus}`);
  console.log(`   ✅ Com imagens: ${stats.skusWithImages} (${((stats.skusWithImages/stats.totalSkus)*100).toFixed(1)}%)`);
  console.log(`   ❌ Sem imagens: ${stats.skusWithoutImages} (${((stats.skusWithoutImages/stats.totalSkus)*100).toFixed(1)}%)`);
  console.log(`   🔗 Total de URLs: ${stats.totalUrls}`);
  console.log(`   📦 SKUs com múltiplas imagens: ${stats.skusWithMultipleImages}`);
  console.log(`   📊 Média de imagens por SKU: ${(stats.totalUrls / stats.skusWithImages).toFixed(2)}\n`);

  console.log('📂 SKUs por Categoria:\n');
  Object.entries(stats.byCategory)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .forEach(([cat, count]) => {
      const percentage = ((count / stats.skusWithImages) * 100).toFixed(1);
      console.log(`   ${cat.padEnd(20)} ${count.toString().padStart(5)} SKUs (${percentage}%)`);
    });

  console.log('\n📸 Distribuição por Quantidade de Imagens:\n');
  Object.entries(stats.byImageCount)
    .sort((a, b) => parseInt(a[0]) - parseInt(b[0]))
    .forEach(([count, skus]) => {
      const label = count === '1' ? '1 imagem' : `${count} imagens`;
      console.log(`   ${label.padEnd(20)} ${skus.toString().padStart(5)} SKUs`);
    });

  console.log('\n' + '═'.repeat(70));
  console.log('\n✨ Arquivos gerados:\n');
  console.log(`   📄 ${OUTPUT_JSON_PATH}`);
  console.log(`   📊 ${OUTPUT_CSV_PATH}\n`);
  console.log('💡 Campos CSV:\n');
  console.log('   • sku: Código do produto');
  console.log('   • has_images: true/false');
  console.log('   • image_count: Quantidade de imagens');
  console.log('   • primary_url: URL principal (primeira imagem)');
  console.log('   • all_urls: Todas as URLs separadas por |');
  console.log('   • categories: Categorias separadas por |');
  console.log('   • total_size_bytes: Tamanho total em bytes');
  console.log('   • formats: Formatos de imagem (jpg|png|webp)\n');
  console.log('═'.repeat(70) + '\n');
}

try {
  generateSkuSyncReport();
} catch (error) {
  console.error('❌ Erro:', error.message);
  console.error(error.stack);
  process.exit(1);
}
