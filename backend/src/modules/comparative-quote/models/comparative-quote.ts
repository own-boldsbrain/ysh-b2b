import { model } from "@medusajs/framework/utils";

/**
 * Comparative Quote Request
 * 
 * Solicitação de cotação enviada para múltiplos fornecedores
 */
export const ComparativeQuoteRequest = model.define("comparative_quote_request", {
  id: model.id({ prefix: "cqr" }).primaryKey(),
  
  // Identificação
  request_number: model.text(), // CQR-2025-001
  title: model.text(),
  description: model.text().nullable(),
  
  // Cliente
  customer_id: model.text(),
  company_id: model.text().nullable(),
  
  // Status
  status: model.enum([
    "draft",
    "published",
    "receiving_quotes",
    "evaluation",
    "selected",
    "closed",
    "cancelled"
  ]).default("draft"),
  
  // Prazos
  published_at: model.dateTime().nullable(),
  deadline: model.dateTime(),
  evaluation_ends_at: model.dateTime().nullable(),
  
  // Especificações Técnicas
  technical_specs: model.json(), // Sistema solar desejado
  
  // Itens Solicitados
  items: model.json(), // Array de produtos/serviços
  
  // Critérios de Avaliação
  evaluation_criteria: model.json(), // { price: 40%, quality: 30%, delivery: 20%, warranty: 10% }
  
  // Fornecedores Convidados
  invited_suppliers: model.json(), // Array de supplier_ids
  
  // Metadata
  project_type: model.text().nullable(), // 'residential', 'commercial', 'industrial'
  location: model.json().nullable(),
  budget_range: model.json().nullable(), // { min, max }
  
  // Seleção
  selected_quote_id: model.text().nullable(),
  selection_reason: model.text().nullable(),
  selected_at: model.dateTime().nullable(),
});

/**
 * Supplier Quote Response
 * 
 * Resposta de um fornecedor à solicitação de cotação
 */
export const SupplierQuoteResponse = model.define("supplier_quote_response", {
  id: model.id({ prefix: "sqr" }).primaryKey(),
  
  // Relacionamentos
  request_id: model.text(),
  supplier_id: model.text(),
  supplier_name: model.text(),
  
  // Status
  status: model.enum([
    "invited",
    "viewed",
    "in_progress",
    "submitted",
    "under_review",
    "accepted",
    "rejected",
    "withdrawn"
  ]).default("invited"),
  
  // Prazos
  invited_at: model.dateTime(),
  viewed_at: model.dateTime().nullable(),
  submitted_at: model.dateTime().nullable(),
  
  // Oferta
  items: model.json(), // Array de itens com preços
  
  // Totais
  subtotal: model.bigNumber().default(0),
  discount_total: model.bigNumber().default(0),
  tax_total: model.bigNumber().default(0),
  shipping_total: model.bigNumber().default(0),
  installation_total: model.bigNumber().default(0),
  total: model.bigNumber().default(0),
  
  // Termos
  payment_terms: model.text().nullable(),
  delivery_days: model.number().nullable(),
  warranty_months: model.number().nullable(),
  additional_terms: model.text().nullable(),
  
  // Documentos
  proposal_pdf_url: model.text().nullable(),
  technical_datasheet_url: model.text().nullable(),
  certificates_urls: model.json().nullable(),
  
  // Avaliação
  score: model.number().nullable(), // 0-100
  evaluation_notes: model.text().nullable(),
  
  // Seleção
  is_selected: model.boolean().default(false),
  rejection_reason: model.text().nullable(),
});
