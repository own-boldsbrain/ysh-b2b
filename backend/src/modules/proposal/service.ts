import { MedusaService } from "@medusajs/framework/utils";
import { Proposal } from "./models/proposal";
import {
  CreateProposalDTO,
  UpdateProposalDTO,
  SendProposalDTO,
  AcceptProposalDTO,
  RejectProposalDTO,
  ProposalDTO,
  GeneratePDFOptions,
} from "./types";

class ProposalModuleService extends MedusaService({ Proposal }) {
  /**
   * Create Proposal
   */
  async createProposal(data: CreateProposalDTO): Promise<ProposalDTO> {
    const proposalNumber = await this.generateProposalNumber();
    
    const validUntil = new Date();
    validUntil.setDate(validUntil.getDate() + (data.valid_days || 30));
    
    // Calculate totals
    const subtotal = data.items.reduce((sum, item) => sum + item.subtotal, 0);
    const discountTotal = data.items.reduce((sum, item) => sum + item.discount_amount, 0);
    const taxTotal = data.items.reduce((sum, item) => sum + item.tax_amount, 0);
    const total = data.items.reduce((sum, item) => sum + item.total, 0);
    
    const proposal = await this.createProposal_({
      ...data,
      proposal_number: proposalNumber,
      valid_until: validUntil,
      subtotal,
      discount_total: discountTotal,
      tax_total: taxTotal,
      shipping_total: 0,
      installation_total: data.financial_data.capex.installation,
      total,
      status: "draft",
    });

    return this.toDTO(proposal);
  }

  /**
   * Update Proposal
   */
  async updateProposal(id: string, data: UpdateProposalDTO): Promise<ProposalDTO> {
    // Recalculate totals if items changed
    if (data.items) {
      const subtotal = data.items.reduce((sum, item) => sum + item.subtotal, 0);
      const discountTotal = data.items.reduce((sum, item) => sum + item.discount_amount, 0);
      const taxTotal = data.items.reduce((sum, item) => sum + item.tax_amount, 0);
      const total = data.items.reduce((sum, item) => sum + item.total, 0);
      
      data = {
        ...data,
        subtotal,
        discount_total: discountTotal,
        tax_total: taxTotal,
        total,
      } as any;
    }

    const proposal = await this.updateProposal_(id, data);
    return this.toDTO(proposal);
  }

  /**
   * Send Proposal
   */
  async sendProposal(data: SendProposalDTO): Promise<ProposalDTO> {
    const proposal = await this.retrieveProposal_(data.proposal_id, {
      relations: [],
    });

    if (!proposal) {
      throw new Error(`Proposal ${data.proposal_id} not found`);
    }

    // Generate PDF if not exists
    if (!proposal.pdf_url) {
      await this.generatePDF(data.proposal_id);
    }

    // TODO: Send email with PDF attachment
    // await this.emailService.send({
    //   to: data.recipient_email,
    //   subject: `Proposta ${proposal.proposal_number} - ${proposal.title}`,
    //   template: 'proposal',
    //   data: { proposal, message: data.message },
    //   attachments: [{ filename: 'proposta.pdf', path: proposal.pdf_url }]
    // })

    const updated = await this.updateProposal_(data.proposal_id, {
      status: "sent",
      sent_at: new Date(),
    });

    return this.toDTO(updated);
  }

  /**
   * Accept Proposal
   */
  async acceptProposal(data: AcceptProposalDTO): Promise<ProposalDTO> {
    const proposal = await this.updateProposal_(data.proposal_id, {
      status: "accepted",
      accepted_at: new Date(),
      signed_by: data.signed_by,
      signed_at: new Date(),
      signature_url: data.signature_data, // In production, upload to S3
    });

    // TODO: Trigger order creation workflow
    // await createOrderFromProposalWorkflow.run({ proposal_id: data.proposal_id })

    return this.toDTO(proposal);
  }

