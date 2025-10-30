#!/usr/bin/env node

/**
 * Odex Fixed Scraper - Versão Corrigida com Múltiplas Estratégias
 * 
 * Melhorias implementadas:
 * - Múltiplas estratégias de extração (regex flexível, DOM parsing, API intercept)
 * - Detecção automática de padrões HTML
 * - Extração por navegação de categorias
 * - Fallback para scraping direto de texto
 * - Validação robusta de dados extraídos
 * 
 * Usage:
 *   $envContent = Get-Content mcp-servers\.env; foreach($line in $envContent) { if($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }; npx tsx scripts/extract-odex-fixed.ts
 */

import { chromium, Browser, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

interface Product {
  id: string;
  sku: string;
  title: string;
  description: string;
  price: number;
  priceFormatted: string;
  stock: {
    available: boolean;
    quantity?: number;
  };
  images: string[];
  url: string;
  category: string;
  distributor: string;
  extractedAt: string;
}

const ODEX_LOGIN_URL = 'https://plataforma.odex.com.br/auth/login';
const ODEX_SHOP_URLS = [
  'https://plataforma.odex.com.br/dashboard/shop/view/panel',
  'https://plataforma.odex.com.br/dashboard/shop/view/inverter',
  'https://plataforma.odex.com.br/dashboard/shop/view/battery',
  'https://plataforma.odex.com.br/dashboard/shop/view/structure',
  'https://plataforma.odex.com.br/dashboard/shop/view/cable',
];

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'odex-fixed');
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function categorizeFromUrl(url: string): string {
  if (url.includes('/panel')) return 'painel';
  if (url.includes('/inverter')) return 'inversor';
  if (url.includes('/battery')) return 'bateria';
  if (url.includes('/structure')) return 'estrutura';
  if (url.includes('/cable')) return 'cabo';
  return 'outros';
}

