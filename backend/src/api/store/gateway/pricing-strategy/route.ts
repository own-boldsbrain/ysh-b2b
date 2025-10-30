/**
 * YSH B2B Store Gateway - Pricing Strategy Endpoint
 * Retorna análise completa da estratégia de precificação
 * 
 * @standard Facebook Commerce Platform Compatible
 */

import { Request, Response, NextFunction } from 'express';
import { loadEnrichedData } from "../route";
import { formatDecimal } from "../utils";

/**
 * GET /store/gateway/pricing-strategy
 * Análise completa da estratégia de precificação dinâmica
 */
export const GET = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const enrichedData = await loadEnrichedData();

        // Calcular métricas gerais
        const totalProducts = enrichedData.length;
        const avgFinalMarkup = enrichedData.reduce((sum: number, p: any) => sum + p.dynamic_markup.finalMarkup, 0) / totalProducts;
        const avgGrossMargin = enrichedData.reduce((sum: number, p: any) => sum + p.dynamic_markup.grossMargin, 0) / totalProducts;
        const avgNetMargin = enrichedData.reduce((sum: number, p: any) => sum + p.dynamic_markup.netMargin, 0) / totalProducts;
        
        const withCharmPricing = enrichedData.filter((p: any) => p.psychological_pricing.charm_applied).length;
        const withAdjustments = enrichedData.filter((p: any) => p.dynamic_adjustments.total_adjustment !== 0).length;

        // Análise por cenário
        const scenarioStats = new Map<string, {
            scenario: string;
            count: number;
            avg_markup: number;
            avg_gross_margin: number;
            avg_net_margin: number;
        }>();

        for (const product of enrichedData) {
            const scenario = product.dynamic_markup.scenario;
            if (!scenarioStats.has(scenario)) {
                scenarioStats.set(scenario, {
                    scenario,
                    count: 0,
                    avg_markup: 0,
                    avg_gross_margin: 0,
                    avg_net_margin: 0
                });
            }
            const stats = scenarioStats.get(scenario)!;
            stats.count++;
            stats.avg_markup += product.dynamic_markup.finalMarkup;
            stats.avg_gross_margin += product.dynamic_markup.grossMargin;
            stats.avg_net_margin += product.dynamic_markup.netMargin;
        }

        const scenarios = Array.from(scenarioStats.values()).map(stats => ({
            scenario: stats.scenario,
            products: stats.count,
            percentage: formatDecimal(stats.count / totalProducts * 100),
            avg_markup: formatDecimal(stats.avg_markup / stats.count),
            avg_gross_margin: formatDecimal(stats.avg_gross_margin / stats.count),
            avg_net_margin: formatDecimal(stats.avg_net_margin / stats.count)
        }));

        // Distribuição de categorias de preço
        const priceCategories = {
            competitive: enrichedData.filter((p: any) => p.price_score.category === 'competitive').length,
            average: enrichedData.filter((p: any) => p.price_score.category === 'average').length,
            premium: enrichedData.filter((p: any) => p.price_score.category === 'premium').length
        };

        // Top 10 produtos por margem
        const topMarginProducts = enrichedData
            .sort((a: any, b: any) => b.dynamic_markup.netMargin - a.dynamic_markup.netMargin)
            .slice(0, 10)
            .map((p: any) => ({
                sku: p.sku,
                net_margin: p.dynamic_markup.netMargin,
                gross_margin: p.dynamic_markup.grossMargin,
                final_price: p.final_price,
                scenario: p.dynamic_markup.scenario
            }));

        // Bottom 10 produtos por margem
        const lowMarginProducts = enrichedData
            .sort((a: any, b: any) => a.dynamic_markup.netMargin - b.dynamic_markup.netMargin)
            .slice(0, 10)
            .map((p: any) => ({
                sku: p.sku,
                net_margin: p.dynamic_markup.netMargin,
                gross_margin: p.dynamic_markup.grossMargin,
                final_price: p.final_price,
                scenario: p.dynamic_markup.scenario
            }));

        // Análise de ajustes dinâmicos
        const adjustmentTypes = {
            time: enrichedData.filter((p: any) => p.dynamic_adjustments.time_adjustment !== 0).length,
            inventory: enrichedData.filter((p: any) => p.dynamic_adjustments.inventory_adjustment !== 0).length,
            competition: enrichedData.filter((p: any) => p.dynamic_adjustments.competition_adjustment !== 0).length,
            segment: enrichedData.filter((p: any) => p.dynamic_adjustments.segment_adjustment !== 0).length,
            urgency: enrichedData.filter((p: any) => p.dynamic_adjustments.urgency_adjustment !== 0).length
        };

        res.json({
            success: true,
            data: {
                summary: {
                    total_products: totalProducts,
                    avg_final_markup: formatDecimal(avgFinalMarkup),
                    avg_gross_margin: formatDecimal(avgGrossMargin),
                    avg_net_margin: formatDecimal(avgNetMargin),
                    with_charm_pricing: withCharmPricing,
                    charm_pricing_pct: formatDecimal(withCharmPricing / totalProducts * 100),
                    with_adjustments: withAdjustments,
                    adjustments_pct: formatDecimal(withAdjustments / totalProducts * 100)
                },
                scenarios: {
                    analysis: scenarios,
                    distribution: {
                        total_scenarios: scenarios.length,
                        most_used: scenarios[0]?.scenario || 'N/A'
                    }
                },
                price_positioning: {
                    competitive: priceCategories.competitive,
                    average: priceCategories.average,
                    premium: priceCategories.premium,
                    distribution: {
                        competitive: formatDecimal(priceCategories.competitive / totalProducts * 100),
                        average: formatDecimal(priceCategories.average / totalProducts * 100),
                        premium: formatDecimal(priceCategories.premium / totalProducts * 100)
                    }
                },
                top_performers: {
                    highest_margin: topMarginProducts,
                    lowest_margin: lowMarginProducts
                },
                dynamic_adjustments: {
                    usage: adjustmentTypes,
                    total_active: withAdjustments,
                    recommendations: withAdjustments === 0 ? [
                        "Considere ativar ajustes dinâmicos para otimizar margens",
                        "Implemente ajustes de inventário para produtos de baixo giro",
                        "Configure ajustes de competição para produtos sensíveis a preço"
                    ] : []
                },
                recommendations: [
                    avgNetMargin < 15 ? "Considere aumentar markup base para melhorar margem líquida" : null,
                    withAdjustments === 0 ? "Ative ajustes dinâmicos para otimização automática" : null,
                    scenarios.length === 1 ? "Implemente múltiplos cenários (agressivo/premium) para segmentação" : null,
                    withCharmPricing / totalProducts < 0.95 ? "Aumente adoção de charm pricing para 100%" : null
                ].filter(r => r !== null)
            },
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('[Gateway] Pricing strategy error:', error);
        error.statusCode = error.statusCode || 500;
        next(error);
    }
};
