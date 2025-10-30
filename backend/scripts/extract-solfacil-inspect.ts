#!/usr/bin/env node

/**
 * Solfácil Inspector - Descobre estrutura da página
 * 
 * Este script faz login e inspeciona a estrutura HTML
 * para identificar os seletores corretos dos produtos
 */

import { chromium, Browser, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

const OUTPUT_DIR = path.join(process.cwd(), 'output', 'solfacil-inspect');
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

async function waitForNetworkIdle(page: Page, timeout: number = 5000): Promise<void> {
  return new Promise((resolve) => {
    let timer: NodeJS.Timeout;
    const onRequest = () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        page.removeListener('request', onRequest);
        page.removeListener('response', onResponse);
        resolve();
      }, timeout);
    };
    const onResponse = onRequest;

    page.on('request', onRequest);
    page.on('response', onResponse);

    timer = setTimeout(() => {
      page.removeListener('request', onRequest);
      page.removeListener('response', onResponse);
      resolve();
    }, timeout);
  });
}

async function inspectPage(page: Page, step: string): Promise<void> {
  console.log(`\n📸 [${step}] Inspecionando página...`);
  
  const info = await page.evaluate(() => {
    const allElements = Array.from(document.querySelectorAll('*'));
    const classSet = new Set<string>();
    allElements.forEach(el => {
      if (el.className && typeof el.className === 'string') {
        el.className.split(' ').forEach(c => c && classSet.add(c));
      }
    });
    const topClasses = Array.from(classSet).slice(0, 20);
    
    const elementsWithId = Array.from(document.querySelectorAll('[id]'));
    const topIds = elementsWithId
      .map(el => el.id)
      .filter(id => id)
      .slice(0, 10);

    return {
      url: window.location.href,
      title: document.title,
      
      // Links
      links: Array.from(document.querySelectorAll('a'))
        .map(a => ({ href: a.href, text: a.textContent?.trim().substring(0, 50) }))
        .filter(l => l.text)
        .slice(0, 30),
      
      // Buttons
      buttons: Array.from(document.querySelectorAll('button'))
        .map(b => ({ text: b.textContent?.trim().substring(0, 50), class: b.className }))
        .filter(b => b.text)
        .slice(0, 20),
      
      // Divs with common product patterns
      productDivs: Array.from(document.querySelectorAll('div[class*="product"], div[class*="card"], div[class*="item"]'))
        .map(d => ({
          tag: d.tagName,
          class: d.className,
          id: d.id,
          children: d.children.length,
        }))
        .slice(0, 15),
      
      // Images
      images: Array.from(document.querySelectorAll('img'))
        .map(img => ({ src: img.src, alt: img.alt }))
        .slice(0, 20),
      
      // Classes statistics
      topClasses: topClasses,
      topIds: topIds,
      
      // Text content indicators
      hasProducts: document.body.innerText.toLowerCase().includes('produto'),
      hasCatalog: document.body.innerText.toLowerCase().includes('catálogo') || 
                   document.body.innerText.toLowerCase().includes('catalogo'),
      hasPrice: document.body.innerText.includes('R$'),
      
      // Menu items
      menuItems: Array.from(document.querySelectorAll('nav a, [role="navigation"] a, header a'))
        .map(a => ({ href: a.getAttribute('href'), text: a.textContent?.trim() }))
        .filter(m => m.text)
        .slice(0, 20),
    };
  });

  // Save to file
  const filename = `${step.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.json`;
  fs.writeFileSync(
    path.join(OUTPUT_DIR, filename),
    JSON.stringify(info, null, 2)
  );

  // Console summary
  console.log(`  📋 URL: ${info.url}`);
  console.log(`  📋 Título: ${info.title}`);
  console.log(`  📋 Links: ${info.links.length}`);
  console.log(`  📋 Botões: ${info.buttons.length}`);
  console.log(`  📋 Product Divs: ${info.productDivs.length}`);
  console.log(`  📋 Imagens: ${info.images.length}`);
  console.log(`  📋 Has "produto": ${info.hasProducts}`);
  console.log(`  📋 Has "catálogo": ${info.hasCatalog}`);
  console.log(`  📋 Has "R$": ${info.hasPrice}`);
  
  console.log(`\n  📦 Top Classes:`);
  info.topClasses.slice(0, 10).forEach(c => console.log(`    - ${c}`));
  
  console.log(`\n  🔗 Menu Items:`);
  info.menuItems.slice(0, 10).forEach(m => console.log(`    - ${m.text}: ${m.href}`));
  
  console.log(`\n  ✅ Arquivo salvo: ${filename}`);
}

