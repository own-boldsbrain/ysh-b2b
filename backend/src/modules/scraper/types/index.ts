/**
 * Tipos para Scraper Orchestration Module
 */

export type DistributorCode = 
  | "edeltec"
  | "fortlev"
  | "odex"
  | "solfacil"
  | "fotus"
  | "dynamis"
  | "neosolar";

export type ScraperStatus = "idle" | "running" | "completed" | "error" | "timeout";

export type ProductCategory = 
  | "painel_solar"
  | "inversor"
  | "bateria"
  | "estrutura"
  | "string_box"
  | "cabo"
  | "conector"
  | "outros";

/**
 * Produto normalizado extraído de distribuidores
 */
export interface NormalizedProduct {
  distributor: DistributorCode;
  sku: string;
  name: string;
  category: ProductCategory;
  price: number;
  currency: string;
  availability: "in_stock" | "out_of_stock" | "limited" | "unknown";
  stock_quantity?: number;
  
  // Especificações técnicas
  specifications?: {
    power_watts?: number;
    voltage?: string;
    efficiency?: number;
    warranty_years?: number;
    brand?: string;
    model?: string;
    [key: string]: any;
  };
  
  // Metadados
  image_url?: string;
  product_url?: string;
  last_updated: Date;
  scrape_session_id: string;
}

/**
 * Resultado de execução de scraper
 */
export interface ScraperExecutionResult {
  distributor: DistributorCode;
  status: ScraperStatus;
  started_at: Date;
  completed_at?: Date;
  duration_ms?: number;
  
  products_found: number;
  products_normalized: number;
  products_with_errors: number;
  
  error_message?: string;
  error_stack?: string;
  
  output_file?: string;
  screenshot_file?: string;
}

/**
 * Requisição de scraping
 */
export interface ScrapeRequestDTO {
  distributors: DistributorCode[];
  product_categories?: ProductCategory[];
  max_products_per_distributor?: number;
  timeout_ms?: number;
  save_screenshots?: boolean;
  save_html?: boolean;
  retry_on_error?: boolean;
  max_retries?: number;
}

/**
 * Resultado agregado de scraping multi-distribuidor
 */
export interface MultiDistributorScrapeResult {
  request_id: string;
  started_at: Date;
  completed_at: Date;
  total_duration_ms: number;
  
  distributors_requested: number;
  distributors_successful: number;
  distributors_failed: number;
  
  total_products_found: number;
  total_products_normalized: number;
  
  results: ScraperExecutionResult[];
  products: NormalizedProduct[];
  
  errors: Array<{
    distributor: DistributorCode;
    error: string;
  }>;
}

/**
 * Configuração de mapeamento de produto
 */
export interface ProductMappingConfig {
  distributor: DistributorCode;
  raw_selectors: {
    product_card?: string;
    sku?: string[];
    name?: string[];
    price?: string[];
    availability?: string[];
    image?: string[];
    [key: string]: string | string[] | undefined;
  };
  regex_patterns: {
    sku?: RegExp;
    price?: RegExp;
    power?: RegExp;
    voltage?: RegExp;
  };
  category_mapping: Record<string, ProductCategory>;
}

/**
 * Credenciais de distribuidor
 */
export interface DistributorCredentials {
  distributor: DistributorCode;
  email?: string;
  password?: string;
  api_key?: string;
  api_secret?: string;
  requires_auth: boolean;
}

/**
 * Status de disponibilidade de scraper
 */
export interface ScraperAvailability {
  distributor: DistributorCode;
  is_available: boolean;
  has_credentials: boolean;
  last_successful_run?: Date;
  last_error?: string;
  average_products_per_run?: number;
  average_duration_ms?: number;
  success_rate?: number; // 0-100
}

/**
 * DTO para comparação de preços entre distribuidores
 */
export interface ComparePricesDTO {
  product_name_or_sku: string;
  distributors?: DistributorCode[];
  max_price_difference_percent?: number;
  include_out_of_stock?: boolean;
}

/**
 * Resultado de comparação de preços
 */
export interface PriceComparisonResult {
  search_query: string;
  matched_products: Array<{
    distributor: DistributorCode;
    product: NormalizedProduct;
    price: number;
    availability: string;
    match_score: number; // 0-100 (similaridade do nome)
  }>;
  
  best_price: {
    distributor: DistributorCode;
    price: number;
    product: NormalizedProduct;
  };
  
  price_statistics: {
    min: number;
    max: number;
    average: number;
    median: number;
    spread_percent: number;
  };
  
  availability_summary: {
    in_stock: number;
    out_of_stock: number;
    limited: number;
    unknown: number;
  };
}
