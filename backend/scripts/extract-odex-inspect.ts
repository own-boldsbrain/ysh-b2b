#!/usr/bin/env node

/**
 * Odex Inspector - Descobrir estrutura de produtos
 */

import { chromium, Browser, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

const ODEX_LOGIN_URL = 'https://plataforma.odex.com.br/auth/login';
const ODEX_PANEL_URL = 'https://plataforma.odex.com.br/dashboard/shop/view/panel';
const ODEX_INVERTER_URL = 'https://plataforma.odex.com.br/dashboard/shop/view/inverter?q=shop';
const ODEX_EMAIL = process.env.ODEX_EMAIL || '';
const ODEX_PASSWORD = process.env.ODEX_PASSWORD || '';

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'odex-inspect');
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function quickLogin(page: Page): Promise<boolean> {
  console.log('🔐 Login rápido...');
  await page.goto(ODEX_LOGIN_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(2000);
  
  await page.fill('input[type="email"]', ODEX_EMAIL);
  await page.fill('input[type="password"]', ODEX_PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(5000);
  
  const url = page.url();
  console.log(`  URL após login: ${url}`);
  return url.includes('/dashboard');
}

async function inspectPage(page: Page, pageName: string) {
  console.log(`\n📋 Inspecionando: ${pageName}`);
  
  const structure = await page.evaluate(() => {
    const productCards = [];
    
    // Try multiple selectors for product cards
    const selectors = [
      '[class*="product"]',
      '[class*="card"]',
      '[class*="item"]',
      'article',
      '[data-product]',
      '.row > div',
    ];
    
    for (const selector of selectors) {
      const elements = Array.from(document.querySelectorAll(selector));
      if (elements.length > 0 && elements.length < 50) {
        productCards.push({
          selector,
          count: elements.length,
          samples: elements.slice(0, 3).map((el: any) => ({
            className: el.className,
            innerHTML: el.innerHTML.substring(0, 500),
            textContent: el.textContent?.substring(0, 200),
          })),
        });
      }
    }
    
    // Find all elements with price patterns
    const priceElements = [];
    const allElements = Array.from(document.querySelectorAll('*'));
    for (const el of allElements) {
      const text = el.textContent || '';
      if (/R\$\s*\d+[,.]?\d*/.test(text) && text.length < 100) {
        priceElements.push({
          tag: el.tagName,
          className: el.className,
          text: text.substring(0, 100),
        });
      }
    }
    
    // Find SKU patterns
    const skuElements = [];
    for (const el of allElements) {
      const text = el.textContent || '';
      if (/SKU#?:?\s*\d+/.test(text) && text.length < 100) {
        skuElements.push({
          tag: el.tagName,
          className: el.className,
          text: text.substring(0, 100),
        });
      }
    }
    
    return {
      productCards,
      priceElements: priceElements.slice(0, 10),
      skuElements: skuElements.slice(0, 10),
      allClasses: Array.from(new Set(
        Array.from(document.querySelectorAll('[class]'))
          .map((el: any) => el.className)
          .filter((c: string) => c && typeof c === 'string')
      )).slice(0, 50),
    };
  });
  
  const filename = path.join(OUTPUT_DIR, `${pageName}-structure.json`);
  fs.writeFileSync(filename, JSON.stringify(structure, null, 2));
  console.log(`  ✅ Salvo: ${filename}`);
  
  await page.screenshot({ 
    path: path.join(OUTPUT_DIR, `${pageName}.png`), 
    fullPage: true 
  });
  console.log(`  ✅ Screenshot: ${pageName}.png`);
  
  return structure;
}

async function main() {
  console.log('\n╔══════════════════════════════════════════╗');
  console.log('║  🔍 ODEX INSPECTOR                      ║');
  console.log('╚══════════════════════════════════════════╝\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 50,
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
  });

  const page = await context.newPage();

  try {
    const loginOk = await quickLogin(page);
    if (!loginOk) {
      console.log('❌ Login falhou');
      return;
    }
    
    console.log('✅ Login OK\n');
    
    // Inspect panels page
    await page.goto(ODEX_PANEL_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    const panelsStructure = await inspectPage(page, 'panels');
    
    console.log('\n📊 Painéis:');
    console.log(`  Cards encontrados: ${panelsStructure.productCards.length} tipos`);
    console.log(`  Preços: ${panelsStructure.priceElements.length}`);
    console.log(`  SKUs: ${panelsStructure.skuElements.length}`);
    
    // Inspect inverters page
    await page.goto(ODEX_INVERTER_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    const invertersStructure = await inspectPage(page, 'inverters');
    
    console.log('\n📊 Inversores:');
    console.log(`  Cards encontrados: ${invertersStructure.productCards.length} tipos`);
    console.log(`  Preços: ${invertersStructure.priceElements.length}`);
    console.log(`  SKUs: ${invertersStructure.skuElements.length}`);
    
    console.log('\n✅ Inspeção completa!');
    console.log(`📁 Resultados em: ${OUTPUT_DIR}`);
    
    await page.waitForTimeout(5000);
    
  } catch (error) {
    console.error('❌ Erro:', error);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'error.png'), fullPage: true });
  } finally {
    await browser.close();
  }
}

main().catch(console.error);
