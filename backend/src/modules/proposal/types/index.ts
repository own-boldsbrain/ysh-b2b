export interface CreateProposalDTO {
  customer_id: string;
  quote_id?: string;
  calculation_id?: string;
  title: string;
  valid_days?: number;
  system_data: ProposalSystemData;
  financial_data: ProposalFinancialData;
  items: ProposalItem[];
  payment_terms?: string;
  delivery_terms?: string;
  warranty_terms?: string;
  notes?: string;
}

export interface UpdateProposalDTO {
  title?: string;
  status?: string;
  valid_until?: Date;
  system_data?: ProposalSystemData;
  financial_data?: ProposalFinancialData;
  items?: ProposalItem[];
  payment_terms?: string;
  delivery_terms?: string;
  warranty_terms?: string;
  notes?: string;
}

export interface SendProposalDTO {
  proposal_id: string;
  recipient_email: string;
  recipient_name?: string;
  message?: string;
  cc_emails?: string[];
}

export interface AcceptProposalDTO {
  proposal_id: string;
  signed_by: string;
  signature_data?: string; // Base64 da assinatura
  notes?: string;
}

export interface RejectProposalDTO {
  proposal_id: string;
  reason: string;
  notes?: string;
}

// Common Types
export interface ProposalSystemData {
  capacity_kwp: number;
  panel_count: number;
  panel_power_wp: number;
  panel_brand: string;
  inverter_count: number;
  inverter_power_kw: number;
  inverter_brand: string;
  estimated_generation_monthly: number;
  estimated_generation_annual: number;
  performance_ratio: number;
  location: {
    city: string;
    state: string;
    hsp: number;
  };
}

export interface ProposalFinancialData {
  capex: {
    equipment: number;
    installation: number;
    engineering: number;
    taxes: number;
    total: number;
  };
  savings: {
    monthly: number;
    annual: number;
    total_25_years: number;
  };
  roi: {
    payback_simple_years: number;
    payback_discounted_years: number;
    irr: number;
    npv: number;
  };
  financing_options?: FinancingOption[];
}

export interface FinancingOption {
  provider: string;
  modality: "CDC" | "LEASING" | "EAAS";
  term_months: number;
  interest_rate_annual: number;
  monthly_installment: number;
  total_with_interest: number;
  down_payment: number;
}

export interface ProposalItem {
  product_id: string;
  product_name: string;
  sku: string;
  description?: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  discount_amount: number;
  subtotal: number;
  tax_percent: number;
  tax_amount: number;
  total: number;
  category?: string;
  brand?: string;
  specifications?: Record<string, string>;
}

// DTOs
export interface ProposalDTO {
  id: string;
  customer_id: string;
  quote_id?: string;
  proposal_number: string;
  title: string;
  version: number;
  status: string;
  valid_until: Date;
  valid_days: number;
  system_data: ProposalSystemData;
  financial_data: ProposalFinancialData;
  items: ProposalItem[];
  subtotal: number;
  discount_total: number;
  tax_total: number;
  shipping_total: number;
  installation_total: number;
  total: number;
  payment_terms?: string;
  delivery_terms?: string;
  warranty_terms?: string;
  notes?: string;
  pdf_url?: string;
  pdf_generated_at?: Date;
  sent_at?: Date;
  viewed_at?: Date;
  accepted_at?: Date;
  rejected_at?: Date;
  rejection_reason?: string;
  signed_by?: string;
  signed_at?: Date;
  created_at: Date;
  updated_at: Date;
}

export interface GeneratePDFOptions {
  include_technical_specs: boolean;
  include_financial_details: boolean;
  include_terms: boolean;
  include_signature_page: boolean;
  language: "pt-BR" | "en-US" | "es-ES";
  branding: {
    logo_url?: string;
    company_name: string;
    company_address?: string;
    company_phone?: string;
    company_email?: string;
  };
}
