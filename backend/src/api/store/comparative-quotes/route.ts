import type {
  AuthenticatedMedusaRequest,
  MedusaRequest,
  MedusaResponse,
} from "@medusajs/framework/http";
import { z } from "zod";
import { COMPARATIVE_QUOTE_MODULE } from "src/modules/comparative-quote";

/**
 * GET /store/comparative-quotes
 * 
 * Lista requisições de cotação comparativa
 * 
 * Query params:
 * - customer_id: Filtrar por cliente
 * - status: Filtrar por status
 * - limit: Limite de resultados
 * - offset: Paginação
 */
export const GET = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const comparativeQuoteService = req.scope.resolve(COMPARATIVE_QUOTE_MODULE);

  const { customer_id, status, limit = 20, offset = 0 } = req.query;

  const filters: any = {};
  if (customer_id) filters.customer_id = customer_id;
  if (status) filters.status = status;

  const requests = await comparativeQuoteService.listComparativeQuoteRequest({
    filters,
    config: {
      take: Number(limit),
      skip: Number(offset),
    },
  });

  res.json({
    comparative_quote_requests: requests,
    count: requests.length,
    limit: Number(limit),
    offset: Number(offset),
  });
};

/**
 * Schema de validação para criação de requisição
 */
const CreateComparativeQuoteSchema = z.object({
  customer_id: z.string(),
  customer_type: z.enum(["b2c", "integrator_b2b", "distributor", "marketplace", "white_label"]),
  region: z.enum(["nordeste", "centro_oeste", "sudeste", "norte", "sul"]),
  monthly_consumption_kwh: z.number().min(100).max(1000000),
  generation_tier: z.enum(["moderado", "consciente", "acelerado", "ultra"]).optional(),
  
  technical_specifications: z.object({
    roof_type: z.enum(["ceramica", "metalico", "laje", "fibrocimento"]).optional(),
    building_type: z.enum(["residential", "commercial", "industrial", "rural"]).optional(),
    roof_area_m2: z.number().optional(),
    voltage: z.enum(["127V", "220V", "380V"]).optional(),
    connection_type: z.enum(["monofasico", "bifasico", "trifasico"]).optional(),
    special_requirements: z.string().optional(),
  }).optional(),

  evaluation_criteria: z.object({
    price_weight: z.number().min(0).max(1).optional(),
    quality_weight: z.number().min(0).max(1).optional(),
    delivery_weight: z.number().min(0).max(1).optional(),
    warranty_weight: z.number().min(0).max(1).optional(),
  }).optional(),

  invited_suppliers: z.array(z.string()).min(1).max(7),
  
  deadline: z.string().datetime().optional(),
  
  metadata: z.record(z.any()).optional(),
});

/**
 * POST /store/comparative-quotes
 * 
 * Cria nova requisição de cotação comparativa multi-fornecedor
 * 
 * Body:
 * - customer_id: ID do cliente
 * - customer_type: b2c, integrator_b2b, distributor, marketplace, white_label
 * - region: nordeste, centro_oeste, sudeste, norte, sul
 * - monthly_consumption_kwh: Consumo mensal em kWh
 * - generation_tier: moderado, consciente (padrão), acelerado, ultra
 * - technical_specifications: Especificações técnicas do projeto
 * - evaluation_criteria: Pesos para avaliação (price, quality, delivery, warranty)
 * - invited_suppliers: Array de fornecedores convidados (edeltec, fortlev, odex, solfacil, fotus, dynamis, neosolar)
 * 
 * Retorna:
 * - Requisição criada com número CQR-YYYY-####
 * - Potência estimada calculada
 * - Categoria do projeto (XPP, PP, P, M, G, XG, XXG)
 */
export const POST = async (
  req: AuthenticatedMedusaRequest,
  res: MedusaResponse
) => {
  const validation = CreateComparativeQuoteSchema.safeParse(req.body);

  if (!validation.success) {
    return res.status(400).json({
      error: "Invalid input",
      details: validation.error.errors,
    });
  }

  const comparativeQuoteService = req.scope.resolve(COMPARATIVE_QUOTE_MODULE);

  try {
    const request = await comparativeQuoteService.createRequest(validation.data);

    res.status(201).json({
      comparative_quote_request: request,
      message: `Requisição ${request.request_number} criada com sucesso`,
      next_steps: [
        `1. Revisar requisição em /comparative-quotes/${request.id}`,
        "2. Publicar requisição para disparar scrapers",
        "3. Aguardar coleta de cotações dos fornecedores",
        "4. Analisar comparação e selecionar vencedor",
      ],
    });
  } catch (error) {
    res.status(500).json({
      error: "Failed to create comparative quote request",
      message: error.message,
    });
  }
};
