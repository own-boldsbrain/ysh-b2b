/**
 * Import Script: Dynamis
 * 
 * Importa produtos do arquivo de catálogo dynamis-catalog-full.json para PostgreSQL
 * 
 * Uso:
 *   npx tsx scripts/import-dynamis-to-db.ts
 * 
 * Variáveis de ambiente (opcional):
 *   - DB_HOST: localhost (padrão)
 *   - DB_PORT: 5432 (padrão)
 *   - DB_NAME: ysh_catalog (padrão)
 *   - DB_USER: supabase_admin (padrão)
 *   - DB_PASSWORD: (requer do ENV ou prompt)
 */

import { Pool } from 'pg';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import type { QueryResult } from 'pg';

const __dirname = dirname(fileURLToPath(import.meta.url));
const __filename = fileURLToPath(import.meta.url);

interface Product {
  code: string;
  title: string;
  price: number;
  image?: string;
  brand?: string;
  category?: string;
  description?: string;
  fullPrice?: number;
  finalPrice?: number;
  family?: string;
  componentId?: string;
  step?: string;
  images?: string[];
  manufacturer?: string;
  specifications?: Record<string, unknown>;
}

// Configuração do PostgreSQL
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'ysh_catalog',
  user: process.env.DB_USER || 'supabase_admin',
  password: process.env.DB_PASSWORD || '',
  max: 20,
  connectionTimeoutMillis: 5000,
});

const DISTRIBUTOR_ID = 'dynamis';
const DISTRIBUTOR_NAME = 'Dynamis';

async function getDistributorId(client: typeof pool): Promise<string> {
  const query = 'SELECT id FROM ysh_catalog.distributors WHERE id = $1';
  const result = await client.query(query, [DISTRIBUTOR_ID]);
  
  if (result.rows.length === 0) {
    throw new Error(`Distributor '${DISTRIBUTOR_ID}' not found in database`);
  }
  
  return result.rows[0].id;
}

function generateYshSku(distributor: string, code: string): string {
  const cleanCode = code.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
  return `${distributor.toUpperCase()}-${cleanCode}`.substring(0, 50);
}

function normalizePriceValue(price: string | number | undefined): number {
  if (!price) return 0;
  
  const priceStr = String(price);
  // Remove caracteres não numéricos exceto vírgula e ponto
  const normalized = priceStr.replace(/[^\d,.]/g, '');
  // Converte vírgula para ponto (padrão BR)
  const withDot = normalized.replace(',', '.');
  const parsed = parseFloat(withDot);
  
  return isNaN(parsed) ? 0 : parsed;
}

function categorizeProduct(title: string | undefined): string {
  if (!title) return 'uncategorized';
  
  const titleLower = title.toLowerCase();
  
  if (titleLower.includes('inversor') || titleLower.includes('inverter')) {
    return 'inverter';
  }
  if (titleLower.includes('painel') || titleLower.includes('panel')) {
    return 'solar_panel';
  }
  if (titleLower.includes('bateria') || titleLower.includes('battery')) {
    return 'battery';
  }
  if (titleLower.includes('controlador') || titleLower.includes('controller')) {
    return 'charge_controller';
  }
  if (titleLower.includes('cabo') || titleLower.includes('cable')) {
    return 'cable';
  }
  if (titleLower.includes('conector') || titleLower.includes('connector')) {
    return 'connector';
  }
  if (titleLower.includes('estrutura') || titleLower.includes('structure')) {
    return 'mounting_structure';
  }
  
  return 'miscellaneous';
}

function extractManufacturer(title: string | undefined): string {
  if (!title) return 'unknown';
  
  // Heurística: primeira palavra capitalized
  const words = title.split(/\s+/);
  return (words[0] || 'unknown').substring(0, 50);
}

function extractModel(title: string | undefined): string {
  if (!title) return '';
  
  // Heurística: segunda palavra ou após a marca
  const words = title.split(/\s+/);
  if (words.length > 1) {
    return (words.slice(1, 3).join(' ') || '').substring(0, 100);
  }
  
  return '';
}

