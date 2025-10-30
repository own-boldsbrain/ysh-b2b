/**
 * Integration Tests for Autonomous Agents
 * 
 * Valida comportamento autônomo de cada agente:
 * 1. Self-Healing Scraper
 * 2. Price Anomaly Detection
 * 3. Predictive Quote Failure
 * 4. Dynamic Negotiation
 */

import { describe, it, expect, beforeEach, afterEach } from "@jest/globals";
import { SelfHealingScraperAgent } from "../self-healing-scraper";
import { PriceAnomalyDetectionAgent } from "../price-anomaly-detection";
import { QuoteFailurePredictionAgent } from "../predictive-quote-failure";
import { DynamicNegotiationAgent } from "../dynamic-negotiation";

// Mock logger
const mockLogger = {
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
  debug: jest.fn(),
};

// ================================================================================
// SELF-HEALING SCRAPER TESTS
// ================================================================================

describe("SelfHealingScraperAgent", () => {
  let agent: SelfHealingScraperAgent;

  beforeEach(() => {
    agent = new SelfHealingScraperAgent(mockLogger as any);
    jest.clearAllMocks();
  });

  it("should validate product quality correctly", () => {
    const goodProducts = [
      { sku: "ABC123", title: "Product 1", price: 100, distributor: "Test", category: "solar" },
      { sku: "ABC124", title: "Product 2", price: 200, distributor: "Test", category: "solar" },
      { sku: "ABC125", title: "Product 3", price: 300, distributor: "Test", category: "solar" },
      { sku: "ABC126", title: "Product 4", price: 400, distributor: "Test", category: "solar" },
      { sku: "ABC127", title: "Product 5", price: 500, distributor: "Test", category: "solar" },
      { sku: "ABC128", title: "Product 6", price: 600, distributor: "Test", category: "solar" },
      { sku: "ABC129", title: "Product 7", price: 700, distributor: "Test", category: "solar" },
      { sku: "ABC130", title: "Product 8", price: 800, distributor: "Test", category: "solar" },
      { sku: "ABC131", title: "Product 9", price: 900, distributor: "Test", category: "solar" },
      { sku: "ABC132", title: "Product 10", price: 1000, distributor: "Test", category: "solar" },
      { sku: "ABC133", title: "Product 11", price: 1100, distributor: "Test", category: "solar" },
    ];

    const validation = (agent as any).validateProducts(goodProducts);

    expect(validation.qualityScore).toBeGreaterThan(0.9);
    expect(validation.issues.length).toBe(0);
  });

  it("should detect low product count as quality issue", () => {
    const fewProducts = [
      { sku: "ABC123", title: "Product 1", price: 100, distributor: "Test", category: "solar" },
      { sku: "ABC124", title: "Product 2", price: 200, distributor: "Test", category: "solar" },
    ];

    const validation = (agent as any).validateProducts(fewProducts);

    expect(validation.qualityScore).toBeLessThan(0.8);
    expect(validation.issues.some((i: string) => i.includes("Low product count"))).toBe(true);
  });

  it("should detect missing prices as quality issue", () => {
    const productsWithoutPrices = Array(15).fill(null).map((_, i) => ({
      sku: `ABC${i}`,
      title: `Product ${i}`,
      price: 0, // Invalid price
      distributor: "Test",
      category: "solar",
    }));

    const validation = (agent as any).validateProducts(productsWithoutPrices);

    expect(validation.qualityScore).toBeLessThan(0.5);
    expect(validation.issues.some((i: string) => i.includes("invalid price rate"))).toBe(true);
  });

  it("should detect duplicate SKUs", () => {
    const productsWithDuplicates = [
      ...Array(10).fill(null).map((_, i) => ({
        sku: "DUPLICATE",
        title: `Product ${i}`,
        price: 100 + i * 10,
        distributor: "Test",
        category: "solar",
      })),
      { sku: "UNIQUE", title: "Unique Product", price: 500, distributor: "Test", category: "solar" },
    ];

    const validation = (agent as any).validateProducts(productsWithDuplicates);

    expect(validation.issues.some((i: string) => i.includes("duplicate SKU"))).toBe(true);
  });
});

// ================================================================================
// PRICE ANOMALY DETECTION TESTS
// ================================================================================

