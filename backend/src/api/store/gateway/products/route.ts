/**
 * YSH B2B Store Gateway - Products Endpoint
 * Lista produtos com precificação dinâmica e filtros avançados
 * 
 * @standard Facebook Commerce Platform Compatible
 */

import { Request, Response, NextFunction } from 'express';
import { loadEnrichedData } from "../route";
import { extractCategoryFromSKU, formatDecimal } from "../utils";

interface ProductQueryParams {
    category?: string;
    manufacturer?: string;
    min_price?: number;
    max_price?: number;
    limit?: number;
    offset?: number;
    sort?: 'price' | 'margin' | 'sku';
    order?: 'asc' | 'desc';
    scenario?: 'neutro' | 'agressivo' | 'premium';
}

/**
 * GET /store/gateway/products
 * Lista produtos com precificação dinâmica
 */
export const GET = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const {
            category,
            manufacturer,
            min_price,
            max_price,
            limit = 50,
            offset = 0,
            sort = 'sku',
            order = 'asc',
            scenario
        } = req.query as ProductQueryParams;

        const enrichedData = await loadEnrichedData();

        // Aplicar filtros
        let filtered = enrichedData.filter((product: any) => {
            const skuCategory = extractCategoryFromSKU(product.sku);
            
            const matchesCategory = !category || skuCategory === category.toLowerCase();
            const matchesMinPrice = !min_price || product.final_price >= min_price;
            const matchesMaxPrice = !max_price || product.final_price <= max_price;
            const matchesScenario = !scenario || product.dynamic_markup.scenario === scenario;
            const matchesManufacturer = !manufacturer || product.sku.toUpperCase().includes(manufacturer.toUpperCase());

            return matchesCategory && matchesMinPrice && matchesMaxPrice && matchesScenario && matchesManufacturer;
        });

        // Ordenação
        filtered.sort((a: any, b: any) => {
            let comparison = 0;
            switch (sort) {
                case 'price':
                    comparison = a.final_price - b.final_price;
                    break;
                case 'margin':
                    comparison = a.dynamic_markup.netMargin - b.dynamic_markup.netMargin;
                    break;
                case 'sku':
                default:
                    comparison = a.sku.localeCompare(b.sku);
            }
            return order === 'desc' ? -comparison : comparison;
        });

        // Paginação
        const total = filtered.length;
        const paginated = filtered.slice(offset, offset + limit);

        // Formatar resposta
        const products = paginated.map((product: any) => ({
            sku: product.sku,
            cost_price: product.cost_price,
            final_price: product.final_price,
            pricing: {
                base_markup: product.dynamic_markup.baseMarkup,
                adjustment: product.dynamic_markup.adjustment,
                final_markup: product.dynamic_markup.finalMarkup,
                gross_margin: product.dynamic_markup.grossMargin,
                net_margin: product.dynamic_markup.netMargin,
                scenario: product.dynamic_markup.scenario,
            },
            channel: {
                channel: product.channel_pricing.channel,
                discount: product.channel_pricing.discount,
                channel_price: product.channel_pricing.channelPrice,
                commission: product.channel_pricing.commission,
            },
            features: {
                charm_pricing: product.psychological_pricing.charm_applied,
                has_adjustments: product.dynamic_adjustments.total_adjustment !== 0,
            },
            kpis: product.kpis || {},
            // Adicionar imagens se disponíveis
            images: product.images || [],
            // Project splits para orçamentos
            project_splits: product.project_splits
        }));

        // Estatísticas da consulta
        const avgPrice = products.length > 0 ? products.reduce((sum: number, p: any) => sum + p.final_price, 0) / products.length : 0;
        const avgMargin = products.length > 0 ? products.reduce((sum: number, p: any) => sum + p.pricing.net_margin, 0) / products.length : 0;
        
        const stats = {
            avg_price: formatDecimal(avgPrice),
            avg_margin: formatDecimal(avgMargin),
            price_range: {
                min: Math.min(...products.map((p: any) => p.final_price)),
                max: Math.max(...products.map((p: any) => p.final_price))
            }
        };

        res.json({
            success: true,
            data: {
                products,
                count: total,
                limit,
                offset,
                has_more: offset + limit < total,
                stats
            },
            query: {
                category,
                manufacturer,
                min_price,
                max_price,
                scenario,
                sort,
                order
            },
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('[Gateway] Products error:', error);
        error.statusCode = error.statusCode || 500;
        next(error);
    }
};
