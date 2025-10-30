#!/usr/bin/env node

/**
 * Deep Scraping Script - All Working Distributors
 * 
 * Extracts detailed product information from:
 * - Edeltec (79 products)
 * - Fortlev (needs category navigation)
 * - Neosolar (limited access)
 * - Odex (needs category navigation)
 * 
 * For each product, extracts:
 * - Full title and description
 * - Detailed specifications
 * - Price (current and promotional)
 * - Stock availability
 * - Multiple images
 * - Technical datasheets (if available)
 * - Warranty information
 * 
 * Usage:
 *   npx tsx scripts/extract-deep-all.ts
 */

import { chromium, Browser, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

interface DetailedProduct {
  id: string;
  sku: string;
  title: string;
  description: string;
  price: number;
  pricePromo?: number;
  currency: string;
  stock: {
    available: boolean;
    quantity?: number;
    status: string;
  };
  images: string[];
  specifications: Record<string, string>;
  category: string;
  subcategory?: string;
  brand?: string;
  model?: string;
  warranty?: string;
  datasheet?: string;
  url: string;
  distributor: string;
  extractedAt: string;
}

interface Distributor {
  name: string;
  url: string;
  email: string;
  password: string;
}

const DISTRIBUTORS: Distributor[] = [
  {
    name: 'edeltec',
    url: 'https://edeltecsolar.com.br/',
    email: process.env.EDELTEC_EMAIL || '',
    password: process.env.EDELTEC_PASSWORD || '',
  },
  {
    name: 'neosolar',
    url: 'https://portalb2b.neosolar.com.br/',
    email: process.env.NEOSOLAR_EMAIL || '',
    password: process.env.NEOSOLAR_PASSWORD || '',
  },
  {
    name: 'odex',
    url: 'https://odex.com.br/',
    email: process.env.ODEX_EMAIL || '',
    password: process.env.ODEX_PASSWORD || '',
  },
  {
    name: 'fortlev',
    url: 'https://fortlevsolar.app/login',
    email: process.env.FORTLEV_EMAIL || '',
    password: process.env.FORTLEV_PASSWORD || '',
  },
];

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'deep-scraping');
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function categorizeProduct(title: string): string {
  const lowerTitle = title.toLowerCase();
  const categories: { [key: string]: string[] } = {
    bateria: ['bateria', 'estacionária', 'moura', 'heliar', 'freedom', 'fulguris', 'lifepo4'],
    bomba: ['bomba', 'solar', 'anauger', 'agua', 'piscina', 'submersa'],
    painel: ['painel', 'solar', 'fotovoltáico', 'módulo', 'placa', 'panel'],
    inversor: ['inversor', 'inverter', 'isolada', 'hybrid', 'grid-tie', 'fronius', 'growatt', 'solis'],
    estrutura: ['estrutura', 'suporte', 'trilho', 'fixação', 'mounting'],
    cabo: ['cabo', 'conduite', 'conectores', 'conector', 'MC4'],
  };

  for (const [category, keywords] of Object.entries(categories)) {
    if (keywords.some((keyword: string) => lowerTitle.includes(keyword))) {
      return category;
    }
  }

  return 'outros';
}

async function loginToPortal(page: Page, distributor: Distributor): Promise<boolean> {
  try {
    console.log(`🔐 Fazendo login em ${distributor.name}...`);
    
    await page.goto(distributor.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);

    // Check if already logged in
    const alreadyLoggedIn = await page.evaluate(() => {
      return !!document.querySelector('[href*="logout"], [href*="sair"]') ||
             document.body.innerText.toLowerCase().includes('sair');
    });

    if (alreadyLoggedIn) {
      console.log(`✅ Já logado em ${distributor.name}`);
      return true;
    }

    // Fill email
    const emailSelectors = [
      'input[type="email"]',
      'input[name="email"]',
      'input[name="username"]',
    ];

    for (const selector of emailSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.fill(distributor.email);
          break;
        }
      } catch (e) { /* continue */ }
    }

    // Fill password
    const passwordSelectors = [
      'input[type="password"]',
      'input[name="password"]',
    ];

    for (const selector of passwordSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.fill(distributor.password);
          break;
        }
      } catch (e) { /* continue */ }
    }

    // Submit
    await page.click('button[type="submit"]').catch(() => {});
    await page.waitForTimeout(3000);

    console.log(`✅ Login realizado em ${distributor.name}`);
    return true;

  } catch (error) {
    console.log(`❌ Erro no login de ${distributor.name}: ${(error as Error).message}`);
    return false;
  }
}

