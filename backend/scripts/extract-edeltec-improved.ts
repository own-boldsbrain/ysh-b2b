#!/usr/bin/env node

/**
 * Edeltec Improved Deep Scraping Script
 * 
 * Enhanced version of the Edeltec extraction with better product detection.
 * 
 * Issues identified in previous extraction:
 * - Extracting category pages instead of individual products
 * - Generic titles like "Gerador de Energia Solar", "Inversores"
 * - Missing product specifications
 * - Capturing logos/banners instead of product images
 * 
 * Improvements:
 * - Navigate into individual product pages
 * - Extract actual product SKUs and detailed specs
 * - Filter out non-product pages
 * - Better image filtering (exclude logos, banners, seals)
 * - Extract brand and model information
 * 
 * Usage:
 *   Set credentials in mcp-servers/.env:
 *     EDELTEC_EMAIL=your@email.com
 *     EDELTEC_PASSWORD=yourpassword
 *   
 *   Then run:
 *   $envContent = Get-Content mcp-servers\.env; foreach($line in $envContent) { if($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }; npx tsx scripts/extract-edeltec-improved.ts
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

const EDELTEC_URL = 'https://edeltecsolar.com.br/';
const EDELTEC_EMAIL = process.env.EDELTEC_EMAIL || '';
const EDELTEC_PASSWORD = process.env.EDELTEC_PASSWORD || '';

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'edeltec-improved');
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function categorizeProduct(title: string): string {
  const lowerTitle = title.toLowerCase();
  const categories: { [key: string]: string[] } = {
    bateria: ['bateria', 'estacionária', 'moura', 'heliar', 'freedom', 'fulguris', 'lifepo4'],
    bomba: ['bomba', 'solar', 'anauger', 'agua', 'piscina', 'submersa'],
    painel: ['painel', 'solar', 'fotovoltáico', 'módulo', 'placa', 'panel', 'wp', 'watt'],
    inversor: ['inversor', 'inverter', 'isolada', 'hybrid', 'grid-tie', 'fronius', 'growatt', 'solis', 'deye'],
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
    console.log('🔐 Realizando login no Edeltec...');

    if (!EDELTEC_EMAIL || !EDELTEC_PASSWORD) {
      throw new Error('EDELTEC_EMAIL e EDELTEC_PASSWORD devem estar definidos');
    }

    await page.goto(EDELTEC_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);

    // Check if already logged in
    const alreadyLoggedIn = await page.evaluate(() => {
      return !!document.querySelector('[href*="logout"], [href*="sair"]');
    });

    if (alreadyLoggedIn) {
      console.log('✅ Já logado no Edeltec');
      return true;
    }

    // Try to find login button/link first
    const loginLinks = [
      'a:has-text("Entrar")',
      'a:has-text("Login")',
      '[href*="login"]',
      'button:has-text("Login")',
    ];

    for (const selector of loginLinks) {
      try {
        const link = page.locator(selector).first();
        if (await link.isVisible({ timeout: 2000 })) {
          console.log(`✓ Clicando em link de login: ${selector}`);
          await link.click();
          await page.waitForTimeout(3000);
          break;
        }
      } catch (e) { /* continue */ }
    }

    // Fill email with multiple strategies
    const emailSelectors = [
      'input[type="email"]',
      'input[name="email"]',
      'input[name="username"]',
      'input[placeholder*="email" i]',
    ];

    let emailFilled = false;
    for (const selector of emailSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 3000 })) {
          await input.fill(EDELTEC_EMAIL);
          emailFilled = true;
          console.log(`✓ Email preenchido com: ${selector}`);
          break;
        }
      } catch (e) {
        console.log(`  × Tentando próximo seletor de email...`);
      }
    }

    if (!emailFilled) {
      // List all inputs for debugging
      const inputs = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('input')).map(i => ({
          type: i.type,
          name: i.name,
          placeholder: i.placeholder,
        }));
      });
      console.log('Inputs encontrados:', JSON.stringify(inputs));
      throw new Error('Campo de email não encontrado');
    }

    // Fill password
    const passwordSelectors = [
      'input[type="password"]',
      'input[name="password"]',
      'input[name="senha"]',
    ];

    let passwordFilled = false;
    for (const selector of passwordSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 3000 })) {
          await input.fill(EDELTEC_PASSWORD);
          passwordFilled = true;
          console.log(`✓ Senha preenchida com: ${selector}`);
          break;
        }
      } catch (e) {
        console.log(`  × Tentando próximo seletor de senha...`);
      }
    }

    if (!passwordFilled) {
      throw new Error('Campo de senha não encontrado');
    }

    // Submit
    console.log('⏳ Submetendo formulário...');
    await page.click('button[type="submit"]').catch(() => {
      console.log('  × Submit button não encontrado, tentando Enter...');
    });
    await page.keyboard.press('Enter');
    await page.waitForTimeout(5000);

    console.log('✅ Login realizado com sucesso no Edeltec');
    return true;

  } catch (error) {
    console.error(`❌ Erro no login: ${(error as Error).message}`);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'login-error.png'), fullPage: true });
    return false;
  }
}

