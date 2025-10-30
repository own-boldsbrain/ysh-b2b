/**
 * Tipos para Pricing Intelligence Module
 * 
 * Implementa estratégias de precificação de PRICING_STRATEGY_YSH.md
 */

export type PriceCategory = "excellent" | "good" | "average" | "expensive";
export type CustomerChannel = "b2c" | "integrator_b2b" | "distributor" | "marketplace" | "white_label";
export type Region = "nordeste" | "centro_oeste" | "sudeste" | "norte" | "sul";
export type Scenario = "otimista" | "neutro" | "pessimista";

/**
 * Resultado de análise de competitividade de preço
 */
export interface PriceScoreResult {
  category: PriceCategory;
  delta: number; // Percentual acima do melhor preço
  bestPrice: number;
  explanation: string;
}

/**
 * Resultado de aplicação de markup dinâmico
 */
export interface DynamicMarkupResult {
  costPrice: number;
  baseMarkup: number;
  adjustment: number;
  finalMarkup: number;
  sellingPrice: number;
  grossMargin: number; // Margem bruta em %
  netMargin: number; // Margem líquida em %
  scenario: Scenario;
}

/**
 * Resultado de precificação por canal
 */
export interface ChannelPricingResult {
  basePrice: number;
  channel: CustomerChannel;
  discount: number; // Percentual de desconto
  channelPrice: number;
  commission: number; // Comissão esperada
}

/**
 * Configuração de bundle estratégico
 */
export interface BundleConfiguration {
  name: string;
  description: string;
  components: Array<{
    product_id: string;
    quantity: number;
    unit_price: number;
  }>;
  bundle_discount: number; // Percentual de desconto no bundle
  target_margin: number; // Margem-alvo após desconto
}

/**
 * Resultado de precificação de bundle
 */
export interface BundlePricingResult {
  individual_total: number;
  bundle_discount: number;
  bundle_price: number;
  savings: number;
  margin: number;
  profitable: boolean; // Se mantém margem mínima
}

/**
 * Estratégia de financiamento
 */
export interface FinancingTier {
  name: string;
  installments: number;
  monthly_rate: number; // Taxa mensal em %
  annual_cet: number; // Custo Efetivo Total anual em %
  minimum_purchase: number;
  maximum_purchase: number;
}

/**
 * Cálculo de financiamento
 */
export interface FinancingCalculation {
  principal: number; // Valor principal
  tier: FinancingTier;
  installment_value: number; // Valor da parcela
  total_amount: number; // Valor total com juros
  total_interest: number; // Juros totais
  effective_rate: number; // Taxa efetiva
}

/**
 * Tier de assinatura SaaS
 */
export interface SubscriptionTier {
  name: string;
  monthly_price: number;
  cost_per_month: number;
  margin: number; // Margem em %
  features: string[];
  max_systems: number;
  included_monitoring: boolean;
}

/**
 * Política de price matching
 */
export interface PriceMatchPolicy {
  max_discount: number; // Máximo 15%
  min_margin: number; // Mínimo 12%
  require_proof: boolean;
  competitor_whitelist: string[];
}

/**
 * Resultado de price matching
 */
export interface PriceMatchResult {
  original_price: number;
  competitor_price: number;
  matched_price: number;
  discount_applied: number;
  margin_after_match: number;
  approved: boolean;
  rejection_reason?: string;
}

/**
 * Configuração de precificação dinâmica contextual
 */
export interface DynamicPricingContext {
  time_of_day: "morning" | "afternoon" | "evening" | "night";
  day_of_week: "weekday" | "weekend";
  season: "summer" | "winter" | "spring" | "fall";
  inventory_level: "high" | "medium" | "low";
  competition_level: "high" | "medium" | "low";
  customer_segment: "new" | "returning" | "vip";
  urgency: "low" | "medium" | "high";
}

/**
 * Ajustes de precificação dinâmica
 */
export interface DynamicPricingAdjustments {
  time_adjustment: number; // -5% a +3%
  inventory_adjustment: number; // -10% a +5%
  competition_adjustment: number; // -8% a +2%
  segment_adjustment: number; // -15% a +10%
  urgency_adjustment: number; // -20% a 0%
  total_adjustment: number;
}

/**
 * Configuração de precificação psicológica
 */
export interface PsychologicalPricingConfig {
  use_charm_pricing: boolean; // .99 ou .95 endings
  use_anchor_pricing: boolean; // Mostrar preço "De/Por"
  anchor_multiplier: number; // Ex: 1.25 para mostrar 25% acima
  urgency_message: boolean; // "Últimas unidades"
  scarcity_threshold: number; // Estoque abaixo do qual mostrar escassez
}

/**
 * Resultado de precificação psicológica
 */
export interface PsychologicalPricingResult {
  original_price: number;
  charm_price: number; // Com terminação .99/.95
  anchor_price?: number; // Preço "De"
  display_savings?: number; // Economia mostrada
  urgency_tag?: string;
}

/**
 * Splits de projeto por componente
 */
export interface ProjectSplits {
  scenario: Scenario;
  region: Region;
  total_value: number;
  equipments: {
    percentage: number;
    value: number;
  };
  labor: {
    percentage: number;
    value: number;
  };
  engineering: {
    percentage: number;
    value: number;
  };
  art_trt: {
    percentage: number;
    value: number;
  };
  homologation: {
    percentage: number;
    value: number;
  };
  commission: {
    percentage: number;
    value: number;
  };
  logistics: {
    percentage: number;
    value: number;
  };
  margin: {
    percentage: number;
    value: number;
  };
}

/**
 * KPIs de precificação
 */
export interface PricingKPIs {
  gross_margin_target: number; // 28%
  net_margin_target: number; // 18%
  quote_to_sale_conversion_target: number; // 35%
  average_ticket_value: number;
  win_rate: number; // Taxa de vitória em cotações
  price_competitiveness_index: number; // 0-100
}

/**
 * DTO para calcular precificação completa de projeto
 */
export interface CalculateProjectPricingDTO {
  project_id?: string;
  cost_price: number;
  region: Region;
  customer_channel: CustomerChannel;
  competitor_prices?: number[];
  scenario?: Scenario;
  apply_psychological_pricing?: boolean;
  dynamic_context?: Partial<DynamicPricingContext>;
}

/**
 * Resultado completo de precificação de projeto
 */
export interface ProjectPricingResult {
  cost_price: number;
  price_score?: PriceScoreResult;
  dynamic_markup: DynamicMarkupResult;
  channel_pricing: ChannelPricingResult;
  regional_adjustments: {
    generation_factor: number;
    cost_factor: number;
  };
  psychological_pricing?: PsychologicalPricingResult;
  dynamic_adjustments?: DynamicPricingAdjustments;
  project_splits: ProjectSplits;
  final_price: number;
  recommended_price: number; // Com psychological pricing
  kpis: {
    gross_margin: number;
    net_margin: number;
    meets_target: boolean;
  };
}
