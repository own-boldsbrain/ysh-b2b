#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(process.cwd());
const INPUT_SYNCED = path.join(ROOT, 'enriched-skus-for-dynamodb-synced.json');
const OUT_FIXED = path.join(ROOT, 'enriched-skus-for-dynamodb-images-fixed.json');
const OUT_REPORT = path.join(ROOT, 'ENRICHED_SKUS_DYNAMIC_PRICING_REPORT-images-fixed.json');

// external datasets (from attachments)
const EQUIP_PATH = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/data/equipamentos.json';
const STORE_READY_PATH = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/data/store-ready-skus.json';
const IMGS_INDEX_JSON = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/assets/products/imgs-index.json';
const PRODUCTS_DETAILED = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/assets/products/products-detailed-catalog.json';
const PRODUCT_IMAGE_MAP = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/assets/products/product_image_map.json';
const SKU_IMAGES_SYNC = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/assets/products/sku-images-sync.json';
const PRODUCTS_FULLY_PRICED = 'c:/Users/fjuni/YSH-APPS/YSH-HELIO/src/assets/products/products-fully-priced-catalog.json';

function normalize(s){ if(!s) return ''; return String(s).toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g,'').trim(); }

function loadJson(p){ try { return JSON.parse(fs.readFileSync(p,'utf8')); } catch(e){ console.error('Falha ao abrir',p,e.message); return null; }}

if(!fs.existsSync(INPUT_SYNCED)){
  console.error('Arquivo de SKUs sincronizados não encontrado:', INPUT_SYNCED);
  process.exit(1);
}

console.log('Carregando SKUs sincronizados...');
const skus = loadJson(INPUT_SYNCED) || [];
console.log('Carregando datasets auxiliares...');
const equip = loadJson(EQUIP_PATH) || [];
const store = loadJson(STORE_READY_PATH) || [];
const imgsIndex = loadJson(IMGS_INDEX_JSON) || {};
const productsDetailed = loadJson(PRODUCTS_DETAILED) || {};
const productImageMap = loadJson(PRODUCT_IMAGE_MAP) || {};
const skuImagesSync = loadJson(SKU_IMAGES_SYNC) || {};
const productsFully = loadJson(PRODUCTS_FULLY_PRICED) || {};

// build lookups
const bySku = new Map();
const byModel = new Map();
const byNormalizedName = new Map();

function addToMap(map, key, item){ if(!key) return; const k = normalize(key); if(!k) return; if(!map.has(k)) map.set(k, []); map.get(k).push(item); }

// index helper: images index (array under imgsIndex.images)
if (imgsIndex && Array.isArray(imgsIndex.images)) {
  for (const it of imgsIndex.images) {
    const sk = it.sku || it.SKU || it.product_sku || '';
    if (sk) addToMap(bySku, sk, it);
    if (it.filename) addToMap(byNormalizedName, it.filename.replace(/\.[a-z0-9]+$/i, ''), it);
    if (it.cdn_url) addToMap(byNormalizedName, it.cdn_url, it);
  }
}

// products detailed/catalog can include image_url and sku
if (productsDetailed && Array.isArray(productsDetailed.products)) {
  for (const p of productsDetailed.products) {
    if (p.sku) addToMap(bySku, p.sku, p);
    if (p.model) addToMap(byModel, p.model, p);
    const name = p.title || p.name || p.product_name || p.sku || p.model || '';
    addToMap(byNormalizedName, name, p);
    if (p.image_url) addToMap(byNormalizedName, p.image_url, p);
  }
}

// products fully priced CSV/JSON
if (productsFully && Array.isArray(productsFully.products)){
  for(const p of productsFully.products){
    if(p.sku) addToMap(bySku, p.sku, p);
    if(p.image_url) addToMap(byNormalizedName, p.image_url, p);
  }
}

// product_image_map may map sku keys
if (productImageMap && productImageMap.images) {
  for (const key of Object.keys(productImageMap.images)){
    const arr = productImageMap.images[key];
    if (Array.isArray(arr) && arr.length) addToMap(bySku, key, { images: arr });
  }
}

// sku-images-sync summary
if (skuImagesSync && skuImagesSync.skus && Array.isArray(skuImagesSync.skus)){
  for(const entry of skuImagesSync.skus){
    // entries in that file may be shaped; look for sku and primary_url/all_urls
    const k = entry.sku || entry.SKU || null;
    if(k){ addToMap(bySku, k, entry); }
  }
}

// also seed from equipment and store arrays
for(const p of [...equip, ...store]){
  if(p.sku) addToMap(bySku, p.sku, p);
  if(p.model) addToMap(byModel, p.model, p);
  const name = p.name || p.title || p.product_name || p.model || p.sku || '';
  addToMap(byNormalizedName, name, p);
}

