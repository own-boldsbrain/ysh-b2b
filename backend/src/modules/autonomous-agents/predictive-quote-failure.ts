/**
 * Predictive Quote Failure Agent
 * 
 * Capacidades autônomas:
 * - Análise de risco pré-execução de cotações
 * - Identificação de fatores de risco
 * - Ações preventivas automáticas
 * - Mitigação de gargalos
 * - Reagendamento inteligente
 * 
 * Impacto esperado: -50% em cotações falhadas
 */

import { Logger } from "@medusajs/framework/logger";

// ================================================================================
// TYPES
// ================================================================================

interface ComparativeQuote {
  id: string;
  customer_id: string;
  invited_suppliers: string[];
  requirements: {
    items: Array<{ sku: string; quantity: number; specs?: any }>;
    custom_specs?: boolean;
    delivery_deadline?: Date;
    payment_terms?: string;
  };
  status: string;
  created_at: Date;
  metadata?: Record<string, any>;
}

interface RiskFactor {
  factor: string;
  impact: number; // 0.0 to 1.0
  mitigation: string;
  confidence: number;
}

interface QuoteRiskAssessment {
  quote_id: string;
  failure_probability: number;
  risk_level: "low" | "medium" | "high" | "critical";
  risk_factors: RiskFactor[];
  recommended_actions: string[];
  assessment_timestamp: Date;
}

interface SupplierAvailability {
  supplier: string;
  status: "healthy" | "degraded" | "unavailable";
  response_rate: number; // 0.0 to 1.0
  avg_response_time_hours: number;
  last_successful_quote: Date;
}

interface StockHistory {
  sku: string;
  frequently_out_of_stock: boolean;
  stockout_rate: number;
  last_available: Date;
  substitute_products: string[];
}

// ================================================================================
// PREDICTIVE QUOTE FAILURE AGENT
// ================================================================================

export class QuoteFailurePredictionAgent {
  private logger: Logger;

  constructor(logger: Logger) {
    this.logger = logger;
  }

  // ================================================================================
  // MAIN PREDICTION METHOD
  // ================================================================================

  async predictQuoteFailure(quote: ComparativeQuote): Promise<QuoteRiskAssessment> {
    this.logger.info(`[QuotePrediction] 🔮 Analyzing quote ${quote.id} for failure risk...`);

    const riskFactors: RiskFactor[] = [];
    let failureProbability = 0.0;

    // Risk Factor 1: Supplier Availability
    const supplierRisks = await this.assessSupplierAvailability(quote);
    riskFactors.push(...supplierRisks.factors);
    failureProbability += supplierRisks.totalRisk;

    // Risk Factor 2: Item Availability
    const itemRisks = await this.assessItemAvailability(quote);
    riskFactors.push(...itemRisks.factors);
    failureProbability += itemRisks.totalRisk;

    // Risk Factor 3: Timing
    const timingRisks = await this.assessTiming(quote);
    riskFactors.push(...timingRisks.factors);
    failureProbability += timingRisks.totalRisk;

    // Risk Factor 4: Complexity
    const complexityRisks = await this.assessComplexity(quote);
    riskFactors.push(...complexityRisks.factors);
    failureProbability += complexityRisks.totalRisk;

    // Risk Factor 5: Customer History
    const customerRisks = await this.assessCustomerHistory(quote);
    riskFactors.push(...customerRisks.factors);
    failureProbability += customerRisks.totalRisk;

    // Cap probability at 1.0
    failureProbability = Math.min(failureProbability, 1.0);

    // Determine risk level
    const riskLevel = this.classifyRisk(failureProbability);

    // Generate recommendations
    const recommendedActions = this.generateRecommendations(riskFactors, failureProbability);

    const assessment: QuoteRiskAssessment = {
      quote_id: quote.id,
      failure_probability: failureProbability,
      risk_level: riskLevel,
      risk_factors: riskFactors,
      recommended_actions: recommendedActions,
      assessment_timestamp: new Date(),
    };

    // Log assessment
    this.logger.info(
      `[QuotePrediction] 📊 Assessment complete for quote ${quote.id}:\n` +
      `  Failure Probability: ${(failureProbability * 100).toFixed(1)}%\n` +
      `  Risk Level: ${riskLevel.toUpperCase()}\n` +
      `  Risk Factors: ${riskFactors.length}\n` +
      `  Recommended Actions: ${recommendedActions.length}`
    );

    // Execute preventive actions if high risk
    if (failureProbability > 0.5) {
      this.logger.warn(
        `[QuotePrediction] ⚠️ HIGH RISK (${(failureProbability * 100).toFixed(1)}%) - ` +
        `Executing preventive actions...`
      );
      await this.executePreventiveActions(quote, riskFactors);
    }

    return assessment;
  }

