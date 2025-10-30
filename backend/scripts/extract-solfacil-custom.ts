#!/usr/bin/env node

/**
 * Solfácil Custom Extractor
 * 
 * Handles Keycloak SSO authentication flow
 * URL: https://integrador.solfacil.com.br/
 * SSO: https://sso.solfacil.com.br/realms/General/protocol/openid-connect/auth
 * 
 * Usage:
 *   npx tsx scripts/extract-solfacil-custom.ts
 */

import { chromium, Browser, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

interface Product {
  id: string;
  sku: string;
  title: string;
  price: number;
  url: string;
  imageUrl: string;
  category: string;
  distributor: string;
}

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'solfacil');
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function categorizeProduct(title: string): string {
  const lowerTitle = title.toLowerCase();
  const categories: { [key: string]: string[] } = {
    bateria: ['bateria', 'estacionária', 'moura', 'heliar', 'freedom', 'fulguris', 'lifepo4'],
    bomba: ['bomba', 'solar', 'anauger', 'agua', 'piscina', 'submersa'],
    painel: ['painel', 'solar', 'fotovoltáico', 'módulo', 'placa'],
    inversor: ['inversor', 'inverter', 'isolada', 'hybrid', 'grid-tie', 'fronius', 'growatt'],
    estrutura: ['estrutura', 'suporte', 'trilho', 'fixação', 'mounting'],
    cabo: ['cabo', 'conduite', 'conectores', 'conector', 'MC4'],
  };

  for (const [category, keywords] of Object.entries(categories)) {
    if (keywords.some(keyword => lowerTitle.includes(keyword))) {
      return category;
    }
  }

  return 'outros';
}

async function loginToKeycloak(page: Page, email: string, password: string): Promise<boolean> {
  try {
    console.log('🔐 Aguardando redirecionamento para Keycloak SSO...');
    
    // Wait for redirect to SSO page
    await page.waitForURL('**/sso.solfacil.com.br/**', { timeout: 10000 });
    console.log('✅ Redirecionado para SSO Keycloak');

    // Wait for login form
    await page.waitForSelector('#username', { timeout: 5000 });
    console.log('✅ Formulário de login detectado');

    // Fill Keycloak login form
    await page.fill('#username', email);
    await page.fill('#password', password);
    console.log('✅ Credenciais preenchidas');

    // Submit
    await page.click('input[type="submit"]');
    console.log('🚀 Login enviado');

    // Wait for redirect back to main portal
    await page.waitForURL('**/integrador.solfacil.com.br/**', { timeout: 15000 });
    console.log('✅ Redirecionado de volta ao portal');

    // Wait for page to load
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // Verify login success
    const isLoggedIn = await page.evaluate(() => {
      return document.body.innerText.includes('Sair') || 
             document.body.innerText.includes('Logout') ||
             !!document.querySelector('[href*="logout"]');
    });

    if (isLoggedIn) {
      console.log('✅ Login verificado com sucesso');
      return true;
    }

    console.log('❌ Verificação de login falhou');
    return false;

  } catch (error) {
    console.log(`❌ Erro no login Keycloak: ${(error as Error).message}`);
    return false;
  }
}