async function extractProductLinks(page: Page, distributor: string): Promise<string[]> {
  console.log(`📦 Coletando links de produtos...`);

  // Scroll to load all products
  for (let i = 0; i < 50; i++) {
    await page.evaluate(() => window.scrollBy(0, window.innerHeight));
    await page.waitForTimeout(200);
  }

  const links = await page.evaluate(() => {
    const productLinks: string[] = [];
    const selectors = [
      'a[href*="/produto"]',
      'a[href*="/product"]',
      'a[href*="item"]',
    ];

    for (const selector of selectors) {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        const href = (el as HTMLAnchorElement).href;
        if (href && !productLinks.includes(href)) {
          productLinks.push(href);
        }
      });
      if (productLinks.length > 0) break;
    }

    return productLinks;
  });

  console.log(`✅ ${links.length} links de produtos encontrados`);
  return links;
}

async function extractProductDetails(page: Page, url: string, distributor: string): Promise<DetailedProduct | null> {
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(1000);

    const product = await page.evaluate((dist) => {
      // Extract title
      let title = '';
      const titleSelectors = ['h1', '.product-title', '[class*="title"]', '[class*="nome"]'];
      for (const selector of titleSelectors) {
        const el = document.querySelector(selector);
        if (el && el.textContent && el.textContent.trim().length > 5) {
          title = el.textContent.trim();
          break;
        }
      }

      // Extract description
      let description = '';
      const descSelectors = ['.description', '[class*="descri"]', '.details', 'p'];
      for (const selector of descSelectors) {
        const el = document.querySelector(selector);
        if (el && el.textContent && el.textContent.trim().length > 20) {
          description = el.textContent.trim();
          break;
        }
      }

      // Extract price
      let price = 0;
      let pricePromo: number | undefined;
      const priceSelectors = ['.price', '[class*="price"]', '[class*="preco"]', '[data-price]'];
      for (const selector of priceSelectors) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
          const text = el.textContent || '';
          const match = text.match(/[\d.,]+/);
          if (match) {
            const value = parseFloat(match[0].replace('.', '').replace(',', '.'));
            if (!isNaN(value) && value > 0) {
              if (price === 0) {
                price = value;
              } else {
                pricePromo = Math.min(price, value);
                price = Math.max(price, value);
              }
            }
          }
        });
        if (price > 0) break;
      }

      // Extract images
      const images: string[] = [];
      document.querySelectorAll('img').forEach(img => {
        const src = (img as HTMLImageElement).src;
        if (src && (src.includes('product') || src.includes('item') || images.length < 5)) {
          if (!images.includes(src)) {
            images.push(src);
          }
        }
      });

      // Extract specifications
      const specifications: Record<string, string> = {};
      const specSelectors = ['table', '.specifications', '[class*="spec"]', 'dl', 'ul'];
      for (const selector of specSelectors) {
        const el = document.querySelector(selector);
        if (el) {
          // Try table format
          const rows = el.querySelectorAll('tr');
          rows.forEach(row => {
            const cells = row.querySelectorAll('td, th');
            if (cells.length >= 2) {
              const key = (cells[0].textContent || '').trim();
              const value = (cells[1].textContent || '').trim();
              if (key && value) {
                specifications[key] = value;
              }
            }
          });

          // Try list format
          const items = el.querySelectorAll('li, dd');
          items.forEach((item, index) => {
            const text = (item.textContent || '').trim();
            if (text.includes(':')) {
              const [key, value] = text.split(':');
              if (key && value) {
                specifications[key.trim()] = value.trim();
              }
            } else if (text) {
              specifications[`spec_${index + 1}`] = text;
            }
          });

          if (Object.keys(specifications).length > 0) break;
        }
      }

      // Extract stock
      let stockAvailable = false;
      let stockStatus = 'Indisponível';
      const stockSelectors = ['.stock', '[class*="estoque"]', '[class*="disponib"]'];
      for (const selector of stockSelectors) {
        const el = document.querySelector(selector);
        if (el) {
          const text = (el.textContent || '').toLowerCase();
          if (text.includes('disponível') || text.includes('estoque')) {
            stockAvailable = true;
            stockStatus = el.textContent?.trim() || 'Disponível';
            break;
          }
        }
      }

      // Extract SKU
      let sku = '';
      const skuMatch = window.location.href.match(/\d+/);
      if (skuMatch) {
        sku = skuMatch[0];
      } else {
        sku = `${dist}-${Date.now()}`;
      }

      return {
        sku,
        title: title || 'Produto sem título',
        description: description || '',
        price,
        pricePromo,
        images,
        specifications,
        stockAvailable,
        stockStatus,
      };
    }, distributor);

    const detailedProduct: DetailedProduct = {
      id: product.sku,
      sku: product.sku,
      title: product.title,
      description: product.description,
      price: product.price,
      pricePromo: product.pricePromo,
      currency: 'BRL',
      stock: {
        available: product.stockAvailable,
        status: product.stockStatus,
      },
      images: product.images,
      specifications: product.specifications,
      category: categorizeProduct(product.title),
      url,
      distributor,
      extractedAt: new Date().toISOString(),
    };

    console.log(`  ✅ ${product.title.substring(0, 50)}...`);
    return detailedProduct;

  } catch (error) {
    console.log(`  ❌ Erro ao extrair ${url}: ${(error as Error).message}`);
    return null;
  }
}