let updated = 0;
let stillMissing = 0;
const samples = [];

for(const sku of skus){
  const imgs = new Set(sku.images || []);
  if(sku.image_url) imgs.add(sku.image_url);
  // try exact sku match
  let found = null;
  if (sku.sku && bySku.has(normalize(sku.sku))) found = bySku.get(normalize(sku.sku))[0];
  // try productsFully sku map
  if (!found && productsFully && Array.isArray(productsFully.products)){
    const pf = productsFully.products.find(p=> p.sku && normalize(p.sku) === normalize(sku.sku));
    if(pf) found = pf;
  }
  // try model
  if (!found && sku.model && byModel.has(normalize(sku.model))) found = byModel.get(normalize(sku.model))[0];
  // try normalized name/title
  if (!found){
    const cand = byNormalizedName.get(normalize(sku.name || sku.title || sku.sku || sku.model || '')) || [];
    if (cand.length) found = cand[0];
  }
  // fallback: try matching by image filename containing model or sku using imgsIndex images
  if (!found){
    const tokens = (sku.model || sku.sku || sku.name || '').split(/[^a-z0-9]+/i).filter(Boolean).map(t=>normalize(t));
    const imgs = imgsIndex.images || [];
    for(const it of imgs){
      const url = it.cdn_url || it.cdnUrl || it.image_url || it.url || it.filename || '';
      if(!url) continue;
      const lname = normalize(url);
      if(tokens.some(t => t && lname.includes(t))){ found = it; break; }
    }
  }

  if(found){
    // collect images from candidate (robust over many shapes)
    const candidateImgs = new Set(imgs);
    const imgFields = ['cdn_url','cdnUrl','image_url','imageUrl','image','images','pictures','picture','photos','gallery','image_urls','images_url','imageUrls','photo','thumbnail','thumbnails','url'];
    for (const k of imgFields){
      const v = found[k];
      if(!v) continue;
      if(Array.isArray(v)) for(const it of v) if(it) candidateImgs.add(it);
      else candidateImgs.add(v);
    }
    // product_image_map entry shape: { images: [...] }
    if (found.images && Array.isArray(found.images)) for(const it of found.images) if(it) candidateImgs.add(it);
    if (found.all_urls && Array.isArray(found.all_urls)) for(const it of found.all_urls) if(it) candidateImgs.add(it);
    if (found.primary_url) candidateImgs.add(found.primary_url);
    if (found.cdn_url) candidateImgs.add(found.cdn_url);
    if (found.filename && typeof found.filename === 'string') {
      // try construct cdn path from filename if not absolute
      const fname = found.filename;
      if (/^https?:/.test(fname)) candidateImgs.add(fname);
      else {
        // we don't know category; add a safe guess using productsDetailed metadata later
        candidateImgs.add(fname);
      }
    }
    // if SKU has no images but candidate has image_url, set primary image_url
    if (!sku.image_url) {
      const primary = found.cdn_url || found.image_url || found.image || found.url || found.primary_url || null;
      if (primary) sku.image_url = primary;
    }
    sku.images = Array.from(candidateImgs).filter(Boolean);
    if (sku.images.length > 0) updated++;
  } else {
    // no candidate found; try to extract image_url from productsFully CSV (easy path)
    let got = false;
    if ((!sku.images || sku.images.length===0) && !sku.image_url && productsFully && Array.isArray(productsFully.products)){
      const pf = productsFully.products.find(p=> p.sku && normalize(p.sku) === normalize(sku.sku));
      if(pf && (pf.image_url || pf.image)){
        sku.image_url = pf.image_url || pf.image;
        sku.images = [sku.image_url];
        updated++; got = true;
      }
    }
    if(!got){
      if((!sku.images || sku.images.length===0) && !sku.image_url) stillMissing++;
    }
  }

  if(samples.length < 10) samples.push({ sku: sku.sku || sku.name, images: sku.images ? sku.images.slice(0,3) : [], image_url: sku.image_url || null });
}

console.log('Gravando arquivos...');
fs.writeFileSync(OUT_FIXED, JSON.stringify(skus, null, 2), 'utf8');
const report = { timestamp: new Date().toISOString(), total: skus.length, imagesAdded: updated, stillMissing, samples };
fs.writeFileSync(OUT_REPORT, JSON.stringify(report, null, 2), 'utf8');

console.log('Resumo:');
console.log(` Total SKUs: ${report.total}`);
console.log(` Images adicionadas: ${report.imagesAdded}`);
console.log(` Ainda faltando imagens: ${report.stillMissing}`);
console.log(' Arquivos gerados:', OUT_FIXED, OUT_REPORT);
