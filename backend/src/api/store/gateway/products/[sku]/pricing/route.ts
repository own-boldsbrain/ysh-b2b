/**
 * YSH B2B Store Gateway - Pricing Comparison Endpoint
 * Compara preços de um SKU entre distribuidores
 * 
 * @standard Facebook Commerce Platform Compatible
 */

import { Request, Response, NextFunction } from 'express';
import fs from 'node:fs/promises';
import path from 'node:path';
import { formatDecimal } from '../../../utils';

/**
 * GET /store/gateway/products/:sku/pricing
 * Compara preços entre distribuidores para um SKU
 */
export const GET = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const { sku } = req.params;

        if (!sku) {
            const error: any = new Error("SKU parameter is required");
            error.statusCode = 400;
            throw error;
        }

        // Carregar dados de comparação de preços
        const comparisonPath = path.join(process.cwd(), 'distributor-price-comparison.json');
        const comparisonData = JSON.parse(await fs.readFile(comparisonPath, 'utf-8'));

        // Buscar produto específico
        const product = comparisonData.products.find((p: any) => p.sku === sku.toUpperCase());

        if (!product) {
            return res.status(404).json({
                success: false,
                error: "Product pricing comparison not found",
                sku: sku.toUpperCase()
            });
        }

        // Calcular estatísticas
        const offers = product.offers;
        const prices = offers.map((o: any) => o.price);
        const minPrice = Math.min(...prices);
        const maxPrice = Math.max(...prices);
        const avgPrice = prices.reduce((sum: number, p: number) => sum + p, 0) / prices.length;
        const variation = ((maxPrice - minPrice) / minPrice) * 100;

        // Ranquear ofertas
        const rankedOffers = offers.map((offer: any, index: number) => ({
            ...offer,
            rank: index + 1,
            is_best: offer.price === minPrice,
            is_worst: offer.price === maxPrice,
            diff_from_best_pct: ((offer.price - minPrice) / minPrice) * 100,
            diff_from_avg_pct: ((offer.price - avgPrice) / avgPrice) * 100
        }));

        res.json({
            success: true,
            data: {
                sku: product.sku,
                category: product.category,
                manufacturer: product.manufacturer,
                comparison: {
                    total_offers: offers.length,
                    best_price: minPrice,
                    worst_price: maxPrice,
                    average_price: formatDecimal(avgPrice),
                    variation_pct: formatDecimal(variation),
                    savings_potential: formatDecimal(maxPrice - minPrice)
                },
                offers: rankedOffers,
                distributors: offers.map((o: any) => o.distributor),
                recommendation: {
                    best_offer: rankedOffers.find((o: any) => o.is_best),
                    savings: formatDecimal((maxPrice - minPrice) / maxPrice * 100) + '% ao escolher melhor oferta'
                }
            },
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('[Gateway] Pricing comparison error:', error);
        
        // Se arquivo não existir, sugerir alternativa
        if (error.code === 'ENOENT') {
            return res.status(503).json({
                success: false,
                error: "Pricing comparison data not available",
                message: "Run generate-distributor-price-comparison.js to generate comparison data",
                sku: req.params.sku
            });
        }

        error.statusCode = error.statusCode || 500;
        next(error);
    }
};
