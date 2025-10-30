/**
 * YSH B2B Store Gateway - Distributors Endpoint
 * Lista distribuidores com estatísticas
 * 
 * @standard Facebook Commerce Platform Compatible
 */

import { Request, Response, NextFunction } from 'express';
import { loadEnrichedData } from "../route";
import { extractCategoryFromSKU, extractDistributorFromSKU, formatDecimal } from "../utils";

/**
 * GET /store/gateway/distributors
 * Lista distribuidores com estatísticas de produtos e preços
 */
export const GET = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const enrichedData = await loadEnrichedData();

        // Extrair informações únicas de distribuidores do SKU patterns
        const distributorStats = new Map<string, {
            name: string;
            total_products: number;
            categories: Set<string>;
            price_range: { min: number; max: number; avg: number; };
            margin_stats: { avg_net: number; avg_gross: number; };
        }>();

        for (const product of enrichedData) {
            const distributor = extractDistributorFromSKU(product.sku);
            const category = extractCategoryFromSKU(product.sku);

            if (!distributorStats.has(distributor)) {
                distributorStats.set(distributor, {
                    name: distributor,
                    total_products: 0,
                    categories: new Set(),
                    price_range: { min: Infinity, max: 0, avg: 0 },
                    margin_stats: { avg_net: 0, avg_gross: 0 }
                });
            }

            const stats = distributorStats.get(distributor)!;
            stats.total_products++;
            stats.categories.add(category);
            stats.price_range.min = Math.min(stats.price_range.min, product.final_price);
            stats.price_range.max = Math.max(stats.price_range.max, product.final_price);
            stats.margin_stats.avg_net += product.dynamic_markup.netMargin;
            stats.margin_stats.avg_gross += product.dynamic_markup.grossMargin;
        }

        // Processar estatísticas finais
        const distributors = Array.from(distributorStats.values()).map(stats => {
            const avgPrice = enrichedData
                .filter((p: any) => p.sku.startsWith(stats.name))
                .reduce((sum: number, p: any) => sum + p.final_price, 0) / stats.total_products;

            return {
                name: stats.name,
                total_products: stats.total_products,
                categories: Array.from(stats.categories),
                price_range: {
                    min: stats.price_range.min,
                    max: stats.price_range.max,
                    avg: formatDecimal(avgPrice)
                },
                margins: {
                    avg_net_margin: formatDecimal(stats.margin_stats.avg_net / stats.total_products),
                    avg_gross_margin: formatDecimal(stats.margin_stats.avg_gross / stats.total_products)
                }
            };
        });

        // Ordenar por total de produtos
        distributors.sort((a, b) => b.total_products - a.total_products);

        const summary = {
            total_distributors: distributors.length,
            total_products: enrichedData.length,
            avg_products_per_distributor: formatDecimal(enrichedData.length / distributors.length)
        };

        res.json({
            success: true,
            data: {
                distributors,
                summary
            },
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('[Gateway] Distributors error:', error);
        error.statusCode = error.statusCode || 500;
        next(error);
    }
};
