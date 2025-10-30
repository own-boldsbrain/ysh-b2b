#!/usr/bin/env tsx
/**
 * Import Fortlev products from JSON to PostgreSQL ysh_catalog.products
 * Usage: npx tsx scripts/import-fortlev-to-db.ts
 */

import { Pool } from 'pg';
import * as fs from 'fs';
import * as path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface FortlevProduct {
  code: string;
  title: string;
  price: string;
  image: string;
  componentId: string;
  manufacturer: string | null;
  family: string;
  step: number;
  fullPrice: number;
  finalPrice: number;
}

interface FortlevCatalog {
  distributor: string;
  extractedAt: string;
  totalProducts: number;
  categoryCounts: Record<string, number>;
  priceStats: {
    min: number;
    max: number;
    avg: number;
    median: number;
  };
  products: FortlevProduct[];
}

async function main() {
  // PostgreSQL connection
  const pool = new Pool({
    host: 'localhost',
    port: 5432,
    database: 'postgres',
    user: 'supabase_admin',
    password: 'your-super-secret-and-long-postgres-password',
  });

  try {
    // Read JSON file
    const jsonPath = path.join(
      __dirname,
      '..',
      'mcp-servers',
      'fortlev-catalog-full.json'
    );
    console.log(`📂 Reading: ${jsonPath}`);
    const rawData = fs.readFileSync(jsonPath, 'utf-8');
    const catalog: FortlevCatalog = JSON.parse(rawData);

    console.log(`\n📊 Catalog Summary:`);
    console.log(`   Distributor: ${catalog.distributor}`);
    console.log(`   Extracted At: ${catalog.extractedAt}`);
    console.log(`   Total Products: ${catalog.totalProducts}`);
    console.log(`   Categories:`, catalog.categoryCounts);
    console.log(`   Price Range: R$ ${catalog.priceStats.min.toFixed(2)} - R$ ${catalog.priceStats.max.toFixed(2)}`);

    // Get distributor ID
    console.log(`\n🔍 Looking up Fortlev distributor ID...`);
    const distributorResult = await pool.query(
      `SELECT id FROM ysh_catalog.distributors WHERE name = $1`,
      ['fortlev']
    );

    if (distributorResult.rows.length === 0) {
      throw new Error('Distributor "fortlev" not found in database');
    }

    const distributorId = distributorResult.rows[0].id;
    console.log(`   ✅ Found: ${distributorId}`);

    // Check existing products
    console.log(`\n🔍 Checking existing products...`);
    const existingResult = await pool.query(
      `SELECT COUNT(*) as count FROM ysh_catalog.products WHERE distributor_id = $1`,
      [distributorId]
    );
    const existingCount = parseInt(existingResult.rows[0].count);
    console.log(`   Existing products: ${existingCount}`);

    // Insert products
    console.log(`\n📥 Inserting ${catalog.totalProducts} products...`);
    let insertedCount = 0;
    let skippedCount = 0;

    for (const product of catalog.products) {
      try {
        // Generate ysh_sku from code
        const yshSku = `FORTLEV-${product.code}`;
        
        // Check if already exists
        const existingProduct = await pool.query(
          `SELECT id FROM ysh_catalog.products WHERE ysh_sku = $1`,
          [yshSku]
        );

        if (existingProduct.rows.length > 0) {
          console.log(`   ⏭️  Skipped (exists): ${yshSku}`);
          skippedCount++;
          continue;
        }

        // Prepare images array
        const images = product.image ? [product.image] : [];

        // Map family to category
        const categoryMap: Record<string, string> = {
          inverter: 'Inversor',
          miscellaneous: 'Diversos',
          structure: 'Estrutura',
          dependency: 'Dependência',
        };
        const category = categoryMap[product.family] || product.family;

        // Insert product
        await pool.query(
          `INSERT INTO ysh_catalog.products (
            distributor_id,
            ysh_sku,
            distributor_sku,
            name,
            category,
            subcategory,
            brand,
            price_brl,
            images,
            specifications,
            raw_data,
            last_extracted_at
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)`,
          [
            distributorId,
            yshSku,
            product.code,
            product.title,
            category,
            product.family,
            product.manufacturer || 'Fortlev',
            product.finalPrice,
            images,
            JSON.stringify({
              fullPrice: product.fullPrice,
              step: product.step,
              componentId: product.componentId,
            }),
            JSON.stringify({
              code: product.code,
              price: product.price,
              componentId: product.componentId,
              manufacturer: product.manufacturer,
              family: product.family,
              step: product.step,
              fullPrice: product.fullPrice,
              finalPrice: product.finalPrice,
              url: 'https://fortlevsolar.app/produto-avulso',
            }),
            new Date(catalog.extractedAt),
          ]
        );

        console.log(`   ✅ Inserted: ${yshSku} - ${product.title}`);
        insertedCount++;
      } catch (error) {
        console.error(`   ❌ Error inserting ${product.code}:`, error);
      }
    }

    // Final count
    console.log(`\n✅ Import Complete!`);
    console.log(`   Inserted: ${insertedCount}`);
    console.log(`   Skipped: ${skippedCount}`);
    console.log(`   Total: ${insertedCount + skippedCount}`);

    // Verify final count
    const finalResult = await pool.query(
      `SELECT COUNT(*) as count FROM ysh_catalog.products WHERE distributor_id = $1`,
      [distributorId]
    );
    const finalCount = parseInt(finalResult.rows[0].count);
    console.log(`\n📊 Database verification:`);
    console.log(`   Total Fortlev products in DB: ${finalCount}`);

  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  } finally {
    await pool.end();
  }
}

main();
