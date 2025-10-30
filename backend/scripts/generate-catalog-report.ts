#!/usr/bin/env node

/**
 * Relatório 360° de Imagens do Catálogo
 * 
 * Gera análise completa incluindo:
 * - Estatísticas de fabricantes
 * - Padrões de nomenclatura
 * - Métricas de qualidade de imagens
 * - Status de fontes (oficial/distribuidor/placeholder)
 * - Recomendações de melhorias
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_PATH = path.join(__dirname, '..');
const INVENTORY_PATH = path.join(ROOT_PATH, 'data/products-inventory');
const STATIC_PATH = path.join(ROOT_PATH, 'static');
const DOCS_PATH = path.join(ROOT_PATH, 'docs');
const CONFIG_PATH = path.join(ROOT_PATH, 'config/manufacturers-catalog.json');

interface ImageStats {
  totalProducts: number;
  withImages: number;
  withoutImages: number;
  byManufacturer: Record<string, number>;
  bySource: Record<string, number>;
  byCategory: Record<string, number>;
  namingCompliance: number;
  averageResolution?: string;
}

interface ManufacturerMetrics {
  name: string;
  totalProducts: number;
  withOfficialImages: number;
  withDistributorImages: number;
  withPlaceholder: number;
  priority: number;
  coverage: number;
}

function loadManufacturersCatalog() {
  if (!fs.existsSync(CONFIG_PATH)) {
    return { manufacturers: {} };
  }
  return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
}

function scanInventoryFiles(): any[] {
  const products: any[] = [];
  const inventoryDirs = [
    'fortlev',
    'neosolar',
    'solfacil',
    'fotus',
    'dynamis',
    'odex',
    'technical_specs'
  ];

  for (const dir of inventoryDirs) {
    const dirPath = path.join(INVENTORY_PATH, dir);
    if (!fs.existsSync(dirPath)) continue;

    const files = fs.readdirSync(dirPath).filter(f => f.endsWith('.json'));

    for (const file of files) {
      try {
        const data = JSON.parse(fs.readFileSync(path.join(dirPath, file), 'utf8'));
        const items = Array.isArray(data) ? data : [data];
        products.push(...items.map(p => ({ ...p, source: dir })));
      } catch (e) {
        // Skip invalid files
      }
    }
  }

  return products;
}

function extractManufacturer(product: any): string {
  const fields = [
    'fabricante',
    'manufacturer',
    'marca',
    'brand',
    'fabricante_nome',
    'manufacturer_name'
  ];

  for (const field of fields) {
    if (product[field]) {
      return normalizeManufacturerName(product[field]);
    }
  }

  // Try to extract from SKU or model
  const sku = product.sku || product.SKU || product.codigo || '';
  const model = product.modelo || product.model || '';
  
  const combined = `${sku} ${model}`.toUpperCase();

  const manufacturerPatterns = [
    { pattern: /LONGI|LR\d+/, name: 'LONGI' },
    { pattern: /GROWATT|MIN|MIC|NEO/, name: 'GROWATT' },
    { pattern: /SUNGROW|SG\d+/, name: 'SUNGROW' },
    { pattern: /RISEN|RSM/, name: 'RISEN' },
    { pattern: /JINKO|JKM/, name: 'JINKO' },
    { pattern: /TRINA|TSM/, name: 'TRINA' },
    { pattern: /CANADIAN|CS\d+/, name: 'CANADIAN-SOLAR' },
    { pattern: /BYD/, name: 'BYD' },
    { pattern: /FRONIUS/, name: 'FRONIUS' },
    { pattern: /DEYE/, name: 'DEYE' },
    { pattern: /SOLIS/, name: 'SOLIS' },
    { pattern: /HUAWEI/, name: 'HUAWEI' },
    { pattern: /PYLONTECH/, name: 'PYLONTECH' },
    { pattern: /DYNESS/, name: 'DYNESS' },
    { pattern: /ENPHASE/, name: 'ENPHASE' },
    { pattern: /FORTLEV/, name: 'FORTLEV' }
  ];

  for (const { pattern, name } of manufacturerPatterns) {
    if (pattern.test(combined)) {
      return name;
    }
  }

  return 'UNKNOWN';
}

function normalizeManufacturerName(name: string): string {
  const mapping: Record<string, string> = {
    'longi solar': 'LONGI',
    'longi': 'LONGI',
    'growatt': 'GROWATT',
    'sungrow': 'SUNGROW',
    'risen': 'RISEN',
    'risen energy': 'RISEN',
    'jinko': 'JINKO',
    'jinkosolar': 'JINKO',
    'trina': 'TRINA',
    'trina solar': 'TRINA',
    'canadian solar': 'CANADIAN-SOLAR',
    'canadian': 'CANADIAN-SOLAR',
    'byd': 'BYD',
    'fronius': 'FRONIUS',
    'deye': 'DEYE',
    'solis': 'SOLIS',
    'huawei': 'HUAWEI',
    'pylontech': 'PYLONTECH',
    'dyness': 'DYNESS',
    'enphase': 'ENPHASE',
    'fortlev': 'FORTLEV'
  };

  const normalized = name.toLowerCase().trim();
  return mapping[normalized] || name.toUpperCase();
}

function hasImage(product: any): boolean {
  const imageFields = ['image', 'image_url', 'imagem', 'foto', 'photo'];
  return imageFields.some(field => product[field] && product[field] !== '');
}

function getImageSource(product: any): string {
  const imageUrl = product.image || product.image_url || product.imagem || '';
  
  if (!imageUrl) return 'none';
  
  if (imageUrl.includes('placeholder')) return 'placeholder';
  if (imageUrl.includes('longi.com') || 
      imageUrl.includes('growatt.com') ||
      imageUrl.includes('sungrow') ||
      imageUrl.includes('official')) {
    return 'official';
  }
  if (imageUrl.includes('cdn') || imageUrl.includes('cloudfront')) {
    return 'cdn';
  }
  return 'distributor';
}

function checkNamingCompliance(filename: string): boolean {
  // Pattern: MANUFACTURER-MODEL-POWER.ext
  const pattern = /^[A-Z-]+\-[A-Z0-9.-]+\.(png|jpg|jpeg|webp)$/i;
  return pattern.test(filename);
}

function categorizeProduct(product: any): string {
  const type = (
    product.tipo || 
    product.type || 
    product.categoria || 
    product.category || 
    ''
  ).toLowerCase();

  if (type.includes('painel') || type.includes('panel') || type.includes('módulo')) {
    return 'panels';
  }
  if (type.includes('inversor') || type.includes('inverter')) {
    return 'inverters';
  }
  if (type.includes('bateria') || type.includes('battery')) {
    return 'batteries';
  }
  if (type.includes('kit')) {
    return 'kits';
  }
  if (type.includes('string box') || type.includes('cabo') || type.includes('conector')) {
    return 'accessories';
  }

  return 'other';
}

function analyzeImageStats(products: any[]): ImageStats {
  const stats: ImageStats = {
    totalProducts: products.length,
    withImages: 0,
    withoutImages: 0,
    byManufacturer: {},
    bySource: {},
    byCategory: {},
    namingCompliance: 0
  };

  let namingComplianceCount = 0;

  for (const product of products) {
    const manufacturer = extractManufacturer(product);
    const hasImg = hasImage(product);
    const source = getImageSource(product);
    const category = categorizeProduct(product);

    if (hasImg) {
      stats.withImages++;
    } else {
      stats.withoutImages++;
    }

    stats.byManufacturer[manufacturer] = (stats.byManufacturer[manufacturer] || 0) + 1;
    stats.bySource[source] = (stats.bySource[source] || 0) + 1;
    stats.byCategory[category] = (stats.byCategory[category] || 0) + 1;

    // Check naming compliance
    const imageUrl = product.image || product.image_url || '';
    if (imageUrl) {
      const filename = path.basename(imageUrl);
      if (checkNamingCompliance(filename)) {
        namingComplianceCount++;
      }
    }
  }

  stats.namingCompliance = stats.withImages > 0
    ? Math.round((namingComplianceCount / stats.withImages) * 100)
    : 0;

  return stats;
}

function generateManufacturerMetrics(
  products: any[], 
  catalog: any
): ManufacturerMetrics[] {
  const manufacturers = catalog.manufacturers || {};
  const metrics: ManufacturerMetrics[] = [];

  for (const [key, info] of Object.entries(manufacturers) as any) {
    const manufacturerProducts = products.filter(p => {
      const mfr = extractManufacturer(p);
      return mfr === key;
    });

    const withOfficial = manufacturerProducts.filter(p => 
      getImageSource(p) === 'official'
    ).length;

    const withDistributor = manufacturerProducts.filter(p => 
      getImageSource(p) === 'distributor'
    ).length;

    const withPlaceholder = manufacturerProducts.filter(p => 
      getImageSource(p) === 'placeholder'
    ).length;

    const coverage = manufacturerProducts.length > 0
      ? Math.round(((withOfficial + withDistributor) / manufacturerProducts.length) * 100)
      : 0;

    metrics.push({
      name: info.name,
      totalProducts: manufacturerProducts.length,
      withOfficialImages: withOfficial,
      withDistributorImages: withDistributor,
      withPlaceholder,
      priority: info.priority,
      coverage
    });
  }

  return metrics.sort((a, b) => b.totalProducts - a.totalProducts);
}

function generateMarkdownReport(
  stats: ImageStats,
  manufacturerMetrics: ManufacturerMetrics[],
  catalog: any
): string {
  const md: string[] = [];

  md.push('# Relatório 360° - Imagens do Catálogo de Produtos');
  md.push('');
  md.push(`**Gerado em:** ${new Date().toLocaleString('pt-BR')}`);
  md.push('');
  md.push('---');
  md.push('');

  // Sumário Executivo
  md.push('## 📊 Sumário Executivo');
  md.push('');
  md.push('| Métrica | Valor |');
  md.push('|---------|-------|');
  md.push(`| **Total de Produtos** | ${stats.totalProducts.toLocaleString()} |`);
  md.push(`| **Com Imagens** | ${stats.withImages.toLocaleString()} (${Math.round((stats.withImages/stats.totalProducts)*100)}%) |`);
  md.push(`| **Sem Imagens** | ${stats.withoutImages.toLocaleString()} (${Math.round((stats.withoutImages/stats.totalProducts)*100)}%) |`);
  md.push(`| **Nomenclatura Padronizada** | ${stats.namingCompliance}% |`);
  md.push('');

  // Fontes de Imagens
  md.push('## 🎯 Fontes de Imagens');
  md.push('');
  md.push('| Fonte | Quantidade | Percentual |');
  md.push('|-------|------------|------------|');
  
  const sortedSources = Object.entries(stats.bySource)
    .sort(([,a], [,b]) => b - a);

  for (const [source, count] of sortedSources) {
    const percent = Math.round((count / stats.totalProducts) * 100);
    const emoji = source === 'official' ? '⭐' : 
                  source === 'cdn' ? '☁️' :
                  source === 'distributor' ? '📦' : 
                  source === 'placeholder' ? '🔲' : '❓';
    md.push(`| ${emoji} ${source} | ${count.toLocaleString()} | ${percent}% |`);
  }
  md.push('');

  // Fabricantes
  md.push('## 🏭 Fabricantes Catalogados');
  md.push('');
  md.push(`**Total de Fabricantes:** ${Object.keys(catalog.manufacturers || {}).length}`);
  md.push('');
  md.push('| Fabricante | Total | Oficial | Distribuidor | Placeholder | Cobertura |');
  md.push('|------------|-------|---------|--------------|-------------|-----------|');

  for (const metric of manufacturerMetrics.slice(0, 20)) {
    const coverageEmoji = metric.coverage >= 80 ? '🟢' :
                          metric.coverage >= 50 ? '🟡' : '🔴';
    md.push(
      `| ${metric.name} | ${metric.totalProducts} | ${metric.withOfficialImages} | ` +
      `${metric.withDistributorImages} | ${metric.withPlaceholder} | ` +
      `${coverageEmoji} ${metric.coverage}% |`
    );
  }
  md.push('');

  // Categorias
  md.push('## 📦 Produtos por Categoria');
  md.push('');
  md.push('| Categoria | Quantidade | Percentual |');
  md.push('|-----------|------------|------------|');

  const sortedCategories = Object.entries(stats.byCategory)
    .sort(([,a], [,b]) => b - a);

  for (const [category, count] of sortedCategories) {
    const percent = Math.round((count / stats.totalProducts) * 100);
    const emoji = category === 'panels' ? '☀️' :
                  category === 'inverters' ? '⚡' :
                  category === 'batteries' ? '🔋' :
                  category === 'kits' ? '📦' : '🔧';
    md.push(`| ${emoji} ${category} | ${count.toLocaleString()} | ${percent}% |`);
  }
  md.push('');

  // Estratégia de Nomenclatura
  md.push('## 📝 Padrão de Nomenclatura');
  md.push('');
  md.push('**Padrão Adotado:** `{FABRICANTE}-{MODELO}-{POTENCIA}.{ext}`');
  md.push('');
  md.push('**Exemplos de Nomenclatura Correta:**');
  md.push('```');
  md.push('LONGI-LR5-72HPH-585M.png');
  md.push('GROWATT-MIN-3000TL-X.jpg');
  md.push('SUNGROW-SG3.0RS.jpg');
  md.push('BYD-HVM-13.8.png');
  md.push('```');
  md.push('');
  md.push(`**Taxa de Conformidade Atual:** ${stats.namingCompliance}%`);
  md.push('');

  // Hierarquia de Fontes
  md.push('## 🔄 Hierarquia de Fontes');
  md.push('');
  md.push('```mermaid');
  md.push('graph TD');
  md.push('    A[Produto] --> B{Fabricante Catalogado?}');
  md.push('    B -->|Sim| C[1. Site Oficial]');
  md.push('    B -->|Não| G[Buscar em Distribuidor]');
  md.push('    C -->|Sucesso| H[✓ Imagem Oficial]');
  md.push('    C -->|Falha| D[2. CDN Fabricante]');
  md.push('    D -->|Sucesso| H');
  md.push('    D -->|Falha| E[3. Browser Automation]');
  md.push('    E -->|Sucesso| H');
  md.push('    E -->|Falha| G');
  md.push('    G -->|Sucesso| I[✓ Imagem Distribuidor]');
  md.push('    G -->|Falha| F[4. Placeholder]');
  md.push('    F --> J[⚠ Placeholder Genérico]');
  md.push('```');
  md.push('');

  // Métricas de Qualidade
  md.push('## 📈 Métricas de Qualidade');
  md.push('');
  md.push('| Métrica | Meta | Atual | Status |');
  md.push('|---------|------|-------|--------|');

  const officialPercent = stats.bySource['official'] 
    ? Math.round((stats.bySource['official'] / stats.totalProducts) * 100)
    : 0;
  const officialStatus = officialPercent >= 80 ? '🟢 Excelente' :
                         officialPercent >= 50 ? '🟡 Bom' :
                         officialPercent >= 20 ? '🟠 Regular' : '🔴 Crítico';

  md.push(`| Imagens Oficiais | >80% | ${officialPercent}% | ${officialStatus} |`);
  md.push(`| Nomenclatura Padronizada | 100% | ${stats.namingCompliance}% | ${stats.namingCompliance >= 80 ? '🟢' : stats.namingCompliance >= 50 ? '🟡' : '🔴'} |`);
  
  const coveragePercent = Math.round((stats.withImages / stats.totalProducts) * 100);
  md.push(`| Cobertura Total | >95% | ${coveragePercent}% | ${coveragePercent >= 95 ? '🟢' : coveragePercent >= 80 ? '🟡' : '🔴'} |`);
  md.push('');

  // Recomendações
  md.push('## 💡 Recomendações');
  md.push('');

  if (officialPercent < 50) {
    md.push('### Prioridade Alta ⚠️');
    md.push('- Aumentar extração de imagens oficiais dos fabricantes');
    md.push('- Implementar browser automation para fabricantes sem padrões de URL');
    md.push('- Adicionar mais fabricantes ao catálogo oficial');
    md.push('');
  }

  if (stats.namingCompliance < 80) {
    md.push('### Padronização 📝');
    md.push('- Migrar imagens de distribuidores para nomenclatura padronizada');
    md.push('- Executar script de renomeação em lote');
    md.push('- Validar conformidade antes de upload para S3');
    md.push('');
  }

  if (stats.withoutImages > stats.totalProducts * 0.1) {
    md.push('### Cobertura 📊');
    md.push('- Implementar fallback para produtos sem imagens');
    md.push('- Criar placeholders específicos por categoria');
    md.push('- Adicionar mais fontes de distribuidores');
    md.push('');
  }

  // Próximos Passos
  md.push('## 🚀 Próximos Passos');
  md.push('');
  md.push('1. ✅ **Extração Completa**');
  md.push('   - Executar pipeline unificado em todos os produtos');
  md.push('   - Priorizar fabricantes com maior volume');
  md.push('');
  md.push('2. 🔄 **Normalização**');
  md.push('   - Renomear imagens existentes para padrão oficial');
  md.push('   - Organizar por fabricante em estrutura de pastas');
  md.push('');
  md.push('3. ☁️ **Upload AWS**');
  md.push('   - Upload para S3 bucket `ysh-b2b-products`');
  md.push('   - Atualizar URLs no DynamoDB');
  md.push('   - Configurar CloudFront CDN');
  md.push('');
  md.push('4. ✅ **Validação**');
  md.push('   - Verificar resolução mínima (800x600)');
  md.push('   - Validar integridade de arquivos');
  md.push('   - Testar carregamento no frontend');
  md.push('');

  // Scripts Disponíveis
  md.push('## 🛠️ Scripts Disponíveis');
  md.push('');
  md.push('```bash');
  md.push('# Pipeline completo de extração');
  md.push('npx tsx scripts/run-unified-image-pipeline.ts');
  md.push('');
  md.push('# Extração apenas de fabricantes oficiais');
  md.push('npx tsx scripts/extract-manufacturer-images.ts');
  md.push('');
  md.push('# Gerar este relatório');
  md.push('npx tsx scripts/generate-catalog-report.ts');
  md.push('');
  md.push('# Upload para S3');
  md.push('node scripts/upload-images-s3.js');
  md.push('');
  md.push('# Upload para DynamoDB');
  md.push('node scripts/upload-to-dynamodb.js');
  md.push('```');
  md.push('');

  md.push('---');
  md.push('');
  md.push('**Mantido por:** YSH B2B Platform Team');
  md.push(`**Última Atualização:** ${new Date().toLocaleDateString('pt-BR')}`);

  return md.join('\n');
}

function main() {
  console.log('🚀 Gerando Relatório 360° de Imagens do Catálogo\n');
  console.log('═'.repeat(70));
  console.log('');

  // Load catalog
  console.log('📖 Carregando catálogo de fabricantes...');
  const catalog = loadManufacturersCatalog();
  console.log(`   ✓ ${Object.keys(catalog.manufacturers || {}).length} fabricantes\n`);

  // Scan inventory
  console.log('📦 Escaneando inventários...');
  const products = scanInventoryFiles();
  console.log(`   ✓ ${products.length.toLocaleString()} produtos\n`);

  // Analyze
  console.log('📊 Analisando estatísticas...');
  const stats = analyzeImageStats(products);
  console.log(`   ✓ ${stats.withImages} com imagens\n`);

  // Manufacturer metrics
  console.log('🏭 Calculando métricas por fabricante...');
  const manufacturerMetrics = generateManufacturerMetrics(products, catalog);
  console.log(`   ✓ ${manufacturerMetrics.length} fabricantes analisados\n`);

  // Generate report
  console.log('📝 Gerando relatório Markdown...');
  const markdown = generateMarkdownReport(stats, manufacturerMetrics, catalog);

  // Save
  const outputPath = path.join(DOCS_PATH, 'CATALOG_IMAGES_360_REPORT.md');
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, markdown, 'utf8');

  console.log(`   ✓ Relatório salvo: ${outputPath}\n`);

  // JSON report
  const jsonReport = {
    generated_at: new Date().toISOString(),
    stats,
    manufacturer_metrics: manufacturerMetrics,
    catalog_summary: {
      total_manufacturers: Object.keys(catalog.manufacturers || {}).length,
      active_manufacturers: Object.values(catalog.manufacturers || {})
        .filter((m: any) => m.active).length
    }
  };

  const jsonPath = path.join(ROOT_PATH, 'output/CATALOG_IMAGES_360_REPORT.json');
  fs.mkdirSync(path.dirname(jsonPath), { recursive: true });
  fs.writeFileSync(jsonPath, JSON.stringify(jsonReport, null, 2), 'utf8');

  console.log(`   ✓ JSON salvo: ${jsonPath}\n`);

  console.log('═'.repeat(70));
  console.log('✅ RELATÓRIO CONCLUÍDO!');
  console.log('');
  console.log('📊 Resumo Rápido:');
  console.log(`   • ${stats.totalProducts.toLocaleString()} produtos`);
  console.log(`   • ${stats.withImages.toLocaleString()} com imagens (${Math.round((stats.withImages/stats.totalProducts)*100)}%)`);
  console.log(`   • ${stats.namingCompliance}% nomenclatura padronizada`);
  console.log(`   • ${manufacturerMetrics.length} fabricantes`);
}

main();
