import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const prices = JSON.parse(fs.readFileSync(path.join(__dirname, '../static/products/products-prices-review.json'), 'utf-8'));

const kits = prices.products
  .filter(p => p.title.toLowerCase().includes('kit') && p.price_brl > 0)
  .sort((a, b) => b.price_brl - a.price_brl);

console.log('\n📦 TOP 10 KITS MAIS CAROS NO INVENTÁRIO:\n');
kits.slice(0, 10).forEach((k, i) => {
  console.log(`${i+1}. R$ ${k.price_brl.toLocaleString('pt-BR', {minimumFractionDigits: 2})} - ${k.title.substring(0, 70)}`);
});

console.log('\n\n📦 TOP 10 KITS MAIS BARATOS NO INVENTÁRIO:\n');
kits.slice(-10).reverse().forEach((k, i) => {
  console.log(`${i+1}. R$ ${k.price_brl.toLocaleString('pt-BR', {minimumFractionDigits: 2})} - ${k.title.substring(0, 70)}`);
});

// Calcular R$/kWp médio
const kitsWithPower = kits.filter(k => {
  const match = k.title.match(/(\d+(?:\.\d+)?)\s*kWp/i);
  if (match) {
    k.kwp = parseFloat(match[1]);
    if (k.kwp > 0) {
      k.price_per_kwp = k.price_brl / k.kwp;
      return true;
    }
  }
  return false;
});

if (kitsWithPower.length > 0) {
  const validPrices = kitsWithPower.filter(k => k.price_per_kwp > 0 && k.price_per_kwp < 50000);
  const avgPricePerKwp = validPrices.reduce((sum, k) => sum + k.price_per_kwp, 0) / validPrices.length;
  const minPricePerKwp = Math.min(...validPrices.map(k => k.price_per_kwp));
  const maxPricePerKwp = Math.max(...validPrices.map(k => k.price_per_kwp));
  
  console.log(`\n\n💡 Análise de Preço por kWp:\n`);
  console.log(`   Mínimo: R$ ${minPricePerKwp.toFixed(2)}/kWp`);
  console.log(`   Máximo: R$ ${maxPricePerKwp.toFixed(2)}/kWp`);
  console.log(`   Médio: R$ ${avgPricePerKwp.toFixed(2)}/kWp`);
  console.log(`   (baseado em ${validPrices.length} kits válidos)\n`);
  
  // Exemplos reais
  console.log('📋 Exemplos de Kits Reais:\n');
  const examples = validPrices.slice(0, 5);
  examples.forEach(k => {
    console.log(`   ${k.kwp}kWp → R$ ${k.price_brl.toLocaleString('pt-BR', {minimumFractionDigits: 2})} (R$ ${k.price_per_kwp.toFixed(2)}/kWp)`);
    console.log(`   ${k.title.substring(0, 70)}\n`);
  });
}
