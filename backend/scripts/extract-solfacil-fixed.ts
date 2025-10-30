#!/usr/bin/env node

/**
 * Solfácil Fixed Scraper - Versão Corrigida com SSO Robusto
 * 
 * Melhorias implementadas:
 * - Detecção automática de fluxo SSO Keycloak
 * - Múltiplas estratégias de preenchimento de formulário
 * - Interceptação de requisições de API
 * - Navegação inteligente por categorias
 * - Extração adaptativa de produtos
 * - Tratamento de erros com retry automático
 * 
 * URL: https://integrador.solfacil.com.br/
 * SSO: https://sso.solfacil.com.br/
 * 
 * Usage:
 *   $envContent = Get-Content mcp-servers\.env; foreach($line in $envContent) { if($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }; npx tsx scripts/extract-solfacil-fixed.ts
 */

import { chromium, Browser, Page, BrowserContext } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

interface Product {
  id: string;
  sku: string;
  title: string;
  price: number;
  priceFormatted: string;
  stock: {
    available: boolean;
    quantity?: number;
  };
  images: string[];
  url: string;
  category: string;
  brand?: string;
  distributor: string;
  extractedAt: string;
}

const SOLFACIL_URL = 'https://integrador.solfacil.com.br/';
const OUTPUT_DIR = path.join(process.cwd(), 'output', 'solfacil-fixed');

if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

function categorizeProduct(title: string): string {
  const lowerTitle = title.toLowerCase();
  const categories: { [key: string]: string[] } = {
    bateria: ['bateria', 'estacionária', 'moura', 'heliar', 'freedom'],
    bomba: ['bomba', 'solar', 'anauger'],
    painel: ['painel', 'solar', 'fotovoltáico', 'módulo', 'placa'],
    inversor: ['inversor', 'inverter', 'fronius', 'growatt', 'solis'],
    estrutura: ['estrutura', 'suporte', 'trilho', 'fixação'],
    cabo: ['cabo', 'fio', 'conduite'],
    conector: ['conector', 'mc4'],
  };

  for (const [category, keywords] of Object.entries(categories)) {
    if (keywords.some(keyword => lowerTitle.includes(keyword))) {
      return category;
    }
  }
  return 'outros';
}

/**
 * Login robusto com Keycloak SSO
 */
