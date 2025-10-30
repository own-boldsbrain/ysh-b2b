#!/usr/bin/env node

/**
 * Odex Category Navigation Script
 * 
 * Navigates through all product categories on Odex B2B portal and extracts
 * detailed product information from each category.
 * 
 * Strategy:
 * 1. Login to Odex portal
 * 2. Find all category links
 * 3. For each category, navigate and extract product links
 * 4. For each product, extract detailed information
 * 
 * Usage:
 *   Set credentials in mcp-servers/.env:
 *     ODEX_EMAIL=your@email.com
 *     ODEX_PASSWORD=yourpassword
 *   
 *   Then run:
 *   $envContent = Get-Content mcp-servers\.env; foreach($line in $envContent) { if($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }; npx tsx scripts/extract-odex-categories.ts
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

interface CategoryInfo {
  name: string;
  url: string;
  productCount: number;
}

const ODEX_URL = 'https://odex.com.br/';
const ODEX_EMAIL = process.env.ODEX_EMAIL || '';
const ODEX_PASSWORD = process.env.ODEX_PASSWORD || '';

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'odex-categories');
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

async function login(page: Page): Promise<boolean> {
  try {
    console.log('🔐 Realizando login no Odex...');
    console.log('📸 Screenshots serão salvos em cada etapa para debug');

    if (!ODEX_EMAIL || !ODEX_PASSWORD) {
      throw new Error('ODEX_EMAIL e ODEX_PASSWORD devem estar definidos');
    }

    await page.goto(ODEX_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);
    await page.screenshot({ path: path.join(OUTPUT_DIR, '01-initial-page.png'), fullPage: true });
    console.log('📸 Screenshot: 01-initial-page.png');

    // Check if already logged in
    const alreadyLoggedIn = await page.evaluate(() => {
      return !!document.querySelector('[href*="logout"], [href*="sair"]') ||
             document.body.innerText.toLowerCase().includes('minha conta');
    });

    if (alreadyLoggedIn) {
      console.log('✅ Já logado no Odex');
      return true;
    }

    // Try to find and click login button/link to open login form
    const loginSelectors = [
      'a:has-text("Entrar")',
      'a:has-text("Login")',
      'a:has-text("Fazer login")',
      'button:has-text("Entrar")',
      '[href*="login"]',
      '[href*="customer/account"]',
      '.authorization-link a',
    ];

    let loginFormOpened = false;
    for (const selector of loginSelectors) {
      try {
        const loginButton = page.locator(selector).first();
        if (await loginButton.isVisible({ timeout: 2000 })) {
          console.log(`✓ Clicando em botão de login: ${selector}`);
          await loginButton.click();
          await page.waitForTimeout(3000);
          await page.screenshot({ path: path.join(OUTPUT_DIR, '02-after-login-click.png'), fullPage: true });
          console.log('📸 Screenshot: 02-after-login-click.png');
          loginFormOpened = true;
          break;
        }
      } catch (e) { 
        console.log(`  × Link de login não encontrado: ${selector}`);
      }
    }

    // List all form elements for debugging
    const formInfo = await page.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll('input')).map(i => ({
        type: i.type,
        name: i.name,
        id: i.id,
        placeholder: i.placeholder,
        visible: i.offsetParent !== null,
      }));
      return { inputs };
    });
    
    console.log('📋 Inputs encontrados:', JSON.stringify(formInfo.inputs, null, 2));

    // Fill email
    const emailSelectors = [
      'input[type="email"]',
      'input[name="email"]',
      'input[name="username"]',
      'input[placeholder*="email" i]',
      'input[placeholder*="e-mail" i]',
    ];

    let emailFilled = false;
    for (const selector of emailSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.fill(ODEX_EMAIL);
          emailFilled = true;
          console.log(`✓ Email preenchido com seletor: ${selector}`);
          await page.screenshot({ path: path.join(OUTPUT_DIR, '03-email-filled.png'), fullPage: true });
          console.log('📸 Screenshot: 03-email-filled.png');
          break;
        }
      } catch (e) { 
        console.log(`  × Seletor ${selector} não funcionou`);
      }
    }

    if (!emailFilled) {
      await page.screenshot({ path: path.join(OUTPUT_DIR, '03-email-not-found.png'), fullPage: true });
      throw new Error('Campo de email não encontrado');
    }

    // Fill password - try forcing visibility via JavaScript
    await page.waitForTimeout(2000);
    
    let passwordFilled = false;
    
    // Try forcing visibility and filling via JavaScript first
    try {
      const jsResult = await page.evaluate((password) => {
        const passInput = document.querySelector('input#pass') as HTMLInputElement;
        if (passInput) {
          // Force visibility
          passInput.style.display = 'block';
          passInput.style.visibility = 'visible';
          passInput.style.opacity = '1';
          passInput.type = 'text'; // Temporarily change to text for debugging
          
          // Set value
          passInput.value = password;
          
          // Trigger events
          passInput.dispatchEvent(new Event('input', { bubbles: true }));
          passInput.dispatchEvent(new Event('change', { bubbles: true }));
          
          // Change back to password
          setTimeout(() => { passInput.type = 'password'; }, 500);
          
          return { success: true, visible: passInput.offsetParent !== null };
        }
        return { success: false, visible: false };
      }, ODEX_PASSWORD);
      
      if (jsResult.success) {
        passwordFilled = true;
        console.log(`✓ Senha preenchida via JavaScript (visível: ${jsResult.visible})`);
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(OUTPUT_DIR, '04-password-filled-js.png'), fullPage: true });
        console.log('📸 Screenshot: 04-password-filled-js.png');
      }
    } catch (e) {
      console.log(`  × Falha ao preencher via JavaScript: ${(e as Error).message}`);
    }
    
    if (!passwordFilled) {
      await page.screenshot({ path: path.join(OUTPUT_DIR, '04-password-not-found.png'), fullPage: true });
      console.log('⚠️  Campo de senha não foi preenchido');
      console.log('💡 Por favor, observe o browser e o screenshot');
      console.log('� O browser permanecerá aberto por 30 segundos para inspeção...');
      await page.waitForTimeout(30000);
      throw new Error('Campo de senha não encontrado');
    }

    // Submit form
    console.log('⏳ Submetendo formulário de login...');
    await page.click('button[type="submit"]').catch(() => {
      console.log('  × Botão submit não encontrado via click, tentando Enter');
    });
    
    // Also try pressing Enter on the password field
    await page.keyboard.press('Enter').catch(() => {});
    
    console.log('⏳ Aguardando resposta do servidor (10 segundos)...');
    await page.waitForTimeout(10000);
    await page.screenshot({ path: path.join(OUTPUT_DIR, '05-after-submit.png'), fullPage: true });
    console.log('📸 Screenshot: 05-after-submit.png');

    // Verify login with multiple checks
    const loginSuccess = await page.evaluate(() => {
      const indicators = {
        hasLogoutLink: !!document.querySelector('[href*="logout"]'),
        hasSairLink: !!document.querySelector('[href*="sair"]'),
        hasCustomerName: !!document.querySelector('.customer-name'),
        hasLoggedClass: !!document.querySelector('[class*="logged"]'),
        hasMinhaContaText: document.body.innerText.toLowerCase().includes('minha conta'),
        hasSairText: document.body.innerText.toLowerCase().includes('sair'),
        hasLogoutText: document.body.innerText.toLowerCase().includes('logout'),
        noLoginText: !document.body.innerText.toLowerCase().includes('login'),
        currentUrl: window.location.href,
      };
      
      console.log('Login indicators:', indicators);
      
      // Return true if at least 2 indicators are positive
      const positiveCount = Object.values(indicators).filter(i => typeof i === 'boolean' && i).length;
      
      return { success: positiveCount >= 2, indicators, positiveCount };
    });

    console.log('📊 Resultado da verificação:', JSON.stringify(loginSuccess, null, 2));

    if (loginSuccess.success) {
      console.log('✅ Login realizado com sucesso no Odex');
      await page.screenshot({ path: path.join(OUTPUT_DIR, '06-login-success.png'), fullPage: true });
      console.log('📸 Screenshot: 06-login-success.png');
      return true;
    } else {
      console.log('⚠️  Login pode não ter sido bem-sucedido');
      console.log(`📊 Indicadores positivos: ${loginSuccess.positiveCount}/8`);
      console.log('💡 Por favor, observe o browser e o screenshot 05-after-submit.png');
      console.log('💡 O browser permanecerá aberto por 30 segundos para inspeção...');
      await page.waitForTimeout(30000);
      throw new Error('Login não verificado após submissão');
    }

  } catch (error) {
    console.error(`❌ Erro no login: ${(error as Error).message}`);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'error-login.png'), fullPage: true });
    console.log('📸 Screenshot de erro: error-login.png');
    console.log('💡 O browser permanecerá aberto por 30 segundos para inspeção...');
    await page.waitForTimeout(30000);
    return false;
  }
}

async function extractCategories(page: Page): Promise<CategoryInfo[]> {
  console.log('📂 Extraindo categorias de produtos...');

  try {
    // Common category selectors for e-commerce sites
    const categories = await page.evaluate(() => {
      const categoryLinks: { name: string; url: string }[] = [];
      
      // Try multiple category selector patterns
      const selectors = [
        'nav a[href*="/categoria"]',
        'nav a[href*="/category"]',
        'a[href*="/produtos"]',
        'a[href*="/product"]',
        '.menu a[href*="/categoria"]',
        '.category-link',
        '[class*="category"] a',
        'a[href*="/c/"]',
      ];

      for (const selector of selectors) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
          const link = el as HTMLAnchorElement;
          const href = link.href;
          const text = link.textContent?.trim() || '';
          
          if (href && text && !categoryLinks.some(c => c.url === href)) {
            categoryLinks.push({ name: text, url: href });
          }
        });
      }

      return categoryLinks;
    });

    console.log(`✓ Encontradas ${categories.length} categorias`);
    
    return categories.map(cat => ({
      ...cat,
      productCount: 0, // Will be updated later
    }));

  } catch (error) {
    console.error(`❌ Erro ao extrair categorias: ${(error as Error).message}`);
    return [];
  }
}

async function extractProductLinksFromCategory(page: Page, categoryUrl: string): Promise<string[]> {
  console.log(`📦 Navegando para categoria: ${categoryUrl}`);

  try {
    await page.goto(categoryUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(3000);

    // Scroll to load all products
    for (let i = 0; i < 20; i++) {
      await page.evaluate(() => window.scrollBy(0, window.innerHeight));
      await page.waitForTimeout(300);
    }

    const links = await page.evaluate(() => {
      const productLinks: string[] = [];
      const selectors = [
        'a[href*="/produto/"]',
        'a[href*="/product/"]',
        'a[href*="/p/"]',
        'a[href*="/item/"]',
        '.product-link',
        '[class*="product"] a[href*="/"]',
      ];

      for (const selector of selectors) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
          const href = (el as HTMLAnchorElement).href;
          if (href && !productLinks.includes(href) && href.includes('produto')) {
            productLinks.push(href);
          }
        });
      }

      return productLinks;
    });

    console.log(`✓ Encontrados ${links.length} produtos nesta categoria`);
    return links;

  } catch (error) {
    console.error(`❌ Erro ao extrair produtos da categoria: ${(error as Error).message}`);
    return [];
  }
}

async function extractProductDetails(page: Page, productUrl: string): Promise<DetailedProduct | null> {
  try {
    await page.goto(productUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(3000);

    const productData = await page.evaluate(() => {
      // Extract title
      const titleSelectors = [
        'h1',
        '[class*="product-title"]',
        '[class*="product-name"]',
        '.title',
      ];
      let title = '';
      for (const selector of titleSelectors) {
        const el = document.querySelector(selector);
        if (el?.textContent?.trim()) {
          title = el.textContent.trim();
          break;
        }
      }

      // Extract description
      const descSelectors = [
        '[class*="product-description"]',
        '[class*="description"]',
        '.desc',
        'p',
      ];
      let description = '';
      for (const selector of descSelectors) {
        const el = document.querySelector(selector);
        if (el?.textContent?.trim() && el.textContent.trim().length > 50) {
          description = el.textContent.trim();
          break;
        }
      }

      // Extract price
      const priceSelectors = [
        '[class*="price"]',
        '[class*="valor"]',
        '.price',
        'span[data-price]',
      ];
      let priceText = '';
      for (const selector of priceSelectors) {
        const el = document.querySelector(selector);
        if (el?.textContent?.trim()) {
          priceText = el.textContent.trim();
          break;
        }
      }

      // Extract images
      const images: string[] = [];
      const imgSelectors = [
        'img[class*="product"]',
        '.product-image img',
        'img[src*="produto"]',
      ];
      for (const selector of imgSelectors) {
        const imgs = document.querySelectorAll(selector);
        imgs.forEach(img => {
          const src = (img as HTMLImageElement).src;
          if (src && !images.includes(src)) {
            images.push(src);
          }
        });
      }

      // Extract specifications
      const specs: Record<string, string> = {};
      const specRows = document.querySelectorAll('table tr, [class*="spec"] tr, dl dt');
      specRows.forEach(row => {
        const key = row.querySelector('th, dt')?.textContent?.trim();
        const value = row.querySelector('td, dd')?.textContent?.trim();
        if (key && value) {
          specs[key] = value;
        }
      });

      // Extract SKU
      let sku = '';
      const skuMatch = document.body.textContent?.match(/SKU[:\s]+([A-Z0-9-]+)/i);
      if (skuMatch) {
        sku = skuMatch[1];
      }

      return {
        title,
        description,
        priceText,
        images,
        specifications: specs,
        sku,
      };
    });

    // Parse price
    let price = 0;
    if (productData.priceText) {
      const priceMatch = productData.priceText.match(/[\d.,]+/);
      if (priceMatch) {
        price = parseFloat(priceMatch[0].replace('.', '').replace(',', '.'));
      }
    }

    const product: DetailedProduct = {
      id: productData.sku || `odex-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      sku: productData.sku || '',
      title: productData.title,
      description: productData.description,
      price,
      currency: 'BRL',
      stock: {
        available: price > 0,
        status: price > 0 ? 'em estoque' : 'indisponível',
      },
      images: productData.images,
      specifications: productData.specifications,
      category: categorizeProduct(productData.title),
      url: productUrl,
      distributor: 'odex',
      extractedAt: new Date().toISOString(),
    };

    return product;

  } catch (error) {
    console.error(`❌ Erro ao extrair produto ${productUrl}: ${(error as Error).message}`);
    return null;
  }
}

async function main() {
  console.log('🚀 Iniciando extração de categorias do Odex...\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 50,
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  });

  const page = await context.newPage();

  try {
    // Step 1: Login
    const loginSuccess = await login(page);
    if (!loginSuccess) {
      throw new Error('Falha no login');
    }

    // Step 2: Extract categories
    const categories = await extractCategories(page);
    if (categories.length === 0) {
      throw new Error('Nenhuma categoria encontrada');
    }

    console.log(`\n📊 Total de categorias encontradas: ${categories.length}\n`);

    // Step 3: Navigate through categories and extract products
    const allProducts: DetailedProduct[] = [];
    
    for (const category of categories) {
      console.log(`\n🔍 Processando categoria: ${category.name}`);
      
      const productLinks = await extractProductLinksFromCategory(page, category.url);
      category.productCount = productLinks.length;

      // Limit products per category to avoid long execution times
      const linksToProcess = productLinks.slice(0, 20);
      
      for (let i = 0; i < linksToProcess.length; i++) {
        const link = linksToProcess[i];
        console.log(`  Extraindo produto ${i + 1}/${linksToProcess.length}: ${link}`);
        
        const product = await extractProductDetails(page, link);
        if (product) {
          allProducts.push(product);
          console.log(`  ✓ ${product.title} - R$ ${product.price}`);
        }
        
        // Small delay to be respectful
        await page.waitForTimeout(1000);
      }
    }

    // Step 4: Save results
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputFile = path.join(OUTPUT_DIR, `odex-categories-${timestamp}.json`);
    
    fs.writeFileSync(outputFile, JSON.stringify({
      distributor: 'odex',
      extractedAt: new Date().toISOString(),
      totalCategories: categories.length,
      totalProducts: allProducts.length,
      categories: categories.map(c => ({
        name: c.name,
        url: c.url,
        productCount: c.productCount,
      })),
      products: allProducts,
    }, null, 2));

    console.log(`\n✅ Extração concluída!`);
    console.log(`📁 Arquivo salvo: ${outputFile}`);
    console.log(`📊 Total de categorias: ${categories.length}`);
    console.log(`📦 Total de produtos extraídos: ${allProducts.length}`);

    // Generate summary by category
    const byCategory: Record<string, number> = {};
    allProducts.forEach(p => {
      byCategory[p.category] = (byCategory[p.category] || 0) + 1;
    });

    console.log('\n📊 Produtos por categoria:');
    Object.entries(byCategory)
      .sort((a, b) => b[1] - a[1])
      .forEach(([cat, count]) => {
        console.log(`  ${cat}: ${count}`);
      });

  } catch (error) {
    console.error(`\n❌ Erro durante a extração: ${(error as Error).message}`);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'error.png'), fullPage: true });
  } finally {
    await browser.close();
  }
}

main();