  // ================================================================================
  // RISK ASSESSMENT: SUPPLIER AVAILABILITY
  // ================================================================================

  private async assessSupplierAvailability(
    quote: ComparativeQuote
  ): Promise<{ factors: RiskFactor[]; totalRisk: number }> {
    const factors: RiskFactor[] = [];
    let totalRisk = 0;

    for (const supplier of quote.invited_suppliers) {
      const availability = await this.checkSupplierAvailability(supplier);

      if (availability.status === "unavailable") {
        factors.push({
          factor: `Supplier ${supplier} is currently unavailable`,
          impact: 0.4,
          mitigation: "Add alternative supplier or delay quote",
          confidence: 0.95,
        });
        totalRisk += 0.4;

      } else if (availability.status === "degraded") {
        factors.push({
          factor: `Supplier ${supplier} has degraded service (${(availability.response_rate * 100).toFixed(0)}% response rate)`,
          impact: 0.3,
          mitigation: "Add alternative supplier as backup",
          confidence: 0.85,
        });
        totalRisk += 0.3;

      } else if (availability.response_rate < 0.7) {
        factors.push({
          factor: `Supplier ${supplier} has low response rate (${(availability.response_rate * 100).toFixed(0)}%)`,
          impact: 0.15,
          mitigation: "Monitor closely or add alternative",
          confidence: 0.75,
        });
        totalRisk += 0.15;
      }

      // Check response time
      if (availability.avg_response_time_hours > 48) {
        factors.push({
          factor: `Supplier ${supplier} has slow response time (${availability.avg_response_time_hours.toFixed(0)}h avg)`,
          impact: 0.1,
          mitigation: "Set longer deadline or choose faster supplier",
          confidence: 0.8,
        });
        totalRisk += 0.1;
      }
    }

    // Risk if too few suppliers
    if (quote.invited_suppliers.length < 3) {
      factors.push({
        factor: `Only ${quote.invited_suppliers.length} supplier(s) invited - low redundancy`,
        impact: 0.2,
        mitigation: "Invite additional suppliers",
        confidence: 0.9,
      });
      totalRisk += 0.2;
    }

    return { factors, totalRisk };
  }

  // ================================================================================
  // RISK ASSESSMENT: ITEM AVAILABILITY
  // ================================================================================

  private async assessItemAvailability(
    quote: ComparativeQuote
  ): Promise<{ factors: RiskFactor[]; totalRisk: number }> {
    const factors: RiskFactor[] = [];
    let totalRisk = 0;

    const items = quote.requirements.items || [];

    for (const item of items) {
      const stockHistory = await this.analyzeStockHistory(item.sku);

      if (stockHistory.frequently_out_of_stock) {
        factors.push({
          factor: `Item ${item.sku} frequently out of stock (${(stockHistory.stockout_rate * 100).toFixed(0)}% rate)`,
          impact: 0.2,
          mitigation: stockHistory.substitute_products.length > 0
            ? "Request substitute products: " + stockHistory.substitute_products.join(", ")
            : "Consider alternative items",
          confidence: 0.8,
        });
        totalRisk += 0.2;
      }

      // Check last availability
      const daysSinceAvailable = (Date.now() - stockHistory.last_available.getTime()) / (1000 * 60 * 60 * 24);
      
      if (daysSinceAvailable > 30) {
        factors.push({
          factor: `Item ${item.sku} not seen in stock for ${daysSinceAvailable.toFixed(0)} days`,
          impact: 0.15,
          mitigation: "Verify availability before sending quote",
          confidence: 0.75,
        });
        totalRisk += 0.15;
      }
    }

    // Risk if too many unique items (complexity)
    if (items.length > 50) {
      factors.push({
        factor: `High item count (${items.length} items) increases coordination complexity`,
        impact: 0.1,
        mitigation: "Consider splitting into multiple quotes",
        confidence: 0.7,
      });
      totalRisk += 0.1;
    }

    return { factors, totalRisk };
  }

