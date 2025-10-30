/**
 * YSH B2B Store Gateway - Product Detail Endpoint
 * Retorna detalhes completos de um produto com estratégia de precificação
 * 
 * @standard Facebook Commerce Platform Compatible
 */

import { Request, Response, NextFunction } from 'express';
import { loadEnrichedData } from "../../route";
import { extractCategoryFromSKU } from "../../utils";

/**
 * GET /store/gateway/products/:sku
 * Retorna detalhes completos de um produto
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

        const enrichedData = await loadEnrichedData();
        const product = enrichedData.find((p: any) => p.sku === sku.toUpperCase());

        if (!product) {
            return res.status(404).json({
                success: false,
                error: "Product not found",
                sku: sku.toUpperCase()
            });
        }

        // Extrair categoria do SKU
        const category = extractCategoryFromSKU(product.sku);

        res.json({
            success: true,
            data: {
                // Informações básicas
                sku: product.sku,
                category,
                cost_price: product.cost_price,
                final_price: product.final_price,
                
                // Estratégia de precificação completa
                pricing_strategy: {
                    dynamic_markup: {
                        cost_price: product.dynamic_markup.costPrice,
                        base_markup: product.dynamic_markup.baseMarkup,
                        adjustment: product.dynamic_markup.adjustment,
                        final_markup: product.dynamic_markup.finalMarkup,
                        selling_price: product.dynamic_markup.sellingPrice,
                        gross_margin: product.dynamic_markup.grossMargin,
                        net_margin: product.dynamic_markup.netMargin,
                        scenario: product.dynamic_markup.scenario
                    },
                    adjustments: {
                        time: product.dynamic_adjustments.time_adjustment,
                        inventory: product.dynamic_adjustments.inventory_adjustment,
                        competition: product.dynamic_adjustments.competition_adjustment,
                        segment: product.dynamic_adjustments.segment_adjustment,
                        urgency: product.dynamic_adjustments.urgency_adjustment,
                        total: product.dynamic_adjustments.total_adjustment,
                        active: product.dynamic_adjustments.total_adjustment !== 0
                    },
                    channel_pricing: {
                        base_price: product.channel_pricing.basePrice,
                        channel: product.channel_pricing.channel,
                        discount: product.channel_pricing.discount,
                        channel_price: product.channel_pricing.channelPrice,
                        commission: product.channel_pricing.commission
                    },
                    psychological: {
                        charm_applied: product.psychological_pricing.charm_applied,
                        original_price: product.dynamic_markup.sellingPrice,
                        charm_price: product.final_price
                    }
                },

                // Score de preço competitivo
                price_score: {
                    category: product.price_score.category,
                    delta: product.price_score.delta,
                    best_price: product.price_score.bestPrice,
                    explanation: product.price_score.explanation
                },

                // Splits de projeto para orçamentos
                project_splits: product.project_splits,

                // KPIs e confiança
                kpis: product.kpis || {},

                // Imagens
                images: product.images || [],

                // Metadata adicional
                metadata: {
                    has_dynamic_adjustments: product.dynamic_adjustments.total_adjustment !== 0,
                    pricing_scenario: product.dynamic_markup.scenario,
                    channel: product.channel_pricing.channel,
                    is_charm_priced: product.psychological_pricing.charm_applied
                }
            },
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('[Gateway] Product detail error:', error);
        error.statusCode = error.statusCode || 500;
        next(error);
    }
};