async function importProducts(): Promise<void> {
  console.log(`\n════════════════════════════════════════════════════════════════════════════════`);
  console.log(`📦 IMPORTADOR: ${DISTRIBUTOR_NAME}`);
  console.log(`════════════════════════════════════════════════════════════════════════════════`);
  
  try {
    // Conectar ao banco
    console.log(`\n📡 Conectando ao PostgreSQL...`);
    const client = await pool.connect();
    console.log(`✅ Conectado`);
    
    try {
      // Verificar distribuidor
      console.log(`\n🔍 Verificando distribuidor '${DISTRIBUTOR_ID}'...`);
      await getDistributorId(client);
      console.log(`✅ Distribuidor encontrado`);
      
      // Ler arquivo de catálogo
      console.log(`\n📂 Lendo catálogo: ${DISTRIBUTOR_NAME}`);
      const catalogPath = join(__dirname, '..', `${DISTRIBUTOR_ID}-catalog-full.json`);
      
      if (!require('fs').existsSync(catalogPath)) {
        throw new Error(`Catalog file not found: ${catalogPath}`);
      }
      
      const catalogData = JSON.parse(readFileSync(catalogPath, 'utf-8')) as Product[];
      console.log(`✅ Lido: ${catalogData.length} produtos`);
      
      if (catalogData.length === 0) {
        console.warn(`⚠️  Arquivo vazio: ${catalogPath}`);
        return;
      }
      
      // Processar e inserir produtos
      console.log(`\n⚙️  Processando produtos...`);
      
      let inserted = 0;
      let skipped = 0;
      let failed = 0;
      const insertedSkus: string[] = [];
      const failedProducts: Array<{ sku: string; error: string }> = [];
      
      for (const product of catalogData) {
        try {
          const yshSku = generateYshSku(DISTRIBUTOR_ID, product.code);
          
          // Verificar se já existe
          const checkQuery = 'SELECT id FROM ysh_catalog.products WHERE ysh_sku = $1';
          const checkResult = await client.query(checkQuery, [yshSku]);
          
          if (checkResult.rows.length > 0) {
            skipped++;
            continue;
          }
          
          // Preparar dados
          const distributorSku = product.code || '';
          const name = product.title || '';
          const category = product.category || categorizeProduct(product.title);
          const subcategory = product.family || '';
          const brand = product.brand || extractManufacturer(product.title);
          const model = extractModel(product.title);
          const priceBrl = normalizePriceValue(product.price || product.finalPrice);
          const originalPrice = normalizePriceValue(product.fullPrice || product.price);
          const images = product.images || (product.image ? [product.image] : []);
          
          const specifications = {
            componentId: product.componentId,
            step: product.step,
            extractedFrom: DISTRIBUTOR_NAME,
            extractedAt: new Date().toISOString(),
            ...product.specifications,
          };
          
          const rawData = {
            original: product,
            importedAt: new Date().toISOString(),
            importScript: __filename,
          };
          
          // Inserir produto
          const insertQuery = `
            INSERT INTO ysh_catalog.products (
              distributor_id,
              ysh_sku,
              distributor_sku,
              name,
              description,
              category,
              subcategory,
              brand,
              model,
              price_brl,
              original_price_brl,
              images,
              specifications,
              raw_data,
              created_at,
              updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NOW(), NOW())
          `;
          
          await client.query(insertQuery, [
            DISTRIBUTOR_ID,
            yshSku,
            distributorSku,
            name,
            product.description || null,
            category,
            subcategory,
            brand,
            model,
            priceBrl,
            originalPrice,
            JSON.stringify(images),
            JSON.stringify(specifications),
            JSON.stringify(rawData),
          ]);
          
          inserted++;
          insertedSkus.push(yshSku);
          
          // Log a cada 10 produtos
          if (inserted % 10 === 0) {
            process.stdout.write(`.`);
          }
        } catch (error) {
          failed++;
          failedProducts.push({
            sku: product.code || 'unknown',
            error: error instanceof Error ? error.message : String(error),
          });
        }
      }
      
      // Relatório final
      console.log(`\n\n📊 RELATÓRIO DE IMPORTAÇÃO`);
      console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
      console.log(`✅ Inseridos: ${inserted} produtos`);
      console.log(`⏭️  Ignorados: ${skipped} produtos (já existiam)`);
      console.log(`❌ Falhas: ${failed} produtos`);
      console.log(`📊 Total: ${inserted + skipped + failed} / ${catalogData.length}`);
      console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
      
      if (insertedSkus.length > 0) {
        console.log(`\n✨ Primeiros 5 inseridos:`);
        insertedSkus.slice(0, 5).forEach((sku) => console.log(`   • ${sku}`));
      }
      
      if (failedProducts.length > 0 && failedProducts.length <= 5) {
        console.log(`\n⚠️  Produtos com erro:`);
        failedProducts.forEach((p) => console.log(`   • ${p.sku}: ${p.error}`));
      }
      
      console.log(`\n🎉 Importação concluída!`);
      console.log(`   Verificar no banco: SELECT COUNT(*) FROM ysh_catalog.products WHERE distributor_id = '${DISTRIBUTOR_ID}'`);
      
    } finally {
      client.release();
    }
  } catch (error) {
    console.error(`\n❌ Erro crítico:`, error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

// Executar
importProducts().catch(console.error);
