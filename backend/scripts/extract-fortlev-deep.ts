#!/usr/bin/env node

/**
 * Fortlev Deep Scraping - Navigate Categories and Extract Products
 * 
 * Explores the "Produto Avulso" section and extracts individual products
 */

import { chromium, Browser, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

interface Product {
  sku: string;
  title: string;
  description: string;
  price: number;
  priceFormatted: string;
  url: string;
  imageUrl: string;
  category: string;
  brand: string;
  distributor: string;
}

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'fortlev-deep');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function login(page: Page, email: string, password: string): Promise<boolean> {
  try {
    await page.goto('https://fortlevsolar.app/login', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000);

    // Fill login form
    await page.fill('input[type="email"], input[name="email"]', email);
    await page.fill('input[type="password"], input[name="password"]', password);
    
    // Submit
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    return true;
  } catch (error) {
    console.log(`❌ Login error: ${(error as Error).message}`);
    return false;
  }
}

async function extractProducts(page: Page): Promise<Product[]> {
  // Scroll to load all products
  for (let i = 0; i < 50; i++) {
    await page.evaluate(() => window.scrollBy(0, window.innerHeight));
    await page.waitForTimeout(300);
  }

  const products = await page.evaluate(() => {
    const items: any[] = [];
    
    // Try multiple product selectors
    const productSelectors = [
      'a[href*="/produto"]',
      '[class*="product"] a',
      '.card a',
      '[data-product]',
    ];

    let productLinks: Element[] = [];
    for (const selector of productSelectors) {
      const found = Array.from(document.querySelectorAll(selector));
      if (found.length > 0) {
        productLinks = found;
        break;
      }
    }

    productLinks.forEach((link, index) => {
      try {
        const href = (link as HTMLAnchorElement).href;
        
        // Extract title
        let title = (link.textContent || '').trim();
        if (!title || title.length < 3) {
          const parent = link.closest('[class*="product"], .card, [class*="item"]');
          const titleEl = parent?.querySelector('h1, h2, h3, h4, .title, [class*="title"]');
          if (titleEl) {
            title = (titleEl.textContent || '').trim();
          }
        }

        // Extract SKU
        const skuMatch = href.match(/\d+/);
        const sku = skuMatch ? skuMatch[0] : `fortlev-${index}`;

        // Extract image
        let imageUrl = '';
        const parent = link.closest('[class*="product"], .card, [class*="item"]');
        const img = parent?.querySelector('img') as HTMLImageElement;
        if (img && img.src) {
          imageUrl = img.src;
        }

        // Extract price
        let price = 0;
        let priceFormatted = '';
        const priceEl = parent?.querySelector('[class*="price"], .preco, .valor');
        if (priceEl) {
          priceFormatted = (priceEl.textContent || '').trim();
          const priceMatch = priceFormatted.match(/[\d.,]+/);
          if (priceMatch) {
            price = parseFloat(priceMatch[0].replace(/\./g, '').replace(',', '.'));
          }
        }

        if (title && title.length > 3) {
          items.push({
            sku,
            title,
            url: href,
            imageUrl,
            price: isNaN(price) ? 0 : price,
            priceFormatted,
          });
        }
      } catch (e) {
        // Skip
      }
    });

    return items;
  });

  return products.map(p => ({
    ...p,
    description: '',
    category: categorizeProduct(p.title),
    brand: 'Fortlev',
    distributor: 'fortlev',
  }));
}

function categorizeProduct(title: string): string {
  const lowerTitle = title.toLowerCase();
  const categories: { [key: string]: string[] } = {
    bateria: ['bateria', 'battery', 'growatt', 'byd'],
    inversor: ['inversor', 'inverter'],
    modulo: ['módulo', 'modulo', 'painel', 'placa'],
    cabo: ['cabo', 'cable'],
    estrutura: ['estrutura', 'structure', 'suporte'],
  };

  for (const [category, keywords] of Object.entries(categories)) {
    if (keywords.some(keyword => lowerTitle.includes(keyword))) {
      return category;
    }
  }

  return 'outros';
}

async function main() {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  🔍 FORTLEV DEEP SCRAPING - NAVEGAÇÃO POR CATEGORIAS      ║
╚════════════════════════════════════════════════════════════╝
  `);

  const email = process.env.FORTLEV_EMAIL || '';
  const password = process.env.FORTLEV_PASSWORD || '';

  if (!email || !password) {
    console.log('❌ FORTLEV_EMAIL and FORTLEV_PASSWORD required');
    return;
  }

  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('🔐 Logging in...');
  const loginSuccess = await login(page, email, password);

  if (!loginSuccess) {
    console.log('❌ Login failed');
    await browser.close();
    return;
  }

  console.log('✅ Login successful\n');

  // Navigate to produto-avulso
  console.log('📦 Navigating to Produto Avulso...');
  await page.goto('https://fortlevsolar.app/produto-avulso', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3000);

  console.log('🔍 Extracting products...');
  const products = await extractProducts(page);

  await browser.close();

  console.log(`✅ Extracted ${products.length} products\n`);

  // Save
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = path.join(OUTPUT_DIR, `products-deep-${timestamp}.json`);
  fs.writeFileSync(outputFile, JSON.stringify(products, null, 2));

  // CSV
  const csvFile = path.join(OUTPUT_DIR, `products-deep-${timestamp}.csv`);
  const csvHeader = 'SKU,Title,Price,URL,Category,Brand\n';
  const csvRows = products.map(p => 
    `"${p.sku}","${p.title}","${p.priceFormatted}","${p.url}","${p.category}","${p.brand}"`
  ).join('\n');
  fs.writeFileSync(csvFile, csvHeader + csvRows);

  console.log(`
╔════════════════════════════════════════════════════════════╗
║  ✨ EXTRAÇÃO COMPLETA                                     ║
╚════════════════════════════════════════════════════════════╝

📊 ESTATÍSTICAS:
  • Total de produtos: ${products.length}
  • Com preço: ${products.filter(p => p.price > 0).length}

📁 ARQUIVOS:
  • JSON: ${outputFile}
  • CSV: ${csvFile}

🎉 Processo concluído!
  `);
}

main().catch(console.error);