  // ================================================================================
  // RISK ASSESSMENT: TIMING
  // ================================================================================

  private async assessTiming(
    quote: ComparativeQuote
  ): Promise<{ factors: RiskFactor[]; totalRisk: number }> {
    const factors: RiskFactor[] = [];
    let totalRisk = 0;

    const createdHour = quote.created_at.getHours();
    const createdDay = quote.created_at.getDay(); // 0 = Sunday

    // Risk: After business hours
    if (createdHour >= 18 || createdHour < 8) {
      factors.push({
        factor: "Quote created after business hours - lower supplier response rate",
        impact: 0.15,
        mitigation: "Schedule for next business day (9 AM)",
        confidence: 0.85,
      });
      totalRisk += 0.15;
    }

    // Risk: Weekend
    if (createdDay === 0 || createdDay === 6) {
      factors.push({
        factor: "Quote created on weekend - minimal supplier availability",
        impact: 0.2,
        mitigation: "Delay until Monday morning",
        confidence: 0.9,
      });
      totalRisk += 0.2;
    }

    // Risk: Tight deadline
    if (quote.requirements.delivery_deadline) {
      const daysUntilDeadline = 
        (quote.requirements.delivery_deadline.getTime() - Date.now()) / (1000 * 60 * 60 * 24);

      if (daysUntilDeadline < 3) {
        factors.push({
          factor: `Very tight deadline (${daysUntilDeadline.toFixed(1)} days) - limited supplier options`,
          impact: 0.25,
          mitigation: "Negotiate extended deadline or expedite supplier contact",
          confidence: 0.9,
        });
        totalRisk += 0.25;
      } else if (daysUntilDeadline < 7) {
        factors.push({
          factor: `Short deadline (${daysUntilDeadline.toFixed(1)} days)`,
          impact: 0.1,
          mitigation: "Prioritize fast-responding suppliers",
          confidence: 0.8,
        });
        totalRisk += 0.1;
      }
    }

    return { factors, totalRisk };
  }

  // ================================================================================
  // RISK ASSESSMENT: COMPLEXITY
  // ================================================================================

  private async assessComplexity(
    quote: ComparativeQuote
  ): Promise<{ factors: RiskFactor[]; totalRisk: number }> {
    const factors: RiskFactor[] = [];
    let totalRisk = 0;

    // Risk: Custom specifications
    if (quote.requirements.custom_specs) {
      factors.push({
        factor: "Custom specifications require manual review",
        impact: 0.25,
        mitigation: "Flag for specialist review before sending to suppliers",
        confidence: 0.9,
      });
      totalRisk += 0.25;
    }

    // Risk: Complex payment terms
    const complexPaymentTerms = ["financing", "lease", "custom"];
    if (quote.requirements.payment_terms && 
        complexPaymentTerms.includes(quote.requirements.payment_terms.toLowerCase())) {
      factors.push({
        factor: "Complex payment terms may require additional approvals",
        impact: 0.15,
        mitigation: "Pre-approve payment structure with finance team",
        confidence: 0.85,
      });
      totalRisk += 0.15;
    }

    // Risk: Mixed item categories (harder to fulfill)
    const items = quote.requirements.items || [];
    const categories = new Set(items.map(item => this.guessCategory(item.sku)));
    
    if (categories.size > 5) {
      factors.push({
        factor: `Multiple item categories (${categories.size}) - harder to fulfill from single supplier`,
        impact: 0.1,
        mitigation: "Consider splitting quote by category",
        confidence: 0.75,
      });
      totalRisk += 0.1;
    }

    return { factors, totalRisk };
  }

