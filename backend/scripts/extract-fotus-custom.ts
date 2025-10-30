#!/usr/bin/env node

/**
 * Fotus Custom Extractor
 * 
 * Handles React SPA authentication flow
 * URL: https://app.fotus.com.br/login
 * 
 * Usage:
 *   npx tsx scripts/extract-fotus-custom.ts
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

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'fotus');
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function waitForNetworkIdle(page: Page, timeout: number = 3000): Promise<void> {
  let idleTimer: NodeJS.Timeout;
  let resolver: () => void;
  
  const promise = new Promise<void>((resolve) => {
    resolver = resolve;
  });

  const resetTimer = () => {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => resolver(), timeout);
  };

  page.on('request', resetTimer);
  page.on('response', resetTimer);
  
  resetTimer();

  const timeoutPromise = new Promise<void>((resolve) => {
    setTimeout(resolve, timeout * 2);
  });

  await Promise.race([promise, timeoutPromise]);
  
  page.off('request', resetTimer);
  page.off('response', resetTimer);
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

async function loginToFotus(page: Page, email: string, password: string): Promise<boolean> {
  try {
    console.log('🔐 Procurando formulário de login...');
    
    // Wait for React app to load
    await page.waitForTimeout(2000);

    // Try different input selectors for email
    const emailSelectors = [
      'input[type="email"]',
      'input[name="email"]',
      'input[name="username"]',
      'input[placeholder*="email" i]',
      'input[placeholder*="e-mail" i]',
      'input[id*="email" i]',
      'input[id*="user" i]',
    ];

    let emailFilled = false;
    for (const selector of emailSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.fill(email);
          console.log(`✅ Email preenchido (${selector})`);
          emailFilled = true;
          break;
        }
      } catch (e) {
        // Try next selector
      }
    }

    if (!emailFilled) {
      console.log('❌ Campo de email não encontrado');
      return false;
    }

    // Try different input selectors for password
    const passwordSelectors = [
      'input[type="password"]',
      'input[name="password"]',
      'input[name="senha"]',
      'input[placeholder*="senha" i]',
      'input[placeholder*="password" i]',
      'input[id*="password" i]',
      'input[id*="senha" i]',
    ];

    let passwordFilled = false;
    for (const selector of passwordSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.fill(password);
          console.log(`✅ Senha preenchida (${selector})`);
          passwordFilled = true;
          break;
        }
      } catch (e) {
        // Try next selector
      }
    }

    if (!passwordFilled) {
      console.log('❌ Campo de senha não encontrado');
      return false;
    }

    // Try to find and click submit button
    const submitSelectors = [
      'button[type="submit"]',
      'button:has-text("Entrar")',
      'button:has-text("Login")',
      'input[type="submit"]',
      '[type="submit"]',
    ];

    let submitted = false;
    for (const selector of submitSelectors) {
      try {
        const button = page.locator(selector).first();
        if (await button.isVisible({ timeout: 2000 })) {
          await button.click();
          console.log(`✅ Login enviado (${selector})`);
          submitted = true;
          break;
        }
      } catch (e) {
        // Try next selector
      }
    }

    if (!submitted) {
      console.log('❌ Botão de submit não encontrado');
      return false;
    }

    // Wait for navigation with adaptive network idle
    console.log('⏳ Aguardando resposta e estabilização da rede...');
    await waitForNetworkIdle(page, 3000);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'after-submit.png'), fullPage: true });

    // Verify login success with multiple indicators
    const loginResult = await page.evaluate(() => {
      const indicators = {
        hasLogoutLink: !!document.querySelector('[href*="logout"]'),
        hasSairLink: !!document.querySelector('[href*="sair"]'),
        hasUserMenu: !!document.querySelector('[class*="user-menu"], [class*="profile"]'),
        hasMinhaContaText: document.body.innerText.toLowerCase().includes('minha conta'),
        hasPerfilText: document.body.innerText.toLowerCase().includes('perfil'),
        hasDashboardText: document.body.innerText.toLowerCase().includes('dashboard'),
        hasProdutosText: document.body.innerText.toLowerCase().includes('produto'),
        noLoginForm: !document.querySelector('input[type="password"]'),
      };
      
      const positiveCount = Object.values(indicators).filter(v => v).length;
      
      return {
        success: positiveCount >= 3,
        indicators,
        positiveCount,
      };
    });

    console.log(`\n  📊 Indicadores de login: ${loginResult.positiveCount}/8`);
    Object.entries(loginResult.indicators).forEach(([key, value]) => {
      console.log(`    ${value ? '✅' : '❌'} ${key}`);
    });

    if (loginResult.success) {
      console.log('\n✅ Login verificado com sucesso');
      await page.screenshot({ path: path.join(OUTPUT_DIR, 'login-success.png'), fullPage: true });
      return true;
    }

    console.log('\n⚠️  Login não confirmado, aguardando verificação manual (30s)...');
    await page.waitForTimeout(30000);
    
    // Final check
    const finalCheck = await page.evaluate(() => {
      return !!document.querySelector('[href*="logout"]') ||
             document.body.innerText.toLowerCase().includes('produto');
    });
    
    return finalCheck;

  } catch (error) {
    console.log(`❌ Erro no login: ${(error as Error).message}`);
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
        const sku = skuMatch ? skuMatch[0] : `fotus-${index}`;

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
          distributor: 'fotus',
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

async function extractFotus(): Promise<void> {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  🎯 FOTUS - REACT SPA AUTHENTICATION                     ║
╚════════════════════════════════════════════════════════════╝
  `);

  const email = process.env.FOTUS_EMAIL || '';
  const password = process.env.FOTUS_PASSWORD || '';

  if (!email || !password) {
    console.log('❌ Erro: FOTUS_EMAIL e FOTUS_PASSWORD devem estar definidos');
    process.exit(1);
  }

  console.log(`👤 Email: ${email}`);
  console.log(`🌐 URL: https://app.fotus.com.br/login`);

  const browser: Browser = await chromium.launch({ 
    headless: false, // Set to false for debugging
    slowMo: 100 
  });
  
  try {
    const page = await browser.newPage();
    
    // Navigate to login page
    console.log('🌐 Navegando para a página de login...');
    await page.goto('https://app.fotus.com.br/login', { 
      waitUntil: 'domcontentloaded',
      timeout: 30000 
    });

    // Login
    const loginSuccess = await loginToFotus(page, email, password);
    
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
extractFotus().catch(console.error);
