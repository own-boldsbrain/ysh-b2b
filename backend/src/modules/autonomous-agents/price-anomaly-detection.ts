/**
 * Price Anomaly Detection Agent
 * 
 * Capacidades autônomas:
 * - Detecção de outliers usando análise estatística (3σ)
 * - Investigação automática de causa da anomalia
 * - Re-scraping seletivo quando detecta erro
 * - Alertas contextuais para equipe
 * - Identificação de oportunidades (promoções)
 * 
 * Impacto esperado: -80% em erros de preço
 */

import { Logger } from "@medusajs/framework/logger";

// ================================================================================
// TYPES
// ================================================================================

interface PriceDataPoint {
  distributor: string;
  sku: string;
  price: number;
  timestamp: Date;
  source: "scraper" | "api" | "manual";
}

interface HistoricalStats {
  sku: string;
  mean: number;
  median: number;
  std: number;
  min: number;
  max: number;
  dataPoints: number;
  lastUpdated: Date;
}

interface AnomalyInvestigation {
  isAnomaly: boolean;
  zScore: number;
  likelyError: boolean;
  marketShift: boolean;
  promotion: boolean;
  reason: string;
  discountPercentage?: number;
  confidence: number;
}

interface PriceAnomaly {
  sku: string;
  distributor: string;
  currentPrice: number;
  expectedPrice: number;
  deviation: number;
  zScore: number;
  investigation: AnomalyInvestigation;
  detectedAt: Date;
  severity: "low" | "medium" | "high" | "critical";
}

// ================================================================================
// PRICE ANOMALY DETECTION AGENT
// ================================================================================

export class PriceAnomalyDetectionAgent {
  private logger: Logger;
  private monitoringInterval: NodeJS.Timeout | null = null;
  private priceHistory: Map<string, PriceDataPoint[]> = new Map();

  constructor(logger: Logger) {
    this.logger = logger;
  }

  // ================================================================================
  // CONTINUOUS MONITORING
  // ================================================================================