  // ================================================================================
  // RISK ASSESSMENT: CUSTOMER HISTORY
  // ================================================================================

  private async assessCustomerHistory(
    quote: ComparativeQuote
  ): Promise<{ factors: RiskFactor[]; totalRisk: number }> {
    const factors: RiskFactor[] = [];
    let totalRisk = 0;

    const customerHistory = await this.getCustomerHistory(quote.customer_id);

    // Risk: New customer (no history)
    if (customerHistory.quote_count === 0) {
      factors.push({
        factor: "New customer - no historical data for reliability prediction",
        impact: 0.05,
        mitigation: "Apply standard approval process",
        confidence: 0.7,
      });
      totalRisk += 0.05;
    }

    // Risk: High cancellation rate
    if (customerHistory.cancellation_rate > 0.3) {
      factors.push({
        factor: `Customer has high quote cancellation rate (${(customerHistory.cancellation_rate * 100).toFixed(0)}%)`,
        impact: 0.15,
        mitigation: "Require deposit or pre-approval before sending quote",
        confidence: 0.8,
      });
      totalRisk += 0.15;
    }

    // Risk: Recent failed quotes
    if (customerHistory.recent_failed_quotes > 2) {
      factors.push({
        factor: `Customer has ${customerHistory.recent_failed_quotes} recent failed quotes`,
        impact: 0.1,
        mitigation: "Review past failure reasons before proceeding",
        confidence: 0.75,
      });
      totalRisk += 0.1;
    }

    return { factors, totalRisk };
  }

  // ================================================================================
  // RISK CLASSIFICATION
  // ================================================================================

  private classifyRisk(probability: number): "low" | "medium" | "high" | "critical" {
    if (probability >= 0.7) return "critical";
    if (probability >= 0.5) return "high";
    if (probability >= 0.3) return "medium";
    return "low";
  }

  // ================================================================================
  // RECOMMENDATIONS
  // ================================================================================

  private generateRecommendations(
    riskFactors: RiskFactor[],
    failureProbability: number
  ): string[] {
    const recommendations: string[] = [];

    // Sort by impact descending
    const sortedFactors = [...riskFactors].sort((a, b) => b.impact - a.impact);

    // Add top 5 mitigations
    for (const factor of sortedFactors.slice(0, 5)) {
      if (!recommendations.includes(factor.mitigation)) {
        recommendations.push(factor.mitigation);
      }
    }

    // General recommendations based on probability
    if (failureProbability >= 0.7) {
      recommendations.unshift("CRITICAL: Consider postponing quote until risks are mitigated");
    } else if (failureProbability >= 0.5) {
      recommendations.unshift("HIGH RISK: Implement preventive actions before sending quote");
    } else if (failureProbability >= 0.3) {
      recommendations.push("Monitor quote closely for early warning signs");
    }

    return recommendations;
  }

  // ================================================================================
  // PREVENTIVE ACTIONS
  // ================================================================================

