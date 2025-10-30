/**
 * YSH B2B Store Gateway - Categories Endpoint
 * Retorna estatísticas de categorias
 * 
 * @standard Facebook Commerce Platform Compatible
 */

import { Request, Response, NextFunction } from 'express';
import { loadEnrichedData } from "../route";
import { extractCategoryFromSKU } from "../utils";

/**
 * GET /store/gateway/categories
 * Lista categorias com estatísticas de produtos e preços
 */
export const GET = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const enrichedData = await loadEnrichedData();

        // Mapear categorias
        const categoryStats = new Map<string, {
            name: string;
            total_products: number;
            price_range: { min: number; max: number; avg: number; };
            margin_stats: { avg_net: number; avg_gross: number; };
            with_images: number;
            with_adjustments: number;
        }>();

        const CATEGORIES = ['kits', 'panels', 'inverters', 'batteries', 'structures', 'cables', 'stringboxes', 'accessories'];

        for (const cat of CATEGORIES) {
            categoryStats.set(cat, {
                name: cat,
                total_products: 0,
                price_range: { min: Infinity, max: 0, avg: 0 },
                margin_stats: { avg_net: 0, avg_gross: 0 },
                with_images: 0,
                with_adjustments: 0
            });
        }

        for (const product of enrichedData) {
            const category = extractCategoryFromSKU(product.sku);

            const stats = categoryStats.get(category)!;
            stats.total_products++;
            stats.price_range.min = Math.min(stats.price_range.min, product.final_price);
            stats.price_range.max = Math.max(stats.price_range.max, product.final_price);
            stats.margin_stats.avg_net += product.dynamic_markup.netMargin;
            stats.margin_stats.avg_gross += product.dynamic_markup.grossMargin;
            
            if (product.images && product.images.length > 0) {
                stats.with_images++;
            }
            
            if (product.dynamic_adjustments.total_adjustment !== 0) {
                stats.with_adjustments++;
            }
        }

        // Processar estatísticas finais
        const categories = Array.from(categoryStats.values())
            .filter(stats => stats.total_products > 0)
            .map(stats => {
                const categoryProducts = enrichedData.filter((p: any) => 
                    extractCategoryFromSKU(p.sku) === stats.name
                );

                const avgPrice = categoryProducts.reduce((sum: number, p: any) => sum + p.final_price, 0) / stats.total_products;

                return {
                    name: stats.name,
                    total_products: stats.total_products,
                    price_range: {
                        min: stats.price_range.min,
                        max: stats.price_range.max,
                        avg: Number.parseFloat(avgPrice.toFixed(2))
                    },
                    margins: {
                        avg_net_margin: Number.parseFloat((stats.margin_stats.avg_net / stats.total_products).toFixed(2)),
                        avg_gross_margin: Number.parseFloat((stats.margin_stats.avg_gross / stats.total_products).toFixed(2))
                    },
                    coverage: {
                        with_images: stats.with_images,
                        image_coverage_pct: Number.parseFloat((stats.with_images / stats.total_products * 100).toFixed(2)),
                        with_adjustments: stats.with_adjustments,
                        adjustments_pct: Number.parseFloat((stats.with_adjustments / stats.total_products * 100).toFixed(2))
                    }
                };
            });

        // Ordenar por total de produtos
        categories.sort((a, b) => b.total_products - a.total_products);

        const summary = {
            total_categories: categories.length,
            total_products: enrichedData.length,
            avg_products_per_category: Number.parseFloat((enrichedData.length / categories.length).toFixed(2))
        };

        res.json({
            success: true,
            data: {
                categories,
                summary
            },
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('[Gateway] Categories error:', error);
        error.statusCode = error.statusCode || 500;
        next(error);
    }
};
