// Demo: leitura do DynamoDB diretamente do browser usando Cognito Identity Pool (somente leitura)
// Usa AWS SDK v3 modular via CDN (jsdelivr) - apenas para debug/local dashboards

import { CognitoIdentityClient } from 'https://cdn.jsdelivr.net/npm/@aws-sdk/client-cognito-identity@3.385.0/dist-es/CognitoIdentityClient.min.js';
import { fromCognitoIdentityPool } from 'https://cdn.jsdelivr.net/npm/@aws-sdk/credential-providers@3.385.0/dist-es/index.min.js';
import { DynamoDBClient } from 'https://cdn.jsdelivr.net/npm/@aws-sdk/client-dynamodb@3.385.0/dist-es/DynamoDBClient.min.js';
import { DynamoDBDocumentClient, ScanCommand, GetCommand } from 'https://cdn.jsdelivr.net/npm/@aws-sdk/lib-dynamodb@3.385.0/dist-es/index.min.js';

const $ = id => document.getElementById(id);

function log(msg) {
  const out = $('results');
  const el = document.createElement('div');
  el.innerHTML = msg;
  out.prepend(el);
}

function clearResults() {
  $('results').innerHTML = '';
}

function validateSKU(sku) {
  // Campos obrigatórios definidos pela equipe: sku, category, price_brl, pricing.final_price, kpis.gross_margin_percent
  const missing = [];
  if (!sku) return { ok:false, missing:['sku object is falsy'] };
  if (!sku.sku && !sku.name) missing.push('sku (id/name)');
  if (!sku.category) missing.push('category');
  if (typeof sku.price_brl === 'undefined' || sku.price_brl === null) missing.push('price_brl');
  if (!sku.pricing || typeof sku.pricing.final_price === 'undefined') missing.push('pricing.final_price');
  if (!sku.kpis || typeof sku.kpis.gross_margin_percent === 'undefined') missing.push('kpis.gross_margin_percent');
  return { ok: missing.length === 0, missing };
}

async function buildDocumentClient(region, identityPoolId) {
  const cognitoClient = new CognitoIdentityClient({ region });
  const credentials = fromCognitoIdentityPool({
    client: cognitoClient,
    identityPoolId,
  });
  const ddbClient = new DynamoDBClient({ region, credentials });
  const ddbDoc = DynamoDBDocumentClient.from(ddbClient, { marshallOptions: { removeUndefinedValues: true } });
  return ddbDoc;
}

async function scanTable(ddbDoc, tableName, limit = 100) {
  const command = new ScanCommand({ TableName: tableName, Limit: limit });
  const resp = await ddbDoc.send(command);
  return resp.Items || [];
}

async function getItem(ddbDoc, tableName, key) {
  // Assume key is primary key (attribute name uncertain). Try with common patterns
  const candidates = [
    { sku: key },
    { id: key },
    { PK: key },
    { productId: key }
  ];
  for (const Key of candidates) {
    try {
      const cmd = new GetCommand({ TableName: tableName, Key });
      const res = await ddbDoc.send(cmd);
      if (res.Item) return res.Item;
    } catch (err) {
      // continue
    }
  }
  return null;
}

// UI events
$('btnScan').addEventListener('click', async () => {
  clearResults();
  const region = $('region').value.trim();
  const identityPoolId = $('identityPoolId').value.trim();
  const tableName = $('tableName').value.trim();
  const limit = parseInt($('limitSelect').value, 10) || 100;

  if (!identityPoolId) return log('<div class="missing">Informe o Cognito Identity Pool ID antes de usar.</div>');

  log(`<div>🔌 Conectando (region=${region})...</div>`);
  try {
    const ddbDoc = await buildDocumentClient(region, identityPoolId);
    log('<div>🔎 Executando Scan (leitura somente)...</div>');
    const items = await scanTable(ddbDoc, tableName, limit);
    log(`<div>✅ Scan retornou ${items.length} itens</div>`);

    for (const item of items) {
      const v = validateSKU(item);
      const container = document.createElement('div');
      container.className = 'sku';
      container.innerHTML = `<strong>${item.sku || item.name || item.id || '—'}</strong> &nbsp; ` +
        (v.ok ? `<span class="ok">OK</span>` : `<span class="missing">FALTANDO: ${v.missing.join(', ')}</span>`);
      const detail = document.createElement('pre');
      detail.textContent = JSON.stringify(item, null, 2);
      container.appendChild(detail);
      $('results').appendChild(container);
    }
  } catch (err) {
    log(`<div class="missing">Erro: ${err.message || err}</div>`);
    console.error(err);
  }
});

$('btnGetSample').addEventListener('click', async () => {
  clearResults();
  const region = $('region').value.trim();
  const identityPoolId = $('identityPoolId').value.trim();
  const tableName = $('tableName').value.trim();
  const key = $('keyInput').value.trim();
  if (!identityPoolId) return log('<div class="missing">Informe o Cognito Identity Pool ID antes de usar.</div>');
  if (!key) return log('<div class="missing">Informe a chave do SKU para buscar.</div>');

  try {
    const ddbDoc = await buildDocumentClient(region, identityPoolId);
    log('<div>🔎 Buscando item por chave...</div>');
    const item = await getItem(ddbDoc, tableName, key);
    if (!item) return log('<div class="missing">Item não encontrado com as chaves comuns (sku, id, PK, productId).</div>');
    const v = validateSKU(item);
    const container = document.createElement('div');
    container.className = 'sku';
    container.innerHTML = `<strong>${item.sku || item.name || item.id}</strong> &nbsp; ` +
      (v.ok ? `<span class="ok">OK</span>` : `<span class="missing">FALTANDO: ${v.missing.join(', ')}</span>`);
    const detail = document.createElement('pre');
    detail.textContent = JSON.stringify(item, null, 2);
    container.appendChild(detail);
    $('results').appendChild(container);
  } catch (err) {
    log(`<div class="missing">Erro: ${err.message || err}</div>`);
    console.error(err);
  }
});

// Expose validate function for console quick-check
window.validateSKU = validateSKU;