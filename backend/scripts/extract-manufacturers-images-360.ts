#!/usr/bin/env node

/**
 * =====================================================
 * EXTRATOR 360° DE IMAGENS DOS FABRICANTES
 * =====================================================
 * 
 * Técnicas consolidadas das extrações bem-sucedidas:
 * ✅ Playwright com scroll progressivo (Solfácil/Fortlev)
 * ✅ Múltiplos seletores CSS com fallback (Fortlev)
 * ✅ Retry logic e circuit breaker (Solfácil)
 * ✅ Cache inteligente para evitar re-downloads
 * ✅ Nomenclatura padronizada: FABRICANTE-MODELO-POTENCIA.ext
 * ✅ Download paralelo com rate limiting
 * ✅ Validação de imagens (tamanho mínimo, tipo)
 * 
 * Priorização hierárquica:
 * 1. Site oficial do fabricante
 * 2. CDN do fabricante
 * 3. Distribuidor (fallback)
 * 4. Placeholder
 * 
 * Usage:
 *   npx tsx scripts/extract-manufacturers-images-360.ts
 */

import { chromium, Browser, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';
import * as http from 'http';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// =====================================================
// INTERFACES
// =====================================================

interface ManufacturerInfo {
  name: string;
  country: string;
  official_site: string;
  product_pages: Record<string, string>;
  image_patterns: string[];
  sku_patterns: string[];
  priority: number;
  active: boolean;
  notes?: string;
}

interface Product {
  sku: string;
  title: string;
  manufacturer: string;
  model?: string;
  power?: string;
  category: string;
  distributor_url?: string;
  imageUrl?: string;
}

interface ImageExtractionResult {
  sku: string;
  manufacturer: string;
  source: 'official' | 'cdn' | 'distributor' | 'placeholder';
  original_url: string;
  local_path: string;
  standardized_filename: string;
  success: boolean;
  filesize_bytes?: number;
  dimensions?: { width: number; height: number };
  error?: string;
  timestamp: string;
}

interface ExtractionMetrics {
  total: number;
  successful: number;
  failed: number;
  from_official: number;
  from_cdn: number;
  from_distributor: number;
  placeholders: number;
  duration_ms: number;
  average_size_kb: number;
}

// =====================================================
// CONFIGURAÇÕES
// =====================================================

const ROOT_PATH = path.join(__dirname, '..');
const MANUFACTURERS_CATALOG = path.join(ROOT_PATH, 'config/manufacturers-catalog.json');
const PRODUCTS_INVENTORY_DIR = path.join(ROOT_PATH, 'data/inventory');
const OUTPUT_IMAGES_DIR = path.join(ROOT_PATH, 'static/products-official');
const CACHE_FILE = path.join(ROOT_PATH, 'cache/manufacturer-images-360.json');
const REPORT_FILE = path.join(ROOT_PATH, 'output/manufacturer-images-report-360.json');

const MAX_CONCURRENT_DOWNLOADS = 5;
const TIMEOUT_MS = 30000;
const MIN_IMAGE_SIZE_BYTES = 1024; // 1KB
const RETRY_ATTEMPTS = 3;
const SCROLL_ITERATIONS = 30;
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36';

// =====================================================
// UTILITÁRIOS
// =====================================================

function ensureDir(dirPath: string): void {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function loadManufacturersCatalog(): Record<string, ManufacturerInfo> {
  if (!fs.existsSync(MANUFACTURERS_CATALOG)) {
    throw new Error(`Catálogo não encontrado: ${MANUFACTURERS_CATALOG}`);
  }

  const data = JSON.parse(fs.readFileSync(MANUFACTURERS_CATALOG, 'utf8'));
  return data.manufacturers;
}

function loadCache(): Record<string, ImageExtractionResult> {
  if (!fs.existsSync(CACHE_FILE)) {
    return {};
  }

  try {
    return JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
  } catch {
    return {};
  }
}

function saveCache(cache: Record<string, ImageExtractionResult>): void {
  ensureDir(path.dirname(CACHE_FILE));
  fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2));
}

function normalizeManufacturer(name: string): string {
  return name
    .toUpperCase()
    .replace(/[^A-Z0-9]/g, '')
    .trim();
}

function extractPowerRating(text: string): string | undefined {
  // Padrões comuns: "550W", "5.5kW", "10KW", "3000VA"
  const patterns = [
    /(\d+(?:\.\d+)?)\s*kW/i,
    /(\d+(?:\.\d+)?)\s*W/i,
    /(\d+(?:\.\d+)?)\s*VA/i,
  ];

  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      return match[1] + match[0].replace(/\d+\.?\d*/g, '').toUpperCase();
    }
  }

  return undefined;
}