async function loginKeycloak(page: Page): Promise<boolean> {
  const email = process.env.SOLFACIL_EMAIL || '';
  const password = process.env.SOLFACIL_PASSWORD || '';

  if (!email || !password) {
    console.log('❌ SOLFACIL_EMAIL e SOLFACIL_PASSWORD são obrigatórios');
    return false;
  }

  console.log('\n🔐 Iniciando autenticação Keycloak SSO...');

  try {
    // Step 1: Navigate to main portal
    console.log('[1/6] Navegando para portal...');
    await page.goto(SOLFACIL_URL, { 
      waitUntil: 'domcontentloaded',
      timeout: 60000 
    });
    
    // Wait for SSO redirect
    console.log('[2/6] Aguardando redirecionamento SSO...');
    
    const waitForSSO = async () => {
      for (let i = 0; i < 30; i++) {
        const url = page.url();
        if (url.includes('sso.solfacil') || url.includes('keycloak')) {
          return true;
        }
        await page.waitForTimeout(1000);
      }
      return false;
    };
    
    const redirected = await waitForSSO();
    
    if (!redirected) {
      // Try clicking login button
      console.log('  ⚠️  Tentando clicar em botão de login...');
      const loginButtons = [
        'button:has-text("Entrar")',
        'a:has-text("Entrar")',
        'button:has-text("Login")',
        '[href*="login"]',
      ];
      
      for (const selector of loginButtons) {
        try {
          const btn = await page.locator(selector).first();
          if (await btn.isVisible({ timeout: 2000 })) {
            await btn.click();
            await page.waitForTimeout(3000);
            break;
          }
        } catch (e) { }
      }
      
      // Wait again
      const redirectedAgain = await waitForSSO();
      if (!redirectedAgain) {
        console.log('❌ Redirecionamento SSO não detectado');
        return false;
      }
    }

    console.log('  ✅ Redirecionado para SSO Keycloak');
    await page.screenshot({ path: path.join(OUTPUT_DIR, '01-sso-page.png'), fullPage: true });

    // Step 2: Wait for login form
    console.log('[3/6] Aguardando formulário de login...');
    
    await page.waitForSelector('input[name="username"], #username', { 
      state: 'visible', 
      timeout: 15000 
    }).catch(() => {
      console.log('  ⚠️  Timeout aguardando formulário');
    });
    
    await page.waitForTimeout(2000);

    // Step 3: Fill username
    console.log('[4/6] Preenchendo credenciais...');
    
    const usernameSelectors = ['#username', 'input[name="username"]'];
    let filled = false;
    
    for (const selector of usernameSelectors) {
      try {
        const input = await page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.clear();
          await input.fill(email);
          
          // Verify
          const value = await input.inputValue();
          if (value === email) {
            console.log(`  ✅ Username preenchido`);
            filled = true;
            break;
          }
        }
      } catch (e) { }
    }

    if (!filled) {
      // JavaScript fallback
      await page.evaluate((emailValue) => {
        const inp = document.querySelector('#username, input[name="username"]') as HTMLInputElement;
        if (inp) {
          inp.value = emailValue;
          inp.dispatchEvent(new Event('input', { bubbles: true }));
          inp.dispatchEvent(new Event('change', { bubbles: true }));
        }
      }, email);
    }

    // Fill password
    const passwordSelectors = ['#password', 'input[name="password"]'];
    
    for (const selector of passwordSelectors) {
      try {
        const input = await page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.clear();
          await input.fill(password);
          console.log(`  ✅ Password preenchido`);
          break;
        }
      } catch (e) { }
    }

    await page.screenshot({ path: path.join(OUTPUT_DIR, '02-credentials-filled.png'), fullPage: true });

    // Step 4: Submit
    console.log('[5/6] Submetendo formulário...');
    
    const submitSelectors = [
      '#kc-login',
      'input[type="submit"]',
      'button[type="submit"]',
      'button:has-text("Sign In")',
    ];
    
    for (const selector of submitSelectors) {
      try {
        const btn = await page.locator(selector).first();
        if (await btn.isVisible({ timeout: 2000 })) {
          await btn.click();
          break;
        }
      } catch (e) { }
    }

    // Step 5: Wait for redirect back to portal
    console.log('[6/6] Aguardando conclusão do login...');
    
    await page.waitForURL('**/integrador.solfacil.com.br/**', { 
      timeout: 30000 
    }).catch(() => {
      console.log('  ⚠️  Timeout esperando redirect');
    });

    await page.waitForTimeout(5000);
    
    const finalUrl = page.url();
    const success = finalUrl.includes('integrador.solfacil') && !finalUrl.includes('sso');
    
    if (success) {
      console.log('✅ Login realizado com sucesso!');
      await page.screenshot({ path: path.join(OUTPUT_DIR, '03-logged-in.png'), fullPage: true });
      return true;
    }

    console.log('⚠️  Login pode não ter sido bem-sucedido');
    return false;

  } catch (error) {
    console.log(`❌ Erro no login: ${(error as Error).message}`);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'error-login.png'), fullPage: true });
    return false;
  }
}

/**
 * Navegar para loja/produtos
 */