async function main() {
  const email = process.env.SOLFACIL_EMAIL;
  const password = process.env.SOLFACIL_PASSWORD;

  if (!email || !password) {
    console.error('❌ Variáveis SOLFACIL_EMAIL e SOLFACIL_PASSWORD devem estar definidas');
    process.exit(1);
  }

  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║  🔍 SOLFÁCIL INSPECTOR - DESCOBERTA DE ESTRUTURA         ║');
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
    // Step 1: Navigate to main portal
    console.log('[1/6] Navegando para portal principal...');
    await page.goto('https://integrador.solfacil.com.br/', { waitUntil: 'domcontentloaded' });
    
    // Step 2: Wait for SSO redirect
    console.log('[2/6] Aguardando redirecionamento SSO...');
    await page.waitForURL('**/sso.solfacil.com.br/**', { timeout: 10000 });
    console.log('  ✅ Redirecionado para Keycloak SSO');

    // Step 3: Fill login form
    console.log('[3/6] Preenchendo login...');
    await page.waitForSelector('#username', { timeout: 5000 });
    await page.fill('#username', email);
    await page.fill('#password', password);
    await page.click('input[type="submit"]');
    
    // Step 4: Wait for redirect back
    console.log('[4/6] Aguardando redirecionamento...');
    await page.waitForURL('**/integrador.solfacil.com.br/**', { timeout: 20000 });
    await waitForNetworkIdle(page, 3000);
    console.log('  ✅ Login bem-sucedido');

    // Step 5: Inspect home page
    await page.screenshot({ path: path.join(OUTPUT_DIR, '01-home.png'), fullPage: true });
    await inspectPage(page, '01-home');

    // Step 6: Look for product/catalog links in menu
    console.log('\n[5/6] Procurando links de produtos/catálogo...');
    
    const productLinks = await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      return links
        .filter(a => {
          const text = a.textContent?.toLowerCase() || '';
          const href = a.href?.toLowerCase() || '';
          return text.includes('produto') || 
                 text.includes('catálogo') || 
                 text.includes('catalogo') ||
                 href.includes('produto') ||
                 href.includes('catalog') ||
                 href.includes('item');
        })
        .map(a => ({ href: a.href, text: a.textContent?.trim() }));
    });

    console.log(`  📦 Encontrados ${productLinks.length} links relacionados a produtos:`);
    productLinks.forEach(link => {
      console.log(`    - ${link.text}: ${link.href}`);
    });

    // Try clicking first product/catalog link
    if (productLinks.length > 0) {
      console.log(`\n[6/6] Navegando para: ${productLinks[0].text}`);
      await page.click(`a[href="${new URL(productLinks[0].href).pathname}"]`);
      await waitForNetworkIdle(page, 3000);
      await page.screenshot({ path: path.join(OUTPUT_DIR, '02-products-page.png'), fullPage: true });
      await inspectPage(page, '02-products-page');
    } else {
      console.log('\n[6/6] Inspecionando URLs alternativas...');
      
      // Try common product URLs
      const urlsToTry = [
        'https://integrador.solfacil.com.br/produtos',
        'https://integrador.solfacil.com.br/catalogo',
        'https://integrador.solfacil.com.br/catalog',
        'https://integrador.solfacil.com.br/items',
      ];

      for (const url of urlsToTry) {
        try {
          console.log(`  🔗 Tentando: ${url}`);
          await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 5000 });
          await waitForNetworkIdle(page, 2000);
          
          const hasContent = await page.evaluate(() => document.body.innerText.length > 100);
          if (hasContent) {
            console.log(`  ✅ Página encontrada!`);
            await page.screenshot({ path: path.join(OUTPUT_DIR, `02-${url.split('/').pop()}.png`), fullPage: true });
            await inspectPage(page, `02-${url.split('/').pop()}`);
            break;
          }
        } catch (e) {
          console.log(`  ❌ Não encontrado`);
        }
      }
    }

    console.log('\n\n╔════════════════════════════════════════════════════════════╗');
    console.log('║  ✅ INSPEÇÃO CONCLUÍDA                                   ║');
    console.log('╚════════════════════════════════════════════════════════════╝');
    console.log(`\n📁 Resultados salvos em: ${OUTPUT_DIR}`);
    console.log('\n💡 Aguarde 30 segundos para inspeção manual...\n');
    
    await page.waitForTimeout(30000);

  } catch (error) {
    console.error(`\n❌ Erro: ${(error as Error).message}`);
    await page.screenshot({ path: path.join(OUTPUT_DIR, 'error.png'), fullPage: true });
  } finally {
    await browser.close();
  }
}

main();
