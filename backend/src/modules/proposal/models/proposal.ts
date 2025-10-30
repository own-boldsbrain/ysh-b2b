import { model } from "@medusajs/framework/utils";

/**
 * Proposal - Propostas Comerciais
 * 
 * Documenta propostas técnico-comerciais para clientes
 * com todos os cálculos, especificações e termos
 */
export const Proposal = model.define("proposal", {
  id: model.id({ prefix: "prop" }).primaryKey(),
  
  // Relacionamentos
  customer_id: model.text(),
  quote_id: model.text().nullable(),
  calculation_id: model.text().nullable(), // Link para solar calculation
  
  // Identificação
  proposal_number: model.text(), // PROP-2025-001
  title: model.text(),
  version: model.number().default(1),
  
  // Status
  status: model.enum([
    "draft",
    "pending_review",
    "sent",
    "viewed",
    "accepted",
    "rejected",
    "expired"
  ]).default("draft"),
  
  // Validade
  valid_until: model.dateTime(),
  valid_days: model.number().default(30),
  
  // Sistema Solar
  system_data: model.json(), // { kwp, panels, inverters, generation, etc }
  
  // Financeiro
  financial_data: model.json(), // { capex, opex, roi, payback, etc }
  
  // Itens (produtos)
  items: model.json(), // Array de produtos com preços
  
  // Totais
  subtotal: model.bigNumber(),
  discount_total: model.bigNumber().default(0),
  tax_total: model.bigNumber().default(0),
  shipping_total: model.bigNumber().default(0),
  installation_total: model.bigNumber().default(0),
  total: model.bigNumber(),
  
  // Termos e Condições
  payment_terms: model.text().nullable(),
  delivery_terms: model.text().nullable(),
  warranty_terms: model.text().nullable(),
  notes: model.text().nullable(),
  
  // Documentos Gerados
  pdf_url: model.text().nullable(),
  pdf_generated_at: model.dateTime().nullable(),
  
  // Metadata
  sent_at: model.dateTime().nullable(),
  viewed_at: model.dateTime().nullable(),
  accepted_at: model.dateTime().nullable(),
  rejected_at: model.dateTime().nullable(),
  rejection_reason: model.text().nullable(),
  
  // Assinatura
  signed_by: model.text().nullable(),
  signed_at: model.dateTime().nullable(),
  signature_url: model.text().nullable(),
  
  // Audit
  created_by: model.text().nullable(),
  updated_by: model.text().nullable(),
});
