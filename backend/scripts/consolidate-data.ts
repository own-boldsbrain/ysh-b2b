#!/usr/bin/env node

/**
 * Data Consolidation Script
 * 
 * Consolidates all product data from all distributors into a unified schema
 * Performs:
 * - Data normalization
 * - Deduplication
 * - Schema validation
 * - Category standardization
 * - Price comparison across distributors
 * 
 * Usage:
 *   npx tsx scripts/consolidate-data.ts
 */

import * as fs from 'fs';
import * as path from 'path';

interface RawProduct {
  sku?: string;
  id?: string;
  title: string;
  description?: string;
  price: number;
  pricePromo?: number;
  url: string;
  imageUrl?: string;
  images?: string[];
  category?: string;
  distributor: string;
  stock?: {
    available: boolean;
    quantity?: number;
    status: string;
  };
  specifications?: Record<string, string>;
  brand?: string;
  model?: string;
  warranty?: string;
  extractedAt?: string;
}

interface UnifiedProduct {
  id: string;
  sku: string;
  title: string;
  normalizedTitle: string;
  description: string;
  category: string;
  subcategory?: string;
  brand?: string;
  model?: string;
  specifications: Record<string, string>;
  images: string[];
  warranty?: string;
  datasheet?: string;
  prices: {
    distributor: string;
    price: number;
    pricePromo?: number;
    currency: string;
    url: string;
    stock: {
      available: boolean;
      quantity?: number;
      status: string;
    };
    extractedAt: string;
  }[];
  lowestPrice: number;
  highestPrice: number;
  averagePrice: number;
  createdAt: string;
  updatedAt: string;
}

const OUTPUT_DIR = path.join(process.cwd(), 'output');
const CONSOLIDATED_DIR = path.join(OUTPUT_DIR, 'consolidated');

if (!fs.existsSync(CONSOLIDATED_DIR)) {
  fs.mkdirSync(CONSOLIDATED_DIR, { recursive: true });
}

