#!/usr/bin/env node

/**
 * Script para catalogar todas as URLs de imagens remotas
 * - Extrai URLs de NORMALIZATION_REPORT.json
 * - Extrai URLs de fortlev-catalog-full.json
 * - Extrai URLs de outros inventários JSON
 * - Gera catálogo estruturado para download
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_PATH = path.join(__dirname, "..");

async function catalogRemoteImages() {
  console.log("\n📊 CATALOGAÇÃO DE IMAGENS REMOTAS\n");
  console.log("═".repeat(70));

  const remoteUrls = new Set();
  const urlsBySource = {};

  try {
    // 1. NORMALIZATION_REPORT.json
    console.log("\n📄 ETAPA 1: Analisando NORMALIZATION_REPORT.json\n");

    const normalizationPath = path.join(ROOT_PATH, "NORMALIZATION_REPORT.json");
    if (fs.existsSync(normalizationPath)) {
      const normData = JSON.parse(fs.readFileSync(normalizationPath, "utf8"));

      if (normData.external_image_urls && Array.isArray(normData.external_image_urls)) {
        normData.external_image_urls.forEach((url) => {
          remoteUrls.add(url);
          if (!urlsBySource.NORMALIZATION_REPORT) {
            urlsBySource.NORMALIZATION_REPORT = [];
          }
          urlsBySource.NORMALIZATION_REPORT.push(url);
        });
        console.log(`✓ ${normData.external_image_urls.length} URLs encontradas\n`);
      }
    } else {
      console.log("⚠️  Arquivo não encontrado\n");
    }

    // 2. fortlev-catalog-full.json
    console.log("📄 ETAPA 2: Analisando fortlev-catalog-full.json\n");

    const fortlevPath = path.join(ROOT_PATH, "mcp-servers/fortlev-catalog-full.json");
    if (fs.existsSync(fortlevPath)) {
      const fortlevData = JSON.parse(fs.readFileSync(fortlevPath, "utf8"));

      const fortlevUrls = [];
      const extractUrls = (obj) => {
        if (typeof obj === "string" && obj.startsWith("https://prod-platform-api.s3.amazonaws.com")) {
          remoteUrls.add(obj);
          fortlevUrls.push(obj);
        } else if (Array.isArray(obj)) {
          obj.forEach(extractUrls);
        } else if (obj && typeof obj === "object") {
          Object.values(obj).forEach(extractUrls);
        }
      };

      extractUrls(fortlevData);
      urlsBySource.FORTLEV_CATALOG = fortlevUrls;
      console.log(`✓ ${fortlevUrls.length} URLs encontradas\n`);
    } else {
      console.log("⚠️  Arquivo não encontrado\n");
    }

    // 3. Outros inventários
    console.log("📄 ETAPA 3: Analisando outros inventários\n");

    const inventoryPath = path.join(ROOT_PATH, "data/products-inventory");
    if (fs.existsSync(inventoryPath)) {
      const scanDir = (dirPath, depth = 0) => {
        if (depth > 3) return; // Limitar profundidade

        const files = fs.readdirSync(dirPath);
        for (const file of files) {
          const fullPath = path.join(dirPath, file);
          const stat = fs.statSync(fullPath);

          if (stat.isDirectory()) {
            scanDir(fullPath, depth + 1);
          } else if (file.endsWith(".json")) {
            try {
              const content = fs.readFileSync(fullPath, "utf8");
              const data = JSON.parse(content);

              const fileUrls = [];
              const extractUrls = (obj) => {
                if (typeof obj === "string" && (
                  obj.startsWith("https://prod-platform-api.s3.amazonaws.com") ||
                  obj.startsWith("http")
                )) {
                  remoteUrls.add(obj);
                  fileUrls.push(obj);
                } else if (Array.isArray(obj)) {
                  obj.forEach(extractUrls);
                } else if (obj && typeof obj === "object") {
                  Object.values(obj).forEach(extractUrls);
                }
              };

              extractUrls(data);

              if (fileUrls.length > 0) {
                const relativePath = path.relative(ROOT_PATH, fullPath);
                urlsBySource[relativePath] = fileUrls;
              }
            } catch (error) {
              // Ignorar arquivos JSON inválidos
            }
          }
        }
      };

      scanDir(inventoryPath);
      console.log(`✓ Inventários escaneados\n`);
    }

    // 4. Gerar catálogo estruturado
    console.log("💾 ETAPA 4: Gerando Catálogo\n");

    const catalog = {
      timestamp: new Date().toISOString(),
      total_unique_urls: remoteUrls.size,
      urls_by_source: urlsBySource,
      unique_urls: Array.from(remoteUrls).sort(),
      download_plan: {
        description: "Estrutura para download organizado",
        target_directory: "static/products",
        naming_convention: "Extrair fabricante/categoria da URL ou metadados",
        organization: {
          example: "static/products/LONGI/LONGI-585W.png",
          structure: "manufacturer/product-image.ext",
        },
      },
      statistics: {
        total_sources: Object.keys(urlsBySource).length,
        urls_per_source: Object.entries(urlsBySource).map(([source, urls]) => ({
          source,
          count: urls.length,
        })),
      },
    };

    const catalogPath = path.join(ROOT_PATH, "REMOTE_IMAGES_CATALOG.json");
    fs.writeFileSync(catalogPath, JSON.stringify(catalog, null, 2));

    console.log("✓ Catálogo salvo: REMOTE_IMAGES_CATALOG.json\n");

    // 5. Resultado final
    console.log("═".repeat(70));
    console.log("\n✅ CATALOGAÇÃO CONCLUÍDA!\n");
    console.log(`📊 Estatísticas:`);
    console.log(`   • URLs únicas: ${remoteUrls.size}`);
    console.log(`   • Fontes: ${Object.keys(urlsBySource).length}`);
    console.log(`   • Catálogo: REMOTE_IMAGES_CATALOG.json\n`);

    console.log(`🔍 Próximos passos:`);
    console.log(`   1. Baixar imagens remotas`);
    console.log(`   2. Organizar por fabricante/categoria`);
    console.log(`   3. Atualizar mapeamentos\n`);

    return catalog;
  } catch (error) {
    console.error("\n❌ ERRO NA CATALOGAÇÃO:\n");
    console.error(error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

catalogRemoteImages().catch(console.error);