describe("PriceAnomalyDetectionAgent", () => {
  let agent: PriceAnomalyDetectionAgent;

  beforeEach(() => {
    agent = new PriceAnomalyDetectionAgent(mockLogger as any);
    jest.clearAllMocks();
  });

  it("should detect price anomaly with z-score > 3", async () => {
    const historicalStats = {
      sku: "TEST123",
      mean: 1000,
      median: 1000,
      std: 100,
      min: 800,
      max: 1200,
      dataPoints: 50,
      lastUpdated: new Date(),
    };

    const currentPrice = 1500; // 5 standard deviations above mean

    const anomaly = await (agent as any).detectAnomaly(
      "TEST123",
      "TestDistributor",
      currentPrice,
      historicalStats
    );

    expect(anomaly).not.toBeNull();
    expect(anomaly.zScore).toBeGreaterThan(3);
    expect(anomaly.severity).toBe("high");
  });

  it("should NOT detect anomaly with z-score < 3", async () => {
    const historicalStats = {
      sku: "TEST123",
      mean: 1000,
      median: 1000,
      std: 100,
      min: 800,
      max: 1200,
      dataPoints: 50,
      lastUpdated: new Date(),
    };

    const currentPrice = 1100; // Only 1 standard deviation

    const anomaly = await (agent as any).detectAnomaly(
      "TEST123",
      "TestDistributor",
      currentPrice,
      historicalStats
    );

    expect(anomaly).toBeNull();
  });

  it("should investigate anomaly and detect likely error", async () => {
    const historicalStats = {
      sku: "TEST123",
      mean: 1000,
      median: 1000,
      std: 100,
      min: 800,
      max: 1200,
      dataPoints: 50,
      lastUpdated: new Date(),
    };

    const currentPrice = 300; // Way below minimum - likely error

    const investigation = await (agent as any).investigateAnomaly(
      "TEST123",
      "TestDistributor",
      currentPrice,
      historicalStats,
      -7 // z-score
    );

    expect(investigation.likelyError).toBe(true);
    expect(investigation.confidence).toBeGreaterThan(0.8);
  });

  it("should detect promotion (significant discount in valid range)", async () => {
    const historicalStats = {
      sku: "TEST123",
      mean: 1000,
      median: 1000,
      std: 100,
      min: 800,
      max: 1200,
      dataPoints: 50,
      lastUpdated: new Date(),
    };

    const currentPrice = 750; // 25% discount - possible promotion

    const investigation = await (agent as any).investigateAnomaly(
      "TEST123",
      "TestDistributor",
      currentPrice,
      historicalStats,
      -2.5
    );

    expect(investigation.promotion).toBe(true);
    expect(investigation.discountPercentage).toBeGreaterThan(20);
  });

  it("should calculate severity correctly", () => {
    const agent = new PriceAnomalyDetectionAgent(mockLogger as any);

    const criticalCase = (agent as any).calculateSeverity(6, { likelyError: true, confidence: 0.9 });
    expect(criticalCase).toBe("critical");

    const highCase = (agent as any).calculateSeverity(4.5, { likelyError: false, confidence: 0.8 });
    expect(highCase).toBe("high");

    const mediumCase = (agent as any).calculateSeverity(3.6, { likelyError: false, confidence: 0.7 });
    expect(mediumCase).toBe("medium");

    const lowCase = (agent as any).calculateSeverity(3.1, { likelyError: false, confidence: 0.6 });
    expect(lowCase).toBe("low");
  });
});

// ================================================================================
// PREDICTIVE QUOTE FAILURE TESTS
// ================================================================================

describe("QuoteFailurePredictionAgent", () => {
  let agent: QuoteFailurePredictionAgent;

  beforeEach(() => {
    agent = new QuoteFailurePredictionAgent(mockLogger as any);
    jest.clearAllMocks();
  });

  it("should assess quote and return risk assessment", async () => {
    const mockQuote = {
      id: "quote-123",
      customer_id: "customer-456",
      invited_suppliers: ["supplier-1", "supplier-2"],
      requirements: {
        items: [
          { sku: "ITEM-1", quantity: 10 },
          { sku: "ITEM-2", quantity: 5 },
        ],
      },
      status: "draft",
      created_at: new Date(),
    };

    const assessment = await agent.predictQuoteFailure(mockQuote as any);

    expect(assessment).toBeDefined();
    expect(assessment.quote_id).toBe("quote-123");
    expect(assessment.failure_probability).toBeGreaterThanOrEqual(0);
    expect(assessment.failure_probability).toBeLessThanOrEqual(1);
    expect(assessment.risk_level).toBeDefined();
    expect(["low", "medium", "high", "critical"]).toContain(assessment.risk_level);
  });

  it("should classify risk levels correctly", () => {
    expect((agent as any).classifyRisk(0.8)).toBe("critical");
    expect((agent as any).classifyRisk(0.6)).toBe("high");
    expect((agent as any).classifyRisk(0.4)).toBe("medium");
    expect((agent as any).classifyRisk(0.2)).toBe("low");
  });

  it("should detect timing risk for after-hours quotes", async () => {
    const afterHoursDate = new Date();
    afterHoursDate.setHours(19, 0, 0, 0); // 7 PM

    const mockQuote = {
      id: "quote-123",
      customer_id: "customer-456",
      invited_suppliers: ["supplier-1"],
      requirements: { items: [] },
      status: "draft",
      created_at: afterHoursDate,
    };

    const timingAssessment = await (agent as any).assessTiming(mockQuote);

    expect(timingAssessment.factors.length).toBeGreaterThan(0);
    expect(timingAssessment.factors.some((f: any) => 
      f.factor.includes("business hours")
    )).toBe(true);
  });

  it("should detect timing risk for weekend quotes", async () => {
    const weekendDate = new Date();
    // Set to Sunday (day 0)
    weekendDate.setDate(weekendDate.getDate() + (7 - weekendDate.getDay()));
    weekendDate.setHours(10, 0, 0, 0);

    const mockQuote = {
      id: "quote-123",
      customer_id: "customer-456",
      invited_suppliers: ["supplier-1"],
      requirements: { items: [] },
      status: "draft",
      created_at: weekendDate,
    };

    const timingAssessment = await (agent as any).assessTiming(mockQuote);

    expect(timingAssessment.factors.some((f: any) => 
      f.factor.includes("weekend")
    )).toBe(true);
  });

  it("should detect complexity risk for custom specs", async () => {
    const mockQuote = {
      id: "quote-123",
      customer_id: "customer-456",
      invited_suppliers: ["supplier-1"],
      requirements: {
        items: [],
        custom_specs: true,
      },
      status: "draft",
      created_at: new Date(),
    };

    const complexityAssessment = await (agent as any).assessComplexity(mockQuote);

    expect(complexityAssessment.factors.some((f: any) => 
      f.factor.includes("Custom specifications")
    )).toBe(true);
  });
});