function normalizeTitle(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function extractBrand(title: string): string | undefined {
  const knownBrands = [
    'growatt', 'fronius', 'solis', 'goodwe', 'huawei', 'sma',
    'canadian solar', 'jinko', 'trina', 'znshine', 'osda',
    'moura', 'heliar', 'freedom', 'fulguris', 'unipower',
    'anauger', 'schneider', 'weg', 'steca', 'epever',
    'deye', 'saj', 'solplanet', 'sine energy'
  ];

  const lowerTitle = title.toLowerCase();
  for (const brand of knownBrands) {
    if (lowerTitle.includes(brand)) {
      return brand.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    }
  }

  return undefined;
}

function extractModel(title: string): string | undefined {
  // Extract model patterns like "XYZ-123", "ABC 1000", etc.
  const modelPatterns = [
    /([A-Z]{2,}[-\s]?\d+[A-Z]*)/i,
    /(\d+W)/i,
    /(\d+V)/i,
    /(\d+A)/i,
  ];

  for (const pattern of modelPatterns) {
    const match = title.match(pattern);
    if (match) {
      return match[1].toUpperCase();
    }
  }

  return undefined;
}

function loadAllProducts(): RawProduct[] {
  const allProducts: RawProduct[] = [];
  
  const distributors = ['edeltec', 'neosolar', 'odex', 'fortlev', 'solfacil', 'fotus', 'dynamis'];
  
  // Load from basic scraping
  for (const dist of distributors) {
    const distDir = path.join(OUTPUT_DIR, dist);
    if (fs.existsSync(distDir)) {
      const files = fs.readdirSync(distDir).filter(f => f.endsWith('.json'));
      for (const file of files) {
        const filePath = path.join(distDir, file);
        const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
        if (Array.isArray(data)) {
          allProducts.push(...data);
        }
      }
    }
  }

  // Load from deep scraping
  const deepScrapingDir = path.join(OUTPUT_DIR, 'deep-scraping');
  if (fs.existsSync(deepScrapingDir)) {
    const distDirs = fs.readdirSync(deepScrapingDir);
    for (const dist of distDirs) {
      const distPath = path.join(deepScrapingDir, dist);
      if (fs.statSync(distPath).isDirectory()) {
        const files = fs.readdirSync(distPath).filter(f => f.endsWith('.json'));
        for (const file of files) {
          const filePath = path.join(distPath, file);
          const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
          if (Array.isArray(data)) {
            allProducts.push(...data);
          }
        }
      }
    }
  }

  // Load from multi-distributor
  const multiDir = path.join(OUTPUT_DIR, 'multi-distributor');
  if (fs.existsSync(multiDir)) {
    const files = fs.readdirSync(multiDir).filter(f => f.startsWith('all-products-') && f.endsWith('.json'));
    for (const file of files) {
      const filePath = path.join(multiDir, file);
      const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      if (Array.isArray(data)) {
        allProducts.push(...data);
      }
    }
  }

  console.log(`📦 Carregados ${allProducts.length} produtos brutos de todos os distribuidores`);
  return allProducts;
}

function consolidateProducts(rawProducts: RawProduct[]): UnifiedProduct[] {
  const productMap = new Map<string, UnifiedProduct>();

  for (const raw of rawProducts) {
    const normalizedTitle = normalizeTitle(raw.title);
    const brand = raw.brand || extractBrand(raw.title);
    const model = raw.model || extractModel(raw.title);

    // Generate a unique key based on normalized title and model
    const uniqueKey = `${normalizedTitle}-${model || 'unknown'}`;

    let unified = productMap.get(uniqueKey);

    if (!unified) {
      // Create new unified product
      unified = {
        id: raw.id || raw.sku || `prod-${Date.now()}-${Math.random()}`,
        sku: raw.sku || raw.id || '',
        title: raw.title,
        normalizedTitle,
        description: raw.description || '',
        category: raw.category || 'outros',
        brand,
        model,
        specifications: raw.specifications || {},
        images: raw.images || (raw.imageUrl ? [raw.imageUrl] : []),
        warranty: raw.warranty,
        prices: [],
        lowestPrice: raw.price,
        highestPrice: raw.price,
        averagePrice: raw.price,
        createdAt: raw.extractedAt || new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    }

    // Add price information from this distributor
    unified.prices.push({
      distributor: raw.distributor,
      price: raw.price,
      pricePromo: raw.pricePromo,
      currency: 'BRL',
      url: raw.url,
      stock: raw.stock || {
        available: false,
        status: 'Indisponível',
      },
      extractedAt: raw.extractedAt || new Date().toISOString(),
    });

    // Update price statistics
    const prices = unified.prices.map(p => p.pricePromo || p.price).filter(p => p > 0);
    if (prices.length > 0) {
      unified.lowestPrice = Math.min(...prices);
      unified.highestPrice = Math.max(...prices);
      unified.averagePrice = prices.reduce((sum, p) => sum + p, 0) / prices.length;
    }

    // Merge images (deduplicate)
    if (raw.images) {
      for (const img of raw.images) {
        if (!unified.images.includes(img)) {
          unified.images.push(img);
        }
      }
    } else if (raw.imageUrl && !unified.images.includes(raw.imageUrl)) {
      unified.images.push(raw.imageUrl);
    }

    // Merge specifications
    if (raw.specifications) {
      unified.specifications = {
        ...unified.specifications,
        ...raw.specifications,
      };
    }

    // Update description if current one is empty or shorter
    if (!unified.description || (raw.description && raw.description.length > unified.description.length)) {
      unified.description = raw.description || unified.description;
    }

    productMap.set(uniqueKey, unified);
  }

  const consolidated = Array.from(productMap.values());
  console.log(`✅ Consolidados em ${consolidated.length} produtos únicos`);
  
  return consolidated;
}

function generateReport(products: UnifiedProduct[]): void {
  const report = {
    summary: {
      totalProducts: products.length,
      byCategory: {} as Record<string, number>,
      byDistributor: {} as Record<string, number>,
      byBrand: {} as Record<string, number>,
      priceStatistics: {
        averageLowest: 0,
        averageHighest: 0,
        averageAverage: 0,
      },
    },
    products: products.map(p => ({
      title: p.title,
      brand: p.brand,
      category: p.category,
      lowestPrice: p.lowestPrice,
      highestPrice: p.highestPrice,
      availableIn: p.prices.map(pr => pr.distributor),
    })),
    generatedAt: new Date().toISOString(),
  };

  // Calculate statistics
  for (const product of products) {
    // By category
    report.summary.byCategory[product.category] = 
      (report.summary.byCategory[product.category] || 0) + 1;

    // By brand
    if (product.brand) {
      report.summary.byBrand[product.brand] = 
        (report.summary.byBrand[product.brand] || 0) + 1;
    }

    // By distributor
    for (const price of product.prices) {
      report.summary.byDistributor[price.distributor] = 
        (report.summary.byDistributor[price.distributor] || 0) + 1;
    }
  }

  // Price statistics
  const validPrices = products.filter(p => p.lowestPrice > 0);
  if (validPrices.length > 0) {
    report.summary.priceStatistics.averageLowest = 
      validPrices.reduce((sum, p) => sum + p.lowestPrice, 0) / validPrices.length;
    report.summary.priceStatistics.averageHighest = 
      validPrices.reduce((sum, p) => sum + p.highestPrice, 0) / validPrices.length;
    report.summary.priceStatistics.averageAverage = 
      validPrices.reduce((sum, p) => sum + p.averagePrice, 0) / validPrices.length;
  }

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const reportFile = path.join(CONSOLIDATED_DIR, `report-${timestamp}.json`);
  fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
  console.log(`📊 Relatório salvo: ${reportFile}`);

  // Print summary
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  📊 RELATÓRIO DE CONSOLIDAÇÃO                            ║
╚════════════════════════════════════════════════════════════╝

📦 PRODUTOS:
  • Total: ${report.summary.totalProducts}

🏷️  POR CATEGORIA:
${Object.entries(report.summary.byCategory)
  .sort((a, b) => b[1] - a[1])
  .map(([cat, count]) => `  • ${cat}: ${count}`)
  .join('\n')}

🏪 POR DISTRIBUIDOR:
${Object.entries(report.summary.byDistributor)
  .sort((a, b) => b[1] - a[1])
  .map(([dist, count]) => `  • ${dist}: ${count}`)
  .join('\n')}

🏭 TOP 10 MARCAS:
${Object.entries(report.summary.byBrand)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 10)
  .map(([brand, count]) => `  • ${brand}: ${count}`)
  .join('\n')}

💰 ESTATÍSTICAS DE PREÇO:
  • Preço médio (menor): R$ ${report.summary.priceStatistics.averageLowest.toFixed(2)}
  • Preço médio (maior): R$ ${report.summary.priceStatistics.averageHighest.toFixed(2)}
  • Preço médio geral: R$ ${report.summary.priceStatistics.averageAverage.toFixed(2)}

🎉 Consolidação completa!
  `);
}

async function consolidateData(): Promise<void> {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  🔄 CONSOLIDAÇÃO DE DADOS                                ║
╚════════════════════════════════════════════════════════════╝
  `);

  // Load all products
  const rawProducts = loadAllProducts();

  if (rawProducts.length === 0) {
    console.log('⚠️  Nenhum produto encontrado para consolidar');
    return;
  }

  // Consolidate
  console.log('\n🔄 Consolidando produtos...');
  const consolidated = consolidateProducts(rawProducts);

  // Save consolidated data
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const consolidatedFile = path.join(CONSOLIDATED_DIR, `unified-products-${timestamp}.json`);
  fs.writeFileSync(consolidatedFile, JSON.stringify(consolidated, null, 2));
  console.log(`💾 Dados consolidados salvos: ${consolidatedFile}`);

  // Generate report
  console.log('\n📊 Gerando relatório...');
  generateReport(consolidated);
}

// Run
consolidateData().catch(console.error);
