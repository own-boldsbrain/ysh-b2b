#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(process.cwd());
const INPUT_SKUS = path.join(ROOT, 'enriched-skus-for-dynamodb.json');
const DISTRIB_DIR = path.join(ROOT, 'data', 'products-inventory', 'distributors');
const OUT_SYNCED = path.join(ROOT, 'enriched-skus-for-dynamodb-synced.json');
const OUT_REPORT = path.join(ROOT, 'ENRICHED_SKUS_DYNAMIC_PRICING_REPORT-sync.json');

function normalize(s) {
  if (!s) return '';
  return String(s).toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, '').trim();
}

function tokenize(s) {
  return String(s || '').toLowerCase().split(/[^a-z0-9]+/).filter(Boolean);
}

function loadDistributorProducts(dir) {
  const files = fs.readdirSync(dir);
  const products = [];
  for (const f of files) {
    const full = path.join(dir, f);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      products.push(...loadDistributorProducts(full));
      continue;
    }
    if (!f.endsWith('.json')) continue;
    try {
      const data = JSON.parse(fs.readFileSync(full, 'utf8'));
      if (Array.isArray(data)) {
        for (const p of data) {
          p.__source_file = f;
          products.push(p);
        }
      } else if (data && typeof data === 'object') {
        // if object with keys categories
        for (const key of Object.keys(data)) {
          const entry = data[key];
          if (Array.isArray(entry)) {
            for (const p of entry) { p.__source_file = f; products.push(p); }
          }
        }
      }
    } catch (err) {
      // ignore parse errors
    }
  }
  return products;
}

function matchProductToSKU(sku, products) {
  const skuName = normalize(sku.name || sku.sku || sku.title || '');
  const skuTokens = tokenize(sku.name || sku.sku || sku.title || '');
  const skuModel = normalize(sku.model || '');
  let best = null;
  for (const p of products) {
    const pName = normalize(p.name || p.title || p.product_name || p.description || '');
    const pTokens = tokenize(p.name || p.title || p.product_name || '');
    let score = 0;
    // exact sku / part number equality
    if (sku.sku && p.sku && normalize(p.sku) === normalize(sku.sku)) score += 100;
    if (sku.sku && p.part_number && normalize(p.part_number) === normalize(sku.sku)) score += 100;
    if (p.model && sku.model && normalize(p.model) === normalize(sku.model)) score += 40;
    if (pName && skuName && (pName === skuName)) score += 50;
    if (pName && skuName && (pName.includes(skuName) || skuName.includes(pName))) score += 30;
    // model containment
    if (p.model && skuModel && skuModel.includes(normalize(p.model))) score += 25;
    // token overlap
    const common = pTokens.filter(t => skuTokens.includes(t)).length;
    score += common * 2;
    // token overlap ratio bonus
    const maxTokens = Math.max(pTokens.length || 1, skuTokens.length || 1);
    const ratio = common / maxTokens;
    if (ratio > 0.5) score += 30;
    // fuzzy name similarity (Levenshtein)
    const nameA = skuName;
    const nameB = pName;
    const lev = levenshteinDistance(nameA, nameB);
    const maxLen = Math.max(nameA.length, nameB.length, 1);
    const levRatio = lev / maxLen;
    if (levRatio < 0.25) score += 50;
    else if (levRatio < 0.45) score += 20;

    if (!best || score > best.score) best = { score, product: p };
  }
  return best;
}

function levenshteinDistance(a, b) {
  if (a === b) return 0;
  const alen = a.length, blen = b.length;
  if (alen === 0) return blen;
  if (blen === 0) return alen;
  const v0 = new Array(blen + 1);
  const v1 = new Array(blen + 1);
  for (let j = 0; j <= blen; j++) v0[j] = j;
  for (let i = 0; i < alen; i++) {
    v1[0] = i + 1;
    for (let j = 0; j < blen; j++) {
      const cost = a[i] === b[j] ? 0 : 1;
      v1[j + 1] = Math.min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost);
    }
    for (let j = 0; j <= blen; j++) v0[j] = v1[j];
  }
  return v0[blen];
}