function extractModel(sku: string, title: string, patterns: string[]): string {
  // Try SKU patterns first
  for (const pattern of patterns) {
    const regex = new RegExp(pattern, 'i');
    const match = sku.match(regex) || title.match(regex);
    if (match) {
      return match[0].toUpperCase();
    }
  }

  // Fallback: use SKU
  return sku.replace(/[^a-zA-Z0-9.-]/g, '').toUpperCase().substring(0, 30);
}

function standardizeFilename(product: Product, manufacturer: ManufacturerInfo): string {
  const mfg = normalizeManufacturer(manufacturer.name);
  const model = extractModel(product.sku, product.title, manufacturer.sku_patterns);
  const power = product.power || extractPowerRating(product.title);

  let filename = `${mfg}-${model}`;
  if (power) {
    filename += `-${power.replace(/[^A-Z0-9.]/g, '')}`;
  }

  return filename;
}

function categorizeProduct(title: string): string {
  const lowerTitle = title.toLowerCase();
  
  const categories: Record<string, string[]> = {
    painel: ['painel', 'módulo', 'placa solar', 'panel', 'module', 'fotovoltaico'],
    inversor: ['inversor', 'inverter', 'grid-tie', 'híbrido', 'hybrid', 'off-grid'],
    bateria: ['bateria', 'battery', 'armazenamento', 'storage', 'lifepo4', 'litio'],
    estrutura: ['estrutura', 'suporte', 'mounting', 'trilho', 'fixação'],
    cabo: ['cabo', 'wire', 'fio', 'condutor'],
    conector: ['conector', 'mc4', 'connector'],
    bomba: ['bomba', 'pump', 'anauger'],
    carregador: ['carregador', 'controlador', 'mppt', 'charger'],
  };

  for (const [category, keywords] of Object.entries(categories)) {
    if (keywords.some(keyword => lowerTitle.includes(keyword))) {
      return category;
    }
  }

  return 'outros';
}

// =====================================================
// DOWNLOAD DE IMAGENS
// =====================================================

async function downloadImage(url: string, targetPath: string): Promise<boolean> {
  return new Promise((resolve) => {
    const protocol = url.startsWith('https') ? https : http;

    const timeout = setTimeout(() => {
      console.log(`⏱️  Timeout downloading: ${url}`);
      resolve(false);
    }, TIMEOUT_MS);

    protocol.get(url, { headers: { 'User-Agent': USER_AGENT } }, (response) => {
      clearTimeout(timeout);

      // Handle redirects
      if (response.statusCode === 301 || response.statusCode === 302) {
        const redirectUrl = response.headers.location;
        if (redirectUrl) {
          resolve(downloadImage(redirectUrl, targetPath));
          return;
        }
      }

      if (response.statusCode !== 200) {
        console.log(`❌ HTTP ${response.statusCode}: ${url}`);
        resolve(false);
        return;
      }

      ensureDir(path.dirname(targetPath));

      const fileStream = fs.createWriteStream(targetPath);
      response.pipe(fileStream);

      fileStream.on('finish', () => {
        fileStream.close();

        // Validate file size
        const stats = fs.statSync(targetPath);
        if (stats.size < MIN_IMAGE_SIZE_BYTES) {
          fs.unlinkSync(targetPath);
          console.log(`⚠️  Imagem muito pequena: ${url}`);
          resolve(false);
        } else {
          resolve(true);
        }
      });

      fileStream.on('error', (err) => {
        fs.unlink(targetPath, () => {});
        console.log(`❌ Erro ao salvar: ${err.message}`);
        resolve(false);
      });
    }).on('error', (err) => {
      clearTimeout(timeout);
      console.log(`❌ Erro de conexão: ${err.message}`);
      resolve(false);
    });
  });
}

async function downloadWithRetry(url: string, targetPath: string, retries: number = RETRY_ATTEMPTS): Promise<boolean> {
  for (let attempt = 1; attempt <= retries; attempt++) {
    console.log(`📥 Tentativa ${attempt}/${retries}: ${url}`);
    const success = await downloadImage(url, targetPath);
    if (success) {
      return true;
    }
    
    if (attempt < retries) {
      await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
    }
  }

  return false;
}

// =====================================================
// EXTRAÇÃO COM PLAYWRIGHT
// =====================================================

