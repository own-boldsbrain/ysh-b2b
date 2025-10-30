#!/usr/bin/env node

/**
 * Edeltec Deep Scraping - Extract Complete Product Details
 * 
 * Visits each product page individually to extract full metadata
 * (titles, descriptions, prices, specifications)
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
  images: string[];
  category: string;
  brand: string;
  specifications: { [key: string]: string };
  stock: string;
  distributor: string;
}

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'edeltec-deep');
const BATCH_SIZE = 10; // Process 10 products at a time

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function scrapeProductPage(page: Page, url: string, sku: string): Promise<Product | null> {
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2000); // Wait for dynamic content

    const product = await page.evaluate((productSku) => {
      const result: any = {
        sku: productSku,
        title: '',
        description: '',
        price: 0,
        priceFormatted: '',
        url: window.location.href,
        imageUrl: '',
        images: [],
        category: '',
        brand: '',
        specifications: {},
        stock: '',
      };

      // Extract title
      const titleSelectors = [
        'h1',
        '.product-title',
        '[class*="product-name"]',
        '[class*="title"]',
      ];
      
      for (const selector of titleSelectors) {
        const el = document.querySelector(selector);
        if (el && el.textContent && el.textContent.trim().length > 5) {
          result.title = el.textContent.trim();
          break;
        }
      }

      // Extract description
      const descSelectors = [
        '.product-description',
        '[class*="description"]',
        '.details',
        'meta[name="description"]',
      ];
      
      for (const selector of descSelectors) {
        const el = document.querySelector(selector);
        if (el) {
          if (el.tagName === 'META') {
            result.description = (el as HTMLMetaElement).content || '';
          } else {
            result.description = el.textContent?.trim() || '';
          }
          if (result.description.length > 10) break;
        }
      }

      // Extract price
      const priceSelectors = [
        '.price',
        '[class*="price"]',
        '[data-price]',
        '.valor',
      ];
      
      for (const selector of priceSelectors) {
        const el = document.querySelector(selector);
        if (el) {
          const priceText = el.textContent?.trim() || '';
          result.priceFormatted = priceText;
          
          // Extract numeric value
          const priceMatch = priceText.match(/[\d.,]+/);
          if (priceMatch) {
            const numericPrice = priceMatch[0].replace(/\./g, '').replace(',', '.');
            result.price = parseFloat(numericPrice);
          }
          break;
        }
      }

      // Extract main image
      const imgSelectors = [
        'img.product-image',
        '.product-gallery img',
        '[class*="product"] img',
        'img[src*="produto"]',
      ];
      
      for (const selector of imgSelectors) {
        const img = document.querySelector(selector) as HTMLImageElement;
        if (img && img.src && !img.src.includes('placeholder')) {
          result.imageUrl = img.src;
          break;
        }
      }

      // Extract all images
      const allImages = document.querySelectorAll('img');
      allImages.forEach(img => {
        if (img.src && !img.src.includes('placeholder') && !img.src.includes('logo')) {
          result.images.push(img.src);
        }
      });
      result.images = [...new Set(result.images)]; // Deduplicate

      // Extract brand
      const brandSelectors = [
        '.brand',
        '[class*="brand"]',
        '[class*="manufacturer"]',
      ];
      
      for (const selector of brandSelectors) {
        const el = document.querySelector(selector);
        if (el && el.textContent) {
          result.brand = el.textContent.trim();
          break;
        }
      }

      // Extract specifications
      const specTables = document.querySelectorAll('table, .specifications, [class*="spec"]');
      specTables.forEach(table => {
        const rows = table.querySelectorAll('tr, li, .spec-item');
        rows.forEach(row => {
          const cells = row.querySelectorAll('td, th, span, div');
          if (cells.length >= 2) {
            const key = cells[0].textContent?.trim() || '';
            const value = cells[1].textContent?.trim() || '';
            if (key && value && key.length < 50) {
              result.specifications[key] = value;
            }
          }
        });
      });

      // Extract stock status
      const stockSelectors = [
        '.stock',
        '[class*="stock"]',
        '[class*="availability"]',
        '.disponibilidade',
      ];
      
      for (const selector of stockSelectors) {
        const el = document.querySelector(selector);
        if (el && el.textContent) {
          result.stock = el.textContent.trim();
          break;
        }
      }

      return result;
    }, sku);

    return {
      ...product,
      distributor: 'edeltec',
    } as Product;

  } catch (error) {
    console.log(`   ❌ Error scraping ${url}: ${(error as Error).message}`);
    return null;
  }
}

function categorizeProduct(title: string): string {
  const lowerTitle = title.toLowerCase();
  const categories: { [key: string]: string[] } = {
    inversor: ['inversor', 'inverter'],
    modulo: ['módulo', 'modulo', 'painel', 'placa solar'],
    bateria: ['bateria', 'battery', 'lifepo4', 'lithium'],
    gerador: ['gerador', 'generator'],
    cabo: ['cabo', 'cable', 'conector', 'connector'],
    estrutura: ['estrutura', 'structure', 'suporte', 'mounting'],
    stringbox: ['string box', 'stringbox'],
    transformador: ['transformador', 'transformer'],
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
║  🔍 EDELTEC DEEP SCRAPING - DETALHES COMPLETOS            ║
╚════════════════════════════════════════════════════════════╝
  `);

  // Load base extraction
  const baseFiles = fs.readdirSync('output/edeltec').filter(f => f.endsWith('.json'));
  if (baseFiles.length === 0) {
    console.log('❌ No base extraction found. Run extract-all-distributors.ts first.');
    return;
  }

  const latestFile = baseFiles.sort().reverse()[0];
  const baseProducts = JSON.parse(fs.readFileSync(path.join('output/edeltec', latestFile), 'utf-8'));
  
  console.log(`📦 Base products: ${baseProducts.length}`);
  console.log(`📋 Processing in batches of ${BATCH_SIZE}\n`);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // Login (reuse session)
  const email = process.env.EDELTEC_EMAIL || '';
  const password = process.env.EDELTEC_PASSWORD || '';

  if (!email || !password) {
    console.log('❌ EDELTEC_EMAIL and EDELTEC_PASSWORD required');
    await browser.close();
    return;
  }

  console.log('🔐 Logging in to Edeltec...');
  await page.goto('https://edeltecsolar.com.br/', { waitUntil: 'domcontentloaded' });
  
  // Check if already logged in
  const isLoggedIn = await page.evaluate(() => {
    return !!document.querySelector('a[href*="logout"], [class*="user-menu"]');
  });

  if (!isLoggedIn) {
    console.log('🔐 Attempting login...');
    // Login logic here if needed
  } else {
    console.log('✅ Already logged in\n');
  }

  const detailedProducts: Product[] = [];
  const errors: { url: string; error: string }[] = [];
  let processed = 0;

  for (let i = 0; i < baseProducts.length; i += BATCH_SIZE) {
    const batch = baseProducts.slice(i, i + BATCH_SIZE);
    console.log(`📦 Batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(baseProducts.length / BATCH_SIZE)}`);

    for (const baseProduct of batch) {
      processed++;
      console.log(`   [${processed}/${baseProducts.length}] ${baseProduct.url}`);

      const detailed = await scrapeProductPage(page, baseProduct.url, baseProduct.sku);
      
      if (detailed) {
        detailed.category = categorizeProduct(detailed.title);
        detailedProducts.push(detailed);
        console.log(`   ✅ ${detailed.title.substring(0, 60)}...`);
      } else {
        errors.push({ url: baseProduct.url, error: 'Failed to scrape' });
      }

      await page.waitForTimeout(1000); // Rate limiting
    }

    // Save progress after each batch
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const progressFile = path.join(OUTPUT_DIR, `products-detailed-progress-${timestamp}.json`);
    fs.writeFileSync(progressFile, JSON.stringify(detailedProducts, null, 2));
    console.log(`   💾 Progress saved (${detailedProducts.length} products)\n`);
  }

  await browser.close();

  // Final save
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = path.join(OUTPUT_DIR, `products-detailed-${timestamp}.json`);
  fs.writeFileSync(outputFile, JSON.stringify(detailedProducts, null, 2));

  // Save errors
  if (errors.length > 0) {
    const errorsFile = path.join(OUTPUT_DIR, `errors-${timestamp}.json`);
    fs.writeFileSync(errorsFile, JSON.stringify(errors, null, 2));
  }

  // Statistics
  const withPrice = detailedProducts.filter(p => p.price > 0).length;
  const withDescription = detailedProducts.filter(p => p.description.length > 10).length;
  const withSpecs = detailedProducts.filter(p => Object.keys(p.specifications).length > 0).length;

  console.log(`
╔════════════════════════════════════════════════════════════╗
║  ✨ DEEP SCRAPING COMPLETO                                ║
╚════════════════════════════════════════════════════════════╝

📊 ESTATÍSTICAS:
  • Total processado: ${processed}
  • Sucesso: ${detailedProducts.length}
  • Falhas: ${errors.length}
  
📋 QUALIDADE DOS DADOS:
  • Com preço: ${withPrice} (${((withPrice/detailedProducts.length)*100).toFixed(1)}%)
  • Com descrição: ${withDescription} (${((withDescription/detailedProducts.length)*100).toFixed(1)}%)
  • Com especificações: ${withSpecs} (${((withSpecs/detailedProducts.length)*100).toFixed(1)}%)

📁 ARQUIVOS:
  • Produtos: ${outputFile}
  • Erros: ${errors.length > 0 ? `${errors.length} URLs falharam` : 'Nenhum'}

🎉 Processo concluído!
  `);
}

main().catch(console.error);
