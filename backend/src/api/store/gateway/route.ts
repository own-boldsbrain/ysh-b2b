/**
 * YSH B2B Store - API Gateway (Facebook Commerce Platform Compatible)
 * Gateway unificado para acesso da loja com dados enriquecidos
 * 
 * @description
 * Este gateway consolida:
 * - Catálogo de produtos compatível com Facebook Catalog API
 * - Precificação dinâmica (enriched SKUs)
 * - Comparação de distribuidores
 * - Export para Facebook Commerce (CSV, XML, Batch API)
 * 
 * @standard Facebook Commerce Platform Catalog API
 * @see https://developers.facebook.com/docs/commerce-platform/catalog/
 */

import { Request, Response, NextFunction } from 'express';
import fs from 'node:fs/promises';
import path from 'node:path';

// Cache para dados enriquecidos
let enrichedCache: any = null;
let cacheTimestamp = 0;
const CACHE_TTL = 300000; // 5 minutos

/**
 * Carrega dados enriquecidos do arquivo JSON
 */
async function loadEnrichedData() {
    if (enrichedCache && Date.now() - cacheTimestamp < CACHE_TTL) {
        return enrichedCache;
    }

    try {
        const dataPath = path.join(process.cwd(), 'enriched-skus-for-dynamodb-images-fixed.json');
        const data = await fs.readFile(dataPath, 'utf-8');
        enrichedCache = JSON.parse(data);
        cacheTimestamp = Date.now();
        
        console.log(`[Gateway] Loaded ${enrichedCache.length} enriched SKUs`);
        return enrichedCache;
    } catch (error) {
        console.error('[Gateway] Error loading enriched data:', error);
        const err: any = new Error("Failed to load enriched product data");
        err.statusCode = 500;
        throw err;
    }
}

/**
 * GET /store/gateway
 * Gateway overview - retorna informações sobre os endpoints disponíveis
 * Compatible with Facebook Commerce Platform standards
 */
export const GET = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const enrichedData = await loadEnrichedData();

        res.status(200).json({
            name: "YSH B2B Store API Gateway",
            version: "1.0.0",
            status: "operational",
            data: {
                total_skus: enrichedData.length,
                last_update: new Date(cacheTimestamp).toISOString(),
                cache_ttl: CACHE_TTL / 1000 + 's',
            },
            endpoints: {
                overview: {
                    path: "/store/gateway",
                    method: "GET",
                    description: "Gateway overview and health"
                },
                products: {
                    path: "/store/gateway/products",
                    method: "GET",
                    description: "List all products with dynamic pricing",
                    params: {
                        category: "Filter by category (kits, panels, inverters, etc.)",
                        min_price: "Minimum price filter",
                        max_price: "Maximum price filter",
                        limit: "Results per page (default: 50, max: 200)",
                        offset: "Pagination offset (default: 0)",
                        sort: "Sort field (price, margin, sku)",
                        order: "Sort order (asc, desc)"
                    }
                },
                product_detail: {
                    path: "/store/gateway/products/:sku",
                    method: "GET",
                    description: "Get detailed product information with pricing strategy"
                },
                pricing_comparison: {
                    path: "/store/gateway/products/:sku/pricing",
                    method: "GET",
                    description: "Compare pricing across distributors for a SKU"
                },
                distributors: {
                    path: "/store/gateway/distributors",
                    method: "GET",
                    description: "List all distributors with statistics"
                },
                categories: {
                    path: "/store/gateway/categories",
                    method: "GET",
                    description: "Get category statistics and product counts"
                },
                pricing_strategy: {
                    path: "/store/gateway/pricing-strategy",
                    method: "GET",
                    description: "Get overall pricing strategy and KPIs"
                }
            },
            features: [
                "Dynamic pricing with markup adjustments",
                "Multi-distributor price comparison",
                "Charm pricing (psychological pricing)",
                "Channel-based pricing (B2C/B2B)",
                "Scenario-based pricing (neutro/agressivo/premium)",
                "Margin and profitability analysis",
                "Category and manufacturer filtering",
                "Real-time cache (5min TTL)"
            ],
            pricing_info: {
                avg_markup: "25%",
                avg_gross_margin: "20%",
                avg_net_margin: "11%",
                charm_pricing_adoption: "99%",
                scenarios: ["neutro", "agressivo", "premium"]
            }
        });
    } catch (error: any) {
        console.error('[Gateway] Error:', error);
        error.statusCode = error.statusCode || 500;
        next(error);
    }
};

/**
 * Exporta função para reutilização em outros endpoints
 */
export { loadEnrichedData };