  async executePreventiveActions(
    quote: ComparativeQuote,
    riskFactors: RiskFactor[]
  ): Promise<void> {
    this.logger.info(`[QuotePrediction] 🛡️ Executing preventive actions for quote ${quote.id}`);

    for (const risk of riskFactors) {
      // Action 1: Add alternative suppliers
      if (risk.mitigation.includes("Add alternative supplier")) {
        const alternative = await this.findAlternativeSupplier(quote);
        if (alternative) {
          quote.invited_suppliers.push(alternative);
          this.logger.info(`[QuotePrediction] ✅ Added alternative supplier: ${alternative}`);
        }
      }

      // Action 2: Request substitute products
      if (risk.mitigation.includes("Request substitute products")) {
        const substitutes = await this.findProductSubstitutes(quote);
        if (substitutes.length > 0) {
          quote.metadata = quote.metadata || {};
          quote.metadata.substitute_options = substitutes;
          this.logger.info(`[QuotePrediction] ✅ Added ${substitutes.length} substitute options`);
        }
      }

      // Action 3: Reschedule for better timing
      if (risk.mitigation.includes("Schedule for next business day")) {
        const nextBusinessDay = this.getNextBusinessDay();
        await this.rescheduleQuote(quote.id, nextBusinessDay);
        this.logger.info(
          `[QuotePrediction] ✅ Rescheduled quote for ${nextBusinessDay.toISOString()}`
        );
      }

      // Action 4: Flag for specialist review
      if (risk.mitigation.includes("specialist review")) {
        await this.flagForSpecialistReview(quote.id, risk.factor);
        this.logger.info(`[QuotePrediction] ✅ Flagged for specialist review`);
      }

      // Action 5: Split complex quotes
      if (risk.mitigation.includes("splitting into multiple quotes")) {
        await this.suggestQuoteSplit(quote.id);
        this.logger.info(`[QuotePrediction] ✅ Suggested quote split strategy`);
      }
    }
  }

  // ================================================================================
  // HELPER METHODS (Stubs)
  // ================================================================================

  private async checkSupplierAvailability(supplier: string): Promise<SupplierAvailability> {
    // TODO: Implementar - consultar banco de dados
    return {
      supplier,
      status: "healthy",
      response_rate: 0.85,
      avg_response_time_hours: 12,
      last_successful_quote: new Date(),
    };
  }

  private async analyzeStockHistory(sku: string): Promise<StockHistory> {
    // TODO: Implementar - consultar histórico de estoque
    return {
      sku,
      frequently_out_of_stock: false,
      stockout_rate: 0.1,
      last_available: new Date(),
      substitute_products: [],
    };
  }

  private async getCustomerHistory(customer_id: string): Promise<{
    quote_count: number;
    cancellation_rate: number;
    recent_failed_quotes: number;
  }> {
    // TODO: Implementar - consultar histórico do cliente
    return {
      quote_count: 10,
      cancellation_rate: 0.15,
      recent_failed_quotes: 1,
    };
  }

  private guessCategory(sku: string): string {
    // Simple heuristic - melhorar depois
    const lower = sku.toLowerCase();
    if (lower.includes("painel") || lower.includes("panel")) return "painel";
    if (lower.includes("inversor") || lower.includes("inverter")) return "inversor";
    if (lower.includes("bateria") || lower.includes("battery")) return "bateria";
    return "other";
  }

  private async findAlternativeSupplier(quote: ComparativeQuote): Promise<string | null> {
    // TODO: Implementar - buscar fornecedor alternativo
    return null;
  }

  private async findProductSubstitutes(quote: ComparativeQuote): Promise<any[]> {
    // TODO: Implementar - buscar produtos substitutos
    return [];
  }

  private getNextBusinessDay(): Date {
    const date = new Date();
    date.setDate(date.getDate() + 1);
    date.setHours(9, 0, 0, 0);

    // Skip weekends
    while (date.getDay() === 0 || date.getDay() === 6) {
      date.setDate(date.getDate() + 1);
    }

    return date;
  }

  private async rescheduleQuote(quoteId: string, newDate: Date): Promise<void> {
    // TODO: Implementar - atualizar banco de dados
    this.logger.info(`[QuotePrediction] Rescheduling quote ${quoteId} to ${newDate.toISOString()}`);
  }

  private async flagForSpecialistReview(quoteId: string, reason: string): Promise<void> {
    // TODO: Implementar - criar flag no banco de dados
    this.logger.info(`[QuotePrediction] Flagging quote ${quoteId} for review: ${reason}`);
  }

  private async suggestQuoteSplit(quoteId: string): Promise<void> {
    // TODO: Implementar - criar sugestão de split
    this.logger.info(`[QuotePrediction] Suggesting split for quote ${quoteId}`);
  }
}