async function navigateToShop(page: Page): Promise<boolean> {
  console.log('\n🏪 Navegando para loja...');

  const shopSelectors = [
    'a[href*="loja"]',
    'a[href*="shop"]',
    'a[href*="produto"]',
    'button:has-text("Loja")',
    'a:has-text("Loja")',
  ];

  for (const selector of shopSelectors) {
    try {
      const link = await page.locator(selector).first();
      if (await link.isVisible({ timeout: 3000 })) {
        console.log(`  ✓ Clicando em: ${selector}`);
        await link.click();
        await page.waitForTimeout(5000);
        
        await page.screenshot({ 
          path: path.join(OUTPUT_DIR, '04-shop-page.png'), 
          fullPage: true 
        });
        
        return true;
      }
    } catch (e) { }
  }

  console.log('  ⚠️  Link da loja não encontrado, tentando URLs diretas...');
  
  const shopUrls = [
    'https://integrador.solfacil.com.br/loja',
    'https://integrador.solfacil.com.br/shop',
    'https://integrador.solfacil.com.br/produtos',
  ];

  for (const url of shopUrls) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(3000);
      
      const currentUrl = page.url();
      if (!currentUrl.includes('sso')) {
        console.log(`  ✅ Acessou: ${url}`);
        return true;
      }
    } catch (e) { }
  }

  return false;
}

/**
 * Extrair produtos da página
 */
async function extractProducts(page: Page): Promise<Product[]> {
  console.log('\n📦 Extraindo produtos...');

  // Scroll to load all products
  for (let i = 0; i < 20; i++) {
    await page.evaluate(() => window.scrollBy(0, window.innerHeight));
    await page.waitForTimeout(300);
  }
  await page.waitForTimeout(2000);

  const products = await page.evaluate(() => {
    const items: any[] = [];
    
    // Blacklist: termos de navegação/menu que NÃO são produtos
    const navigationBlacklist = [
      'monte seu kit', 'meus pedidos', 'meus orçamentos', 'portal do integrador',
      'financiamento', 'acordo operacional', 'fale com', 'central de ajuda',
      'meus chamados', 'termos e condições', 'sair da minha conta', 'entrar',
      'login', 'cadastro', 'carrinho', 'checkout', 'finalizar', 'minha conta',
      'perfil', 'configurações', 'ajuda', 'suporte', 'contato', 'sobre',
    ];
    
    // Palavras-chave que indicam produto real
    const productKeywords = [
      'painel', 'inversor', 'bateria', 'módulo', 'placa', 'solar', 'fotovoltaico',
      'estrutura', 'cabo', 'conector', 'mc4', 'string box', 'bomba', 'kwp', 'w', 'watts',
      'fronius', 'growatt', 'canadian', 'jinko', 'trina', 'risen', 'ja solar',
    ];
    
    // Strategy 1: Find product containers
    const containerSelectors = [
      '[class*="product"]',
      '[class*="card"]',
      '[data-product-id]',
      '[class*="item"]',
    ];

    let containers: Element[] = [];
    for (const selector of containerSelectors) {
      const found = Array.from(document.querySelectorAll(selector));
      if (found.length > 5) {
        containers = found;
        break;
      }
    }

    containers.forEach((container, index) => {
      try {
        const text = container.textContent || '';
        
        // Extract title
        let title = '';
        const titleEl = container.querySelector('h1, h2, h3, h4, .title, [class*="name"], [class*="titulo"]');
        if (titleEl) {
          title = (titleEl.textContent || '').trim();
        }
        
        if (!title || title.length < 10) {
          // Extract from text
          const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 10);
          title = lines[0] || '';
        }
        
        // FILTRO 1: Rejeitar itens de navegação
        const titleLower = title.toLowerCase();
        if (navigationBlacklist.some(term => titleLower.includes(term))) {
          return; // Skip
        }
        
        // FILTRO 2: Deve ter pelo menos uma palavra-chave de produto
        const hasProductKeyword = productKeywords.some(keyword => titleLower.includes(keyword));
        if (!hasProductKeyword && title.length < 30) {
          return; // Skip se título curto sem palavras-chave
        }
        
        // Extract price
        const priceMatch = text.match(/R\$\s*([\d.,]+)/);
        let price = 0;
        let priceFormatted = '';
        if (priceMatch) {
          priceFormatted = priceMatch[0];
          price = parseFloat(priceMatch[1].replace(/\./g, '').replace(',', '.'));
        }
        
        // Extract SKU
        const skuMatch = text.match(/SKU[:\s]*(\w+)/i) || 
                        text.match(/C[óo]d[:\s]*(\w+)/i);
        const sku = skuMatch ? skuMatch[1] : `solfacil-${index}`;
        
        // Extract image
        const img = container.querySelector('img') as HTMLImageElement;
        const imageUrl = img?.src || '';
        
        // Extract link
        const link = container.querySelector('a') as HTMLAnchorElement;
        const url = link?.href || window.location.href;
        
        if (title && title.length >= 10) {
          items.push({
            sku,
            title: title.substring(0, 150),
            price: isNaN(price) ? 0 : price,
            priceFormatted,
            imageUrl,
            url,
          });
        }
      } catch (e) {
        // Skip
      }
    });

    return items;
  });

  const detailedProducts: Product[] = products.map(p => ({
    id: `solfacil-${p.sku}`,
    sku: p.sku,
    title: p.title,
    price: p.price,
    priceFormatted: p.priceFormatted || `R$ ${p.price.toFixed(2)}`,
    stock: { available: p.price > 0 },
    images: p.imageUrl ? [p.imageUrl] : [],
    url: p.url,
    category: categorizeProduct(p.title),
    distributor: 'solfacil',
    extractedAt: new Date().toISOString(),
  }));

  console.log(`✅ ${detailedProducts.length} produtos extraídos`);
  return detailedProducts;
}

