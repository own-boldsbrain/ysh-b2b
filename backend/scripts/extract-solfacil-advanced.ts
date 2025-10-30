#!/usr/bin/env node

/**
 * Solfácil Advanced Extractor with Computer-Use-Inspired Techniques
 * 
 * Implementa técnicas avançadas de automação:
 * - Detecção inteligente de redirecionamentos SSO
 * - Espera adaptativa por elementos dinâmicos
 * - Múltiplas estratégias de preenchimento de formulário
 * - Interceptação de requisições de rede
 * - Análise de estado da aplicação React
 * - Fallback automático para estratégias alternativas
 * 
 * URL: https://integrador.solfacil.com.br/
 * SSO: https://sso.solfacil.com.br/realms/General/protocol/openid-connect/auth
 * 
 * Usage:
 *   $envContent = Get-Content mcp-servers\.env; foreach($line in $envContent) { if($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }; npx tsx scripts/extract-solfacil-advanced.ts
 */

import { chromium, Browser, Page, BrowserContext } from 'playwright';
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
  extractedAt: string;
}

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'solfacil-advanced');
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

async function waitForNetworkIdle(page: Page, timeout: number = 5000): Promise<void> {
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
    setTimeout(resolve, timeout * 3);
  });

  await Promise.race([promise, timeoutPromise]);
  
  page.off('request', resetTimer);
  page.off('response', resetTimer);
}

