import type {
  AuthenticatedMedusaRequest,
  MedusaResponse,
} from "@medusajs/framework/http";
import { z } from "zod";
import { COMPARATIVE_QUOTE_MODULE } from "src/modules/comparative-quote";

/**
 * GET /store/comparative-quotes/:id
 * 
 * Obtém detalhes de uma requisição de cotação comparativa
 */
export const GET = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const comparativeQuoteService = req.scope.resolve(COMPARATIVE_QUOTE_MODULE);
  const { id } = req.params;

  try {
    const request = await comparativeQuoteService.retrieveComparativeQuoteRequest(id);

    // Obter cotações associadas
    const quotes = await comparativeQuoteService.listSupplierQuoteResponse({
      filters: { comparative_quote_request_id: id },
    });

    res.json({
      comparative_quote_request: request,
      supplier_quotes: quotes,
      quotes_count: quotes.length,
    });
  } catch (error) {
    res.status(404).json({
      error: "Comparative quote request not found",
      message: error.message,
    });
  }
};

/**
 * Schema para atualização de requisição
 */
const UpdateComparativeQuoteSchema = z.object({
  technical_specifications: z.record(z.any()).optional(),
  evaluation_criteria: z.record(z.any()).optional(),
  invited_suppliers: z.array(z.string()).optional(),
  deadline: z.string().datetime().optional(),
  metadata: z.record(z.any()).optional(),
});

/**
 * POST /store/comparative-quotes/:id
 * 
 * Atualiza requisição de cotação comparativa
 * 
 * Apenas permitido para requisições em status "draft"
 */
export const POST = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const validation = UpdateComparativeQuoteSchema.safeParse(req.body);

  if (!validation.success) {
    return res.status(400).json({
      error: "Invalid input",
      details: validation.error.errors,
    });
  }

  const comparativeQuoteService = req.scope.resolve(COMPARATIVE_QUOTE_MODULE);
  const { id } = req.params;

  try {
    const currentRequest = await comparativeQuoteService.retrieveComparativeQuoteRequest(id);

    if (currentRequest.status !== "draft") {
      return res.status(422).json({
        error: "Cannot update published request",
        message: `Requisição ${currentRequest.request_number} está em status "${currentRequest.status}"`,
      });
    }

    const updated = await comparativeQuoteService.updateComparativeQuoteRequest(
      id,
      validation.data
    );

    res.json({
      comparative_quote_request: updated,
      message: `Requisição ${updated.request_number} atualizada com sucesso`,
    });
  } catch (error) {
    res.status(500).json({
      error: "Failed to update comparative quote request",
      message: error.message,
    });
  }
};

/**
 * DELETE /store/comparative-quotes/:id
 * 
 * Cancela requisição de cotação comparativa
 * 
 * Muda status para "cancelled"
 */
export const DELETE = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const comparativeQuoteService = req.scope.resolve(COMPARATIVE_QUOTE_MODULE);
  const { id } = req.params;

  try {
    const request = await comparativeQuoteService.retrieveComparativeQuoteRequest(id);

    if (request.status === "closed" || request.status === "cancelled") {
      return res.status(422).json({
        error: "Request already closed or cancelled",
        message: `Requisição ${request.request_number} está em status final "${request.status}"`,
      });
    }

    const cancelled = await comparativeQuoteService.updateComparativeQuoteRequest(id, {
      status: "cancelled",
      updated_at: new Date(),
    });

    res.json({
      comparative_quote_request: cancelled,
      message: `Requisição ${cancelled.request_number} cancelada com sucesso`,
    });
  } catch (error) {
    res.status(500).json({
      error: "Failed to cancel comparative quote request",
      message: error.message,
    });
  }
};
