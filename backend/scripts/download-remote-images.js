#!/usr/bin/env node

/**
 * Script para download de imagens remotas
 * - Lê catálogo de URLs remotas
 * - Baixa imagens com retry e rate limiting
 * - Organiza por fabricante/categoria inferida
 * - Atualiza mapeamento local
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import https from "https";
import http from "http";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_PATH = path.join(__dirname, "..");
const CATALOG_PATH = path.join(ROOT_PATH, "REMOTE_IMAGES_CATALOG.json");
const TARGET_DIR = path.join(ROOT_PATH, "static/products");
const DOWNLOAD_REPORT_PATH = path.join(ROOT_PATH, "DOWNLOAD_REPORT.json");

// Configuração
const MAX_CONCURRENT = 5;
const RETRY_ATTEMPTS = 3;
const TIMEOUT_MS = 30000;
const RATE_LIMIT_MS = 100;

// Mapeamento de fabricantes conhecidos
const MANUFACTURER_PATTERNS = {
  LONGI: /longi/i,
  GROWATT: /growatt/i,
  SUNGROW: /sungrow/i,
  RISEN: /risen/i,
  BYD: /byd/i,
  JINKO: /jinko/i,
  TRINA: /trina/i,
  "CANADIAN-SOLAR": /canadian/i,
  FRONIUS: /fronius/i,
  DEYE: /deye/i,
  SOLIS: /solis/i,
  HUAWEI: /huawei/i,
  PYLONTECH: /pylontech/i,
  DYNESS: /dyness/i,
  ENPHASE: /enphase/i,
  FORTLEV: /fortlev|IIN\d+|IMO\d+/i,
  "GENERIC-COMPONENTS": /corrugado|imagem\.png$/i,
};

// Categorias por padrão de nome
const CATEGORY_PATTERNS = {
  INVERSORES: /inverter|inversor|mic|min|mid|sg\d+|tl-x/i,
  PAINEIS: /painel|panel|mlk|wp|módulo|modulo/i,
  BATERIAS: /bateria|battery|kwh/i,
  KITS: /kit/i,
  ESTRUTURAS: /estrutura|structure|trilho|corrugado/i,
  CABOS: /cabo|cable/i,
  ACESSORIOS: /acessorio|accessory|conector|connector/i,
};

function inferManufacturer(url, filename) {
  const testString = `${url} ${filename}`.toLowerCase();

  for (const [manufacturer, pattern] of Object.entries(MANUFACTURER_PATTERNS)) {
    if (pattern.test(testString)) {
      return manufacturer;
    }
  }

  return "UNKNOWN-MANUFACTURER";
}

function inferCategory(url, filename) {
  const testString = `${url} ${filename}`.toLowerCase();

  for (const [category, pattern] of Object.entries(CATEGORY_PATTERNS)) {
    if (pattern.test(testString)) {
      return category;
    }
  }

  return "OUTROS";
}

function getFilenameFromUrl(url) {
  const urlPath = new URL(url).pathname;
  const parts = urlPath.split("/");
  return parts[parts.length - 1] || "image.png";
}

function downloadImage(url, targetPath) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith("https") ? https : http;

    const timeout = setTimeout(() => {
      reject(new Error("Timeout"));
    }, TIMEOUT_MS);

    protocol
      .get(url, (response) => {
        clearTimeout(timeout);

        if (response.statusCode === 301 || response.statusCode === 302) {
          const redirectUrl = response.headers.location;
          if (redirectUrl) {
            resolve(downloadImage(redirectUrl, targetPath));
            return;
          }
        }

        if (response.statusCode !== 200) {
          reject(new Error(`HTTP ${response.statusCode}`));
          return;
        }

        const writeStream = fs.createWriteStream(targetPath);
        response.pipe(writeStream);

        writeStream.on("finish", () => {
          writeStream.close();
          resolve({ success: true, path: targetPath });
        });

        writeStream.on("error", (error) => {
          fs.unlink(targetPath, () => {});
          reject(error);
        });
      })
      .on("error", (error) => {
        clearTimeout(timeout);
        reject(error);
      });
  });
}

async function downloadWithRetry(url, targetPath, attempts = RETRY_ATTEMPTS) {
  for (let i = 0; i < attempts; i++) {
    try {
      return await downloadImage(url, targetPath);
    } catch (error) {
      if (i === attempts - 1) {
        throw error;
      }
      await new Promise((resolve) => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}

async function downloadRemoteImages() {
  console.log("\n⬇️  DOWNLOAD DE IMAGENS REMOTAS\n");
  console.log("═".repeat(70));

  try {
    // 1. Carregar catálogo
    console.log("\n📖 ETAPA 1: Carregando Catálogo\n");

    if (!fs.existsSync(CATALOG_PATH)) {
      console.error("❌ Catálogo não encontrado: REMOTE_IMAGES_CATALOG.json");
      console.log("   Execute: node scripts/catalog-remote-images.js\n");
      process.exit(1);
    }

    const catalog = JSON.parse(fs.readFileSync(CATALOG_PATH, "utf8"));
    const urls = catalog.unique_urls.filter((url) =>
      url.startsWith("https://prod-platform-api.s3.amazonaws.com")
    );

    console.log(`✓ ${urls.length} URLs carregadas\n`);

    // 2. Preparar estrutura
    console.log("📁 ETAPA 2: Preparando Estrutura\n");

    if (!fs.existsSync(TARGET_DIR)) {
      fs.mkdirSync(TARGET_DIR, { recursive: true });
    }

    const downloadPlan = [];
    const existingFiles = new Set();

    for (const url of urls) {
      const filename = getFilenameFromUrl(url);
      const manufacturer = inferManufacturer(url, filename);
      const category = inferCategory(url, filename);

      const manufacturerDir = path.join(TARGET_DIR, manufacturer);
      const targetPath = path.join(manufacturerDir, filename);

      if (fs.existsSync(targetPath)) {
        existingFiles.add(url);
        continue;
      }

      if (!fs.existsSync(manufacturerDir)) {
        fs.mkdirSync(manufacturerDir, { recursive: true });
      }

      downloadPlan.push({
        url,
        targetPath,
        filename,
        manufacturer,
        category,
      });
    }

    console.log(`✓ ${downloadPlan.length} imagens para download`);
    console.log(`✓ ${existingFiles.size} imagens já existem\n`);

    // 3. Download em batches
    console.log("⬇️  ETAPA 3: Download de Imagens\n");

    const results = {
      success: [],
      failed: [],
      skipped: Array.from(existingFiles),
    };

    let processed = 0;

    for (let i = 0; i < downloadPlan.length; i += MAX_CONCURRENT) {
      const batch = downloadPlan.slice(i, i + MAX_CONCURRENT);

      const promises = batch.map(async (item) => {
        try {
          await downloadWithRetry(item.url, item.targetPath);
          results.success.push({
            url: item.url,
            path: item.targetPath,
            manufacturer: item.manufacturer,
            category: item.category,
          });
          return { success: true };
        } catch (error) {
          results.failed.push({
            url: item.url,
            error: error.message,
            manufacturer: item.manufacturer,
          });
          return { success: false };
        }
      });

      await Promise.all(promises);

      processed += batch.length;

      if (processed % 50 === 0 || processed === downloadPlan.length) {
        console.log(`   ✓ ${processed}/${downloadPlan.length} processadas`);
      }

      await new Promise((resolve) => setTimeout(resolve, RATE_LIMIT_MS));
    }

    console.log(
      `\n✓ Downloads: ${results.success.length} sucesso, ${results.failed.length} falhas\n`
    );

    // 4. Gerar relatório
    console.log("💾 ETAPA 4: Gerando Relatório\n");

    const report = {
      timestamp: new Date().toISOString(),
      statistics: {
        total_urls: urls.length,
        already_downloaded: existingFiles.size,
        attempted: downloadPlan.length,
        success: results.success.length,
        failed: results.failed.length,
      },
      downloads_by_manufacturer: {},
      downloads_by_category: {},
      success: results.success,
      failed: results.failed,
      skipped: results.skipped,
    };

    // Agrupar por fabricante
    for (const item of results.success) {
      if (!report.downloads_by_manufacturer[item.manufacturer]) {
        report.downloads_by_manufacturer[item.manufacturer] = 0;
      }
      report.downloads_by_manufacturer[item.manufacturer]++;

      if (!report.downloads_by_category[item.category]) {
        report.downloads_by_category[item.category] = 0;
      }
      report.downloads_by_category[item.category]++;
    }

    fs.writeFileSync(DOWNLOAD_REPORT_PATH, JSON.stringify(report, null, 2));

    console.log("✓ Relatório salvo: DOWNLOAD_REPORT.json\n");

    // 5. Resultado final
    console.log("═".repeat(70));
    console.log("\n✅ DOWNLOAD CONCLUÍDO!\n");
    console.log(`📊 Estatísticas:`);
    console.log(`   • Total: ${urls.length} URLs`);
    console.log(`   • Já existiam: ${existingFiles.size}`);
    console.log(`   • Baixadas: ${results.success.length}`);
    console.log(`   • Falhas: ${results.failed.length}\n`);

    if (results.failed.length > 0) {
      console.log(`⚠️  ${results.failed.length} imagens falharam:`);
      results.failed.slice(0, 5).forEach((item) => {
        console.log(`   • ${item.url.substring(0, 80)}...`);
        console.log(`     Erro: ${item.error}`);
      });
      if (results.failed.length > 5) {
        console.log(`   ... e mais ${results.failed.length - 5} falhas`);
      }
      console.log("");
    }

    console.log(`📁 Imagens salvas em: ${TARGET_DIR}\n`);
    console.log(`🔍 Próximos passos:`);
    console.log(`   1. Atualizar product_image_map.json`);
    console.log(`   2. Upload para S3`);
    console.log(`   3. Upload SKUs para DynamoDB\n`);

    process.exit(results.failed.length > 0 ? 1 : 0);
  } catch (error) {
    console.error("\n❌ ERRO NO DOWNLOAD:\n");
    console.error(error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

downloadRemoteImages().catch(console.error);