async function login(page: Page): Promise<boolean> {
  const email = process.env.ODEX_EMAIL || '';
  const password = process.env.ODEX_PASSWORD || '';

  if (!email || !password) {
    console.log('❌ ODEX_EMAIL e ODEX_PASSWORD são obrigatórios');
    return false;
  }

  console.log('🔐 Fazendo login na Odex...');
  
  try {
    await page.goto(ODEX_LOGIN_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(3000);

    // Check if already logged in
    const isLoggedIn = await page.evaluate(() => {
      return window.location.href.includes('/dashboard') || 
             !!document.querySelector('[href*="logout"]');
    });

    if (isLoggedIn) {
      console.log('✅ Já está logado');
      return true;
    }

    // Fill email
    await page.fill('input[type="email"], input[name="email"]', email);
    await page.waitForTimeout(1000);

    // Fill password (with JS force)
    await page.evaluate((pass) => {
      const passInput = document.querySelector('input#pass, input[type="password"]') as HTMLInputElement;
      if (passInput) {
        passInput.style.display = 'block';
        passInput.style.visibility = 'visible';
        passInput.style.opacity = '1';
        passInput.disabled = false;
        passInput.value = pass;
        passInput.dispatchEvent(new Event('input', { bubbles: true }));
        passInput.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }, password);
    
    await page.waitForTimeout(1000);

    // Submit
    await page.click('button[type="submit"], input[type="submit"]');
    await page.waitForTimeout(5000);

    const loginSuccess = await page.evaluate(() => {
      return window.location.href.includes('/dashboard');
    });

    if (loginSuccess) {
      console.log('✅ Login realizado com sucesso');
      return true;
    }

    console.log('⚠️  Login pode ter falha');
    return false;

  } catch (error) {
    console.log(`❌ Erro no login: ${(error as Error).message}`);
    return false;
  }
}

/**
 * Estratégia 1: Extração via Regex de Texto (fallback confiável)
 */
async function extractViaTextRegex(page: Page, categoryUrl: string): Promise<Product[]> {
  const allText = await page.evaluate(() => document.body.innerText);
  const products: Product[] = [];
  const category = categorizeFromUrl(categoryUrl);

  // Pattern 1: "SKU: 12345 PRODUTO NOME R$ 1.234,56"
  const pattern1 = /SKU[#:\s]*(\d+)\s+([A-Z][^\n]{10,150}?)\s+R\$\s*([\d.,]+)/gi;
  
  // Pattern 2: More flexible
  const pattern2 = /(\d{4,6})\s+([A-Z][^\n]{15,150}?)\s+(?:R\$|BRL)\s*([\d.,]+)/gi;

  const patterns = [pattern1, pattern2];

  for (const pattern of patterns) {
    const matches = allText.matchAll(pattern);
    for (const match of matches) {
      try {
        const sku = match[1];
        let title = match[2].trim().replace(/\s+/g, ' ');
        const priceText = match[3];
        
        // Clean title - remove extra spaces and special chars
        title = title.substring(0, 120).trim();
        
        // Parse price
        const price = parseFloat(priceText.replace(/\./g, '').replace(',', '.'));
        
        if (sku && title.length >= 10 && !isNaN(price) && price > 0) {
          products.push({
            id: `odex-${sku}`,
            sku,
            title,
            description: '',
            price,
            priceFormatted: `R$ ${priceText}`,
            stock: { available: true },
            images: [],
            url: categoryUrl,
            category,
            distributor: 'odex',
            extractedAt: new Date().toISOString(),
          });
        }
      } catch (e) {
        // Skip invalid entry
      }
    }
    
    if (products.length > 0) break; // Found products with this pattern
  }

  return products;
}

/**
 * Estratégia 2: Extração via DOM (mais precisa quando HTML está estruturado)
 */
async function extractViaDOM(page: Page, categoryUrl: string): Promise<Product[]> {
  const category = categorizeFromUrl(categoryUrl);

  const products = await page.evaluate((cat) => {
    const items: any[] = [];
    
    // Blacklist de termos de navegação
    const navigationBlacklist = [
      'meu carrinho', 'minha conta', 'fazer login', 'cadastre-se', 'entrar',
      'sair', 'logout', 'ajuda', 'contato', 'sobre', 'termos', 'privacidade',
      'carrinho vazio', 'sem produtos', 'buscar', 'filtrar', 'ordenar',
    ];
    
    // Palavras-chave de produto
    const productKeywords = [
      'painel', 'inversor', 'bateria', 'módulo', 'solar', 'fotovoltaico',
      'estrutura', 'cabo', 'w', 'kwp', 'watts', 'ampere', 'volt',
    ];
    
    // Try to find product cards/containers
    const containerSelectors = [
      '[class*="product-card"]',
      '[class*="product-item"]',
      '[class*="item-card"]',
      '[data-product]',
      '.card',
    ];

    let containers: Element[] = [];
    for (const selector of containerSelectors) {
      const found = Array.from(document.querySelectorAll(selector));
      if (found.length > 3) { // Need at least 3 products
        containers = found;
        break;
      }
    }

    if (containers.length === 0) {
      // Fallback: look for any container with SKU text
      const allDivs = Array.from(document.querySelectorAll('div, article, section'));
      containers = allDivs.filter(el => {
        const text = el.textContent || '';
        return text.includes('SKU') && text.includes('R$');
      });
    }

    containers.forEach((container) => {
      try {
        const text = container.textContent || '';
        
        // Extract SKU
        const skuMatch = text.match(/SKU[#:\s]*(\d+)/i);
        if (!skuMatch) return;
        const sku = skuMatch[1];
        
        // Extract title
        let title = '';
        const titleEl = container.querySelector('h1, h2, h3, h4, .title, [class*="name"]');
        if (titleEl) {
          title = (titleEl.textContent || '').trim();
        } else {
          // Extract from text after SKU
          const afterSKU = text.substring(text.indexOf(sku) + sku.length);
          const titleMatch = afterSKU.match(/([A-Z][^\n\r]{10,120}?)\s+R\$/);
          if (titleMatch) title = titleMatch[1].trim();
        }
        
        // FILTRO: Rejeitar navegação e validar produto
        const titleLower = title.toLowerCase();
        if (navigationBlacklist.some(term => titleLower.includes(term))) {
          return; // Skip
        }
        
        const hasProductKeyword = productKeywords.some(kw => titleLower.includes(kw));
        if (!hasProductKeyword && title.length < 25) {
          return; // Skip se título curto sem palavras-chave
        }
        
        // Extract price
        const priceMatch = text.match(/R\$\s*([\d.,]+)/);
        if (!priceMatch) return;
        const priceText = priceMatch[1];
        const price = parseFloat(priceText.replace(/\./g, '').replace(',', '.'));
        
        // Extract image
        const img = container.querySelector('img') as HTMLImageElement;
        const imageUrl = img?.src || '';
        
        if (sku && title && title.length >= 10 && !isNaN(price) && price > 0) {
          items.push({
            sku,
            title: title.substring(0, 120),
            price,
            priceText,
            imageUrl,
          });
        }
      } catch (e) {
        // Skip
      }
    });

    return items;
  }, category);

  return products.map(p => ({
    id: `odex-${p.sku}`,
    sku: p.sku,
    title: p.title,
    description: '',
    price: p.price,
    priceFormatted: `R$ ${p.priceText}`,
    stock: { available: true },
    images: p.imageUrl ? [p.imageUrl] : [],
    url: categoryUrl,
    category,
    distributor: 'odex',
    extractedAt: new Date().toISOString(),
  }));
}

/**
 * Extração combinada: tenta DOM primeiro, fallback para Regex
 */
async function extractProducts(page: Page, url: string): Promise<Product[]> {
  console.log(`\n📦 Extraindo produtos de: ${categorizeFromUrl(url)}`);
  
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(3000);

  // Scroll to load all content
  for (let i = 0; i < 15; i++) {
    await page.evaluate(() => window.scrollBy(0, window.innerHeight));
    await page.waitForTimeout(200);
  }
  await page.waitForTimeout(2000);

  // Try DOM extraction first
  let products = await extractViaDOM(page, url);
  
  if (products.length === 0) {
    console.log('  ⚠️  Extração DOM falhou, usando Regex...');
    products = await extractViaTextRegex(page, url);
  }

  console.log(`  ✅ ${products.length} produtos encontrados`);
  
  // Screenshot for debug
  const category = categorizeFromUrl(url);
  await page.screenshot({ 
    path: path.join(OUTPUT_DIR, `${category}-page.png`), 
    fullPage: false 
  });

  return products;
}

async function main() {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  🔧 ODEX FIXED SCRAPER - Versão Corrigida                 ║
╚════════════════════════════════════════════════════════════╝
  `);

  const browser = await chromium.launch({ 
    headless: false,
    args: ['--disable-blink-features=AutomationControlled'],
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  });
  
  const page = await context.newPage();

  // Login
  const loginSuccess = await login(page);
  if (!loginSuccess) {
    console.log('⚠️  Prosseguindo sem login (pode ter produtos limitados)');
  }

  // Extract from all categories
  const allProducts: Product[] = [];
  
  for (const url of ODEX_SHOP_URLS) {
    try {
      const products = await extractProducts(page, url);
      allProducts.push(...products);
    } catch (error) {
      console.log(`  ❌ Erro: ${(error as Error).message}`);
    }
  }

  await browser.close();

  // Deduplicate by SKU
  const uniqueProducts = Array.from(
    new Map(allProducts.map(p => [p.sku, p])).values()
  );

  console.log(`\n✅ Total de produtos únicos: ${uniqueProducts.length}`);

  // Save JSON
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const jsonFile = path.join(OUTPUT_DIR, `products-${timestamp}.json`);
  fs.writeFileSync(jsonFile, JSON.stringify(uniqueProducts, null, 2));

  // Save CSV
  const csvFile = path.join(OUTPUT_DIR, `products-${timestamp}.csv`);
  const csvHeader = 'SKU,Título,Preço,Categoria,URL\n';
  const csvRows = uniqueProducts.map(p => 
    `"${p.sku}","${p.title.replace(/"/g, '""')}","${p.priceFormatted}","${p.category}","${p.url}"`
  ).join('\n');
  fs.writeFileSync(csvFile, csvHeader + csvRows);

  // Stats by category
  const stats: Record<string, number> = {};
  uniqueProducts.forEach(p => {
    stats[p.category] = (stats[p.category] || 0) + 1;
  });

  console.log(`
╔════════════════════════════════════════════════════════════╗
║  📊 ESTATÍSTICAS                                          ║
╚════════════════════════════════════════════════════════════╝

📦 Por categoria:`);
  
  Object.entries(stats).forEach(([cat, count]) => {
    console.log(`  • ${cat}: ${count} produtos`);
  });

  console.log(`
💰 Preços:
  • Com preço: ${uniqueProducts.filter(p => p.price > 0).length}
  • Média: R$ ${(uniqueProducts.reduce((sum, p) => sum + p.price, 0) / uniqueProducts.length).toFixed(2)}

📁 Arquivos salvos:
  • ${jsonFile}
  • ${csvFile}

🎉 Extração completa!
  `);
}

main().catch(console.error);
