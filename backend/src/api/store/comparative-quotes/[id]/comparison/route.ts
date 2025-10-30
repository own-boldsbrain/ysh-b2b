import type {
  AuthenticatedMedusaRequest,
  MedusaResponse,
} from "@medusajs/framework/http";
import { z } from "zod";
import { COMPARATIVE_QUOTE_MODULE } from "src/modules/comparative-quote";

/**
 * Schema de validação para geração de comparação
 */
const GenerateComparisonSchema = z.object({
  base_markup: z.number().min(15).max(50).optional(),
  force_reevaluation: z.boolean().optional().default(false),
}).optional();

/**
 * GET /store/comparative-quotes/:id/comparison
 * 
 * Gera análise comparativa entre fornecedores
 * 
 * Retorna:
 * - Estatísticas de preços (média, mínimo, máximo, spread)
 * - Ranking de fornecedores por score
 * - Melhor fornecedor recomendado
 * - Análise de trade-offs (preço vs qualidade vs prazo)
 * - Preços finais com markup e ajustes de canal aplicados
 * - Margem e rentabilidade de cada opção
 * 
 * Query params:
 * - base_markup: Markup base percentual (15-50%, padrão varia por cenário)
 * - force_reevaluation: Forçar reavaliação de todas as cotações
 */
export const GET = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const validation = GenerateComparisonSchema.safeParse(req.query || {});

  if (!validation.success) {
    return res.status(400).json({
      error: "Invalid query parameters",
      details: validation.error.errors,
    });
  }

  const comparativeQuoteService = req.scope.resolve(COMPARATIVE_QUOTE_MODULE);
  const { id } = req.params;

  try {
    const comparison = await comparativeQuoteService.generateComparison(
      id,
      validation.data
    );

    res.json({
      comparison,
      message: `Análise comparativa gerada para requisição ${comparison.request_number}`,
      summary: {
        total_suppliers: comparison.total_quotes,
        best_supplier: comparison.best_supplier.supplier_name,
        best_score: comparison.best_supplier.score,
        price_spread: `${comparison.price_statistics.spread_percent.toFixed(1)}%`,
        recommended_margin: `${comparison.best_supplier.margin.toFixed(1)}%`,
      },
    });
  } catch (error) {
    res.status(500).json({
      error: "Failed to generate comparison",
      message: error.message,
    });
  }
};

/**
 * POST /store/comparative-quotes/:id/comparison
 * 
 * Força geração de nova análise comparativa
 * 
 * Útil quando:
 * - Novas cotações foram submetidas
 * - Critérios de avaliação foram alterados
 * - Markup base precisa ser recalculado
 */
export const POST = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const validation = GenerateComparisonSchema.safeParse(req.body || {});

  if (!validation.success) {
    return res.status(400).json({
      error: "Invalid input",
      details: validation.error.errors,
    });
  }

  const comparativeQuoteService = req.scope.resolve(COMPARATIVE_QUOTE_MODULE);
  const { id } = req.params;

  try {
    // Forçar reavaliação de todas as cotações
    const comparison = await comparativeQuoteService.generateComparison(id, {
      ...validation.data,
      force_reevaluation: true,
    });

    res.json({
      comparison,
      message: "Nova análise comparativa gerada com sucesso",
      regenerated_at: new Date(),
    });
  } catch (error) {
    res.status(500).json({
      error: "Failed to regenerate comparison",
      message: error.message,
    });
  }
};
