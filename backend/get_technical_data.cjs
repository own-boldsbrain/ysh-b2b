const { execSync } = require('child_process');

// Função para executar comando AWS CLI
function runAws(command) {
  try {
    return execSync(command, { encoding: 'utf8' });
  } catch (error) {
    console.error('Erro no comando:', command, error.message);
    return null;
  }
}

// Obter alguns itens do DynamoDB e filtrar por categoria
console.log('Obtendo itens do DynamoDB...');
const scanResult = runAws('aws dynamodb scan --table-name ysh-products-catalog --region us-east-1 --max-items 50 --output json');

if (!scanResult) {
  console.error('Falha ao fazer scan do DynamoDB');
  process.exit(1);
}

let items;
try {
  const parsed = JSON.parse(scanResult);
  items = parsed.Items;
} catch (e) {
  console.error('Erro ao parsear resultado do scan:', e.message);
  process.exit(1);
}

console.log(`Encontrados ${items.length} itens no DynamoDB`);

// Agrupar por categoria
const categories = ['kits', 'componentes', 'paineis', 'estrutura'];
const itemsByCategory = {};

categories.forEach(cat => {
  itemsByCategory[cat] = items.filter(item => item.category && item.category.S === cat).slice(0, 3);
  console.log(`Categoria ${cat}: ${itemsByCategory[cat].length} itens`);
});

// Extrair dados técnicos
const technicalData = {};
Object.keys(itemsByCategory).forEach(cat => {
  technicalData[cat] = itemsByCategory[cat].map(item => ({
    sku: item.sku.S,
    category: cat,
    cost_price: item.cost_price ? parseFloat(item.cost_price.N) : null,
    final_price: item.final_price ? parseFloat(item.final_price.N) : null,
    images: item.images ? item.images.L.map(img => img.S) : [],
    enriched_at: item.enriched_at ? item.enriched_at.S : null,
    kpis: item.kpis ? {
      gross_margin_percent: parseFloat(item.kpis.M.gross_margin_percent.N),
      net_margin_percent: parseFloat(item.kpis.M.net_margin_percent.N),
      selling_price: parseFloat(item.kpis.M.selling_price.N),
      markup_applied: parseFloat(item.kpis.M.markup_applied.N)
    } : null
  }));
});

console.log('=== DADOS TÉCNICOS POR CATEGORIA ===');
console.log(JSON.stringify(technicalData, null, 2));