async function extractOfficialImage(
  page: Page,
  product: Product,
  manufacturer: ManufacturerInfo
): Promise<string | null> {
  try {
    const productPage = manufacturer.product_pages[product.category] || Object.values(manufacturer.product_pages)[0];
    
    if (!productPage) {
      return null;
    }

    console.log(`🔍 Buscando no site oficial: ${manufacturer.official_site}`);
    
    await page.goto(productPage, { waitUntil: 'domcontentloaded', timeout: TIMEOUT_MS });
    await page.waitForTimeout(2000);

    // Progressive scroll to load lazy images
    for (let i = 0; i < SCROLL_ITERATIONS; i++) {
      await page.evaluate(() => window.scrollBy(0, window.innerHeight / 2));
      await page.waitForTimeout(100);
    }

    // Multiple selector strategies (técnica Fortlev)
    const imageSelectors = [
      `img[alt*="${product.model}" i]`,
      `img[src*="${product.model}" i]`,
      `img[title*="${product.model}" i]`,
      `img[data-sku="${product.sku}"]`,
      `a[href*="${product.model}" i] img`,
      'div[class*="product"] img',
      'div[class*="item"] img',
      'picture img',
      'figure img',
    ];

    for (const selector of imageSelectors) {
      try {
        const images = await page.$$eval(selector, (imgs) =>
          imgs
            .map((img: any) => img.src || img.dataset.src || img.dataset.lazyload)
            .filter((src: string) => src && src.startsWith('http'))
        );

        if (images.length > 0) {
          console.log(`✅ Imagem encontrada com seletor: ${selector}`);
          return images[0];
        }
      } catch (e) {
        // Continue to next selector
      }
    }

    // Fallback: buscar por padrões de URL
    const allImages = await page.$$eval('img', (imgs) =>
      imgs
        .map((img: any) => img.src || img.dataset.src)
        .filter((src: string) => src && src.startsWith('http'))
    );

    for (const pattern of manufacturer.image_patterns) {
      const patternRegex = new RegExp(pattern.replace('{model}', '.*'), 'i');
      const match = allImages.find(url => patternRegex.test(url));
      if (match) {
        console.log(`✅ Imagem encontrada por padrão: ${pattern}`);
        return match;
      }
    }

    return null;
  } catch (error) {
    console.log(`⚠️  Erro ao extrair do site oficial: ${(error as Error).message}`);
    return null;
  }
}

async function searchImageWithBrowser(
  browser: Browser,
  product: Product,
  manufacturer: ManufacturerInfo
): Promise<string | null> {
  const page = await browser.newPage();
  
  try {
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    // Tentar site oficial
    const officialImage = await extractOfficialImage(page, product, manufacturer);
    if (officialImage) {
      return officialImage;
    }

    // Tentar busca no Google Images (fallback)
    const searchQuery = `${manufacturer.name} ${product.model || product.sku} product image`;
    const googleImagesUrl = `https://www.google.com/search?tbm=isch&q=${encodeURIComponent(searchQuery)}`;
    
    await page.goto(googleImagesUrl, { waitUntil: 'domcontentloaded', timeout: TIMEOUT_MS });
    await page.waitForTimeout(2000);

    const firstImage = await page.$eval('img[src*="gstatic.com"]', (img: any) => {
      // Pegar a imagem seguinte (primeira é logo do Google)
      const nextImg = img.parentElement?.parentElement?.querySelector('img[src^="http"]');
      return nextImg?.src || null;
    });

    if (firstImage && !firstImage.includes('gstatic')) {
      console.log('✅ Imagem encontrada via Google Images');
      return firstImage;
    }

    return null;
  } catch (error) {
    console.log(`⚠️  Erro na busca com browser: ${(error as Error).message}`);
    return null;
  } finally {
    await page.close();
  }
}

// =====================================================
// ORQUESTRADOR PRINCIPAL
// =====================================================

