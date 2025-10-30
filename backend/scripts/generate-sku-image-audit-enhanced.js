#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.join(__dirname, '..');

const enrichedPath = path.join(root, 'enriched-skus-for-dynamodb.json');
const imgsIndexPath = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/assets/products/imgs-index.json';
const productsDetailedPath = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/assets/products/products-detailed-catalog.json';
const productImageMapPath = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/assets/products/product_image_map.json';
const skuImagesSyncPath = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/assets/products/sku-images-sync.json';
const productsFullyPath = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/assets/products/products-fully-priced-catalog.json';

function load(p) {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf-8'));
  } catch (e) {
    return null;
  }
}

const enriched = load(enrichedPath) || [];
const imgsIndex = load(imgsIndexPath) || {};
const productsDetailed = load(productsDetailedPath) || {};
const productImageMap = load(productImageMapPath) || {};
const skuImagesSync = load(skuImagesSyncPath) || {};
const productsFully = load(productsFullyPath) || {};

function normalize(s) {
  if (!s) return '';
  return String(s).toLowerCase().trim();
}

// helper maps
const imgsByCdn = new Map();
if (imgsIndex && Array.isArray(imgsIndex.images)) {
  for (const it of imgsIndex.images) {
    if (it.cdn_url) imgsByCdn.set(normalize(it.cdn_url), it);
    if (it.filename) imgsByCdn.set(normalize(it.filename), it);
  }
}

const pimMap = productImageMap && productImageMap.images ? productImageMap.images : {};

const productsFullyMap = new Map();
if (productsFully && Array.isArray(productsFully.products)) {
  for (const p of productsFully.products) {
    if (p.sku) productsFullyMap.set(normalize(p.sku), p);
  }
}

const detailedMap = new Map();
if (productsDetailed && Array.isArray(productsDetailed.products)) {
  for (const p of productsDetailed.products) {
    if (p.sku) detailedMap.set(normalize(p.sku), p);
  }
}

const skuSyncMap = new Map();
if (skuImagesSync && Array.isArray(skuImagesSync.skus)) {
  for (const s of skuImagesSync.skus) {
    if (s.sku) skuSyncMap.set(normalize(s.sku), s);
  }
}

const rows = [];

for (const sku of enriched) {
  const key = sku.sku || sku.SKU || '';
  const primary = sku.image_url || (Array.isArray(sku.images) && sku.images[0]) || '';
  const all = Array.isArray(sku.images) ? sku.images.slice() : sku.image_url ? [sku.image_url] : [];

  let source = 'unknown';
  let score = 50;
  const nprimary = normalize(primary);

  if (primary && imgsByCdn.has(nprimary)) {
    source = 'imgs-index';
    score = 100;
  } else if (
    primary &&
    Object.keys(pimMap).some((k) => {
      const arr = pimMap[k] || [];
      return arr.some((x) => normalize(x) === nprimary);
    })
  ) {
    source = 'product_image_map';
    score = 95;
  } else if (productsFullyMap.has(normalize(key))) {
    source = 'products-fully-priced';
    score = 85;
  } else if (detailedMap.has(normalize(key))) {
    source = 'products-detailed';
    score = 90;
  } else if (skuSyncMap.has(normalize(key))) {
    source = 'sku-images-sync';
    score = 92;
  } else if (primary && nprimary.includes('cdn.yellosolarhub.com')) {
    source = 'cdn-guess';
    score = 70;
  } else if (all.length > 0) {
    const found = all.find((a) => imgsByCdn.has(normalize(a)));
    if (found) {
      source = 'imgs-index';
      score = 95;
    }
  }

  // Collect candidate URLs from multiple sources (top-N strategy)
  const candidates = new Set();
  const nkey = normalize(key);

  // from imgs-index
  if (imgsIndex && Array.isArray(imgsIndex.images)) {
    for (const it of imgsIndex.images) {
      if (it.sku && normalize(it.sku) === nkey && it.cdn_url) {
        candidates.add(it.cdn_url);
      }
    }
  }

  // from productImageMap
  if (pimMap[key] && Array.isArray(pimMap[key])) {
    for (const url of pimMap[key]) {
      candidates.add(url);
    }
  }

  // from productsFullyMap
  const pfEntry = productsFullyMap.get(nkey);
  if (pfEntry && pfEntry.image_url) candidates.add(pfEntry.image_url);

  // from detailedMap
  const detEntry = detailedMap.get(nkey);
  if (detEntry && detEntry.image_url) candidates.add(detEntry.image_url);

  // from skuSyncMap
  const syncEntry = skuSyncMap.get(nkey);
  if (syncEntry) {
    if (syncEntry.primary_url) candidates.add(syncEntry.primary_url);
    if (Array.isArray(syncEntry.all_urls)) {
      for (const u of syncEntry.all_urls) candidates.add(u);
    }
  }

  const candidatesList = Array.from(candidates).slice(0, 5); // top-5

  // Extract pricing/kpi from enriched SKU
  const price = sku.pricing?.final_price || sku.price_brl || 0;
  const grossMargin = sku.kpis?.gross_margin_percent || 0;
  const weight = sku.weight_kg || 0;

  rows.push({
    sku: key,
    primary_image: primary || '',
    all_images: all.join('|'),
    source,
    score,
    price_brl: price,
    gross_margin_percent: grossMargin,
    weight_kg: weight,
    candidate_urls: candidatesList.join('|'),
  });
}

// write full CSV
const out = [
  'sku,primary_image,all_images,source,score,price_brl,gross_margin_percent,weight_kg,candidate_urls',
];
for (const r of rows) {
  const esc = (v) => '"' + String(v || '').replaceAll('"', '""') + '"';
  out.push(
    [
      esc(r.sku),
      esc(r.primary_image),
      esc(r.all_images),
      esc(r.source),
      r.score,
      r.price_brl,
      r.gross_margin_percent,
      r.weight_kg,
      esc(r.candidate_urls),
    ].join(',')
  );
}

const outPath = path.join(root, 'sku-image-audit-enhanced.csv');
fs.writeFileSync(outPath, out.join('\n'), 'utf-8');
console.log('CSV completo gerado:', outPath, `rows=${rows.length}`);

// generate top-250 by price
const sorted = rows.slice().sort((a, b) => b.price_brl - a.price_brl);
const top250 = sorted.slice(0, 250);

const top250Out = [
  'sku,primary_image,all_images,source,score,price_brl,gross_margin_percent,weight_kg,candidate_urls',
];
for (const r of top250) {
  const esc = (v) => '"' + String(v || '').replaceAll('"', '""') + '"';
  top250Out.push(
    [
      esc(r.sku),
      esc(r.primary_image),
      esc(r.all_images),
      esc(r.source),
      r.score,
      r.price_brl,
      r.gross_margin_percent,
      r.weight_kg,
      esc(r.candidate_urls),
    ].join(',')
  );
}

const top250Path = path.join(root, 'sku-image-audit-top250.csv');
fs.writeFileSync(top250Path, top250Out.join('\n'), 'utf-8');
console.log('CSV top-250 por valor gerado:', top250Path, `rows=${top250.length}`);