async function loginKeycloakAdvanced(page: Page, email: string, password: string): Promise<boolean> {
  try {
    console.log('\n🔐 ESTRATÉGIA AVANÇADA DE LOGIN KEYCLOAK');
    console.log('=' .repeat(60));

    // Step 1: Navigate and wait for Keycloak redirect
    console.log('\n[1/7] Navegando para portal principal...');
    await page.goto('https://integrador.solfacil.com.br/', { 
      waitUntil: 'domcontentloaded',
      timeout: 60000 
    });
    
    console.log('  ⏳ Aguardando redirecionamento automático para SSO...');
    
    // Wait for URL to contain sso.solfacil.com.br with timeout
    try {
      await page.waitForURL('**/sso.solfacil.com.br/**', { timeout: 15000 });
      console.log('  ✅ Redirecionado para Keycloak SSO');
    } catch (e) {
      console.log('  ⚠️  Redirecionamento não detectado, verificando página atual...');
      const currentUrl = page.url();
      
      if (!currentUrl.includes('sso.solfacil')) {
        // Try to find and click login button
        console.log('  🔍 Procurando botão de login...');
        const loginButtons = [
          'button:has-text("Entrar")',
          'a:has-text("Entrar")',
          'button:has-text("Login")',
          'a:has-text("Login")',
          '[href*="login"]',
        ];
        
        for (const selector of loginButtons) {
          try {
            const btn = page.locator(selector).first();
            if (await btn.isVisible({ timeout: 2000 })) {
              console.log(`    ✓ Clicando em: ${selector}`);
              await btn.click();
              await page.waitForTimeout(3000);
              break;
            }
          } catch (e) { }
        }
        
        // Try waiting for redirect again
        await page.waitForURL('**/sso.solfacil.com.br/**', { timeout: 10000 }).catch(() => {});
      }
    }

    await page.screenshot({ path: path.join(OUTPUT_DIR, '01-sso-page.png'), fullPage: true });

    // Step 2: Wait for Keycloak form to be fully loaded
    console.log('\n[2/7] Aguardando formulário de login Keycloak...');
    
    // Try multiple strategies to detect form readiness
    const formReady = await Promise.race([
      page.waitForSelector('#username', { state: 'visible', timeout: 10000 }).then(() => true),
      page.waitForSelector('input[name="username"]', { state: 'visible', timeout: 10000 }).then(() => true),
      page.waitForTimeout(10000).then(() => false),
    ]);

    if (!formReady) {
      console.log('  ⚠️  Formulário não detectado no timeout esperado');
      console.log('  🔍 Analisando elementos disponíveis...');
      
      const inputs = await page.evaluate(() => {
        return Array.from(document.querySelectorAll('input')).map(i => ({
          type: i.type,
          name: i.name,
          id: i.id,
          placeholder: i.placeholder,
        }));
      });
      console.log('    Inputs encontrados:', JSON.stringify(inputs));
    } else {
      console.log('  ✅ Formulário detectado e visível');
    }

    await page.screenshot({ path: path.join(OUTPUT_DIR, '02-form-ready.png'), fullPage: true });

    // Step 3: Fill username with multiple strategies
    console.log('\n[3/7] Preenchendo username (email)...');
    
    const usernameSelectors = [
      '#username',
      'input[name="username"]',
      'input[type="text"]',
      'input[type="email"]',
      'input[id*="user"]',
      'input[placeholder*="email" i]',
    ];

    let usernameFilled = false;
    for (const selector of usernameSelectors) {
      try {
        const input = page.locator(selector).first();
        const isVisible = await input.isVisible({ timeout: 2000 });
        
        if (isVisible) {
          // Multiple fill attempts
          await input.click();
          await page.waitForTimeout(300);
          await input.clear();
          await input.fill(email);
          await page.waitForTimeout(300);
          
          // Verify
          const value = await input.inputValue();
          if (value === email) {
            console.log(`  ✅ Username preenchido com: ${selector}`);
            usernameFilled = true;
            break;
          }
        }
      } catch (e) { }
    }

    if (!usernameFilled) {
      // Fallback: try JavaScript injection
      console.log('  ⚠️  Tentando preencher via JavaScript...');
      const jsResult = await page.evaluate((emailValue) => {
        const usernameInput = document.querySelector('#username') as HTMLInputElement ||
                            document.querySelector('input[name="username"]') as HTMLInputElement;
        if (usernameInput) {
          usernameInput.value = emailValue;
          usernameInput.dispatchEvent(new Event('input', { bubbles: true }));
          usernameInput.dispatchEvent(new Event('change', { bubbles: true }));
          return true;
        }
        return false;
      }, email);
      
      if (jsResult) {
        console.log('  ✅ Username preenchido via JavaScript');
        usernameFilled = true;
      }
    }

    if (!usernameFilled) {
      throw new Error('Falha ao preencher username');
    }

    await page.screenshot({ path: path.join(OUTPUT_DIR, '03-username-filled.png'), fullPage: true });

    // Step 4: Fill password
    console.log('\n[4/7] Preenchendo password...');
    
    const passwordSelectors = [
      '#password',
      'input[name="password"]',
      'input[type="password"]',
      'input[id*="password"]',
    ];

    let passwordFilled = false;
    for (const selector of passwordSelectors) {
      try {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 2000 })) {
          await input.click();
          await page.waitForTimeout(300);
          await input.clear();
          await input.fill(password);
          await page.waitForTimeout(300);
          
          console.log(`  ✅ Password preenchido com: ${selector}`);
          passwordFilled = true;
          break;
        }
      } catch (e) { }
    }

    if (!passwordFilled) {
      throw new Error('Falha ao preencher password');
    }

    await page.screenshot({ path: path.join(OUTPUT_DIR, '04-credentials-filled.png'), fullPage: true });

    // Step 5: Submit form
    console.log('\n[5/7] Submetendo formulário...');
    
    const submitSelectors = [
      'input[type="submit"]',
      'button[type="submit"]',
      '#kc-login',
      'input[name="login"]',
      'button:has-text("Sign In")',
      'button:has-text("Entrar")',
    ];

    let submitted = false;
    for (const selector of submitSelectors) {
      try {
        const btn = page.locator(selector).first();
        if (await btn.isVisible({ timeout: 2000 })) {
          console.log(`  ⏳ Clicando em: ${selector}`);
          await btn.click();
          submitted = true;
          break;
        }
      } catch (e) { }
    }

    if (!submitted) {
      console.log('  ⚠️  Botão não encontrado, tentando Enter...');
      await page.keyboard.press('Enter');
    }

    console.log('  ✅ Formulário submetido');

    // Step 6: Wait for redirect back
    console.log('\n[6/7] Aguardando redirecionamento de volta ao portal...');
    
    try {
      await page.waitForURL('**/integrador.solfacil.com.br/**', { timeout: 20000 });
      console.log('  ✅ Redirecionado para portal principal');
    } catch (e) {
      console.log('  ⚠️  Redirecionamento não detectado via URL, verificando manualmente...');
    }

    // Wait for page to stabilize
    await waitForNetworkIdle(page, 3000);
    await page.screenshot({ path: path.join(OUTPUT_DIR, '05-after-login.png'), fullPage: true });

    // Step 7: Verify login success
    console.log('\n[7/7] Verificando sucesso do login...');
    
    const loginSuccess = await page.evaluate(() => {
      const indicators = {
        hasLogoutButton: !!document.querySelector('[href*="logout"]') || 
                         Array.from(document.querySelectorAll('button, a')).some(el => 
                           el.textContent?.toLowerCase().includes('sair')),
        hasUserMenu: !!document.querySelector('[class*="user"], [class*="profile"]'),
        hasDashboard: document.body.innerText.toLowerCase().includes('dashboard'),
        hasProdutos: document.body.innerText.toLowerCase().includes('produto'),
        noLoginForm: !document.querySelector('#username, input[name="username"]'),
        currentUrl: window.location.href,
      };
      
      const positiveCount = Object.values(indicators).filter(v => typeof v === 'boolean' && v).length;
      
      return {
        success: positiveCount >= 2,
        indicators,
        positiveCount,
      };
    });

    console.log(`\n  📊 Indicadores positivos: ${loginSuccess.positiveCount}/5`);
    console.log(`  📋 URL atual: ${loginSuccess.indicators.currentUrl}`);

    Object.entries(loginSuccess.indicators).forEach(([key, value]) => {
      if (typeof value === 'boolean') {
        console.log(`    ${value ? '✅' : '❌'} ${key}`);
      }
    });

    if (loginSuccess.success) {
      console.log('\n  ✅ LOGIN BEM-SUCEDIDO!\n');
      await page.screenshot({ path: path.join(OUTPUT_DIR, '06-login-success.png'), fullPage: true });
      
      // Navigate to shop
      console.log('\n[8/8] Navegando para LOJA de produtos...');
      await page.goto('https://loja.solfacil.com.br/spare-products', { waitUntil: 'domcontentloaded' });
      await waitForNetworkIdle(page, 3000);
      console.log('  ✅ Loja carregada');
      await page.screenshot({ path: path.join(OUTPUT_DIR, '07-shop.png'), fullPage: true });
      
      return true;
    } else {
      console.log('\n  ⚠️  Login não confirmado, aguardando inspeção manual (30s)...\n');
      await page.waitForTimeout(30000);
      
      // Final check
      const finalCheck = await page.evaluate(() => {
        return !document.querySelector('#username') && 
               (document.body.innerText.toLowerCase().includes('produto') ||
                !!document.querySelector('[href*="logout"]'));
      });
      
      if (finalCheck) {
        console.log('\n[8/8] Navegando para LOJA de produtos...');
        await page.goto('https://loja.solfacil.com.br/spare-products', { waitUntil: 'domcontentloaded' });
        await waitForNetworkIdle(page, 3000);
        console.log('  ✅ Loja carregada');
        await page.screenshot({ path: path.join(OUTPUT_DIR, '07-shop.png'), fullPage: true });
      }
      
      return finalCheck;
    }

  } catch (error) {
    console.error(`\n❌ ERRO: ${(error as Error).message}`);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'error-login.png'), fullPage: true });
    return false;
  }
}