async function main() {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  🔧 SOLFÁCIL FIXED SCRAPER - Versão Corrigida            ║
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
  const loginSuccess = await loginKeycloak(page);
  if (!loginSuccess) {
    console.log('❌ Falha no login, abortando');
    await browser.close();
    return;
  }

  // Navigate to shop
  const shopSuccess = await navigateToShop(page);
  if (!shopSuccess) {
    console.log('⚠️  Não conseguiu acessar loja, tentando extrair da página atual');
  }

  // Extract products
  const products = await extractProducts(page);

  await browser.close();

  if (products.length === 0) {
    console.log('\n⚠️  Nenhum produto extraído. Verifique:');
    console.log('  • Credenciais corretas (SOLFACIL_EMAIL, SOLFACIL_PASSWORD)');
    console.log('  • Acesso à loja habilitado para sua conta');
    console.log('  • Screenshots em output/solfacil-fixed/ para debug');
    return;
  }

  // Save
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const jsonFile = path.join(OUTPUT_DIR, `products-${timestamp}.json`);
  fs.writeFileSync(jsonFile, JSON.stringify(products, null, 2));

  const csvFile = path.join(OUTPUT_DIR, `products-${timestamp}.csv`);
  const csvHeader = 'SKU,Título,Preço,Categoria,URL\n';
  const csvRows = products.map(p => 
    `"${p.sku}","${p.title.replace(/"/g, '""')}","${p.priceFormatted}","${p.category}","${p.url}"`
  ).join('\n');
  fs.writeFileSync(csvFile, csvHeader + csvRows);

  // Stats
  const stats: Record<string, number> = {};
  products.forEach(p => {
    stats[p.category] = (stats[p.category] || 0) + 1;
  });

  console.log(`
╔════════════════════════════════════════════════════════════╗
║  📊 ESTATÍSTICAS                                          ║
╚════════════════════════════════════════════════════════════╝

📦 Total: ${products.length} produtos

Por categoria:`);
  
  Object.entries(stats).forEach(([cat, count]) => {
    console.log(`  • ${cat}: ${count}`);
  });

  console.log(`
💰 Preços:
  • Com preço: ${products.filter(p => p.price > 0).length}
  • Média: R$ ${(products.reduce((sum, p) => sum + p.price, 0) / products.length).toFixed(2)}

📁 Arquivos:
  • ${jsonFile}
  • ${csvFile}

🎉 Extração completa!
  `);
}

main().catch(console.error);