function mergeSKU(sku, product, matchScore) {
  const out = { ...sku };
  out.sync = out.sync || {};
  out.sync.matched = !!product;
  out.sync.matchScore = matchScore || 0;
  if (product) {
    out.sync.matchedSource = product.__source_file || null;
    // images: gather from common possible fields
    const imgs = new Set(out.images || []);
    if (out.image_url) imgs.add(out.image_url);
    const imgFields = ['image_url','imageUrl','image','images','pictures','picture','photos','gallery','image_urls','images_url','imageUrls','photo','thumbnail','thumbnails'];
    for (const k of imgFields) {
      const v = product[k];
      if (!v) continue;
      if (Array.isArray(v)) for (const it of v) if (it) imgs.add(it);
      else imgs.add(v);
    }
    // also look into nested media/gallery arrays
    if (product.media && Array.isArray(product.media)) {
      for (const m of product.media) {
        if (m && m.url) imgs.add(m.url);
      }
    }
    out.images = Array.from(imgs).filter(Boolean);
    if (!out.manufacturer && product.manufacturer) out.manufacturer = product.manufacturer;
    if (!out.model && (product.model || product.product_model)) out.model = product.model || product.product_model;
    if (!out.technology && product.technology) out.technology = product.technology;
    // pricing hints
    if ((!out.price_brl || out.price_brl === 0) && (product.price || product.price_brl)) {
      out.price_brl = product.price_brl || product.price || 0;
      // leave pricing block, but set source
      out.pricing = out.pricing || {};
      out.pricing.source = out.pricing.source || 'distributor-sync';
      out.pricing.distributor_price = product.price_brl || product.price || null;
    }
    // supplier
    out.supplier = out.supplier || product.supplier || product.__source_file || 'distributor';
  }
  // sanity: ensure arrays
  if (!out.images) out.images = [];
  return out;
}

function validateSKUFields(sku) {
  const missing = [];
  if (!sku.sku && !sku.name) missing.push('sku/name');
  if (!sku.category) missing.push('category');
  if (typeof sku.price_brl === 'undefined' || sku.price_brl === null) missing.push('price_brl');
  if (!sku.pricing || typeof sku.pricing.final_price === 'undefined') missing.push('pricing.final_price');
  if (!sku.kpis || typeof sku.kpis.gross_margin_percent === 'undefined') missing.push('kpis.gross_margin_percent');
  if (!sku.images || sku.images.length === 0) missing.push('images');
  if (!sku.manufacturer) missing.push('manufacturer');
  return missing;
}

async function main() {
  if (!fs.existsSync(INPUT_SKUS)) {
    console.error('Arquivo de SKUs enriquecidos não encontrado:', INPUT_SKUS);
    process.exit(1);
  }
  console.log('Carregando SKUs...');
  const skus = JSON.parse(fs.readFileSync(INPUT_SKUS, 'utf8'));
  console.log('Carregando dados dos distribuidores...');
  const products = loadDistributorProducts(DISTRIB_DIR);
  console.log(`Produtos carregados de distribuidores: ${products.length}`);

  const synced = [];
  const report = { timestamp: new Date().toISOString(), totalInput: skus.length, matched: 0, unmatched: 0, missingSummary: {}, samples: [] };

  for (let i = 0; i < skus.length; i++) {
    const sku = skus[i];
    const best = matchProductToSKU(sku, products);
    let merged = sku;
    if (best && best.score >= 15) {
      merged = mergeSKU(sku, best.product, best.score);
      report.matched++;
    } else {
      merged = mergeSKU(sku, null, 0);
      report.unmatched++;
    }
    const missing = validateSKUFields(merged);
    if (missing.length > 0) {
      for (const m of missing) report.missingSummary[m] = (report.missingSummary[m] || 0) + 1;
    }
    if (i < 5) report.samples.push({ sku: merged.sku || merged.name, missing, matchScore: merged.sync.matchScore, source: merged.sync.matchedSource || null });
    synced.push(merged);
  }

  console.log('Gravando arquivos de saída...');
  fs.writeFileSync(OUT_SYNCED, JSON.stringify(synced, null, 2), 'utf8');
  fs.writeFileSync(OUT_REPORT, JSON.stringify(report, null, 2), 'utf8');

  console.log('Resumo:');
  console.log(` Total SKUs processados: ${report.totalInput}`);
  console.log(` Matched: ${report.matched}`);
  console.log(` Unmatched: ${report.unmatched}`);
  console.log(' Missing fields summary:', report.missingSummary);
  console.log(' Arquivos gerados:', OUT_SYNCED, OUT_REPORT);
}

main().catch(err => { console.error(err); process.exit(1); });
