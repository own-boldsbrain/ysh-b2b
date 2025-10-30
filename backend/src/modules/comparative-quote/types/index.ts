export interface CreateComparativeQuoteRequestDTO {
  title: string;
  description?: string;
  customer_id: string;
  company_id?: string;
  deadline_days: number; // Deadline em dias a partir de agora
  technical_specs: TechnicalSpecs;
  items: QuoteRequestItem[];
  evaluation_criteria?: EvaluationCriteria;
  invited_suppliers: string[]; // Array de supplier IDs
  project_type?: "residential" | "commercial" | "industrial";
  location?: Location;
  budget_range?: { min: number; max: number };
}

export interface PublishQuoteRequestDTO {
  request_id: string;
  notify_suppliers: boolean;
  message?: string;
}

export interface SubmitSupplierQuoteDTO {
  request_id: string;
  supplier_id: string;
  items: QuoteResponseItem[];
  payment_terms?: string;
  delivery_days?: number;
  warranty_months?: number;
  additional_terms?: string;
  proposal_pdf?: string; // Base64 or URL
  technical_datasheet?: string;
  certificates?: string[];
}

export interface EvaluateQuoteDTO {
  quote_id: string;
  score: number; // 0-100
  evaluation_notes?: string;
}

export interface SelectQuoteDTO {
  request_id: string;
  selected_quote_id: string;
  selection_reason?: string;
}

// Common Types
export interface TechnicalSpecs {
  system_type: "on-grid" | "off-grid" | "hybrid";
  capacity_kwp: number;
  voltage: "monofasico" | "bifasico" | "trifasico";
  location: {
    city: string;
    state: string;
    hsp: number;
  };
  installation_type: "rooftop" | "ground" | "carport";
  preferred_brands?: {
    panels?: string[];
    inverters?: string[];
  };
}

export interface QuoteRequestItem {
  category: string; // 'panel', 'inverter', 'structure', 'cable', etc
  description: string;
  quantity: number;
  required_specs?: Record<string, any>;
  notes?: string;
}

export interface QuoteResponseItem {
  request_item_index: number; // Index do item original
  product_id: string;
  product_name: string;
  sku: string;
  brand: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  discount_amount: number;
  subtotal: number;
  tax_percent: number;
  tax_amount: number;
  total: number;
  specifications?: Record<string, string>;
  datasheet_url?: string;
  availability: "in_stock" | "on_order" | "custom_order";
  lead_time_days?: number;
}

export interface EvaluationCriteria {
  price_weight: number; // 0-100
  quality_weight: number;
  delivery_weight: number;
  warranty_weight: number;
  [key: string]: number;
}

export interface Location {
  street?: string;
  city: string;
  state: string;
  zip_code?: string;
  country: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
}

// DTOs
export interface ComparativeQuoteRequestDTO {
  id: string;
  request_number: string;
  title: string;
  description?: string;
  customer_id: string;
  company_id?: string;
  status: string;
  published_at?: Date;
  deadline: Date;
  evaluation_ends_at?: Date;
  technical_specs: TechnicalSpecs;
  items: QuoteRequestItem[];
  evaluation_criteria: EvaluationCriteria;
  invited_suppliers: string[];
  project_type?: string;
  location?: Location;
  budget_range?: { min: number; max: number };
  selected_quote_id?: string;
  selection_reason?: string;
  selected_at?: Date;
  created_at: Date;
  updated_at: Date;
  
  // Relações
  responses?: SupplierQuoteResponseDTO[];
  responses_count?: number;
  responses_submitted?: number;
}

export interface SupplierQuoteResponseDTO {
  id: string;
  request_id: string;
  supplier_id: string;
  supplier_name: string;
  status: string;
  invited_at: Date;
  viewed_at?: Date;
  submitted_at?: Date;
  items: QuoteResponseItem[];
  subtotal: number;
  discount_total: number;
  tax_total: number;
  shipping_total: number;
  installation_total: number;
  total: number;
  payment_terms?: string;
  delivery_days?: number;
  warranty_months?: number;
  additional_terms?: string;
  proposal_pdf_url?: string;
  technical_datasheet_url?: string;
  certificates_urls?: string[];
  score?: number;
  evaluation_notes?: string;
  is_selected: boolean;
  rejection_reason?: string;
  created_at: Date;
  updated_at: Date;
}

export interface QuoteComparison {
  request: ComparativeQuoteRequestDTO;
  responses: SupplierQuoteResponseDTO[];
  comparison_matrix: {
    suppliers: string[];
    criteria: {
      name: string;
      weight: number;
      scores: number[]; // Score por supplier
    }[];
    total_scores: number[]; // Score total ponderado por supplier
    recommendation: {
      supplier_id: string;
      supplier_name: string;
      score: number;
      reason: string;
    };
  };
  price_comparison: {
    lowest: SupplierQuoteResponseDTO;
    highest: SupplierQuoteResponseDTO;
    average: number;
    savings_vs_highest: number;
  };
}
