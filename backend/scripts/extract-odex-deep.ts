#!/usr/bin/env node

/**
 * Odex Deep Scraping - Navigate Categories and Extract Products
 * 
 * Explores product categories and extracts individual items
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
  distributor: string;
}

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'odex-deep');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function extractCategories(page: Page): Promise<string[]> {
  const categories = await page.evaluate(() => {
    const categoryLinks: string[] = [];
    
    // Find category links
    const selectors = [
      'a[href*="/categoria"]',
      'a[href*="/products"]',
      'a[href*="/produtos"]',
      '.category a',
      '[class*="category"] a',
    ];

    for (const selector of selectors) {
      const links = document.querySelectorAll(selector);
      links.forEach(link => {
        const href = (link as HTMLAnchorElement).href;
        if (href && !categoryLinks.includes(href)) {
          categoryLinks.push(href);
        }
      });
      
      if (categoryLinks.length > 0) break;
    }

    return categoryLinks;
  });

  return categories;
}

async function extractProductsFromPage(page: Page, categoryName: string): Promise<Product[]> {
  // Scroll to load all products
  for (let i = 0; i < 30; i++) {
    await page.evaluate(() => window.scrollBy(0, window.innerHeight));
    await page.waitForTimeout(300);
  }

  const products = await page.evaluate((catName) => {
    const items: any[] = [];
    
    const productSelectors = [
      'a[href*="/produto"]',
      'a[href*="/product"]',
      '[class*="product"] a',
      '.card a',
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
          const parent = link.closest('[class*="product"], .card');
          const titleEl = parent?.querySelector('h1, h2, h3, h4, .title');
          if (titleEl) {
            title = (titleEl.textContent || '').trim();
          }
        }

        // Extract SKU
        const skuMatch = href.match(/\d+/);
        const sku = skuMatch ? skuMatch[0] : `odex-${catName}-${index}`;

        // Extract image
        let imageUrl = '';
        const parent = link.closest('[class*="product"], .card');
        const img = parent?.querySelector('img') as HTMLImageElement;
        if (img && img.src) {
          imageUrl = img.src;
        }

        // Extract price
        let price = 0;
        let priceFormatted = '';
        const priceEl = parent?.querySelector('[class*="price"], .preco');
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
            category: catName,
          });
        }
      } catch (e) {
        // Skip
      }
    });

    return items;
  }, categoryName);

  return products.map(p => ({
    ...p,
    description: '',
    distributor: 'odex',
  }));
}

async function main() {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  🔍 ODEX DEEP SCRAPING - NAVEGAÇÃO POR CATEGORIAS         ║
╚════════════════════════════════════════════════════════════╝
  `);

  const email = process.env.ODEX_EMAIL || '';
  const password = process.env.ODEX_PASSWORD || '';

  if (!email || !password) {
    console.log('❌ ODEX_EMAIL and ODEX_PASSWORD required');
    return;
  }

  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('🔐 Navigating to Odex...');
  await page.goto('https://odex.com.br/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3000);

  // Check if needs login
  const needsLogin = await page.evaluate(() => {
    return !document.querySelector('a[href*="logout"]');
  });

  if (needsLogin) {
    console.log('🔐 Attempting login...');
    // Add login logic if needed
  } else {
    console.log('✅ Already logged in');
  }

  console.log('\n📂 Finding categories...');
  const categories = await extractCategories(page);
  console.log(`✅ Found ${categories.length} categories\n`);

  const allProducts: Product[] = [];

  for (let i = 0; i < Math.min(categories.length, 10); i++) {
    const categoryUrl = categories[i];
    const categoryName = categoryUrl.split('/').pop() || `category-${i}`;
    
    console.log(`📦 [${i + 1}/${Math.min(categories.length, 10)}] ${categoryName}`);
    
    try {
      await page.goto(categoryUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(2000);

      const products = await extractProductsFromPage(page, categoryName);
      allProducts.push(...products);
      
      console.log(`   ✅ ${products.length} products found`);
    } catch (error) {
      console.log(`   ❌ Error: ${(error as Error).message}`);
    }
  }

  await browser.close();

  // Deduplicate
  const uniqueProducts = Array.from(
    new Map(allProducts.map(p => [p.sku, p])).values()
  );

  console.log(`\n✅ Total unique products: ${uniqueProducts.length}\n`);

  // Save
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = path.join(OUTPUT_DIR, `products-deep-${timestamp}.json`);
  fs.writeFileSync(outputFile, JSON.stringify(uniqueProducts, null, 2));

  // CSV
  const csvFile = path.join(OUTPUT_DIR, `products-deep-${timestamp}.csv`);
  const csvHeader = 'SKU,Title,Price,URL,Category\n';
  const csvRows = uniqueProducts.map(p => 
    `"${p.sku}","${p.title}","${p.priceFormatted}","${p.url}","${p.category}"`
  ).join('\n');
  fs.writeFileSync(csvFile, csvHeader + csvRows);

  console.log(`
╔════════════════════════════════════════════════════════════╗
║  ✨ EXTRAÇÃO COMPLETA                                     ║
╚════════════════════════════════════════════════════════════╝

📊 ESTATÍSTICAS:
  • Categorias exploradas: ${Math.min(categories.length, 10)}
  • Total de produtos: ${uniqueProducts.length}
  • Com preço: ${uniqueProducts.filter(p => p.price > 0).length}

📁 ARQUIVOS:
  • JSON: ${outputFile}
  • CSV: ${csvFile}

🎉 Processo concluído!
  `);
}

main().catch(console.error);
