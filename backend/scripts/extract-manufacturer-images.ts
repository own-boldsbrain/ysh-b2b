#!/usr/bin/env node

/**
 * Extrator de Imagens de Fabricantes
 * - Prioriza sites oficiais dos fabricantes
 * - Usa distribuidores apenas como fallback
 * - Padroniza nomenclatura: FABRICANTE-MODELO-POTENCIA.ext
 * - Sistema hierárquico com cache
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import https from "https";
import http from "http";
import { chromium } from "playwright";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_PATH = path.join(__dirname, "..");
const MANUFACTURERS_CATALOG_PATH = path.join(
  ROOT_PATH,
  "config/manufacturers-catalog.json"
);
const TARGET_DIR = path.join(ROOT_PATH, "static/products-official");
const CACHE_PATH = path.join(ROOT_PATH, "cache/manufacturer-images.json");

const MAX_CONCURRENT = 3;
const TIMEOUT_MS = 30000;
const USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36";

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

interface ProductInfo {
  sku: string;
  manufacturer: string;
  model?: string;
  power?: string;
  category?: string;
  distributor_url?: string;
}

interface ImageResult {
  product: ProductInfo;
  source: "official" | "cdn" | "distributor" | "placeholder";
  url: string;
  local_path: string;
  success: boolean;
  error?: string;
}

function loadManufacturersCatalog(): Record<string, ManufacturerInfo> {
  if (!fs.existsSync(MANUFACTURERS_CATALOG_PATH)) {
    throw new Error("Catálogo de fabricantes não encontrado");
  }

  const data = JSON.parse(fs.readFileSync(MANUFACTURERS_CATALOG_PATH, "utf8"));
  return data.manufacturers;
}

function loadCache(): Record<string, ImageResult> {
  if (!fs.existsSync(CACHE_PATH)) {
    return {};
  }

  try {
    return JSON.parse(fs.readFileSync(CACHE_PATH, "utf8"));
  } catch {
    return {};
  }
}

function saveCache(cache: Record<string, ImageResult>) {
  const cacheDir = path.dirname(CACHE_PATH);
  if (!fs.existsSync(cacheDir)) {
    fs.mkdirSync(cacheDir, { recursive: true });
  }

  fs.writeFileSync(CACHE_PATH, JSON.stringify(cache, null, 2));
}

function normalizeFilename(product: ProductInfo): string {
  const manufacturer = product.manufacturer.toUpperCase().replace(/[^A-Z0-9]/g, "");
  const model = (product.model || product.sku)
    .replace(/[^a-zA-Z0-9.-]/g, "")
    .toUpperCase();
  const power = product.power ? `-${product.power}` : "";

  return `${manufacturer}-${model}${power}`;
}

function extractModelFromSku(sku: string, patterns: string[]): string | null {
  for (const pattern of patterns) {
    const regex = new RegExp(pattern, "i");
    const match = sku.match(regex);
    if (match) {
      return match[0];
    }
  }

  return null;
}

async function downloadImage(url: string, targetPath: string): Promise<boolean> {
  return new Promise((resolve) => {
    const protocol = url.startsWith("https") ? https : http;

    const timeout = setTimeout(() => {
      resolve(false);
    }, TIMEOUT_MS);

    protocol
      .get(
        url,
        {
          headers: {
            "User-Agent": USER_AGENT,
          },
        },
        (response) => {
          clearTimeout(timeout);

          if (response.statusCode === 301 || response.statusCode === 302) {
            const redirectUrl = response.headers.location;
            if (redirectUrl) {
              resolve(downloadImage(redirectUrl, targetPath));
              return;
            }
          }

          if (response.statusCode !== 200) {
            resolve(false);
            return;
          }

          const dir = path.dirname(targetPath);
          if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
          }

          const writeStream = fs.createWriteStream(targetPath);
          response.pipe(writeStream);

          writeStream.on("finish", () => {
            writeStream.close();
            resolve(true);
          });

          writeStream.on("error", () => {
            fs.unlink(targetPath, () => {});
            resolve(false);
          });
        }
      )
      .on("error", () => {
        clearTimeout(timeout);
        resolve(false);
      });
  });
}

async function searchOfficialImage(
  product: ProductInfo,
  manufacturerInfo: ManufacturerInfo
): Promise<string | null> {
  const model = extractModelFromSku(product.sku, manufacturerInfo.sku_patterns);

  if (!model) {
    return null;
  }

  // Tentar padrões diretos de URL
  for (const pattern of manufacturerInfo.image_patterns) {
    const url = pattern.replace("{model}", encodeURIComponent(model));

    const testPath = path.join(TARGET_DIR, "temp", `test-${Date.now()}.jpg`);

    const success = await downloadImage(url, testPath);

    if (success && fs.existsSync(testPath)) {
      const stats = fs.statSync(testPath);
      fs.unlinkSync(testPath);

      if (stats.size > 1000) {
        // Imagem válida
        return url;
      }
    }
  }

  return null;
}

async function searchWithBrowser(
  product: ProductInfo,
  manufacturerInfo: ManufacturerInfo
): Promise<string | null> {
  let browser = null;

  try {
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    await page.setUserAgent(USER_AGENT);

    // Buscar na página de produtos
    const productPage = manufacturerInfo.product_pages[product.category || "panels"];

    if (!productPage) {
      return null;
    }

    await page.goto(productPage, { waitUntil: "domcontentloaded", timeout: 30000 });

    // Buscar imagem que contenha o modelo
    const model = extractModelFromSku(product.sku, manufacturerInfo.sku_patterns);

    if (!model) {
      return null;
    }

    const images = await page.$$eval("img", (imgs, searchModel) => {
      return imgs
        .filter((img) => {
          const src = img.src || "";
          const alt = img.alt || "";
          return (
            src.toLowerCase().includes(searchModel.toLowerCase()) ||
            alt.toLowerCase().includes(searchModel.toLowerCase())
          );
        })
        .map((img) => img.src);
    }, model);

    if (images.length > 0) {
      return images[0];
    }

    return null;
  } catch (error) {
    console.warn(`Erro na busca com browser: ${error.message}`);
    return null;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

async function extractManufacturerImages(products: ProductInfo[]) {
  console.log("\n🏭 EXTRAÇÃO DE IMAGENS DE FABRICANTES\n");
  console.log("═".repeat(70));

  try {
    // Carregar catálogo
    console.log("\n📖 ETAPA 1: Carregando Catálogo\n");

    const manufacturers = loadManufacturersCatalog();
    const cache = loadCache();

    console.log(`✓ ${Object.keys(manufacturers).length} fabricantes catalogados\n`);

    // Criar estrutura
    console.log("📁 ETAPA 2: Preparando Estrutura\n");

    if (!fs.existsSync(TARGET_DIR)) {
      fs.mkdirSync(TARGET_DIR, { recursive: true });
    }

    console.log(`✓ Diretório: ${TARGET_DIR}\n`);

    // Processar produtos
    console.log("🔍 ETAPA 3: Extraindo Imagens\n");

    const results: ImageResult[] = [];
    let processed = 0;

    for (const product of products) {
      const cacheKey = `${product.manufacturer}-${product.sku}`;

      // Verificar cache
      if (cache[cacheKey] && fs.existsSync(cache[cacheKey].local_path)) {
        results.push(cache[cacheKey]);
        processed++;
        continue;
      }

      const manufacturerInfo = manufacturers[product.manufacturer];

      if (!manufacturerInfo || !manufacturerInfo.active) {
        results.push({
          product,
          source: "placeholder",
          url: "",
          local_path: "",
          success: false,
          error: "Fabricante não catalogado",
        });
        processed++;
        continue;
      }

      const filename = normalizeFilename(product);
      const targetPath = path.join(
        TARGET_DIR,
        product.manufacturer,
        `${filename}.png`
      );

      let imageUrl: string | null = null;
      let source: ImageResult["source"] = "placeholder";

      // 1. Tentar site oficial
      if (manufacturerInfo.priority === 1) {
        imageUrl = await searchOfficialImage(product, manufacturerInfo);
        if (imageUrl) {
          source = "official";
        }
      }

      // 2. Tentar busca com browser (mais lento)
      if (!imageUrl && manufacturerInfo.priority === 1) {
        imageUrl = await searchWithBrowser(product, manufacturerInfo);
        if (imageUrl) {
          source = "cdn";
        }
      }

      // 3. Fallback para distribuidor
      if (!imageUrl && product.distributor_url) {
        imageUrl = product.distributor_url;
        source = "distributor";
      }

      // 4. Download
      let success = false;

      if (imageUrl) {
        success = await downloadImage(imageUrl, targetPath);
      }

      const result: ImageResult = {
        product,
        source: success ? source : "placeholder",
        url: imageUrl || "",
        local_path: success ? targetPath : "",
        success,
        error: success ? undefined : "Download falhou",
      };

      results.push(result);
      cache[cacheKey] = result;

      processed++;

      if (processed % 10 === 0) {
        console.log(`   ✓ ${processed}/${products.length} produtos processados`);
        saveCache(cache); // Salvar cache periodicamente
      }
    }

    console.log(`\n✓ ${processed}/${products.length} produtos processados\n`);

    // Estatísticas
    console.log("📊 ETAPA 4: Estatísticas\n");

    const bySource = {
      official: results.filter((r) => r.source === "official").length,
      cdn: results.filter((r) => r.source === "cdn").length,
      distributor: results.filter((r) => r.source === "distributor").length,
      placeholder: results.filter((r) => r.source === "placeholder").length,
    };

    console.log(`Fontes de Imagens:`);
    console.log(`   • Oficial: ${bySource.official}`);
    console.log(`   • CDN: ${bySource.cdn}`);
    console.log(`   • Distribuidor: ${bySource.distributor}`);
    console.log(`   • Placeholder: ${bySource.placeholder}\n`);

    const successRate = (
      ((bySource.official + bySource.cdn + bySource.distributor) / results.length) *
      100
    ).toFixed(1);

    console.log(`Taxa de Sucesso: ${successRate}%\n`);

    // Salvar cache final
    saveCache(cache);

    // Salvar relatório
    const report = {
      timestamp: new Date().toISOString(),
      total_products: products.length,
      statistics: bySource,
      success_rate: parseFloat(successRate),
      results: results.slice(0, 100), // Primeiros 100 para não ficar muito grande
    };

    const reportPath = path.join(ROOT_PATH, "MANUFACTURER_EXTRACTION_REPORT.json");
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));

    console.log("═".repeat(70));
    console.log("\n✅ EXTRAÇÃO CONCLUÍDA!\n");
    console.log(`📄 Relatório: MANUFACTURER_EXTRACTION_REPORT.json\n`);

    return results;
  } catch (error) {
    console.error("\n❌ ERRO NA EXTRAÇÃO:\n");
    console.error(error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Exemplo de uso
const sampleProducts: ProductInfo[] = [
  {
    sku: "LR5-72HPH-585M",
    manufacturer: "LONGI",
    model: "LR5-72HPH",
    power: "585W",
    category: "panels",
  },
  {
    sku: "MIN-3000TL-X",
    manufacturer: "GROWATT",
    model: "MIN-3000TL-X",
    category: "inverters",
  },
  {
    sku: "SG3.0RS",
    manufacturer: "SUNGROW",
    model: "SG3.0RS",
    category: "inverters",
  },
];

if (import.meta.url === `file://${process.argv[1]}`) {
  extractManufacturerImages(sampleProducts).catch(console.error);
}

export { extractManufacturerImages, ProductInfo, ImageResult };