async function extractProducts(page: Page): Promise<Product[]> {
  console.log('\n📦 EXTRAÇÃO DE PRODUTOS DA LOJA');
  console.log('='.repeat(60));

  // Scroll to trigger lazy loading
  console.log('\n[1/2] Scrolling para carregar produtos...');
  for (let i = 0; i < 50; i++) {
    await page.evaluate(() => window.scrollBy(0, window.innerHeight));
    await page.waitForTimeout(200);
    
    if (i % 10 === 0) {
      const count = await page.evaluate(() => {
        return document.querySelectorAll('a[href*="produto"], [data-product]').length;
      });
      console.log(`  📊 Scroll ${i}/50 - Elementos encontrados: ${count}`);
    }
  }

  // Extract products
  console.log('\n[2/2] Extraindo dados dos produtos...');
  
  const products = await page.evaluate(() => {
    const items: any[] = [];
    
    // Try multiple card selectors for Solfacil shop
    const cardSelectors = [
      'div[class*="card"]',
      'article',
      'div[class*="product"]',
      'li[class*="item"]',
    ];
    
    let productCards: Element[] = [];
    for (const selector of cardSelectors) {
      const found = Array.from(document.querySelectorAll(selector));
      if (found.length > 0) {
        productCards = found;
        console.log(`Found ${found.length} cards using: ${selector}`);
        break;
      }
    }

    productCards.forEach((card, index) => {
      try {
        // Extract manufacturer (ENPHASE, GOODWE, DEYE, etc.)
        const manufacturerEl = card.querySelector('strong, b, h3, h4');
        const manufacturer = manufacturerEl ? manufacturerEl.textContent?.trim() : '';
        
        // Extract SKU/Model
        let sku = '';
        const textContent = card.textContent || '';
        const skuMatch = textContent.match(/[A-Z0-9]{3,}[-_][A-Z0-9]+/);
        sku = skuMatch ? skuMatch[0] : `solfacil-${index}`;
        
        // Extract title/description
        let title = '';
        const paragraphs = card.querySelectorAll('p');
        if (paragraphs.length > 0) {
          title = Array.from(paragraphs)
            .map(p => p.textContent?.trim())
            .filter(t => t && t.length > 10)
            .join(' ');
        }
        
        // Clean up title
        title = title.replace(/\s+/g, ' ')
                    .replace(/mais detalhes do produto/gi, '')
                    .replace(/Total R\$[\d.,\s]+/g, '')
                    .trim();
        
        // Extract price
        let price = 0;
        const priceMatches = textContent.match(/R\$\s*([\d.,]+)/g);
        if (priceMatches && priceMatches.length > 0) {
          const priceStr = priceMatches[0].replace('R$', '').trim()
                                          .replace(/\./g, '').replace(',', '.');
          price = parseFloat(priceStr);
        }
        
        // Extract image
        let imageUrl = '';
        const img = card.querySelector('img');
        if (img) {
          imageUrl = (img as HTMLImageElement).src || (img as HTMLImageElement).dataset.src || '';
        }
        
        // Extract link
        const link = card.querySelector('a');
        const url = link ? link.href : window.location.href;
        
        // Only add if we have meaningful data
        if (title && title.length > 15 && price > 0) {
          items.push({
            sku,
            manufacturer: manufacturer || 'UNKNOWN',
            title: `${manufacturer} ${sku} ${title}`.trim(),
            url,
            imageUrl,
            price,
          });
        }
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
      distributor: 'solfacil',
      extractedAt: new Date().toISOString(),
    }));

  console.log(`\n  ✅ ${finalProducts.length} produtos extraídos\n`);
  return finalProducts;
}

async function main() {
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║  🚀 SOLFÁCIL - ADVANCED KEYCLOAK SSO EXTRACTOR          ║');
  console.log('╚════════════════════════════════════════════════════════════╝');

  const email = process.env.SOLFACIL_EMAIL || '';
  const password = process.env.SOLFACIL_PASSWORD || '';

  if (!email || !password) {
    console.log('\n❌ Erro: SOLFACIL_EMAIL e SOLFACIL_PASSWORD devem estar definidos');
    process.exit(1);
  }

  console.log(`\n👤 Email: ${email}`);
  console.log(`🌐 URL: https://integrador.solfacil.com.br/\n`);

  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 50,
  });
  
  try {
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    });
    
    const page = await context.newPage();
    
    // Login
    const loginSuccess = await loginKeycloakAdvanced(page, email, password);
    
    if (!loginSuccess) {
      console.log('\n❌ Login falhou - veja os screenshots em output/solfacil-advanced/');
      return;
    }

    // Extract products
    const products = await extractProducts(page);

    if (products.length === 0) {
      console.log('\n⚠️  Nenhum produto encontrado');
      await page.screenshot({ path: path.join(OUTPUT_DIR, 'no-products.png'), fullPage: true });
    }

    // Save results
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const jsonFile = path.join(OUTPUT_DIR, `products-${timestamp}.json`);
    fs.writeFileSync(jsonFile, JSON.stringify({
      distributor: 'solfacil',
      extractedAt: new Date().toISOString(),
      totalProducts: products.length,
      products,
    }, null, 2));

    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║  ✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO                       ║');
    console.log('╚════════════════════════════════════════════════════════════╝');
    console.log(`\n📊 Total de produtos: ${products.length}`);
    console.log(`📁 Arquivo salvo: ${jsonFile}\n`);

    // Category summary
    const byCategory = products.reduce((acc, p) => {
      acc[p.category] = (acc[p.category] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    console.log('📦 Por categoria:');
    Object.entries(byCategory)
      .sort((a, b) => b[1] - a[1])
      .forEach(([cat, count]) => {
        console.log(`  • ${cat}: ${count}`);
      });

    console.log('');

  } catch (error) {
    console.log(`\n❌ Erro: ${(error as Error).message}`);
    throw error;
  } finally {
    await browser.close();
  }
}

main().catch(console.error);
