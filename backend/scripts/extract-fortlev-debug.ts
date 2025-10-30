#!/usr/bin/env node

/**
 * Fortlev Debug Script - Manual Login Inspection
 * 
 * Este script possui recursos avançados de debug para ajudar a resolver problemas de autenticação:
 * - Browser sempre visível (headless: false)
 * - Screenshots detalhados em cada etapa
 * - Logs verbosos de todos os elementos HTML
 * - Pausas prolongadas para inspeção manual
 * - Detecção de múltiplos indicadores de login
 * - Análise de formulários e campos
 * 
 * Strategy:
 * 1. Abrir página de login com máxima visibilidade
 * 2. Detectar todos os campos e botões disponíveis
 * 3. Preencher formulário com múltiplas estratégias
 * 4. Aguardar MANUALMENTE você verificar se funcionou
 * 5. Continuar extração se login bem-sucedido
 * 
 * Usage:
 *   $envContent = Get-Content mcp-servers\.env; foreach($line in $envContent) { if($line -match '^([^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }; npx tsx scripts/extract-fortlev-debug.ts
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

const FORTLEV_URL = 'https://fortlevsolar.app/login';
const FORTLEV_EMAIL = process.env.FORTLEV_EMAIL || '';
const FORTLEV_PASSWORD = process.env.FORTLEV_PASSWORD || '';

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'fortlev-debug');
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
  
  // Screenshot
  await page.screenshot({ 
    path: path.join(OUTPUT_DIR, `${stepName}.png`), 
    fullPage: true 
  });
  console.log(`  ✓ Screenshot salvo: ${stepName}.png`);
  
  // Extract detailed info
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
    
    // All inputs
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
    
    // All buttons
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
    
    // Important links
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
    
    // Forms
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
  
  // Save detailed info to JSON
  fs.writeFileSync(
    path.join(OUTPUT_DIR, `${stepName}-info.json`),
    JSON.stringify(pageInfo, null, 2)
  );
  console.log(`  ✓ Informações salvas: ${stepName}-info.json`);
  
  // Print summary
  console.log(`\n  📋 URL: ${pageInfo.url}`);
  console.log(`  📋 Título: ${pageInfo.title}`);
  console.log(`  📋 Inputs encontrados: ${pageInfo.inputs.length}`);
  console.log(`  📋 Botões encontrados: ${pageInfo.buttons.length}`);
  console.log(`  📋 Links relevantes: ${pageInfo.links.length}`);
  console.log(`  📋 Formulários: ${pageInfo.forms.length}\n`);
  
  if (pageInfo.inputs.length > 0) {
    console.log(`  📝 Inputs visíveis:`);
    pageInfo.inputs
      .filter((inp: any) => inp.visible)
      .forEach((inp: any) => {
        console.log(`    [${inp.index}] ${inp.type} | name="${inp.name}" | id="${inp.id}" | placeholder="${inp.placeholder}"`);
      });
  }
  
  if (pageInfo.buttons.length > 0) {
    console.log(`\n  🔘 Botões visíveis:`);
    pageInfo.buttons
      .filter((btn: any) => btn.visible)
      .forEach((btn: any) => {
        console.log(`    [${btn.index}] "${btn.text}" | type=${btn.type}`);
      });
  }
  
  console.log('');
}

async function loginWithDebug(page: Page): Promise<boolean> {
  try {
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║  🔐 FORTLEV - DEBUG MODE ATIVADO                         ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    if (!FORTLEV_EMAIL || !FORTLEV_PASSWORD) {
      throw new Error('FORTLEV_EMAIL e FORTLEV_PASSWORD devem estar definidos em mcp-servers/.env');
    }

    console.log(`👤 Tentando login com: ${FORTLEV_EMAIL}`);
    console.log(`🌐 URL: ${FORTLEV_URL}\n`);

    // Step 1: Navigate
    console.log('📍 PASSO 1: Navegando para página de login...');
    await page.goto(FORTLEV_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(5000);
    await captureDetailedPageInfo(page, '01-initial-page');

    // Step 2: Check if already logged in
    console.log('📍 PASSO 2: Verificando se já está logado...');
    const alreadyLoggedIn = await page.evaluate(() => {
      return !!document.querySelector('[href*="logout"], [href*="sair"]') ||
             document.body.innerText.toLowerCase().includes('minha conta') ||
             !document.body.innerText.toLowerCase().includes('login');
    });

    if (alreadyLoggedIn) {
      console.log('✅ Já está logado no Fortlev!\n');
      return true;
    }

    // Step 3: Fill email with ALL strategies
    console.log('📍 PASSO 3: Tentando preencher EMAIL com múltiplas estratégias...');
    const emailSelectors = [
      'input[type="email"]',
      'input[name="email"]',
      'input[name="username"]',
      'input[name="user"]',
      'input[placeholder*="email" i]',
      'input[placeholder*="e-mail" i]',
      'input[placeholder*="usuário" i]',
      'input[id*="email"]',
      'input[id*="user"]',
      'input[class*="email"]',
      'input[class*="user"]',
    ];

    let emailFilled = false;
    for (let i = 0; i < emailSelectors.length; i++) {
      const selector = emailSelectors[i];
      try {
        console.log(`  ⏳ [${i + 1}/${emailSelectors.length}] Tentando: ${selector}`);
        const input = page.locator(selector).first();
        
        if (await input.isVisible({ timeout: 2000 })) {
          await input.click();
          await page.waitForTimeout(300);
          await input.fill('');
          await input.fill(FORTLEV_EMAIL);
          await page.waitForTimeout(500);
          
          const value = await input.inputValue();
          if (value === FORTLEV_EMAIL) {
            console.log(`  ✅ Email preenchido com sucesso usando: ${selector}`);
            emailFilled = true;
            await captureDetailedPageInfo(page, '02-email-filled');
            break;
          } else {
            console.log(`  ⚠️  Valor não foi preenchido corretamente`);
          }
        } else {
          console.log(`  ⚠️  Input não está visível`);
        }
      } catch (e) {
        console.log(`  ❌ Falhou: ${(e as Error).message}`);
      }
    }

    if (!emailFilled) {
      console.log('\n❌ ERRO: Não foi possível preencher o campo de email');
      await captureDetailedPageInfo(page, '02-email-FAILED');
      console.log('\n💡 O browser permanecerá aberto por 60 segundos para você inspecionar...');
      await page.waitForTimeout(60000);
      return false;
    }

    // Step 4: Fill password
    console.log('\n📍 PASSO 4: Tentando preencher SENHA com múltiplas estratégias...');
    await page.waitForTimeout(1000);
    
    const passwordSelectors = [
      'input[type="password"]',
      'input[name="password"]',
      'input[name="senha"]',
      'input[name="pass"]',
      'input[placeholder*="senha" i]',
      'input[placeholder*="password" i]',
      'input[id*="password"]',
      'input[id*="senha"]',
      'input[id*="pass"]',
      'input[class*="password"]',
      'input[class*="senha"]',
    ];

    let passwordFilled = false;
    for (let i = 0; i < passwordSelectors.length; i++) {
      const selector = passwordSelectors[i];
      try {
        console.log(`  ⏳ [${i + 1}/${passwordSelectors.length}] Tentando: ${selector}`);
        const input = page.locator(selector).first();
        
        if (await input.isVisible({ timeout: 2000 })) {
          await input.click();
          await page.waitForTimeout(300);
          await input.fill('');
          await input.fill(FORTLEV_PASSWORD);
          await page.waitForTimeout(500);
          
          console.log(`  ✅ Senha preenchida usando: ${selector}`);
          passwordFilled = true;
          await captureDetailedPageInfo(page, '03-password-filled');
          break;
        } else {
          console.log(`  ⚠️  Input não está visível`);
        }
      } catch (e) {
        console.log(`  ❌ Falhou: ${(e as Error).message}`);
      }
    }

    if (!passwordFilled) {
      console.log('\n❌ ERRO: Não foi possível preencher o campo de senha');
      await captureDetailedPageInfo(page, '03-password-FAILED');
      console.log('\n💡 O browser permanecerá aberto por 60 segundos para você inspecionar...');
      await page.waitForTimeout(60000);
      return false;
    }

    // Step 5: Submit
    console.log('\n📍 PASSO 5: Submetendo formulário de login...');
    
    const submitSelectors = [
      'button[type="submit"]',
      'input[type="submit"]',
      'button:has-text("Entrar")',
      'button:has-text("Login")',
      'button:has-text("Acessar")',
      'button:has-text("Continuar")',
      'button[class*="submit"]',
      'button[class*="login"]',
      'button[class*="btn-primary"]',
    ];

    let submitted = false;
    for (let i = 0; i < submitSelectors.length; i++) {
      const selector = submitSelectors[i];
      try {
        console.log(`  ⏳ [${i + 1}/${submitSelectors.length}] Tentando clicar: ${selector}`);
        const button = page.locator(selector).first();
        
        if (await button.isVisible({ timeout: 1000 })) {
          await button.click();
          console.log(`  ✅ Clicado em: ${selector}`);
          submitted = true;
          break;
        }
      } catch (e) {
        console.log(`  ❌ Falhou: ${(e as Error).message}`);
      }
    }

    if (!submitted) {
      console.log('  ⚠️  Nenhum botão de submit encontrado, tentando Enter...');
      await page.keyboard.press('Enter');
      submitted = true;
    }

    console.log('\n⏳ Aguardando resposta do servidor (15 segundos)...');
    await page.waitForTimeout(15000);
    await captureDetailedPageInfo(page, '04-after-submit');

    // Step 6: Verify login
    console.log('📍 PASSO 6: Verificando se o login foi bem-sucedido...');
    
    const loginIndicators = await page.evaluate(() => {
      return {
        hasLogoutLink: !!document.querySelector('[href*="logout"]'),
        hasSairLink: !!document.querySelector('[href*="sair"]'),
        hasMinhaContaText: document.body.innerText.toLowerCase().includes('minha conta'),
        hasDashboardText: document.body.innerText.toLowerCase().includes('dashboard'),
        hasProdutosText: document.body.innerText.toLowerCase().includes('produtos'),
        noPasswordField: !document.querySelector('input[type="password"]'),
        noLoginText: !document.body.innerText.toLowerCase().includes('fazer login'),
        hasUserMenu: !!document.querySelector('[class*="user-menu"], [class*="profile"]'),
        currentUrl: window.location.href,
      };
    });

    console.log('\n📊 Indicadores de Login:');
    Object.entries(loginIndicators).forEach(([key, value]) => {
      const icon = value ? '✅' : '❌';
      console.log(`  ${icon} ${key}: ${value}`);
    });

    const positiveCount = Object.entries(loginIndicators)
      .filter(([key, value]) => typeof value === 'boolean' && value)
      .length;

    console.log(`\n📈 Total de indicadores positivos: ${positiveCount}/8`);

    if (positiveCount >= 3) {
      console.log('\n✅ LOGIN BEM-SUCEDIDO! (3+ indicadores positivos)\n');
      await captureDetailedPageInfo(page, '05-login-success');
      return true;
    } else {
      console.log('\n⚠️  LOGIN PODE TER FALHADO (menos de 3 indicadores positivos)');
      await captureDetailedPageInfo(page, '05-login-UNCERTAIN');
      
      console.log('\n╔════════════════════════════════════════════════════════════╗');
      console.log('║  🔍 MODO INSPEÇÃO MANUAL ATIVADO                         ║');
      console.log('║                                                           ║');
      console.log('║  O browser permanecerá aberto por 60 SEGUNDOS.           ║');
      console.log('║  Por favor:                                               ║');
      console.log('║  1. Observe a tela do browser                            ║');
      console.log('║  2. Veja os screenshots na pasta output/fortlev-debug    ║');
      console.log('║  3. Se login funcionou, aguarde continuar                ║');
      console.log('║  4. Se falhou, anote o erro e tente login manual         ║');
      console.log('╚════════════════════════════════════════════════════════════╝\n');
      
      await page.waitForTimeout(60000);
      
      // Re-check after manual inspection
      const finalCheck = await page.evaluate(() => {
        return !!document.querySelector('[href*="logout"]') ||
               document.body.innerText.toLowerCase().includes('produtos');
      });
      
      if (finalCheck) {
        console.log('✅ Após inspeção: Login detectado!\n');
        return true;
      } else {
        console.log('❌ Após inspeção: Login não confirmado\n');
        return false;
      }
    }

  } catch (error) {
    console.error(`\n❌ ERRO CRÍTICO NO LOGIN: ${(error as Error).message}\n`);
    await captureDetailedPageInfo(page, 'ERROR-login');
    console.log('💡 O browser permanecerá aberto por 60 segundos...');
    await page.waitForTimeout(60000);
    return false;
  }
}

async function extractProductLinks(page: Page): Promise<string[]> {
  console.log('\n📦 Extraindo links de produtos...');

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

      return productLinks;
    });

    console.log(`✅ Encontrados ${links.length} links de produtos\n`);
    return links;

  } catch (error) {
    console.error(`❌ Erro ao extrair links: ${(error as Error).message}`);
    return [];
  }
}

async function extractProductDetails(page: Page, productUrl: string): Promise<DetailedProduct | null> {
  try {
    await page.goto(productUrl, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(2000);

    const productData = await page.evaluate(() => {
      const titleEl = document.querySelector('h1');
      const title = titleEl?.textContent?.trim() || '';

      const priceEl = document.querySelector('[class*="price"], [class*="valor"]');
      const priceText = priceEl?.textContent?.trim() || '';

      const images: string[] = [];
      document.querySelectorAll('img').forEach(img => {
        const src = img.src;
        if (src && !src.includes('logo') && !src.includes('icon')) {
          images.push(src);
        }
      });

      const specs: Record<string, string> = {};
      document.querySelectorAll('table tr').forEach(row => {
        const cells = row.querySelectorAll('th, td');
        if (cells.length >= 2) {
          const key = cells[0].textContent?.trim();
          const value = cells[1].textContent?.trim();
          if (key && value) {
            specs[key] = value;
          }
        }
      });

      return { title, priceText, images, specs };
    });

    let price = 0;
    if (productData.priceText) {
      const priceMatch = productData.priceText.match(/[\d.,]+/);
      if (priceMatch) {
        price = parseFloat(priceMatch[0].replace(/\./g, '').replace(',', '.'));
      }
    }

    const product: DetailedProduct = {
      id: `fortlev-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      sku: '',
      title: productData.title,
      description: '',
      price,
      currency: 'BRL',
      stock: {
        available: price > 0,
        status: price > 0 ? 'disponível' : 'indisponível',
      },
      images: productData.images,
      specifications: productData.specs,
      category: categorizeProduct(productData.title),
      url: productUrl,
      distributor: 'fortlev',
      extractedAt: new Date().toISOString(),
    };

    return product;

  } catch (error) {
    console.error(`❌ Erro ao extrair produto: ${(error as Error).message}`);
    return null;
  }
}

async function main() {
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║  🚀 FORTLEV DEBUG - EXTRAÇÃO COM DIAGNÓSTICO COMPLETO    ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 100,
    args: ['--start-maximized'],
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  });

  const page = await context.newPage();

  try {
    // Step 1: Login com debug completo
    const loginSuccess = await loginWithDebug(page);
    if (!loginSuccess) {
      throw new Error('Login falhou - veja os screenshots e logs acima');
    }

    // Step 2: Extract product links
    const productLinks = await extractProductLinks(page);
    if (productLinks.length === 0) {
      console.log('⚠️  Nenhum produto encontrado. Salvando screenshot...');
      await page.screenshot({ path: path.join(OUTPUT_DIR, 'no-products.png'), fullPage: true });
      return;
    }

    // Step 3: Extract details (limit to 20 for debug)
    const allProducts: DetailedProduct[] = [];
    const linksToProcess = productLinks.slice(0, 20);
    
    console.log(`⚙️  Processando ${linksToProcess.length} produtos...\n`);
    
    for (let i = 0; i < linksToProcess.length; i++) {
      const link = linksToProcess[i];
      console.log(`🔍 [${i + 1}/${linksToProcess.length}] ${link}`);
      
      const product = await extractProductDetails(page, link);
      if (product) {
        allProducts.push(product);
        console.log(`  ✓ ${product.title} - R$ ${product.price.toFixed(2)}`);
      }
      
      await page.waitForTimeout(1500);
    }

    // Save results
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputFile = path.join(OUTPUT_DIR, `fortlev-products-${timestamp}.json`);
    
    fs.writeFileSync(outputFile, JSON.stringify({
      distributor: 'fortlev',
      extractedAt: new Date().toISOString(),
      totalProductsFound: productLinks.length,
      totalProductsExtracted: allProducts.length,
      products: allProducts,
    }, null, 2));

    console.log('\n✅ Extração concluída!');
    console.log(`📁 Arquivo salvo: ${outputFile}`);
    console.log(`📦 Total de produtos: ${allProducts.length}\n`);

  } catch (error) {
    console.error(`\n❌ Erro: ${(error as Error).message}`);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'final-error.png'), fullPage: true });
  } finally {
    console.log('\n💡 O browser será fechado em 10 segundos...');
    await page.waitForTimeout(10000);
    await browser.close();
  }
}

main();