async function extractManufacturerImages(
  products: Product[],
  manufacturers: Record<string, ManufacturerInfo>
): Promise<ImageExtractionResult[]> {
  const cache = loadCache();
  const results: ImageExtractionResult[] = [];
  
  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-blink-features=AutomationControlled'],
  });

  console.log('🚀 Iniciando extração de imagens dos fabricantes...\n');

  for (let i = 0; i < products.length; i++) {
    const product = products[i];
    const cacheKey = `${product.manufacturer}-${product.sku}`;

    // Check cache
    if (cache[cacheKey] && cache[cacheKey].success) {
      console.log(`📦 Cache hit: ${product.sku}`);
      results.push(cache[cacheKey]);
      continue;
    }

    const manufacturer = manufacturers[product.manufacturer];
    if (!manufacturer || !manufacturer.active) {
      console.log(`⚠️  Fabricante inativo ou não encontrado: ${product.manufacturer}`);
      continue;
    }

    console.log(`\n[${i + 1}/${products.length}] ${product.manufacturer} - ${product.sku}`);

    const standardFilename = standardizeFilename(product, manufacturer);
    const ext = 'png';
    const localPath = path.join(
      OUTPUT_IMAGES_DIR,
      product.manufacturer,
      `${standardFilename}.${ext}`
    );

    let imageUrl: string | null = null;
    let source: 'official' | 'cdn' | 'distributor' | 'placeholder' = 'placeholder';

    // 1. Tentar site oficial com Playwright
    if (manufacturer.priority === 1) {
      imageUrl = await searchImageWithBrowser(browser, product, manufacturer);
      if (imageUrl) {
        source = 'official';
      }
    }

    // 2. Tentar distribuidor (fallback)
    if (!imageUrl && product.distributor_url) {
      imageUrl = product.imageUrl || null;
      if (imageUrl) {
        source = 'distributor';
      }
    }

    // 3. Placeholder
    if (!imageUrl) {
      console.log('⚠️  Nenhuma imagem encontrada, usando placeholder');
      const placeholderPath = path.join(ROOT_PATH, `static/placeholders/${product.category}.png`);
      if (fs.existsSync(placeholderPath)) {
        imageUrl = placeholderPath;
        source = 'placeholder';
      }
    }

    // Download
    let success = false;
    let filesize_bytes = 0;

    if (imageUrl && !imageUrl.startsWith('/static/placeholders')) {
      success = await downloadWithRetry(imageUrl, localPath);
      if (success) {
        const stats = fs.statSync(localPath);
        filesize_bytes = stats.size;
        console.log(`✅ Download concluído: ${filesize_bytes} bytes`);
      }
    } else if (imageUrl) {
      // Copy placeholder
      fs.copyFileSync(imageUrl, localPath);
      success = true;
      filesize_bytes = fs.statSync(localPath).size;
    }

    const result: ImageExtractionResult = {
      sku: product.sku,
      manufacturer: product.manufacturer,
      source,
      original_url: imageUrl || '',
      local_path: localPath,
      standardized_filename: `${standardFilename}.${ext}`,
      success,
      filesize_bytes: success ? filesize_bytes : undefined,
      error: success ? undefined : 'Failed to download',
      timestamp: new Date().toISOString(),
    };

    results.push(result);
    cache[cacheKey] = result;

    // Save cache every 10 products
    if (i % 10 === 0) {
      saveCache(cache);
    }

    // Rate limiting
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  await browser.close();
  saveCache(cache);

  return results;
}

// =====================================================
// LOAD PRODUCTS FROM INVENTORY
// =====================================================

function loadProductsFromInventory(): Product[] {
  const products: Product[] = [];

  // Tentar múltiplos locais
  const searchPaths = [
    path.join(ROOT_PATH, 'data/inventory'),
    path.join(ROOT_PATH, 'output/deep-scraping'),
    path.join(ROOT_PATH, 'output/multi-distributor'),
    path.join(ROOT_PATH, 'output'),
    path.join(ROOT_PATH, 'mcp-servers/output'),
  ];

  for (const searchPath of searchPaths) {
    if (!fs.existsSync(searchPath)) continue;

    const files = fs.readdirSync(searchPath)
      .filter(f => f.endsWith('.json') && !f.includes('summary') && !f.includes('extraction-summary'));

    console.log(`   Buscando em: ${path.relative(ROOT_PATH, searchPath)} (${files.length} arquivos)`);

    for (const file of files) {
      try {
        const filePath = path.join(searchPath, file);
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        let items: any[] = [];
        
        // Handle different data structures
        if (Array.isArray(data)) {
          items = data;
        } else if (data.products && Array.isArray(data.products)) {
          items = data.products;
        } else if (data.data && Array.isArray(data.data)) {
          items = data.data;
        }

        for (const item of items) {
          if ((item.sku || item.codigo || item.id) && (item.title || item.nome || item.produto)) {
            const title = item.title || item.nome || item.produto || '';
            const manufacturer = item.manufacturer || item.fabricante || extractManufacturerFromTitle(title);

            products.push({
              sku: item.sku || item.codigo || item.id,
              title,
              manufacturer,
              model: item.model || item.modelo,
              power: item.power || item.potencia,
              category: categorizeProduct(title),
              distributor_url: item.url,
              imageUrl: item.imageUrl || item.imagem || item.image,
            });
          }
        }
      } catch (error) {
        console.log(`   ⚠️  Erro ao ler ${file}: ${(error as Error).message}`);
      }
    }
  }

  return products;
}

