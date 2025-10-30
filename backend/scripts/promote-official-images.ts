#!/usr/bin/env node

/**
 * Promote official manufacturer assets into the catalog image tree.
 * - Copies curated images from static/products-official
 * - Places them under static/products/<category>/<sku>.<ext>
 * - Category is inferred from the latest consolidated products snapshot
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_PATH = path.join(__dirname, "..");
const OFFICIAL_DIR = path.join(ROOT_PATH, "static/products-official");
const TARGET_DIR = path.join(ROOT_PATH, "static/products");
const REPORT_PATH = path.join(ROOT_PATH, "output/manufacturer-images-report-360.json");
const CONSOLIDATED_DIR = path.join(ROOT_PATH, "output/consolidated");

interface ManufacturerImageEntry {
  sku: string;
  manufacturer: string;
  source: "official" | "cdn" | "distributor" | "placeholder";
  local_path: string;
  standardized_filename?: string;
  success: boolean;
}

interface ManufacturerReport {
  results?: ManufacturerImageEntry[];
}

interface ConsolidatedProduct {
  sku?: string;
  id?: string;
  category?: string;
  categoria?: string;
  type?: string;
  tipo?: string;
}

type PromotionResult = {
  sku: string;
  manufacturer: string;
  category: string;
  sourcePath: string;
  targetPath: string;
  replacedExisting: boolean;
};

const CATEGORY_RULES: Array<{ folder: string; keywords: string[] }> = [
  { folder: "inversores", keywords: ["inversor", "inverter", "microinversor"] },
  { folder: "paineis", keywords: ["painel", "panel", "modulo"] },
  { folder: "baterias", keywords: ["bateria", "battery"] },
  { folder: "estruturas", keywords: ["estrutura", "structure", "rack"] },
  { folder: "cabos", keywords: ["cabo", "cable"] },
  { folder: "kits", keywords: ["kit"] },
  { folder: "acessorios", keywords: ["acessorio", "accessory"] },
  { folder: "carregadores", keywords: ["carregador", "charger", "wallbox"] },
  { folder: "outros", keywords: ["outro", "outros", "others"] },
];

function normalizeText(value?: string): string {
  if (!value) return "";
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}

function mapCategory(product?: ConsolidatedProduct): string {
  const candidates = [product?.category, product?.categoria, product?.type, product?.tipo];

  for (const raw of candidates) {
    const normalized = normalizeText(raw);

    if (!normalized) {
      continue;
    }

    for (const rule of CATEGORY_RULES) {
      if (rule.keywords.some((keyword) => normalized.includes(normalizeText(keyword)))) {
        return rule.folder;
      }
    }
  }

  return "outros";
}

function ensureDir(dirPath: string) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function findLatestConsolidatedFile(): string | null {
  if (!fs.existsSync(CONSOLIDATED_DIR)) {
    return null;
  }

  const files = fs
    .readdirSync(CONSOLIDATED_DIR)
    .filter((name) => name.startsWith("unified-products-") && name.endsWith(".json"))
    .sort();

  if (files.length === 0) {
    return null;
  }

  return path.join(CONSOLIDATED_DIR, files[files.length - 1]);
}

function loadConsolidatedIndex(): Map<string, ConsolidatedProduct> {
  const index = new Map<string, ConsolidatedProduct>();
  const latestFile = findLatestConsolidatedFile();

  if (!latestFile) {
    return index;
  }

  try {
    const raw = fs.readFileSync(latestFile, "utf8");
    const data = JSON.parse(raw) as unknown;

    if (Array.isArray(data)) {
      for (const item of data) {
        const product = item as ConsolidatedProduct;
        const key = product.sku || product.id;
        if (key) {
          index.set(String(key), product);
        }
      }
    }
  } catch (error) {
    console.warn(`⚠️  Failed to load consolidated products: ${(error as Error).message}`);
  }

  return index;
}

function loadManufacturerReport(): ManufacturerImageEntry[] {
  if (!fs.existsSync(REPORT_PATH)) {
    throw new Error("Manufacturer image report not found. Run the extractor first.");
  }

  const raw = fs.readFileSync(REPORT_PATH, "utf8");
  const data = JSON.parse(raw) as ManufacturerReport;

  if (!data.results || data.results.length === 0) {
    throw new Error("Manufacturer image report is empty.");
  }

  return data.results;
}

async function runUpdateImageMap(): Promise<void> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(__dirname, "update-image-map.js");
    const child = spawn(process.execPath, [scriptPath], { stdio: "inherit" });

    child.on("exit", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`update-image-map.js exited with code ${code}`));
      }
    });
  });
}

async function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes("--dry-run");
  const updateMap = args.includes("--update-map");
  const manufacturerFilterArg = args.find((arg) => arg.startsWith("--manufacturer="));
  const manufacturerFilter = manufacturerFilterArg
    ? manufacturerFilterArg.split("=")[1].toUpperCase()
    : null;

  const consolidatedIndex = loadConsolidatedIndex();
  if (consolidatedIndex.size === 0) {
    console.warn("Warning: no consolidated products found; category mapping will fall back to 'outros'.");
  }
  const entries = loadManufacturerReport();

  const promotions: PromotionResult[] = [];
  const skipped: Array<{ sku: string; reason: string }> = [];

  for (const entry of entries) {
    if (!entry.success) {
      skipped.push({ sku: entry.sku, reason: "extraction failed" });
      continue;
    }

    if (entry.source !== "official") {
      skipped.push({ sku: entry.sku, reason: `source ${entry.source}` });
      continue;
    }

    if (manufacturerFilter && entry.manufacturer.toUpperCase() !== manufacturerFilter) {
      continue;
    }

    const product = consolidatedIndex.get(String(entry.sku));
    const category = mapCategory(product);
    const manufacturerDir = path.join(OFFICIAL_DIR, entry.manufacturer);
    const filename = entry.standardized_filename || path.basename(entry.local_path);
    const sourcePath = path.join(manufacturerDir, filename);

    if (!fs.existsSync(sourcePath)) {
      skipped.push({ sku: entry.sku, reason: "source image missing" });
      continue;
    }

    const ext = path.extname(sourcePath) || ".png";
    const categoryDir = path.join(TARGET_DIR, category);
    const targetFilename = `${entry.sku}${ext.toLowerCase()}`;
    const targetPath = path.join(categoryDir, targetFilename);

    ensureDir(categoryDir);

    if (!dryRun) {
      let replacedExisting = false;

      if (fs.existsSync(targetPath)) {
        replacedExisting = true;
      }

      fs.copyFileSync(sourcePath, targetPath);

      promotions.push({
        sku: entry.sku,
        manufacturer: entry.manufacturer,
        category,
        sourcePath,
        targetPath,
        replacedExisting,
      });
    } else {
      promotions.push({
        sku: entry.sku,
        manufacturer: entry.manufacturer,
        category,
        sourcePath,
        targetPath,
        replacedExisting: fs.existsSync(targetPath),
      });
    }
  }

  promotions.sort((a, b) => a.sku.localeCompare(b.sku));
  skipped.sort((a, b) => a.sku.localeCompare(b.sku));

  if (promotions.length === 0) {
    console.log("No official images promoted.");
  } else {
    console.log("\nPromoted official images:");
    for (const promo of promotions) {
      const marker = promo.replacedExisting ? "(replaced)" : "(new)";
      console.log(` - ${promo.sku} → ${promo.category}/${path.basename(promo.targetPath)} ${marker}`);
    }
  }

  if (skipped.length > 0) {
    console.log("\nSkipped entries:");
    for (const item of skipped) {
      console.log(` - ${item.sku}: ${item.reason}`);
    }
  }

  if (updateMap && promotions.length > 0) {
    console.log("\nUpdating product image map...");
    await runUpdateImageMap();
  }

  console.log("\nDone.");
}

main().catch((error) => {
  console.error("\n❌ promote-official-images failed");
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
