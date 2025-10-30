/**
 * Autonomous Agents Module
 * 
 * Exporta todos os agentes autônomos implementados
 */

export { SelfHealingScraperAgent } from "./self-healing-scraper";
export { PriceAnomalyDetectionAgent } from "./price-anomaly-detection";
export { QuoteFailurePredictionAgent } from "./predictive-quote-failure";
export { DynamicNegotiationAgent } from "./dynamic-negotiation";

// Re-export types for convenience
export type {
  Product,
  ScraperConfig,
  SelectorDiscoveryResult,
  ScraperAttemptResult,
} from "./self-healing-scraper";

export type {
  PriceDataPoint,
  HistoricalStats,
  AnomalyInvestigation,
  PriceAnomaly,
} from "./price-anomaly-detection";

export type {
  QuoteRiskAssessment,
  RiskFactor,
  SupplierAvailability,
  StockHistory,
} from "./predictive-quote-failure";

export type {
  CounterProposal,
  CustomerIntent,
  CustomerFeedback,
  NegotiationDecision,
  FinancingOption,
} from "./dynamic-negotiation";