async function extractProductLinks(page: Page): Promise<string[]> {
  console.log('📦 Extraindo links de produtos individuais...');

  try {
    // First, try to find and click on "Produtos" menu or similar
    const menuSelectors = [
      'a:has-text("Produtos")',
      'a[href*="/produtos"]',
      '[href*="/produtos"]',
    ];

    for (const selector of menuSelectors) {
      try {
        const menuItem = page.locator(selector).first();
        if (await menuItem.isVisible({ timeout: 2000 })) {
          console.log(`✓ Clicando no menu: ${selector}`);
          await menuItem.click();
          await page.waitForTimeout(3000);
          break;
        }
      } catch (e) { /* continue */ }
    }

    // Scroll to load all products with pagination detection (optimized for 1000+ products)
    console.log('⏳ Carregando todos os produtos (scroll + paginação)...');
    let previousHeight = 0;
    let scrollAttempts = 0;
    let unchangedCount = 0;
    const maxScrolls = 200; // Increased for more products
    const maxUnchanged = 5; // Break if no change after 5 attempts
    
    while (scrollAttempts < maxScrolls && unchangedCount < maxUnchanged) {
      await page.evaluate(() => window.scrollBy(0, window.innerHeight));
      await page.waitForTimeout(300); // Faster scrolling
      
      const currentHeight = await page.evaluate(() => document.body.scrollHeight);
      
      if (currentHeight === previousHeight) {
        unchangedCount++;
        
        // Try clicking "Load More" or pagination buttons
        const loadMoreSelectors = [
          'button:has-text("Carregar mais")',
          'button:has-text("Ver mais")',
          'button:has-text("Mostrar mais")',
          'a:has-text("Próxima")',
          'a:has-text("Próxima página")',
          '[class*="load-more"]',
          '[class*="show-more"]',
          '[class*="pagination"] a:not(.active)',
          '[class*="pagination"] button:not(.active)',
          'button[aria-label*="próxima"]',
          'a[aria-label*="próxima"]',
        ];
        
        let clicked = false;
        for (const selector of loadMoreSelectors) {
          try {
            const button = page.locator(selector).first();
            if (await button.isVisible({ timeout: 1000 })) {
              await button.click();
              await page.waitForTimeout(2000);
              clicked = true;
              unchangedCount = 0; // Reset counter
              console.log(`  ✓ Clicado em: ${selector}`);
              break;
            }
          } catch (e) { /* continue */ }
        }
        
        if (!clicked && unchangedCount >= maxUnchanged) {
          console.log(`  ✓ Fim da página alcançado (tentativas sem mudança: ${unchangedCount})`);
          break;
        }
      } else {
        unchangedCount = 0; // Reset counter
      }
      
      previousHeight = currentHeight;
      scrollAttempts++;
      
      // Log progress every 20 scrolls
      if (scrollAttempts % 20 === 0) {
        const linkCount = await page.evaluate(() => {
          return document.querySelectorAll('a[href*="/produto"]').length;
        });
        console.log(`  📊 Progress: ${scrollAttempts} scrolls, ~${linkCount} links encontrados`);
      }
    }

    const links = await page.evaluate(() => {
      const productLinks: string[] = [];
      
      // Look for actual product links, not category links
      const selectors = [
        'a[href*="/produto/"]',
        'a[href*="/product/"]',
        'a[href*="/item/"]',
        'a[href*="/p/"]',
      ];

      for (const selector of selectors) {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
          const href = (el as HTMLAnchorElement).href;
          // Filter out category pages
          if (href && 
              !href.includes('/produtos/') && 
              !href.includes('/categoria') &&
              !href.includes('/category') &&
              !productLinks.includes(href)) {
            productLinks.push(href);
          }
        });
      }

      // Also look for links with product-specific patterns
      const allLinks = document.querySelectorAll('a[href]');
      allLinks.forEach(el => {
        const href = (el as HTMLAnchorElement).href;
        const text = el.textContent?.toLowerCase() || '';
        
        // Include if it has product-like characteristics
        if (href && 
            !productLinks.includes(href) &&
            !href.includes('/produtos/geradores') &&
            !href.includes('/produtos/inversores') &&
            !href.includes('/produtos/baterias') &&
            (href.includes('/produto-') || 
             href.includes('/prod-') ||
             href.match(/\/[\w-]+-\d+/) ||
             (text.includes('ver') && text.includes('detalhes')))) {
          productLinks.push(href);
        }
      });

      return productLinks;
    });

    console.log(`✓ Encontrados ${links.length} links de produtos`);
    
    // Debug: show first few links
    if (links.length > 0) {
      console.log('📋 Primeiros links encontrados:');
      links.slice(0, 5).forEach((link, i) => {
        console.log(`  ${i + 1}. ${link}`);
      });
    }

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
      // Extract title - look for actual product titles
      const titleSelectors = [
        'h1[class*="product"]',
        'h1[class*="titulo"]',
        'h1[class*="name"]',
        '[class*="product-title"]',
        '[class*="product-name"]',
        'h1',
      ];
      let title = '';
      for (const selector of titleSelectors) {
        const el = document.querySelector(selector);
        if (el?.textContent?.trim() && !el.textContent.trim().includes('Rodovia')) {
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
        '[class*="details"]',
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
        '[class*="preco"]',
        '.price',
        'span[data-price]',
        '[class*="currency"]',
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

      // Extract images - filter out logos, banners, seals
      const images: string[] = [];
      const imgElements = document.querySelectorAll('img');
      const excludePatterns = [
        'logo', 'banner', 'selo', 'seal', 'icon', 'favicon',
        'absolar', 'abgd', 'payment', 'pagamento', 'card'
      ];

      imgElements.forEach(img => {
        const src = img.src;
        const alt = img.alt?.toLowerCase() || '';
        const srcLower = src.toLowerCase();
        
        // Check if it's likely a product image
        const isProductImage = 
          src &&
          !excludePatterns.some(pattern => srcLower.includes(pattern) || alt.includes(pattern)) &&
          (srcLower.includes('produto') || 
           srcLower.includes('product') || 
           srcLower.includes('item') ||
           alt.includes('produto'));

        if (isProductImage && !images.includes(src)) {
          images.push(src);
        }
      });

      // Extract specifications from tables or lists
      const specs: Record<string, string> = {};
      
      // Try table format
      const tables = document.querySelectorAll('table');
      tables.forEach(table => {
        const rows = table.querySelectorAll('tr');
        rows.forEach(row => {
          const cells = row.querySelectorAll('th, td');
          if (cells.length >= 2) {
            const key = cells[0].textContent?.trim();
            const value = cells[1].textContent?.trim();
            if (key && value && key.length < 50) {
              specs[key] = value;
            }
          }
        });
      });

      // Try list format
      const specLists = document.querySelectorAll('[class*="spec"], [class*="details"], [class*="info"]');
      specLists.forEach(list => {
        const items = list.querySelectorAll('li, p, div');
        items.forEach(item => {
          const text = item.textContent?.trim() || '';
          const match = text.match(/^([^:]+):\s*(.+)$/);
          if (match && match[1].length < 50) {
            specs[match[1].trim()] = match[2].trim();
          }
        });
      });

      // Extract SKU
      let sku = '';
      const skuPatterns = [
        /SKU[:\s]+([A-Z0-9-]+)/i,
        /Código[:\s]+([A-Z0-9-]+)/i,
        /Ref[:\s]+([A-Z0-9-]+)/i,
      ];
      
      for (const pattern of skuPatterns) {
        const match = document.body.textContent?.match(pattern);
        if (match) {
          sku = match[1];
          break;
        }
      }

      // Extract brand from text or specs
      let brand = '';
      const brandMatch = document.body.textContent?.match(/Marca[:\s]+([A-Za-z0-9\s]+)/i);
      if (brandMatch) {
        brand = brandMatch[1].trim();
      } else if (specs['Marca']) {
        brand = specs['Marca'];
      }

      // Extract model
      let model = '';
      const modelMatch = document.body.textContent?.match(/Modelo[:\s]+([A-Za-z0-9\s-]+)/i);
      if (modelMatch) {
        model = modelMatch[1].trim();
      } else if (specs['Modelo']) {
        model = specs['Modelo'];
      }

      // Extract warranty
      let warranty = '';
      const warrantyMatch = document.body.textContent?.match(/Garantia[:\s]+([^\n]+)/i);
      if (warrantyMatch) {
        warranty = warrantyMatch[1].trim();
      } else if (specs['Garantia']) {
        warranty = specs['Garantia'];
      }

      return {
        title,
        description,
        priceText,
        images,
        specifications: specs,
        sku,
        brand,
        model,
        warranty,
      };
    });

    // Skip if this looks like a category page
    const isCategoryPage = 
      !productData.title ||
      productData.title.toLowerCase().includes('categoria') ||
      productData.title === 'Inversores' ||
      productData.title === 'Geradores' ||
      productData.title === 'Baterias' ||
      productData.title.includes('Rodovia');

    if (isCategoryPage) {
      console.log(`  ⚠️  Pulando página de categoria: ${productUrl}`);
      return null;
    }

    // Parse price
    let price = 0;
    if (productData.priceText) {
      const priceMatch = productData.priceText.match(/[\d.,]+/);
      if (priceMatch) {
        price = parseFloat(priceMatch[0].replace(/\./g, '').replace(',', '.'));
      }
    }

    const product: DetailedProduct = {
      id: productData.sku || `edeltec-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
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
      brand: productData.brand,
      model: productData.model,
      warranty: productData.warranty,
      url: productUrl,
      distributor: 'edeltec',
      extractedAt: new Date().toISOString(),
    };

    return product;

  } catch (error) {
    console.error(`  ❌ Erro ao extrair: ${(error as Error).message}`);
    return null;
  }
}

async function main() {
  console.log('🚀 Iniciando extração melhorada do Edeltec...\n');

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

    // Step 2: Navigate to products page
    console.log('\n📂 Navegando para página de produtos...');
    
    const productsPageUrls = [
      'https://edeltecsolar.com.br/produtos',
      'https://edeltecsolar.com.br/produtos/todos',
      'https://edeltecsolar.com.br/catalogo',
    ];

    let navigatedToProducts = false;
    for (const url of productsPageUrls) {
      try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(3000);
        navigatedToProducts = true;
        console.log(`✓ Navegado para: ${url}`);
        break;
      } catch (e) {
        console.log(`  × URL não acessível: ${url}`);
      }
    }

    if (!navigatedToProducts) {
      console.log('⚠️  Não conseguiu navegar diretamente, tentando via menu...');
      
      // Try clicking on produtos menu
      const menuSelectors = [
        'a:has-text("Produtos")',
        'a[href*="/produtos"]',
        '[href*="/produtos"]',
        'nav a:has-text("Catálogo")',
      ];

      for (const selector of menuSelectors) {
        try {
          const menuItem = page.locator(selector).first();
          if (await menuItem.isVisible({ timeout: 2000 })) {
            await menuItem.click();
            await page.waitForTimeout(3000);
            console.log(`✓ Clicado no menu: ${selector}`);
            break;
          }
        } catch (e) { /* continue */ }
      }
    }

    // Step 3: Extract product links
    const productLinks = await extractProductLinks(page);
    if (productLinks.length === 0) {
      throw new Error('Nenhum link de produto encontrado');
    }

    console.log(`\n📊 Total de produtos encontrados: ${productLinks.length}\n`);

    // Step 3: Extract details from each product
    const allProducts: DetailedProduct[] = [];
    
    // Process up to 1000 products (increased from 500)
    const linksToProcess = productLinks.slice(0, 1000);
    
    console.log(`⚙️  Processando ${linksToProcess.length} produtos...\n`);
    
    for (let i = 0; i < linksToProcess.length; i++) {
      const link = linksToProcess[i];
      console.log(`🔍 [${i + 1}/${linksToProcess.length}] ${link}`);
      
      const product = await extractProductDetails(page, link);
      if (product) {
        allProducts.push(product);
        console.log(`  ✓ ${product.title} - R$ ${product.price.toFixed(2)}`);
      } else {
        console.log(`  ⚠️  Pulado (página de categoria ou erro)`);
      }
      
      // Small delay
      await page.waitForTimeout(800);
      
      // Show progress summary every 50 products
      if ((i + 1) % 50 === 0) {
        console.log(`\n📊 Progress: ${allProducts.length} produtos válidos de ${i + 1} processados\n`);
      }
    }

    // Step 4: Save results
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputFile = path.join(OUTPUT_DIR, `edeltec-improved-${timestamp}.json`);
    
    fs.writeFileSync(outputFile, JSON.stringify({
      distributor: 'edeltec',
      extractedAt: new Date().toISOString(),
      totalLinksFound: productLinks.length,
      totalProductsExtracted: allProducts.length,
      products: allProducts,
    }, null, 2));

    console.log(`\n✅ Extração concluída!`);
    console.log(`📁 Arquivo salvo: ${outputFile}`);
    console.log(`📦 Total de produtos extraídos: ${allProducts.length} de ${productLinks.length} links`);

    // Generate statistics
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

    const withSpecs = allProducts.filter(p => Object.keys(p.specifications).length > 0).length;
    const withBrand = allProducts.filter(p => p.brand).length;
    const withImages = allProducts.filter(p => p.images.length > 0).length;

    console.log('\n📈 Qualidade dos dados:');
    console.log(`  Com especificações: ${withSpecs}/${allProducts.length} (${((withSpecs/allProducts.length)*100).toFixed(1)}%)`);
    console.log(`  Com marca: ${withBrand}/${allProducts.length} (${((withBrand/allProducts.length)*100).toFixed(1)}%)`);
    console.log(`  Com imagens: ${withImages}/${allProducts.length} (${((withImages/allProducts.length)*100).toFixed(1)}%)`);

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
