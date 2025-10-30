#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import https from 'node:https';
import http from 'node:http';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.join(__dirname, '..');

const enrichedPath = path.join(root, 'enriched-skus-for-dynamodb.json');

function load(p) {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf-8'));
  } catch (e) {
    return null;
  }
}

const enriched = load(enrichedPath) || [];

console.log(`\n🔍 Verificando ${enriched.length} URLs de imagem...\n`);

// collect all image URLs
const urlSet = new Set();
const skuUrlMap = new Map(); // sku -> [urls]

for (const sku of enriched) {
  const key = sku.sku || sku.SKU || '';
  const urls = [];
  
  if (sku.image_url) urls.push(sku.image_url);
  if (Array.isArray(sku.images)) {
    for (const img of sku.images) {
      if (img && typeof img === 'string') urls.push(img);
    }
  }
  
  for (const u of urls) {
    // only add absolute URLs (http/https)
    if (u && typeof u === 'string' && /^https?:\/\//i.test(u)) {
      urlSet.add(u);
    }
  }
  
  if (urls.length > 0) skuUrlMap.set(key, urls);
}

const uniqueUrls = Array.from(urlSet);
console.log(`Total de URLs únicas a verificar: ${uniqueUrls.length}\n`);

// function to test URL (HEAD request with timeout)
function testUrl(url, timeout = 5000) {
  return new Promise((resolve) => {
    const protocol = url.startsWith('https') ? https : http;
    
    const req = protocol.request(
      url,
      { method: 'HEAD', timeout },
      (res) => {
        req.destroy();
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve({ url, status: 'OK', code: res.statusCode });
        } else if (res.statusCode === 404) {
          resolve({ url, status: '404', code: res.statusCode });
        } else {
          resolve({ url, status: 'ERROR', code: res.statusCode });
        }
      }
    );
    
    req.on('timeout', () => {
      req.destroy();
      resolve({ url, status: 'TIMEOUT', code: null });
    });
    
    req.on('error', (err) => {
      resolve({ url, status: 'ERROR', code: null, error: err.message });
    });
    
    req.end();
  });
}

// test all URLs in batches
const batchSize = 50;
const results = [];

for (let i = 0; i < uniqueUrls.length; i += batchSize) {
  const batch = uniqueUrls.slice(i, i + batchSize);
  const promises = batch.map((url) => testUrl(url));
  const batchResults = await Promise.all(promises);
  results.push(...batchResults);
  
  const progress = Math.round(((i + batch.length) / uniqueUrls.length) * 100);
  process.stdout.write(`\r✅ Progresso: ${i + batch.length}/${uniqueUrls.length} URLs (${progress}%)`);
}

console.log('\n\n✅ Verificação concluída!\n');

// aggregate stats
const stats = {
  ok: results.filter((r) => r.status === 'OK').length,
  notFound: results.filter((r) => r.status === '404').length,
  timeout: results.filter((r) => r.status === 'TIMEOUT').length,
  error: results.filter((r) => r.status === 'ERROR').length,
};

console.log('📊 Estatísticas:');
console.log(`   ✓ OK (200-299): ${stats.ok}`);
console.log(`   ✗ 404 Not Found: ${stats.notFound}`);
console.log(`   ⏱  Timeout: ${stats.timeout}`);
console.log(`   ❌ Outros Erros: ${stats.error}`);

// write CSV report
const csvOut = ['url,status,http_code,error'];
for (const r of results) {
  const esc = (v) => '"' + String(v || '').replaceAll('"', '""') + '"';
  csvOut.push([esc(r.url), esc(r.status), r.code || '', esc(r.error || '')].join(','));
}

const reportPath = path.join(root, 'image-url-validation-report.csv');
fs.writeFileSync(reportPath, csvOut.join('\n'), 'utf-8');
console.log(`\n📄 Relatório gerado: ${reportPath}`);

// write JSON report with SKU mapping
const jsonReport = {
  generated_at: new Date().toISOString(),
  summary: {
    total_urls: uniqueUrls.length,
    ok: stats.ok,
    not_found: stats.notFound,
    timeout: stats.timeout,
    error: stats.error,
  },
  results: results.map((r) => ({
    url: r.url,
    status: r.status,
    http_code: r.code,
    error: r.error || null,
  })),
  skus_with_broken_images: [],
};

// identify SKUs with broken images
for (const [sku, urls] of skuUrlMap.entries()) {
  const broken = [];
  for (const u of urls) {
    const result = results.find((r) => r.url === u);
    if (result && result.status !== 'OK') {
      broken.push({ url: u, status: result.status, code: result.code });
    }
  }
  if (broken.length > 0) {
    jsonReport.skus_with_broken_images.push({ sku, broken_urls: broken });
  }
}

const jsonPath = path.join(root, 'image-url-validation-report.json');
fs.writeFileSync(jsonPath, JSON.stringify(jsonReport, null, 2), 'utf-8');
console.log(`📄 Relatório JSON gerado: ${jsonPath}`);
console.log(`   🔴 SKUs com imagens quebradas: ${jsonReport.skus_with_broken_images.length}\n`);