// ================================================================================
// DYNAMIC NEGOTIATION TESTS
// ================================================================================

describe("DynamicNegotiationAgent", () => {
  let agent: DynamicNegotiationAgent;

  beforeEach(() => {
    agent = new DynamicNegotiationAgent(mockLogger as any, {
      maxDiscount: 0.15,
      minMargin: 0.10,
    });
    jest.clearAllMocks();
  });

  it("should parse customer intent correctly - price objection", async () => {
    const feedback = {
      proposal_id: "prop-123",
      customer_id: "cust-456",
      feedback_text: "O preço está muito caro, preciso de um desconto",
      timestamp: new Date(),
    };

    const intent = await (agent as any).parseCustomerIntent(feedback);

    expect(intent.type).toBe("price_too_high");
    expect(intent.confidence).toBeGreaterThan(0.8);
  });

  it("should parse customer intent correctly - payment terms", async () => {
    const feedback = {
      proposal_id: "prop-123",
      customer_id: "cust-456",
      feedback_text: "Vocês têm opções de parcelamento ou financiamento?",
      timestamp: new Date(),
    };

    const intent = await (agent as any).parseCustomerIntent(feedback);

    expect(intent.type).toBe("payment_terms");
    expect(intent.confidence).toBeGreaterThan(0.8);
  });

  it("should detect urgency in feedback", async () => {
    const urgentFeedback = {
      proposal_id: "prop-123",
      customer_id: "cust-456",
      feedback_text: "Preciso urgentemente desta proposta aprovada hoje",
      timestamp: new Date(),
    };

    const intent = await (agent as any).parseCustomerIntent(urgentFeedback);

    expect(intent.urgency).toBe("high");
  });

  it("should determine negotiation strategy - counter offer", () => {
    const proposal = {
      id: "prop-123",
      total_price: 100000,
      margin: 0.25, // 25% margin
      discount: 0,
    };

    const intent = {
      type: "price_too_high",
      urgency: "medium",
      price_sensitivity: 0.7,
      negotiation_room: 0.6,
      key_objections: ["Price"],
      confidence: 0.85,
    };

    const strategy = (agent as any).determineNegotiationStrategy(proposal, intent);

    expect(strategy.action).toBe("counter_offer");
  });

  it("should determine negotiation strategy - add value when no margin", () => {
    const proposal = {
      id: "prop-123",
      total_price: 100000,
      margin: 0.12, // Only 12% margin (close to minimum)
      discount: 0,
    };

    const intent = {
      type: "price_too_high",
      urgency: "medium",
      price_sensitivity: 0.7,
      negotiation_room: 0.6,
      key_objections: ["Price"],
      confidence: 0.85,
    };

    const strategy = (agent as any).determineNegotiationStrategy(proposal, intent);

    expect(strategy.action).toBe("add_value");
  });

  it("should generate counter offer with appropriate discount", async () => {
    const proposal = {
      id: "prop-123",
      customer_id: "cust-456",
      quote_id: "quote-789",
      total_price: 100000,
      margin: 0.25,
      discount: 0,
      items: [],
      payment_terms: "standard",
      valid_until: new Date(),
      status: "sent",
    };

    const intent = {
      type: "price_too_high",
      urgency: "high",
      price_sensitivity: 0.8,
      negotiation_room: 0.7,
      key_objections: ["Price"],
      confidence: 0.9,
    };

    const strategy = { action: "counter_offer", reason: "Test" };

    const counterOffer = await (agent as any).generateCounterOffer(proposal, intent, strategy);

    expect(counterOffer).toBeDefined();
    expect(counterOffer.discount_percentage).toBeGreaterThan(0);
    expect(counterOffer.discount_percentage).toBeLessThanOrEqual(0.15);
    expect(counterOffer.new_price).toBeLessThan(proposal.total_price);
    expect(counterOffer.conditions.length).toBeGreaterThan(0);
  });

  it("should calculate financing options correctly", () => {
    const principal = 100000;
    const downPaymentPercent = 0.20;
    const termMonths = 24;
    const monthlyRate = 0.01; // 1% a.m.

    const financing = (agent as any).calculateFinancingOption(
      principal,
      downPaymentPercent,
      termMonths,
      monthlyRate
    );

    expect(financing.down_payment).toBe(20000);
    expect(financing.monthly_payment).toBeGreaterThan(0);
    expect(financing.total_cost).toBeGreaterThan(principal); // With interest
    expect(financing.term_months).toBe(24);
  });
});