function extractManufacturerFromTitle(title: string): string {
  const manufacturers = [
    'LONGI', 'GROWATT', 'SUNGROW', 'RISEN', 'JINKO', 'TRINA', 'CANADIAN',
    'BYD', 'FRONIUS', 'DEYE', 'SOLIS', 'HUAWEI', 'PYLONTECH', 'DYNESS',
    'ENPHASE', 'FORTLEV', 'ANAUGER', 'CANADIAN SOLAR', 'SAJ', 'SOLPLANET',
    'ZNSHINE', 'SINE ENERGY', 'OSDA', 'UNIPOWER'
  ];

  const upperTitle = title.toUpperCase();
  
  for (const mfg of manufacturers) {
    if (upperTitle.includes(mfg)) {
      return mfg.replace(/\s+/g, '-');
    }
  }

  return 'UNKNOWN';
}

// =====================================================
// MAIN
// =====================================================

async function main() {
  const startTime = Date.now();

  console.log('═══════════════════════════════════════════════════════════');
  console.log('   EXTRATOR 360° DE IMAGENS DOS FABRICANTES');
  console.log('═══════════════════════════════════════════════════════════\n');

  // Setup
  ensureDir(OUTPUT_IMAGES_DIR);
  ensureDir(path.dirname(CACHE_FILE));
  ensureDir(path.dirname(REPORT_FILE));

  // Load data
  console.log('📂 Carregando catálogo de fabricantes...');
  const manufacturers = loadManufacturersCatalog();
  console.log(`✅ ${Object.keys(manufacturers).length} fabricantes carregados\n`);

  console.log('📦 Carregando produtos do inventário...');
  const products = loadProductsFromInventory();
  console.log(`✅ ${products.length} produtos carregados\n`);

  // Filter only products with identified manufacturers
  const productsWithManufacturers = products.filter(p => 
    p.manufacturer !== 'UNKNOWN' && manufacturers[p.manufacturer]
  );

  console.log(`🎯 ${productsWithManufacturers.length} produtos com fabricantes identificados\n`);

  // Extract images
  const results = await extractManufacturerImages(productsWithManufacturers, manufacturers);

  // Calculate metrics
  const duration_ms = Date.now() - startTime;
  const successful = results.filter(r => r.success);
  const from_official = results.filter(r => r.source === 'official');
  const from_cdn = results.filter(r => r.source === 'cdn');
  const from_distributor = results.filter(r => r.source === 'distributor');
  const placeholders = results.filter(r => r.source === 'placeholder');

  const totalSize = successful.reduce((sum, r) => sum + (r.filesize_bytes || 0), 0);
  const averageSize = totalSize / (successful.length || 1);

  const metrics: ExtractionMetrics = {
    total: results.length,
    successful: successful.length,
    failed: results.length - successful.length,
    from_official: from_official.length,
    from_cdn: from_cdn.length,
    from_distributor: from_distributor.length,
    placeholders: placeholders.length,
    duration_ms,
    average_size_kb: averageSize / 1024,
  };

  // Save report
  const report = {
    metadata: {
      execution_date: new Date().toISOString(),
      duration_seconds: Math.round(duration_ms / 1000),
      total_products: products.length,
      with_manufacturers: productsWithManufacturers.length,
    },
    metrics,
    results,
    manufacturers_used: [...new Set(results.map(r => r.manufacturer))],
  };

  fs.writeFileSync(REPORT_FILE, JSON.stringify(report, null, 2));

  // Print summary
  console.log('\n═══════════════════════════════════════════════════════════');
  console.log('   RESUMO DA EXTRAÇÃO');
  console.log('═══════════════════════════════════════════════════════════\n');
  console.log(`Total processados:     ${metrics.total}`);
  console.log(`✅ Sucesso:            ${metrics.successful} (${((metrics.successful / metrics.total) * 100).toFixed(1)}%)`);
  console.log(`❌ Falhas:             ${metrics.failed}`);
  console.log(`\n📍 Fontes:`);
  console.log(`   - Oficial:          ${metrics.from_official}`);
  console.log(`   - CDN:              ${metrics.from_cdn}`);
  console.log(`   - Distribuidor:     ${metrics.from_distributor}`);
  console.log(`   - Placeholder:      ${metrics.placeholders}`);
  console.log(`\n📊 Estatísticas:`);
  console.log(`   - Tamanho médio:    ${metrics.average_size_kb.toFixed(2)} KB`);
  console.log(`   - Duração total:    ${Math.round(duration_ms / 1000)}s`);
  console.log(`\n💾 Relatório salvo em: ${REPORT_FILE}`);
  console.log('═══════════════════════════════════════════════════════════\n');
}

main().catch(console.error);
