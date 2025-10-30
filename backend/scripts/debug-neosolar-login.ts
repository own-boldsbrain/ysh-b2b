#!/usr/bin/env node

/**
 * Debug Neosolar Login Page
 */

import { chromium } from 'playwright';
import { writeFileSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function debugLoginPage() {
  console.log('🔍 Analisando página de login Neosolar...\n');

  const browser = await chromium.launch({ headless: false }); // Show browser
  const page = await browser.newPage();

  try {
    console.log('Navegando para https://portalb2b.neosolar.com.br/...');
    await page.goto('https://portalb2b.neosolar.com.br/', { waitUntil: 'domcontentloaded' });

    console.log('⏳ Aguardando 5 segundos para página carregar...');
    await page.waitForTimeout(5000);

    // Get page info
    const title = await page.title();
    const url = page.url();
    console.log(`\n📄 Título: ${title}`);
    console.log(`📍 URL: ${url}`);

    // Check what inputs are on the page
    const inputs = await page.$$eval('input', (els) =>
      els.map((el: any) => ({
        type: el.type,
        name: el.name,
        id: el.id,
        placeholder: el.placeholder,
      }))
    );

    console.log('\n📝 Campos de entrada (inputs):');
    inputs.forEach((input, i) => {
      console.log(`  ${i + 1}. type="${input.type}" name="${input.name}" id="${input.id}" placeholder="${input.placeholder}"`);
    });

    // Check for buttons
    const buttons = await page.$$eval('button', (els) =>
      els.map((el: any) => ({
        type: el.type,
        text: el.textContent?.trim().substring(0, 50),
        class: el.className,
      }))
    );

    console.log('\n🔘 Botões encontrados:');
    buttons.forEach((btn, i) => {
      console.log(`  ${i + 1}. type="${btn.type}" text="${btn.text}" class="${btn.class}"`);
    });

    // Check for forms
    const forms = await page.$$eval('form', (els) =>
      els.map((el: any) => ({
        action: el.action,
        method: el.method,
        id: el.id,
      }))
    );

    console.log('\n📋 Formulários encontrados:');
    forms.forEach((form, i) => {
      console.log(`  ${i + 1}. action="${form.action}" method="${form.method}" id="${form.id}"`);
    });

    // Save full HTML
    const html = await page.content();
    const timestamp = Date.now();
    const htmlPath = join(__dirname, `login-page-${timestamp}.html`);
    writeFileSync(htmlPath, html);
    console.log(`\n💾 HTML salvo em: ${htmlPath}`);

    // Take screenshot
    const screenshotPath = join(__dirname, `login-page-${timestamp}.png`);
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 Screenshot salvo em: ${screenshotPath}`);

    console.log('\n✅ Análise completa! Verifique os arquivos salvos.');
    console.log('ℹ️  O navegador permanecerá aberto por 60 segundos...');

    await page.waitForTimeout(60000);

  } catch (error) {
    console.error('❌ Erro:', error);
  } finally {
    await browser.close();
  }
}

debugLoginPage();