  /**
   * Reject Proposal
   */
  async rejectProposal(data: RejectProposalDTO): Promise<ProposalDTO> {
    const proposal = await this.updateProposal_(data.proposal_id, {
      status: "rejected",
      rejected_at: new Date(),
      rejection_reason: data.reason,
      notes: data.notes,
    });

    return this.toDTO(proposal);
  }

  /**
   * Generate PDF
   */
  async generatePDF(proposalId: string, options?: GeneratePDFOptions): Promise<string> {
    const proposal = await this.retrieveProposal_(proposalId, {
      relations: [],
    });

    if (!proposal) {
      throw new Error(`Proposal ${proposalId} not found`);
    }

    // TODO: Implement PDF generation with library (puppeteer, jsPDF, etc)
    // For now, return mock URL
    const pdfUrl = `/proposals/${proposalId}/proposal.pdf`;
    
    await this.updateProposal_(proposalId, {
      pdf_url: pdfUrl,
      pdf_generated_at: new Date(),
    });

    return pdfUrl;
  }

  /**
   * Mark as Viewed
   */
  async markViewed(proposalId: string): Promise<void> {
    const proposal = await this.retrieveProposal_(proposalId);
    
    if (!proposal.viewed_at) {
      await this.updateProposal_(proposalId, {
        status: "viewed",
        viewed_at: new Date(),
      });
    }
  }

  /**
   * Clone Proposal (New Version)
   */
  async cloneProposal(proposalId: string): Promise<ProposalDTO> {
    const original = await this.retrieveProposal_(proposalId, {
      relations: [],
    });

    if (!original) {
      throw new Error(`Proposal ${proposalId} not found`);
    }

    const newProposal = await this.createProposal({
      customer_id: original.customer_id,
      quote_id: original.quote_id,
      calculation_id: original.calculation_id,
      title: `${original.title} (v${original.version + 1})`,
      valid_days: original.valid_days,
      system_data: original.system_data as any,
      financial_data: original.financial_data as any,
      items: original.items as any,
      payment_terms: original.payment_terms,
      delivery_terms: original.delivery_terms,
      warranty_terms: original.warranty_terms,
      notes: original.notes,
    });

    return newProposal;
  }

  /**
   * Helper: Generate Proposal Number
   */
  private async generateProposalNumber(): Promise<string> {
    const year = new Date().getFullYear();
    const count = await this.listProposals_({
      filters: {
        created_at: {
          $gte: new Date(`${year}-01-01`),
        },
      },
    });

    const number = (count.length + 1).toString().padStart(4, "0");
    return `PROP-${year}-${number}`;
  }

  /**
   * Helper: Convert to DTO
   */
  private toDTO(proposal: any): ProposalDTO {
    return {
      id: proposal.id,
      customer_id: proposal.customer_id,
      quote_id: proposal.quote_id,
      proposal_number: proposal.proposal_number,
      title: proposal.title,
      version: proposal.version,
      status: proposal.status,
      valid_until: proposal.valid_until,
      valid_days: proposal.valid_days,
      system_data: proposal.system_data,
      financial_data: proposal.financial_data,
      items: proposal.items,
      subtotal: proposal.subtotal,
      discount_total: proposal.discount_total,
      tax_total: proposal.tax_total,
      shipping_total: proposal.shipping_total,
      installation_total: proposal.installation_total,
      total: proposal.total,
      payment_terms: proposal.payment_terms,
      delivery_terms: proposal.delivery_terms,
      warranty_terms: proposal.warranty_terms,
      notes: proposal.notes,
      pdf_url: proposal.pdf_url,
      pdf_generated_at: proposal.pdf_generated_at,
      sent_at: proposal.sent_at,
      viewed_at: proposal.viewed_at,
      accepted_at: proposal.accepted_at,
      rejected_at: proposal.rejected_at,
      rejection_reason: proposal.rejection_reason,
      signed_by: proposal.signed_by,
      signed_at: proposal.signed_at,
      created_at: proposal.created_at,
      updated_at: proposal.updated_at,
    };
  }
}

export default ProposalModuleService;