  startMonitoring(intervalMinutes: number = 60): void {
    this.logger.info(
      `[PriceAnomaly] 🔍 Starting continuous price monitoring (every ${intervalMinutes} minutes)`
    );

    this.monitoringInterval = setInterval(
      () => this.monitorPrices(),
      intervalMinutes * 60 * 1000
    );

    // Run immediately
    this.monitorPrices();
  }

  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
      this.logger.info("[PriceAnomaly] ⏹️ Stopped price monitoring");
    }
  }

  private async monitorPrices(): Promise<void> {
    this.logger.info("[PriceAnomaly] 📊 Running price monitoring cycle...");

    try {
      // Get all current prices from all distributors
      const currentPrices = await this.getAllCurrentPrices();

      this.logger.info(
        `[PriceAnomaly] Analyzing ${Object.keys(currentPrices).length} unique SKUs`
      );

      const anomalies: PriceAnomaly[] = [];

      // Analyze each product
      for (const [sku, prices] of Object.entries(currentPrices)) {
        // Get historical statistics
        const historicalStats = await this.getHistoricalStats(sku);

        if (!historicalStats || historicalStats.dataPoints < 10) {
          // Not enough historical data - skip
          continue;
        }

        // Check each distributor's price
        for (const [distributor, priceData] of Object.entries(prices)) {
          const anomaly = await this.detectAnomaly(
            sku,
            distributor,
            priceData.price,
            historicalStats
          );

          if (anomaly) {
            anomalies.push(anomaly);
          }
        }
      }

      // Process detected anomalies
      if (anomalies.length > 0) {
        this.logger.warn(
          `[PriceAnomaly] ⚠️ Detected ${anomalies.length} price anomalies`
        );

        await this.processAnomalies(anomalies);
      } else {
        this.logger.info("[PriceAnomaly] ✅ No anomalies detected - all prices normal");
      }

    } catch (error) {
      this.logger.error(`[PriceAnomaly] Monitoring cycle failed: ${error.message}`);
    }
  }

  // ================================================================================
  // ANOMALY DETECTION
  // ================================================================================

  private async detectAnomaly(
    sku: string,
    distributor: string,
    currentPrice: number,
    historicalStats: HistoricalStats
  ): Promise<PriceAnomaly | null> {
    
    // Calculate z-score (number of standard deviations from mean)
    const zScore = (currentPrice - historicalStats.mean) / historicalStats.std;

    // Anomaly threshold: 3 standard deviations (99.7% confidence)
    if (Math.abs(zScore) <= 3) {
      return null; // Not an anomaly
    }

    this.logger.warn(
      `[PriceAnomaly] 🚨 ANOMALY DETECTED: ${sku} @ ${distributor}\n` +
      `  Current: R$ ${currentPrice.toFixed(2)}\n` +
      `  Expected: R$ ${historicalStats.mean.toFixed(2)} (±${historicalStats.std.toFixed(2)})\n` +
      `  Z-Score: ${zScore.toFixed(2)}σ`
    );

    // Investigate cause
    const investigation = await this.investigateAnomaly(
      sku,
      distributor,
      currentPrice,
      historicalStats,
      zScore
    );

    // Calculate severity
    const severity = this.calculateSeverity(zScore, investigation);

    // Calculate deviation percentage
    const deviation = ((currentPrice - historicalStats.mean) / historicalStats.mean) * 100;

    return {
      sku,
      distributor,
      currentPrice,
      expectedPrice: historicalStats.mean,
      deviation,
      zScore,
      investigation,
      detectedAt: new Date(),
      severity,
    };
  }

  // ================================================================================
  // ANOMALY INVESTIGATION
  // ================================================================================

  private async investigateAnomaly(
    sku: string,
    distributor: string,
    currentPrice: number,
    historicalStats: HistoricalStats,
    zScore: number
  ): Promise<AnomalyInvestigation> {
    
    this.logger.info(`[PriceAnomaly] 🔬 Investigating anomaly for ${sku} @ ${distributor}`);

    let likelyError = false;
    let marketShift = false;
    let promotion = false;
    let reason = "";
    let discountPercentage: number | undefined;
    let confidence = 0.5;

    // Investigation 1: Check if price is suspiciously low (possible scraping error)
    if (currentPrice < historicalStats.min * 0.5) {
      likelyError = true;
      reason = "Price is 50% below historical minimum - likely scraping error";
      confidence = 0.9;
      
      this.logger.warn(`[PriceAnomaly] 🔴 Likely Error: ${reason}`);
      return { isAnomaly: true, zScore, likelyError, marketShift, promotion, reason, confidence };
    }

    // Investigation 2: Check if price is suspiciously high (possible decimal error)
    if (currentPrice > historicalStats.max * 2) {
      likelyError = true;
      reason = "Price is 2x above historical maximum - likely decimal point error";
      confidence = 0.85;
      
      this.logger.warn(`[PriceAnomaly] 🔴 Likely Error: ${reason}`);
      return { isAnomaly: true, zScore, likelyError, marketShift, promotion, reason, confidence };
    }

    // Investigation 3: Check for promotions (significant price drop)
    if (zScore < -3 && currentPrice >= historicalStats.min * 0.7) {
      const discount = ((historicalStats.mean - currentPrice) / historicalStats.mean) * 100;
      
      if (discount >= 10 && discount <= 50) {
        promotion = true;
        discountPercentage = discount;
        reason = `Possible promotion detected - ${discount.toFixed(0)}% discount`;
        confidence = 0.75;
        
        this.logger.info(`[PriceAnomaly] 🟢 Opportunity: ${reason}`);
        return { 
          isAnomaly: true, 
          zScore, 
          likelyError, 
          marketShift, 
          promotion, 
          reason, 
          discountPercentage,
          confidence 
        };
      }
    }

    // Investigation 4: Check if other distributors also changed (market shift)
    const otherDistributorsChanged = await this.checkOtherDistributors(sku, distributor);
    
    if (otherDistributorsChanged >= 0.5) {
      marketShift = true;
      reason = `Market-wide price shift detected (${(otherDistributorsChanged * 100).toFixed(0)}% of distributors changed)`;
      confidence = 0.8;
      
      this.logger.info(`[PriceAnomaly] 🟡 Market Shift: ${reason}`);
      return { isAnomaly: true, zScore, likelyError, marketShift, promotion, reason, confidence };
    }

    // Investigation 5: Check recent price history for pattern
    const recentHistory = await this.getRecentPriceHistory(sku, distributor, 7);
    
    if (recentHistory.length >= 3) {
      const recentPrices = recentHistory.map(h => h.price);
      const recentMean = recentPrices.reduce((a, b) => a + b, 0) / recentPrices.length;
      
      if (Math.abs(currentPrice - recentMean) < historicalStats.std * 0.5) {
        marketShift = true;
        reason = "Price consistent with recent trend - gradual market adjustment";
        confidence = 0.7;
        
        this.logger.info(`[PriceAnomaly] 🟡 Trend: ${reason}`);
        return { isAnomaly: true, zScore, likelyError, marketShift, promotion, reason, confidence };
      }
    }

    // Default: Unknown cause - treat as potential error
    likelyError = true;
    reason = "Anomaly detected but cause unclear - requires manual review";
    confidence = 0.6;

    return { isAnomaly: true, zScore, likelyError, marketShift, promotion, reason, confidence };
  }

  // ================================================================================
  // ANOMALY PROCESSING & ACTIONS
  // ================================================================================

  private async processAnomalies(anomalies: PriceAnomaly[]): Promise<void> {
    this.logger.info(`[PriceAnomaly] 🔧 Processing ${anomalies.length} anomalies...`);

    // Group by severity
    const critical = anomalies.filter(a => a.severity === "critical");
    const high = anomalies.filter(a => a.severity === "high");
    const medium = anomalies.filter(a => a.severity === "medium");
    const low = anomalies.filter(a => a.severity === "low");

    // Process critical anomalies immediately
    for (const anomaly of critical) {
      await this.handleCriticalAnomaly(anomaly);
    }

    // Process high severity anomalies
    for (const anomaly of high) {
      await this.handleHighSeverityAnomaly(anomaly);
    }

    // Batch notify for medium/low severity
    if (medium.length > 0 || low.length > 0) {
      await this.notifyBatchAnomalies([...medium, ...low]);
    }

    // Log summary
    this.logger.info(
      `[PriceAnomaly] 📊 Processing complete:\n` +
      `  Critical: ${critical.length}\n` +
      `  High: ${high.length}\n` +
      `  Medium: ${medium.length}\n` +
      `  Low: ${low.length}`
    );
  }

  private async handleCriticalAnomaly(anomaly: PriceAnomaly): Promise<void> {
    this.logger.error(
      `[PriceAnomaly] 🚨 CRITICAL: ${anomaly.sku} @ ${anomaly.distributor}\n` +
      `  ${anomaly.investigation.reason}`
    );

    if (anomaly.investigation.likelyError) {
      // Trigger immediate re-scraping
      this.logger.info(`[PriceAnomaly] 🔄 Triggering re-scrape for ${anomaly.distributor}`);
      await this.triggerRescrape(anomaly.distributor, anomaly.sku);

      // Notify team immediately
      await this.notifyTeamUrgent(anomaly);

      // Flag price as suspicious in database
      await this.flagSuspiciousPrice(anomaly);
    }
  }

  private async handleHighSeverityAnomaly(anomaly: PriceAnomaly): Promise<void> {
    this.logger.warn(
      `[PriceAnomaly] ⚠️ HIGH: ${anomaly.sku} @ ${anomaly.distributor} - ${anomaly.investigation.reason}`
    );

    if (anomaly.investigation.likelyError) {
      // Schedule re-scrape (not urgent)
      await this.scheduleRescrape(anomaly.distributor, anomaly.sku, 30); // 30 minutes

    } else if (anomaly.investigation.promotion) {
      // Flag as opportunity
      await this.flagAsOpportunity(anomaly);

      // Notify pricing team
      await this.notifyPricingTeam(
        `🎯 Promotion opportunity: ${anomaly.sku} @ ${anomaly.distributor}\n` +
        `Discount: ${anomaly.investigation.discountPercentage?.toFixed(0)}%`
      );

    } else if (anomaly.investigation.marketShift) {
      // Alert pricing team about market change
      await this.alertPricingTeam(
        `📈 Market shift detected: ${anomaly.sku}\n` +
        `${anomaly.investigation.reason}`
      );
    }
  }

  // ================================================================================
  // SEVERITY CALCULATION
  // ================================================================================

  private calculateSeverity(
    zScore: number,
    investigation: AnomalyInvestigation
  ): "low" | "medium" | "high" | "critical" {
    
    // Critical: Likely error + extreme deviation
    if (investigation.likelyError && Math.abs(zScore) > 5) {
      return "critical";
    }

    // High: Likely error or extreme deviation
    if (investigation.likelyError || Math.abs(zScore) > 4) {
      return "high";
    }

    // Medium: Moderate deviation
    if (Math.abs(zScore) > 3.5) {
      return "medium";
    }

    // Low: Just above threshold
    return "low";
  }

  // ================================================================================
  // HELPER METHODS (Stubs - implementar com lógica real)
  // ================================================================================

  private async getAllCurrentPrices(): Promise<Record<string, Record<string, PriceDataPoint>>> {
    // TODO: Implementar - buscar do banco de dados
    // Formato: { [sku]: { [distributor]: PriceDataPoint } }
    return {};
  }

  private async getHistoricalStats(sku: string): Promise<HistoricalStats | null> {
    // TODO: Implementar - calcular estatísticas de histórico
    
    // Exemplo de cálculo:
    const history = this.priceHistory.get(sku) || [];
    
    if (history.length < 10) {
      return null;
    }

    const prices = history.map(h => h.price);
    const mean = prices.reduce((a, b) => a + b, 0) / prices.length;
    const variance = prices.reduce((sum, price) => sum + Math.pow(price - mean, 2), 0) / prices.length;
    const std = Math.sqrt(variance);
    const sorted = [...prices].sort((a, b) => a - b);
    const median = sorted[Math.floor(sorted.length / 2)];

    return {
      sku,
      mean,
      median,
      std,
      min: Math.min(...prices),
      max: Math.max(...prices),
      dataPoints: prices.length,
      lastUpdated: new Date(),
    };
  }

  private async checkOtherDistributors(sku: string, excludeDistributor: string): Promise<number> {
    // TODO: Implementar - verificar se outros distribuidores também mudaram preço
    // Retorna: percentual de distribuidores que também tiveram mudança significativa
    return 0;
  }

  private async getRecentPriceHistory(
    sku: string,
    distributor: string,
    days: number
  ): Promise<PriceDataPoint[]> {
    // TODO: Implementar - buscar histórico recente do banco
    return [];
  }

  private async triggerRescrape(distributor: string, sku: string): Promise<void> {
    this.logger.info(`[PriceAnomaly] 🔄 Triggering immediate re-scrape: ${distributor} / ${sku}`);
    // TODO: Integrar com scraper orchestration
  }

  private async scheduleRescrape(distributor: string, sku: string, delayMinutes: number): Promise<void> {
    this.logger.info(
      `[PriceAnomaly] ⏱️ Scheduling re-scrape in ${delayMinutes} minutes: ${distributor} / ${sku}`
    );
    // TODO: Integrar com job scheduler
  }

  private async flagSuspiciousPrice(anomaly: PriceAnomaly): Promise<void> {
    this.logger.warn(`[PriceAnomaly] 🚩 Flagging suspicious price: ${anomaly.sku} @ ${anomaly.distributor}`);
    // TODO: Atualizar banco de dados com flag
  }

  private async flagAsOpportunity(anomaly: PriceAnomaly): Promise<void> {
    this.logger.info(`[PriceAnomaly] 🎯 Flagging opportunity: ${anomaly.sku} @ ${anomaly.distributor}`);
    // TODO: Criar registro de oportunidade no banco
  }

  private async notifyTeamUrgent(anomaly: PriceAnomaly): Promise<void> {
    this.logger.error(
      `[PriceAnomaly] 🔔 URGENT NOTIFICATION:\n` +
      `SKU: ${anomaly.sku}\n` +
      `Distributor: ${anomaly.distributor}\n` +
      `Current: R$ ${anomaly.currentPrice.toFixed(2)}\n` +
      `Expected: R$ ${anomaly.expectedPrice.toFixed(2)}\n` +
      `Deviation: ${anomaly.deviation.toFixed(1)}%\n` +
      `Reason: ${anomaly.investigation.reason}`
    );
    // TODO: Integrar com Slack/Email
  }

  private async notifyPricingTeam(message: string): Promise<void> {
    this.logger.info(`[PriceAnomaly] 📧 Pricing Team: ${message}`);
    // TODO: Integrar com Slack channel específico
  }

  private async alertPricingTeam(message: string): Promise<void> {
    this.logger.warn(`[PriceAnomaly] 🔔 Alert: ${message}`);
    // TODO: Integrar com Slack
  }

  private async notifyBatchAnomalies(anomalies: PriceAnomaly[]): Promise<void> {
    this.logger.info(`[PriceAnomaly] 📬 Batch notification for ${anomalies.length} anomalies`);
    // TODO: Enviar relatório consolidado
  }
}
