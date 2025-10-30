#!/usr/bin/env node

/**
 * Fortlev Category Navigation Script
 * 
 * Navigates through all product categories on Fortlev B2B portal and extracts
 * detailed product information from each category.
 * 
 * Strategy:
 * 1. Login to Fortlev portal (https://fortlevsolar.app/login)
 * 2. Find all category/product navigation links
 * 3. For each category, navigate and extract product links
 * 4. For each product, extract detailed information
 * 
 * Usage:
 *   Set credentials in mcp-servers/.env:
 *     FORTLEV_EMAIL=your@email.com
 *     FORTLEV_PASSWORD=yourpassword
 *   
 *   Then run:
 *   $envContent = Get-Content mcp-servers\.env; foreach($line in $envContent) { if($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }; npx tsx scripts/extract-fortlev-categories.ts
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

const FORTLEV_URL = 'https://fortlevsolar.app/login';
const FORTLEV_EMAIL = process.env.FORTLEV_EMAIL || '';
const FORTLEV_PASSWORD = process.env.FORTLEV_PASSWORD || '';

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'fortlev-categories');
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
    console.log('🔐 Realizando login no Fortlev...');
    console.log('📸 Screenshots serão salvos em cada etapa para debug');

    if (!FORTLEV_EMAIL || !FORTLEV_PASSWORD) {
      throw new Error('FORTLEV_EMAIL e FORTLEV_PASSWORD devem estar definidos');
    }

    await page.goto(FORTLEV_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(3000);
    await page.screenshot({ path: path.join(OUTPUT_DIR, '01-initial-page.png'), fullPage: true });
    console.log('📸 Screenshot: 01-initial-page.png');

    // Check if already logged in
    const alreadyLoggedIn = await page.evaluate(() => {
      return !!document.querySelector('[href*="logout"], [href*="sair"]') ||
             document.body.innerText.toLowerCase().includes('minha conta') ||
             !document.body.innerText.toLowerCase().includes('login');
    });

    if (alreadyLoggedIn) {
      console.log('✅ Já logado no Fortlev');
      return true;
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
      const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
        type: b.type,
        text: b.textContent?.trim(),
        visible: b.offsetParent !== null,
      }));
      return { inputs, buttons };
    });
    
    console.log('📋 Inputs encontrados:', JSON.stringify(formInfo.inputs, null, 2));
    console.log('📋 Botões encontrados:', JSON.stringify(formInfo.buttons, null, 2));

    // Fill email
    const emailSelectors = [
      'input[type="email"]',
      'input[name="email"]',
      'input[name="username"]',
      'input[placeholder*="email" i]',
      'input[placeholder*="e-mail" i]',
      'input[id*="email"]',
    ];

    let emailFilled = false;
    for (const selector of emailSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.fill(FORTLEV_EMAIL);
          emailFilled = true;
          console.log(`✓ Email preenchido com seletor: ${selector}`);
          await page.screenshot({ path: path.join(OUTPUT_DIR, '02-email-filled.png'), fullPage: true });
          console.log('📸 Screenshot: 02-email-filled.png');
          break;
        }
      } catch (e) { 
        console.log(`  × Seletor ${selector} não funcionou`);
      }
    }

    if (!emailFilled) {
      await page.screenshot({ path: path.join(OUTPUT_DIR, '02-email-not-found.png'), fullPage: true });
      throw new Error('Campo de email não encontrado');
    }

    // Fill password
    await page.waitForTimeout(1000);
    
    const passwordSelectors = [
      'input[type="password"]',
      'input[name="password"]',
      'input[name="senha"]',
      'input[placeholder*="senha" i]',
      'input[placeholder*="password" i]',
    ];

    let passwordFilled = false;
    for (const selector of passwordSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.fill(FORTLEV_PASSWORD);
          passwordFilled = true;
          console.log(`✓ Senha preenchida com seletor: ${selector}`);
          await page.screenshot({ path: path.join(OUTPUT_DIR, '03-password-filled.png'), fullPage: true });
          console.log('📸 Screenshot: 03-password-filled.png');
          break;
        }
      } catch (e) {
        console.log(`  × Seletor ${selector} não funcionou`);
      }
    }

    if (!passwordFilled) {
      await page.screenshot({ path: path.join(OUTPUT_DIR, '03-password-not-found.png'), fullPage: true });
      throw new Error('Campo de senha não encontrado');
    }

    // Submit form
    console.log('⏳ Submetendo formulário de login...');
    
    const submitSelectors = [
      'button[type="submit"]',
      'button:has-text("Entrar")',
      'button:has-text("Login")',
      'input[type="submit"]',
    ];

    let submitClicked = false;
    for (const selector of submitSelectors) {
      try {
        const button = page.locator(selector).first();
        if (await button.isVisible({ timeout: 1000 })) {
          await button.click();
          submitClicked = true;
          console.log(`✓ Clicado em botão: ${selector}`);
          break;
        }
      } catch (e) { 
        console.log(`  × Botão ${selector} não encontrado`);
      }
    }

    if (!submitClicked) {
      console.log('  × Nenhum botão de submit encontrado, tentando Enter...');
      await page.keyboard.press('Enter');
    }

    console.log('⏳ Aguardando resposta do servidor (10 segundos)...');
    await page.waitForTimeout(10000);
    await page.screenshot({ path: path.join(OUTPUT_DIR, '04-after-submit.png'), fullPage: true });
    console.log('📸 Screenshot: 04-after-submit.png');

    // Verify login with multiple indicators
    const loginSuccess = await page.evaluate(() => {
      const indicators = {
        hasLogoutLink: !!document.querySelector('[href*="logout"]'),
        hasSairLink: !!document.querySelector('[href*="sair"]'),
        hasMinhaContaText: document.body.innerText.toLowerCase().includes('minha conta'),
        noPasswordField: !document.querySelector('input[type="password"]'),
        currentUrl: window.location.href,
        bodyText: document.body.innerText.substring(0, 500),
      };
      
      console.log('Login indicators:', indicators);
      
      const positiveCount = [
        indicators.hasLogoutLink,
        indicators.hasSairLink,
        indicators.hasMinhaContaText,
        indicators.noPasswordField,
      ].filter(i => i).length;
      
      return { success: positiveCount >= 2, indicators };
    });

    console.log('📊 Resultado da verificação:', JSON.stringify(loginSuccess, null, 2));

    if (loginSuccess.success) {
      console.log('✅ Login realizado com sucesso no Fortlev');
      await page.screenshot({ path: path.join(OUTPUT_DIR, '05-login-success.png'), fullPage: true });
      console.log('📸 Screenshot: 05-login-success.png');
      return true;
    } else {
      console.log('⚠️  Login pode não ter sido bem-sucedido');
      console.log('💡 Por favor, observe o browser e o screenshot 04-after-submit.png');
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

async function extractProductLinks(page: Page): Promise<string[]> {
  console.log('📦 Extraindo todos os links de produtos...');

  try {
    // Scroll to load all products
    for (let i = 0; i < 30; i++) {
      await page.evaluate(() => window.scrollBy(0, window.innerHeight));
      await page.waitForTimeout(300);
    }

    const links = await page.evaluate(() => {
      const productLinks: string[] = [];
      const selectors = [
        'a[href*="/produto"]',
        'a[href*="/product"]',
        'a[href*="/p/"]',
        'a[href*="/item"]',
        '.product-link',
        '[class*="product"] a',
        'a[href*="/produtos/"]',
      ];

      for (const selector of selectors) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
          const href = (el as HTMLAnchorElement).href;
          if (href && !productLinks.includes(href)) {
            productLinks.push(href);
          }
        });
      }

      // Also try to find links in card structures
      const cards = document.querySelectorAll('[class*="card"], [class*="item"], [class*="product"]');
      cards.forEach(card => {
        const link = card.querySelector('a');
        if (link?.href && !productLinks.includes(link.href)) {
          productLinks.push(link.href);
        }
      });

      return productLinks;
    });

    console.log(`✓ Encontrados ${links.length} links de produtos`);
    return links;

  } catch (error) {
    console.error(`❌ Erro ao extrair links: ${(error as Error).message}`);
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
        '[class*="title"]',
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
        '[class*="desc"]',
        '.desc',
        'p[class*="text"]',
      ];
      let description = '';
      for (const selector of descSelectors) {
        const el = document.querySelector(selector);
        if (el?.textContent?.trim() && el.textContent.trim().length > 30) {
          description = el.textContent.trim();
          break;
        }
      }

      // Extract price
      const priceSelectors = [
        '[class*="price"]',
        '[class*="valor"]',
        '[class*="preco"]',
        '.price',
        'span[data-price]',
      ];
      let priceText = '';
      for (const selector of priceSelectors) {
        const el = document.querySelector(selector);
        if (el?.textContent?.trim()) {
          const text = el.textContent.trim();
          if (text.match(/R\$|[\d.,]+/)) {
            priceText = text;
            break;
          }
        }
      }

      // Extract images
      const images: string[] = [];
      const imgSelectors = [
        'img[class*="product"]',
        '.product-image img',
        'img[src*="produto"]',
        'img[alt*="produto" i]',
        'main img',
      ];
      for (const selector of imgSelectors) {
        const imgs = document.querySelectorAll(selector);
        imgs.forEach(img => {
          const src = (img as HTMLImageElement).src;
          if (src && !images.includes(src) && !src.includes('logo') && !src.includes('icon')) {
            images.push(src);
          }
        });
      }

      // Extract specifications
      const specs: Record<string, string> = {};
      
      // Try table format
      const specRows = document.querySelectorAll('table tr');
      specRows.forEach(row => {
        const cells = row.querySelectorAll('th, td');
        if (cells.length >= 2) {
          const key = cells[0].textContent?.trim();
          const value = cells[1].textContent?.trim();
          if (key && value) {
            specs[key] = value;
          }
        }
      });

      // Try dl/dt/dd format
      const dlElements = document.querySelectorAll('dl');
      dlElements.forEach(dl => {
        const dts = dl.querySelectorAll('dt');
        const dds = dl.querySelectorAll('dd');
        dts.forEach((dt, i) => {
          const key = dt.textContent?.trim();
          const value = dds[i]?.textContent?.trim();
          if (key && value) {
            specs[key] = value;
          }
        });
      });

      // Extract SKU
      let sku = '';
      const skuMatch = document.body.textContent?.match(/SKU[:\s]+([A-Z0-9-]+)/i);
      if (skuMatch) {
        sku = skuMatch[1];
      }

      // Extract brand
      let brand = '';
      const brandMatch = document.body.textContent?.match(/Marca[:\s]+([A-Za-z0-9\s]+)/i);
      if (brandMatch) {
        brand = brandMatch[1].trim();
      }

      // Extract stock info
      let stockText = '';
      const stockSelectors = ['[class*="stock"]', '[class*="estoque"]', '[class*="disponib"]'];
      for (const selector of stockSelectors) {
        const el = document.querySelector(selector);
        if (el?.textContent?.trim()) {
          stockText = el.textContent.trim();
          break;
        }
      }

      return {
        title,
        description,
        priceText,
        images,
        specifications: specs,
        sku,
        brand,
        stockText,
      };
    });

    // Parse price
    let price = 0;
    if (productData.priceText) {
      const priceMatch = productData.priceText.match(/[\d.,]+/);
      if (priceMatch) {
        price = parseFloat(priceMatch[0].replace(/\./g, '').replace(',', '.'));
      }
    }

    // Determine stock status
    const stockAvailable = price > 0 && !productData.stockText.toLowerCase().includes('indisponível');
    
    const product: DetailedProduct = {
      id: productData.sku || `fortlev-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      sku: productData.sku || '',
      title: productData.title,
      description: productData.description,
      price,
      currency: 'BRL',
      stock: {
        available: stockAvailable,
        status: stockAvailable ? 'em estoque' : 'indisponível',
      },
      images: productData.images,
      specifications: productData.specifications,
      category: categorizeProduct(productData.title),
      brand: productData.brand,
      url: productUrl,
      distributor: 'fortlev',
      extractedAt: new Date().toISOString(),
    };

    return product;

  } catch (error) {
    console.error(`❌ Erro ao extrair produto ${productUrl}: ${(error as Error).message}`);
    return null;
  }
}

async function main() {
  console.log('🚀 Iniciando extração de produtos do Fortlev...\n');

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

    // Step 2: Extract all product links
    const productLinks = await extractProductLinks(page);
    if (productLinks.length === 0) {
      throw new Error('Nenhum link de produto encontrado');
    }

    console.log(`\n📊 Total de produtos encontrados: ${productLinks.length}\n`);

    // Step 3: Extract details from each product
    const allProducts: DetailedProduct[] = [];
    
    // Limit to 50 products to avoid very long execution
    const linksToProcess = productLinks.slice(0, 50);
    
    for (let i = 0; i < linksToProcess.length; i++) {
      const link = linksToProcess[i];
      console.log(`🔍 Extraindo produto ${i + 1}/${linksToProcess.length}: ${link}`);
      
      const product = await extractProductDetails(page, link);
      if (product) {
        allProducts.push(product);
        console.log(`  ✓ ${product.title} - R$ ${product.price.toFixed(2)}`);
      }
      
      // Small delay to be respectful
      await page.waitForTimeout(1500);
    }

    // Step 4: Save results
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputFile = path.join(OUTPUT_DIR, `fortlev-products-${timestamp}.json`);
    
    fs.writeFileSync(outputFile, JSON.stringify({
      distributor: 'fortlev',
      extractedAt: new Date().toISOString(),
      totalProductsFound: productLinks.length,
      totalProductsExtracted: allProducts.length,
      products: allProducts,
    }, null, 2));

    console.log(`\n✅ Extração concluída!`);
    console.log(`📁 Arquivo salvo: ${outputFile}`);
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

    // Price statistics
    const prices = allProducts.filter(p => p.price > 0).map(p => p.price);
    if (prices.length > 0) {
      const avgPrice = prices.reduce((a, b) => a + b, 0) / prices.length;
      const minPrice = Math.min(...prices);
      const maxPrice = Math.max(...prices);

      console.log('\n💰 Estatísticas de preços:');
      console.log(`  Mínimo: R$ ${minPrice.toFixed(2)}`);
      console.log(`  Máximo: R$ ${maxPrice.toFixed(2)}`);
      console.log(`  Média: R$ ${avgPrice.toFixed(2)}`);
    }

  } catch (error) {
    console.error(`\n❌ Erro durante a extração: ${(error as Error).message}`);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'error.png'), fullPage: true });
  } finally {
    await browser.close();
  }
}

main();
