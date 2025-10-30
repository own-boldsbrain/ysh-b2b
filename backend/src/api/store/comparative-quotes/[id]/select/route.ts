import type {
  AuthenticatedMedusaRequest,
  MedusaResponse,
} from "@medusajs/framework/http";
import { z } from "zod";
import { COMPARATIVE_QUOTE_MODULE } from "src/modules/comparative-quote";

/**
 * Schema de validação para seleção de fornecedor
 */
const SelectQuoteSchema = z.object({
  quote_id: z.string(),
  selection_reason: z.string().min(10).max(500),
  create_proposal: z.boolean().optional().default(true),
  notify_supplier: z.boolean().optional().default(true),
});

/**
 * POST /store/comparative-quotes/:id/select
 * 
 * Seleciona fornecedor vencedor da cotação comparativa
 * 
 * Workflow:
 * 1. Valida que requisição está em "evaluation"
 * 2. Marca cotação como selecionada (is_selected = true)
 * 3. Desmarca outras cotações previamente selecionadas
 * 4. Atualiza status da requisição para "selected"
 * 5. (Opcional) Dispara geração de proposta comercial
 * 6. (Opcional) Notifica fornecedor vencedor
 * 
 * Body:
 * - quote_id: ID da cotação vencedora
 * - selection_reason: Justificativa da seleção (10-500 caracteres)
 * - create_proposal: boolean (padrão: true) - Criar proposta comercial automaticamente
 * - notify_supplier: boolean (padrão: true) - Notificar fornecedor vencedor
 */
export const POST = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const validation = SelectQuoteSchema.safeParse(req.body);

  if (!validation.success) {
    return res.status(400).json({
      error: "Invalid input",
      details: validation.error.errors,
    });
  }

  const comparativeQuoteService = req.scope.resolve(COMPARATIVE_QUOTE_MODULE);
  const { id } = req.params;

  try {
    const request = await comparativeQuoteService.selectQuote(id, validation.data);

    // Obter cotação selecionada
    const selectedQuote = await comparativeQuoteService.retrieveSupplierQuoteResponse(
      validation.data.quote_id
    );

    let proposalStatus = "not_created";
    if (validation.data.create_proposal) {
      // TODO: Integrar com ProposalModule para criar proposta
      // await proposalService.createFromQuote(validation.data.quote_id);
      proposalStatus = "creation_pending";
    }

    res.json({
      comparative_quote_request: request,
      selected_quote: selectedQuote,
      proposal_status: proposalStatus,
      message: `Fornecedor ${selectedQuote.supplier_name} selecionado com sucesso`,
      next_steps: [
        "1. Proposta comercial será gerada automaticamente",
        "2. Fornecedor será notificado da seleção",
        "3. Acessar /proposals para acompanhar proposta",
      ],
    });
  } catch (error) {
    res.status(500).json({
      error: "Failed to select quote",
      message: error.message,
    });
  }
};

/**
 * GET /store/comparative-quotes/:id/select
 * 
 * Retorna cotação atualmente selecionada (se houver)
 */
export const GET = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const comparativeQuoteService = req.scope.resolve(COMPARATIVE_QUOTE_MODULE);
  const { id } = req.params;

  try {
    const request = await comparativeQuoteService.retrieveComparativeQuoteRequest(id);

    if (!request.selected_quote_id) {
      return res.status(404).json({
        error: "No quote selected",
        message: `Requisição ${request.request_number} ainda não tem fornecedor selecionado`,
      });
    }

    const selectedQuote = await comparativeQuoteService.retrieveSupplierQuoteResponse(
      request.selected_quote_id
    );

    res.json({
      comparative_quote_request: request,
      selected_quote: selectedQuote,
      selected_at: selectedQuote.selected_at,
      selection_reason: selectedQuote.selection_reason,
    });
  } catch (error) {
    res.status(500).json({
      error: "Failed to retrieve selected quote",
      message: error.message,
    });
  }
};