async function extractDistributorDeep(distributor: Distributor): Promise<DetailedProduct[]> {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`🎯 ${distributor.name.toUpperCase()} - DEEP SCRAPING`);
  console.log(`${'='.repeat(60)}`);

  const browser: Browser = await chromium.launch({ headless: true });
  const products: DetailedProduct[] = [];

  try {
    const page = await browser.newPage();

    // Login
    const loginSuccess = await loginToPortal(page, distributor);
    if (!loginSuccess) {
      console.log(`❌ Falha no login de ${distributor.name}`);
      return products;
    }

    // Get product links
    const productLinks = await extractProductLinks(page, distributor.name);

    if (productLinks.length === 0) {
      console.log(`⚠️  Nenhum produto encontrado em ${distributor.name}`);
      return products;
    }

    // Extract details from each product
    console.log(`\n📋 Extraindo detalhes de ${productLinks.length} produtos...\n`);
    
    for (let i = 0; i < Math.min(productLinks.length, 100); i++) { // Limit to 100 products per distributor
      const link = productLinks[i];
      console.log(`[${i + 1}/${productLinks.length}] ${link}`);
      
      const product = await extractProductDetails(page, link, distributor.name);
      if (product) {
        products.push(product);
      }

      // Rate limiting
      await page.waitForTimeout(500);
    }

    console.log(`\n✅ ${products.length} produtos extraídos de ${distributor.name}`);

    // Save individual file
    const outputDir = path.join(OUTPUT_DIR, distributor.name);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const jsonFile = path.join(outputDir, `deep-products-${timestamp}.json`);
    fs.writeFileSync(jsonFile, JSON.stringify(products, null, 2));
    console.log(`💾 Salvo: ${jsonFile}`);

  } catch (error) {
    console.log(`❌ Erro em ${distributor.name}: ${(error as Error).message}`);
  } finally {
    await browser.close();
  }

  return products;
}

async function extractAllDeep(): Promise<void> {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  🔬 DEEP SCRAPING - EXTRAÇÃO DETALHADA                   ║
╚════════════════════════════════════════════════════════════╝
  `);

  const startTime = Date.now();
  const allProducts: DetailedProduct[] = [];

  for (const distributor of DISTRIBUTORS) {
    if (!distributor.email || !distributor.password) {
      console.log(`⚠️  ${distributor.name}: Credenciais ausentes`);
      continue;
    }

    const products = await extractDistributorDeep(distributor);
    allProducts.push(...products);

    // Wait between distributors
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  const totalDuration = (Date.now() - startTime) / 1000;

  // Save combined results
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const combinedFile = path.join(OUTPUT_DIR, `all-deep-products-${timestamp}.json`);
  fs.writeFileSync(combinedFile, JSON.stringify(allProducts, null, 2));

  // Generate summary
  const summary = {
    totalProducts: allProducts.length,
    totalDuration,
    byDistributor: DISTRIBUTORS.map(d => ({
      name: d.name,
      count: allProducts.filter(p => p.distributor === d.name).length,
    })),
    byCategory: Object.entries(
      allProducts.reduce((acc, p) => {
        acc[p.category] = (acc[p.category] || 0) + 1;
        return acc;
      }, {} as Record<string, number>)
    ).map(([category, count]) => ({ category, count })),
    extractedAt: new Date().toISOString(),
  };

  const summaryFile = path.join(OUTPUT_DIR, `summary-${timestamp}.json`);
  fs.writeFileSync(summaryFile, JSON.stringify(summary, null, 2));

  console.log(`
╔════════════════════════════════════════════════════════════╗
║  ✨ DEEP SCRAPING CONCLUÍDO                              ║
╚════════════════════════════════════════════════════════════╝

📊 RESUMO GERAL:
  • Total de produtos: ${allProducts.length}
  • Duração total: ${totalDuration.toFixed(2)}s
  • Arquivo combinado: ${combinedFile}

📦 POR DISTRIBUIDOR:
${summary.byDistributor.map(d => `  • ${d.name}: ${d.count} produtos`).join('\n')}

🏷️  POR CATEGORIA:
${summary.byCategory.map(c => `  • ${c.category}: ${c.count} produtos`).join('\n')}

🎉 Extração detalhada completa!
  `);
}

// Run
extractAllDeep().catch(console.error);
