#!/usr/bin/env node

/**
 * Odex Debug Script - Manual Login Inspection
 * 
 * Este script possui recursos avançados de debug para ajudar a resolver problemas de autenticação:
 * - Browser sempre visível (headless: false)
 * - Screenshots detalhados em cada etapa
 * - Logs verbosos de todos os elementos HTML
 * - Pausas prolongadas para inspeção manual
 * - Detecção de múltiplos indicadores de login
 * - Forçamento de visibilidade do campo senha via JavaScript
 * 
 * Usage:
 *   $envContent = Get-Content mcp-servers\.env; foreach($line in $envContent) { if($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }; npx tsx scripts/extract-odex-debug.ts
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
  currency: string;
  stock: {
    available: boolean;
    status: string;
  };
  images: string[];
  specifications: Record<string, string>;
  category: string;
  brand?: string;
  url: string;
  distributor: string;
  extractedAt: string;
}

const ODEX_LOGIN_URL = 'https://plataforma.odex.com.br/auth/login';
const ODEX_PANEL_URL = 'https://plataforma.odex.com.br/dashboard/shop/view/panel';
const ODEX_INVERTER_URL = 'https://plataforma.odex.com.br/dashboard/shop/view/inverter?q=shop';
const ODEX_EMAIL = process.env.ODEX_EMAIL || '';
const ODEX_PASSWORD = process.env.ODEX_PASSWORD || '';

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'odex-debug');
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
    cabo: ['cabo', 'wire', 'fio', 'condutor'],
    conector: ['conector', 'mc4', 'connector'],
    carregador: ['carregador', 'charger', 'controlador', 'mppt'],
  };

  for (const [category, keywords] of Object.entries(categories)) {
    if (keywords.some(keyword => lowerTitle.includes(keyword))) {
      return category;
    }
  }

  return 'outros';
}

async function captureDetailedPageInfo(page: Page, stepName: string): Promise<void> {
  console.log(`\n📸 [${stepName}] Capturando informações da página...\n`);
  
  await page.screenshot({ 
    path: path.join(OUTPUT_DIR, `${stepName}.png`), 
    fullPage: true 
  });
  console.log(`  ✓ Screenshot salvo: ${stepName}.png`);
  
  const pageInfo = await page.evaluate(() => {
    const info: any = {
      url: window.location.href,
      title: document.title,
      inputs: [],
      buttons: [],
      links: [],
      forms: [],
      bodyTextSample: document.body.innerText.substring(0, 500),
    };
    
    document.querySelectorAll('input').forEach((inp, i) => {
      info.inputs.push({
        index: i,
        type: inp.type,
        name: inp.name,
        id: inp.id,
        placeholder: inp.placeholder,
        value: inp.value ? '***' : '',
        visible: inp.offsetParent !== null,
        disabled: inp.disabled,
      });
    });
    
    document.querySelectorAll('button').forEach((btn, i) => {
      info.buttons.push({
        index: i,
        type: btn.type,
        text: btn.textContent?.trim() || '',
        className: btn.className,
        visible: btn.offsetParent !== null,
        disabled: btn.disabled,
      });
    });
    
    document.querySelectorAll('a').forEach((link, i) => {
      const href = link.href;
      const text = link.textContent?.trim() || '';
      if (href && (
        href.includes('login') || 
        href.includes('logout') || 
        href.includes('sair') ||
        text.toLowerCase().includes('entrar')
      )) {
        info.links.push({
          index: i,
          href,
          text,
        });
      }
    });
    
    document.querySelectorAll('form').forEach((form, i) => {
      info.forms.push({
        index: i,
        action: form.action,
        method: form.method,
        inputCount: form.querySelectorAll('input').length,
      });
    });
    
    return info;
  });
  
  fs.writeFileSync(
    path.join(OUTPUT_DIR, `${stepName}-info.json`),
    JSON.stringify(pageInfo, null, 2)
  );
  console.log(`  ✓ Informações salvas: ${stepName}-info.json`);
  
  console.log(`\n  📋 URL: ${pageInfo.url}`);
  console.log(`  📋 Título: ${pageInfo.title}`);
  console.log(`  📋 Inputs: ${pageInfo.inputs.length} | Botões: ${pageInfo.buttons.length} | Links: ${pageInfo.links.length}\n`);
}

async function loginWithDebug(page: Page): Promise<boolean> {
  try {
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║  🔐 ODEX - DEBUG MODE ATIVADO                            ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    if (!ODEX_EMAIL || !ODEX_PASSWORD) {
      throw new Error('ODEX_EMAIL e ODEX_PASSWORD devem estar definidos');
    }

    console.log(`👤 Email: ${ODEX_EMAIL}`);
    console.log(`🌐 URL: ${ODEX_LOGIN_URL}\n`);

    // Navigate
    console.log('📍 PASSO 1: Navegando...');
    await page.goto(ODEX_LOGIN_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);
    await captureDetailedPageInfo(page, '01-initial-page');

    // Check if already logged in
    const alreadyLoggedIn = await page.evaluate(() => {
      return !!document.querySelector('[href*="logout"], [href*="sair"]') ||
             document.body.innerText.toLowerCase().includes('minha conta');
    });

    if (alreadyLoggedIn) {
      console.log('✅ Já está logado!\n');
      return true;
    }

    // Try to click login link to open form
    console.log('📍 PASSO 2: Procurando link de login...');
    const loginSelectors = [
      'a:has-text("Entrar")',
      'a:has-text("Login")',
      '[href*="login"]',
      '[href*="customer/account"]',
      '.authorization-link a',
    ];

    for (const selector of loginSelectors) {
      try {
        const link = page.locator(selector).first();
        if (await link.isVisible({ timeout: 2000 })) {
          console.log(`  ✓ Clicando: ${selector}`);
          await link.click();
          await page.waitForTimeout(3000);
          await captureDetailedPageInfo(page, '02-after-login-click');
          break;
        }
      } catch (e) { }
    }

    // Fill email
    console.log('📍 PASSO 3: Preenchendo EMAIL...');
    const emailSelectors = [
      'input[type="email"]',
      'input[name="email"]',
      'input[name="username"]',
      'input[placeholder*="email" i]',
      'input[id*="email"]',
    ];

    let emailFilled = false;
    for (const selector of emailSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.fill(ODEX_EMAIL);
          console.log(`  ✅ Email preenchido: ${selector}`);
          emailFilled = true;
          await captureDetailedPageInfo(page, '03-email-filled');
          break;
        }
      } catch (e) { }
    }

    if (!emailFilled) {
      console.log('❌ Email não preenchido');
      await captureDetailedPageInfo(page, '03-email-FAILED');
      await page.waitForTimeout(60000);
      return false;
    }

    // Fill password with JavaScript force
    console.log('📍 PASSO 4: Preenchendo SENHA (com forçamento JS)...');
    await page.waitForTimeout(2000);
    
    const jsResult = await page.evaluate((password) => {
      const passInput = document.querySelector('input#pass') as HTMLInputElement;
      if (passInput) {
        // Force visibility
        passInput.style.display = 'block';
        passInput.style.visibility = 'visible';
        passInput.style.opacity = '1';
        passInput.type = 'text';
        
        // Set value
        passInput.value = password;
        passInput.dispatchEvent(new Event('input', { bubbles: true }));
        passInput.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Restore password type
        setTimeout(() => { passInput.type = 'password'; }, 500);
        
        return { success: true, visible: passInput.offsetParent !== null };
      }
      return { success: false, visible: false };
    }, ODEX_PASSWORD);
    
    if (jsResult.success) {
      console.log(`  ✅ Senha preenchida via JS (visível: ${jsResult.visible})`);
      await page.waitForTimeout(500);
      await captureDetailedPageInfo(page, '04-password-filled');
    } else {
      console.log('  ⚠️  Falha ao preencher senha via JS, tentando seletores...');
      
      const passwordSelectors = [
        'input[type="password"]',
        'input[name="password"]',
        'input[name="senha"]',
        'input[id="pass"]',
      ];

      let passwordFilled = false;
      for (const selector of passwordSelectors) {
        try {
          const input = page.locator(selector).first();
          if (await input.isVisible({ timeout: 2000 })) {
            await input.fill(ODEX_PASSWORD);
            console.log(`  ✅ Senha preenchida: ${selector}`);
            passwordFilled = true;
            break;
          }
        } catch (e) { }
      }

      if (!passwordFilled) {
        console.log('❌ Senha não preenchida');
        await captureDetailedPageInfo(page, '04-password-FAILED');
        await page.waitForTimeout(60000);
        return false;
      }
    }

    // Submit
    console.log('📍 PASSO 5: Submetendo...');
    await page.click('button[type="submit"]').catch(() => {});
    await page.keyboard.press('Enter').catch(() => {});
    
    console.log('⏳ Aguardando (10s)...');
    await page.waitForTimeout(10000).catch(() => {});
    
    try {
      await captureDetailedPageInfo(page, '05-after-submit');
    } catch (err) {
      console.log('⚠️  Não foi possível capturar informações (página pode ter sido redirecionada)');
    }

    // Verify
    const indicators = await page.evaluate(() => {
      return {
        hasLogout: !!document.querySelector('[href*="logout"]'),
        hasSair: !!document.querySelector('[href*="sair"]'),
        hasCustomerName: !!document.querySelector('.customer-name'),
        hasLoggedClass: !!document.querySelector('[class*="logged"]'),
        hasMinhaContaText: document.body.innerText.toLowerCase().includes('minha conta'),
        hasSairText: document.body.innerText.toLowerCase().includes('sair'),
        noLoginText: !document.body.innerText.toLowerCase().includes('login'),
        currentUrl: window.location.href,
      };
    }).catch(() => {
      console.log('⚠️  Erro ao avaliar indicadores, assumindo login falhou');
      return {
        hasLogout: false,
        hasSair: false,
        hasCustomerName: false,
        hasLoggedClass: false,
        hasMinhaContaText: false,
        hasSairText: false,
        noLoginText: false,
        currentUrl: '',
      };
    });

    console.log('\n📊 Indicadores:');
    Object.entries(indicators).forEach(([key, value]) => {
      console.log(`  ${value ? '✅' : '❌'} ${key}: ${value}`);
    });

    const positiveCount = Object.values(indicators).filter(i => typeof i === 'boolean' && i).length;
    console.log(`\n📈 Positivos: ${positiveCount}/7`);

    // Check URL as primary indicator (redirects to /dashboard after login)
    const currentUrl = page.url();
    const urlIndicatesSuccess = currentUrl.includes('/dashboard');
    
    if (positiveCount >= 2 || urlIndicatesSuccess) {
      console.log('\n✅ LOGIN BEM-SUCEDIDO!\n');
      await captureDetailedPageInfo(page, '06-login-success');
      
      // Navigate to products pages
      console.log('📍 PASSO 7: Navegando para página de painéis...');
      await page.goto(ODEX_PANEL_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(3000);
      await captureDetailedPageInfo(page, '07-panels-page');
      
      console.log('📍 PASSO 8: Navegando para página de inversores...');
      await page.goto(ODEX_INVERTER_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(3000);
      await captureDetailedPageInfo(page, '08-inverters-page');
      
      return true;
    } else {
      console.log('\n⚠️  LOGIN INCERTO - VERIFICANDO (30s)...\n');
      await captureDetailedPageInfo(page, '06-login-UNCERTAIN');
      await page.waitForTimeout(30000);
      
      const finalUrl = page.url();
      const finalCheck = finalUrl.includes('/dashboard') || await page.evaluate(() => {
        return !!document.querySelector('[href*="logout"]') ||
               document.body.innerText.toLowerCase().includes('minha conta');
      });
      
      if (finalCheck) {
        console.log('✅ Login confirmado\n');
        
        console.log('📍 Navegando para página de painéis...');
        await page.goto(ODEX_PANEL_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(3000);
        await captureDetailedPageInfo(page, '07-panels-page');
        
        console.log('📍 Navegando para página de inversores...');
        await page.goto(ODEX_INVERTER_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(3000);
        await captureDetailedPageInfo(page, '08-inverters-page');
      }
      
      return finalCheck;
    }

  } catch (error) {
    console.error(`\n❌ ERRO: ${(error as Error).message}\n`);
    await captureDetailedPageInfo(page, 'ERROR-login');
    await page.waitForTimeout(60000);
    return false;
  }
}

async function extractProductsFromList(page: Page): Promise<DetailedProduct[]> {
  console.log('\n📦 Extraindo produtos da lista...');

  const products = await page.evaluate(() => {
    const productData: any[] = [];
    
    // Get all text and normalize whitespace
    const allText = document.body.innerText;
    
    // Pattern: SKU#: 289244 PAINEL SOLAR... R$ 490,00
    // Use multiline regex to handle line breaks
    const regex = /SKU#?:\s*(\d+)\s+([\s\S]{1,200}?)\s+R\$\s*([\d.,]+)/g;
    const matches = allText.matchAll(regex);
    
    for (const match of matches) {
      const sku = match[1];
      const title = match[2].replace(/\n/g, ' ').trim();
      const priceText = match[3].replace(/\./g, '').replace(',', '.');
      const price = parseFloat(priceText);
      
      // Only add if we have all required fields
      if (sku && title && price && !isNaN(price)) {
        productData.push({
          sku,
          title,
          price,
        });
      }
    }
    
    return productData;
  });

  const currentUrl = page.url();
  const distributor = 'odex';
  const timestamp = new Date().toISOString();
  
  const detailedProducts: DetailedProduct[] = products.map((p, index) => {
    const title = p.title || 'Produto sem nome';
    return {
      id: `odex-${p.sku || index}`,
      sku: p.sku || '',
      title: title,
      description: '',
      price: p.price || 0,
      currency: 'BRL',
      stock: {
        available: p.price > 0,
        status: p.price > 0 ? 'available' : 'unavailable',
      },
      images: [],
      specifications: {},
      category: categorizeProduct(title),
      brand: '',
      url: currentUrl,
      distributor,
      extractedAt: timestamp,
    };
  });

  console.log(`✅ ${detailedProducts.length} produtos extraídos\n`);
  return detailedProducts;
}

async function extractProductDetails(page: Page, productUrl: string): Promise<DetailedProduct | null> {
  try {
    await page.goto(productUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(2000);

    const data = await page.evaluate(() => {
      const title = document.querySelector('h1')?.textContent?.trim() || '';
      const priceText = document.querySelector('[class*="price"]')?.textContent?.trim() || '';
      
      const images: string[] = [];
      document.querySelectorAll('img').forEach(img => {
        if (img.src && !img.src.includes('logo')) {
          images.push(img.src);
        }
      });

      const specs: Record<string, string> = {};
      document.querySelectorAll('table tr').forEach(row => {
        const cells = row.querySelectorAll('th, td');
        if (cells.length >= 2) {
          const k = cells[0].textContent?.trim();
          const v = cells[1].textContent?.trim();
          if (k && v) specs[k] = v;
        }
      });

      return { title, priceText, images, specs };
    });

    let price = 0;
    if (data.priceText) {
      const m = data.priceText.match(/[\d.,]+/);
      if (m) price = parseFloat(m[0].replace(/\./g, '').replace(',', '.'));
    }

    return {
      id: `odex-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      sku: '',
      title: data.title,
      description: '',
      price,
      currency: 'BRL',
      stock: { available: price > 0, status: price > 0 ? 'disponível' : 'indisponível' },
      images: data.images,
      specifications: data.specs,
      category: categorizeProduct(data.title),
      url: productUrl,
      distributor: 'odex',
      extractedAt: new Date().toISOString(),
    };

  } catch (error) {
    return null;
  }
}

async function main() {
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║  🚀 ODEX DEBUG - DIAGNÓSTICO COMPLETO                    ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 100,
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  });

  const page = await context.newPage();

  try {
    const loginSuccess = await loginWithDebug(page);
    if (!loginSuccess) {
      throw new Error('Login falhou');
    }

    const allProducts: DetailedProduct[] = [];
    
    // Extract from panels page
    const panelsProducts = await extractProductsFromList(page);
    allProducts.push(...panelsProducts);
    
    // Extract from inverters page  
    console.log('\n📍 Navegando para inversores...');
    await page.goto(ODEX_INVERTER_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    const invertersProducts = await extractProductsFromList(page);
    allProducts.push(...invertersProducts);
    
    console.log(`\n✅ Total: ${allProducts.length} produtos`);

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputFile = path.join(OUTPUT_DIR, `odex-products-${timestamp}.json`);
    
    fs.writeFileSync(outputFile, JSON.stringify({
      distributor: 'odex',
      extractedAt: new Date().toISOString(),
      totalProductsFound: productLinks.length,
      totalProductsExtracted: allProducts.length,
      products: allProducts,
    }, null, 2));

    console.log(`\n✅ Concluído! ${allProducts.length} produtos\n`);
    console.log(`📁 ${outputFile}\n`);

  } catch (error) {
    console.error(`\n❌ ${(error as Error).message}`);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'error.png'), fullPage: true });
  } finally {
    console.log('💡 Fechando em 10s...');
    await page.waitForTimeout(10000);
    await browser.close();
  }
}

main();