async function extractProducts(page: Page): Promise<Product[]> {
  console.log('📦 Procurando produtos...');

  // Scroll to trigger lazy loading
  console.log('🔄 Scrolling para carregar produtos...');
  for (let i = 0; i < 50; i++) {
    await page.evaluate(() => window.scrollBy(0, window.innerHeight));
    await page.waitForTimeout(200);
  }

  // Extract products from DOM
  const products = await page.evaluate(() => {
    const items: any[] = [];
    
    // Try multiple product link patterns
    const productSelectors = [
      'a[href*="/produto"]',
      'a[href*="/product"]',
      'a[href*="item"]',
      '[data-product]',
      'div[class*="product"]',
      'div[class*="card"]',
    ];

    let productElements: Element[] = [];
    for (const selector of productSelectors) {
      const found = Array.from(document.querySelectorAll(selector));
      if (found.length > 0) {
        productElements = found;
        break;
      }
    }

    productElements.forEach((element, index) => {
      try {
        const link = element as HTMLAnchorElement;
        const href = link.href || window.location.href;
        
        // Extract SKU
        const skuMatch = href.match(/\d+/);
        const sku = skuMatch ? skuMatch[0] : `solfacil-${index}`;

        // Extract title
        let title = (element.textContent || '').trim();
        if (!title || title.length < 5) {
          const titleEl = element.querySelector('h2, h3, h4, .title, [class*="title"], [class*="name"]');
          if (titleEl) {
            title = (titleEl.textContent || '').trim();
          }
        }
        if (!title) title = `Produto ${sku}`;

        // Extract image
        let imageUrl = '';
        const img = element.querySelector('img');
        if (img && (img as HTMLImageElement).src) {
          imageUrl = (img as HTMLImageElement).src;
        }

        // Extract price
        let price = 0;
        const priceEl = element.querySelector('[class*="price"], .preco, [data-price], [class*="valor"]');
        if (priceEl) {
          const priceText = (priceEl.textContent || '').trim();
          const priceMatch = priceText.match(/[\d.,]+/);
          if (priceMatch) {
            price = parseFloat(priceMatch[0].replace('.', '').replace(',', '.'));
          }
        }

        items.push({
          sku,
          title,
          url: href,
          imageUrl,
          price: isNaN(price) ? 0 : price,
          distributor: 'solfacil',
        });
      } catch (e) {
        // Skip
      }
    });

    return items;
  });

  // Deduplicate and categorize
  const uniqueSkus = new Set<string>();
  const finalProducts = products
    .filter(p => {
      if (uniqueSkus.has(p.sku)) return false;
      uniqueSkus.add(p.sku);
      return true;
    })
    .map((p, index) => ({
      ...p,
      id: String(index),
      category: categorizeProduct(p.title),
    }));

  console.log(`✅ ${finalProducts.length} produtos extraídos`);
  return finalProducts;
}

async function extractSolfacil(): Promise<void> {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  🔐 SOLFÁCIL - KEYCLOAK SSO AUTHENTICATION               ║
╚════════════════════════════════════════════════════════════╝
  `);

  const email = process.env.SOLFACIL_EMAIL || '';
  const password = process.env.SOLFACIL_PASSWORD || '';

  if (!email || !password) {
    console.log('❌ Erro: SOLFACIL_EMAIL e SOLFACIL_PASSWORD devem estar definidos');
    process.exit(1);
  }

  console.log(`👤 Email: ${email}`);
  console.log(`🌐 URL: https://integrador.solfacil.com.br/`);

  const browser: Browser = await chromium.launch({ 
    headless: false, // Set to false for debugging
    slowMo: 100 
  });
  
  try {
    const page = await browser.newPage();
    
    // Navigate to main portal
    console.log('🌐 Navegando para o portal...');
    await page.goto('https://integrador.solfacil.com.br/', { 
      waitUntil: 'domcontentloaded',
      timeout: 30000 
    });

    // Login via Keycloak SSO
    const loginSuccess = await loginToKeycloak(page, email, password);
    
    if (!loginSuccess) {
      console.log('❌ Login falhou');
      await page.screenshot({ path: path.join(OUTPUT_DIR, 'login-failed.png'), fullPage: true });
      return;
    }

    // Extract products
    const products = await extractProducts(page);

    if (products.length === 0) {
      console.log('⚠️  Nenhum produto encontrado. Salvando screenshot para debug...');
      await page.screenshot({ path: path.join(OUTPUT_DIR, 'no-products.png'), fullPage: true });
    }

    // Save results
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const jsonFile = path.join(OUTPUT_DIR, `products-${timestamp}.json`);
    fs.writeFileSync(jsonFile, JSON.stringify(products, null, 2));

    console.log(`
╔════════════════════════════════════════════════════════════╗
║  ✨ EXTRAÇÃO CONCLUÍDA                                    ║
╚════════════════════════════════════════════════════════════╝

📊 RESUMO:
  • Total de produtos: ${products.length}
  • Arquivo salvo: ${jsonFile}

📦 CATEGORIAS:
${Object.entries(
  products.reduce((acc, p) => {
    acc[p.category] = (acc[p.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>)
).map(([cat, count]) => `  • ${cat}: ${count}`).join('\n')}

🎉 Processo concluído!
    `);

  } catch (error) {
    console.log(`❌ Erro: ${(error as Error).message}`);
    throw error;
  } finally {
    await browser.close();
  }
}

// Run
extractSolfacil().catch(console.error);
