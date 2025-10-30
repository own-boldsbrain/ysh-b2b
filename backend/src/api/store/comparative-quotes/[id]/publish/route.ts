import type {
  AuthenticatedMedusaRequest,
  MedusaResponse,
} from "@medusajs/framework/http";
import { z } from "zod";
import { COMPARATIVE_QUOTE_MODULE } from "src/modules/comparative-quote";

/**
 * Schema de validação para publicação
 */
const PublishComparativeQuoteSchema = z.object({
  notify_suppliers: z.boolean().optional().default(true),
  trigger_scrapers: z.boolean().optional().default(true),
}).optional();

/**
 * POST /store/comparative-quotes/:id/publish
 * 
 * Publica requisição de cotação e dispara coleta de preços
 * 
 * Workflow:
 * 1. Valida que requisição está em "draft"
 * 2. Muda status para "published"
 * 3. (Opcional) Notifica fornecedores convidados
 * 4. (Opcional) Dispara scrapers para coleta automática de preços
 * 
 * Body:
 * - notify_suppliers: boolean (padrão: true) - Enviar notificações para fornecedores
 * - trigger_scrapers: boolean (padrão: true) - Disparar web scrapers automaticamente
 */
export const POST = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const validation = PublishComparativeQuoteSchema.safeParse(req.body || {});

  if (!validation.success) {
    return res.status(400).json({
      error: "Invalid input",
      details: validation.error.errors,
    });
  }

  const comparativeQuoteService = req.scope.resolve(COMPARATIVE_QUOTE_MODULE);
  const { id } = req.params;

  try {
    const request = await comparativeQuoteService.publishRequest(id, validation.data);

    // Disparar coleta de respostas (scrapers)
    let collectionStatus = "not_triggered";
    if (validation.data?.trigger_scrapers) {
      try {
        await comparativeQuoteService.collectResponses(id);
        collectionStatus = "triggered";
      } catch (error) {
        console.error("Erro ao disparar scrapers:", error);
        collectionStatus = "error";
      }
    }

    res.json({
      comparative_quote_request: request,
      message: `Requisição ${request.request_number} publicada com sucesso`,
      scraper_collection_status: collectionStatus,
      next_steps: [
        "1. Scrapers estão coletando preços dos fornecedores convidados",
        "2. Aguardar respostas até o deadline",
        `3. Acessar /comparative-quotes/${id}/comparison para ver análise`,
      ],
    });
  } catch (error) {
    res.status(500).json({
      error: "Failed to publish comparative quote request",
      message: error.message,
    });
  }
};
