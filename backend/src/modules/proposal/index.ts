/**
 * Proposal Module
 * 
 * Geração de propostas comerciais profissionais em PDF
 * com cálculos técnicos, financeiros e documentação completa
 */

import { Module } from "@medusajs/framework/utils";
import ProposalModuleService from "./service";

export const PROPOSAL_MODULE = "proposal";

export default Module(PROPOSAL_MODULE, { service: ProposalModuleService });
