const fs = require('node:fs');

const syncedFile = 'enriched-skus-for-dynamodb-images-fixed.json';
const data = JSON.parse(fs.readFileSync(syncedFile, 'utf8'));

const categories = {};
let totalWithImages = 0;
let totalWithoutImages = 0;

for (const item of data) {
  const category = item.category || 'sem_categoria';
  if (!categories[category]) {
    categories[category] = { withImages: 0, withoutImages: 0, examples: [] };
  }
  
  const hasImages = item.images && Array.isArray(item.images) && item.images.length > 0;
  
  if (hasImages) {
    categories[category].withImages++;
    totalWithImages++;
    if (categories[category].examples.length < 2) {
      categories[category].examples.push({
        sku: item.sku,
        category: item.category,
        cost_price: item.cost_price,
        final_price: item.final_price,
        images: item.images,
        kpis: item.kpis,
        technical_specs: item.technical_specs
      });
    }
  } else {
    categories[category].withoutImages++;
    totalWithoutImages++;
  }
}

console.log('\n=== ESTATÍSTICAS DE IMAGENS ===\n');
console.log(`Total de produtos: ${data.length}`);
console.log(`Com imagens: ${totalWithImages}`);
console.log(`Sem imagens: ${totalWithoutImages}`);
console.log('\n=== POR CATEGORIA ===\n');

for (const [cat, stats] of Object.entries(categories)) {
  console.log(`${cat}: ${stats.withImages} com imagens, ${stats.withoutImages} sem imagens`);
}

console.log('\n=== EXEMPLOS COM IMAGENS ===\n');
const result = {};
for (const [cat, stats] of Object.entries(categories)) {
  if (stats.examples.length > 0) {
    result[cat] = stats.examples;
  }
}

console.log(JSON.stringify(result, null, 2));
