import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const catalogFile = join(__dirname, '..', 'static', 'products', 'products-fully-priced-catalog.json');
const data = JSON.parse(fs.readFileSync(catalogFile, 'utf8'));
const products = data.products;

console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('📋 DIAGNÓSTICO COMPLETO DO CATÁLOGO YELLO SOLAR HUB');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

// === NÚMEROS TOTAIS ===
console.log('📊 NÚMEROS TOTAIS');
console.log(`- Total SKUs no catálogo: ${data.summary.total_skus}`);
console.log(`- Cobertura de preços: ${data.summary.pricing_coverage}`);
console.log(`- Valor total em estoque: R$ ${data.summary.price_statistics.total_value_brl.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);

// === ESTATÍSTICAS DE PREÇO ===
console.log('\n💰 ESTATÍSTICAS DE PREÇO');
console.log(`- Mínimo: R$ ${data.summary.price_statistics.min_price_brl.toLocaleString('pt-BR')}`);
console.log(`- Máximo: R$ ${data.summary.price_statistics.max_price_brl.toLocaleString('pt-BR')}`);
console.log(`- Média: R$ ${data.summary.price_statistics.avg_price_brl.toLocaleString('pt-BR', {minimumFractionDigits: 2})}`);

// === MÉTODOS DE PRECIFICAÇÃO ===
console.log('\n🎯 MÉTODOS DE PRECIFICAÇÃO');
const directPct = ((data.summary.pricing_methods.direct_match / data.summary.total_skus) * 100).toFixed(1);
const similarPct = ((data.summary.pricing_methods.similar_match / data.summary.total_skus) * 100).toFixed(1);
const estimatedPct = ((data.summary.pricing_methods.estimated / data.summary.total_skus) * 100).toFixed(1);
console.log(`- Match direto: ${data.summary.pricing_methods.direct_match} (${directPct}%)`);
console.log(`- Similar: ${data.summary.pricing_methods.similar_match} (${similarPct}%)`);
console.log(`- Estimado: ${data.summary.pricing_methods.estimated} (${estimatedPct}%)`);

// === TOP CATEGORIAS ===
console.log('\n📁 TOP 10 CATEGORIAS');
const categories = Object.entries(data.summary.by_category)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 10);
categories.forEach(([cat, count]) => {
  console.log(`  ${cat.padEnd(25)} ${count.toString().padStart(4)} produtos`);
});

// === ANÁLISE DE QUALIDADE ===
console.log('\n🔍 ANÁLISE DE QUALIDADE DOS DADOS');

let semImagem = 0;
let semPotencia = 0;
let semFabricante = 0;
let skuInvalido = 0;
let precoZero = 0;
let precoEstimado = 0;
let urlInvalida = 0;

const problemasPorProduto = [];

products.forEach(p => {
  const problemas = [];
  
  // Validar imagem
  if (!p.image_url || !p.cdn_published) {
    semImagem++;
    problemas.push('sem_imagem');
  }
  
  if (p.image_url && !p.image_url.startsWith('https://cdn.yellosolarhub.com')) {
    urlInvalida++;
    problemas.push('url_invalida');
  }
  
  // Validar potência por categoria
  if (p.category === 'inversores' && !p.power_kw && !p.power_w) {
    semPotencia++;
    problemas.push('sem_potencia_inversor');
  }
  if (p.category === 'kits' && !p.power_kwp) {
    semPotencia++;
    problemas.push('sem_potencia_kit');
  }
  if (p.category === 'paineis' && !p.power_w) {
    semPotencia++;
    problemas.push('sem_potencia_painel');
  }
  
  // Validar fabricante
  if (!p.manufacturer || p.manufacturer === 'UNKNOWN-MANUFACTURER') {
    semFabricante++;
    problemas.push('sem_fabricante');
  }
  
  // Validar SKU
  if (!p.sku || p.sku.length < 3) {
    skuInvalido++;
    problemas.push('sku_invalido');
  }
  
  // Validar preço
  if (p.price_brl <= 0) {
    precoZero++;
    problemas.push('preco_zero');
  }
  
  if (p.price_source === 'estimated') {
    precoEstimado++;
  }
  
  if (problemas.length > 0) {
    problemasPorProduto.push({
      sku: p.sku,
      category: p.category,
      problemas
    });
  }
});

console.log('\n❌ PROBLEMAS CRÍTICOS:');
console.log(`- Sem imagem CDN: ${semImagem} (${(semImagem/products.length*100).toFixed(1)}%)`);
console.log(`- Sem potência crítica: ${semPotencia} (${(semPotencia/products.length*100).toFixed(1)}%)`);
console.log(`- Sem fabricante: ${semFabricante} (${(semFabricante/products.length*100).toFixed(1)}%)`);
console.log(`- SKU inválido: ${skuInvalido}`);
console.log(`- Preço zero/negativo: ${precoZero}`);
console.log(`- URL inválida (fora CDN): ${urlInvalida}`);

console.log('\n⚠️  ALERTAS:');
console.log(`- Preços estimados: ${precoEstimado} (${(precoEstimado/products.length*100).toFixed(1)}%)`);

const taxaQualidade = ((products.length - semImagem - semPotencia - semFabricante) / products.length * 100).toFixed(1);
console.log(`\n✅ Taxa de Qualidade Geral: ${taxaQualidade}%`);

// === COMPARAÇÃO: CATÁLOGO vs DEPLOYMENT RDS ===
console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('📊 COMPARAÇÃO: CATÁLOGO vs DEPLOYMENT RDS');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

const catalogTotal = data.summary.total_skus;
const rdsDeployed = 574; // Do último import bem-sucedido
const rdsFailed = 564;

console.log(`📦 Catálogo CDN:     ${catalogTotal} produtos`);
console.log(`✅ RDS Deployed:     ${rdsDeployed} produtos (${((rdsDeployed/catalogTotal)*100).toFixed(1)}%)`);
console.log(`❌ Falha no Import:  ${rdsFailed} produtos (${((rdsFailed/catalogTotal)*100).toFixed(1)}%)`);
console.log(`🚫 Não processados:  ${catalogTotal - rdsDeployed - rdsFailed} produtos`);

// === ANÁLISE DOS TOP 5 PROBLEMAS ===
console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('🔧 TOP 5 PRODUTOS COM MAIS PROBLEMAS');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

const topProblematicos = problemasPorProduto
  .sort((a, b) => b.problemas.length - a.problemas.length)
  .slice(0, 5);

topProblematicos.forEach((p, i) => {
  console.log(`${i + 1}. SKU: ${p.sku}`);
  console.log(`   Categoria: ${p.category}`);
  console.log(`   Problemas: ${p.problemas.join(', ')}`);
  console.log('');
});

// === RECOMENDAÇÕES ===
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('💡 RECOMENDAÇÕES PRIORITÁRIAS');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

console.log('🔴 ALTA PRIORIDADE:');
if (semImagem > 0) {
  console.log(`  1. Resolver ${semImagem} produtos sem imagem na CDN`);
}
if (semPotencia > 0) {
  console.log(`  2. Completar potência de ${semPotencia} produtos críticos`);
}
if (precoEstimado > 1000) {
  console.log(`  3. Atualizar ${precoEstimado} preços estimados para reais`);
}

console.log('\n🟡 MÉDIA PRIORIDADE:');
if (semFabricante > 50) {
  console.log(`  1. Identificar fabricante de ${semFabricante} produtos`);
}
if (urlInvalida > 0) {
  console.log(`  2. Corrigir ${urlInvalida} URLs fora da CDN`);
}

console.log('\n🟢 BAIXA PRIORIDADE:');
console.log('  1. Normalizar padrão de SKUs (formato único)');
console.log('  2. Adicionar campos opcionais (warranty, specs técnicas)');
console.log('  3. Implementar sistema de tags/busca full-text');

console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('📈 PRÓXIMOS PASSOS DEPLOYMENT');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

console.log('1. Corrigir 564 produtos com erro check_kit_structure');
console.log('   - Validar structure_type antes do import');
console.log('   - Adicionar valores padrão para kits sem estrutura');
console.log('');
console.log('2. Re-importar produtos corrigidos');
console.log(`   - Alvo: ${catalogTotal} produtos (100%)`);
console.log('   - Atual: 574 produtos (50.4%)');
console.log('   - Gap: 564 produtos a corrigir');
console.log('');
console.log('3. Validar integração API ← → RDS ← → CDN');
console.log('   - Backend servindo catálogo via /store/catalog/skus');
console.log('   - Imagens carregando de cdn.yellosolarhub.com');
console.log('   - Widgets renderizando produtos corretamente');
