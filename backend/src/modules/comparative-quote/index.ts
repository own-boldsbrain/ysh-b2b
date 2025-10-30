/**
 * Comparative Quote Module
 * 
 * Sistema de cotação comparativa que permite:
 * - Solicitar cotações de múltiplos fornecedores
 * - Comparar ofertas lado a lado
 * - Analisar melhor custo-benefício
 * - Negociar condições
 */

import { Module } from "@medusajs/framework/utils";
import ComparativeQuoteModuleService from "./service";

export const COMPARATIVE_QUOTE_MODULE = "comparative_quote";

export default Module(COMPARATIVE_QUOTE_MODULE, { 
  service: ComparativeQuoteModuleService 
});