// ================================================================================
// INTEGRATION TEST: FULL WORKFLOW
// ================================================================================

describe("Autonomous Agents Integration", () => {
  it("should work together in complete workflow", async () => {
    // 1. Self-healing scraper validates data quality
    const scraperAgent = new SelfHealingScraperAgent(mockLogger as any);
    const scrapedProducts = [
      { sku: "SOLAR-001", title: "Panel 550W", price: 850, distributor: "TestDist", category: "painel" },
      { sku: "SOLAR-002", title: "Panel 600W", price: 950, distributor: "TestDist", category: "painel" },
      { sku: "SOLAR-003", title: "Inverter 10kW", price: 5200, distributor: "TestDist", category: "inversor" },
      { sku: "SOLAR-004", title: "Battery 5kWh", price: 8500, distributor: "TestDist", category: "bateria" },
      { sku: "SOLAR-005", title: "Structure Kit", price: 1200, distributor: "TestDist", category: "estrutura" },
      { sku: "SOLAR-006", title: "Cable 10mm", price: 15, distributor: "TestDist", category: "cabo" },
      { sku: "SOLAR-007", title: "Panel 450W", price: 750, distributor: "TestDist", category: "painel" },
      { sku: "SOLAR-008", title: "Inverter 5kW", price: 3800, distributor: "TestDist", category: "inversor" },
      { sku: "SOLAR-009", title: "Battery 10kWh", price: 15000, distributor: "TestDist", category: "bateria" },
      { sku: "SOLAR-010", title: "Monitoring System", price: 2500, distributor: "TestDist", category: "monitoring" },
      { sku: "SOLAR-011", title: "Panel 500W", price: 800, distributor: "TestDist", category: "painel" },
    ];

    const validation = (scraperAgent as any).validateProducts(scrapedProducts);
    expect(validation.qualityScore).toBeGreaterThan(0.9);

    // 2. Quote prediction analyzes risk
    const predictionAgent = new QuoteFailurePredictionAgent(mockLogger as any);
    const mockQuote = {
      id: "quote-integration-test",
      customer_id: "customer-test",
      invited_suppliers: ["TestDist", "OtherDist"],
      requirements: {
        items: scrapedProducts.slice(0, 5).map(p => ({ sku: p.sku, quantity: 10 })),
      },
      status: "draft",
      created_at: new Date(),
    };

    const riskAssessment = await predictionAgent.predictQuoteFailure(mockQuote as any);
    expect(riskAssessment.failure_probability).toBeLessThan(0.5); // Should be low risk

    // 3. Negotiation agent responds to feedback
    const negotiationAgent = new DynamicNegotiationAgent(mockLogger as any);
    const mockProposal = {
      id: "prop-integration-test",
      customer_id: "customer-test",
      quote_id: "quote-integration-test",
      total_price: 50000,
      margin: 0.20,
      discount: 0,
      items: [],
      payment_terms: "standard",
      valid_until: new Date(),
      status: "sent",
    };

    const customerFeedback = {
      proposal_id: "prop-integration-test",
      customer_id: "customer-test",
      feedback_text: "Gostei da proposta mas o preço está um pouco alto. Tem como melhorar?",
      timestamp: new Date(),
    };

    const counterOffer = await negotiationAgent.negotiatePriceAutonomously(
      mockProposal as any,
      customerFeedback as any
    );

    expect(counterOffer).toBeDefined();
    expect(counterOffer?.new_price).toBeLessThan(mockProposal.total_price);

    // Workflow completed successfully
    expect(true).toBe(true);
  });
});
