/**
 * Dynamic Negotiation Agent
 * 
 * Capacidades autônomas:
 * - Negociação automática de preços dentro de limites
 * - Contra-propostas inteligentes baseadas em contexto
 * - Análise de intenção do cliente
 * - Condições personalizadas
 * - Registro de decisões para aprendizado
 * 
 * Impacto esperado: +25% em taxa de conversão
 */

import { Logger } from "@medusajs/framework/logger";

// ================================================================================
// TYPES
// ================================================================================

interface Proposal {
  id: string;
  customer_id: string;
  quote_id: string;
  total_price: number;
  items: Array<{
    sku: string;
    quantity: number;
    unit_price: number;
    total_price: number;
  }>;
  margin: number;
  discount: number;
  payment_terms: string;
  valid_until: Date;
  status: string;
  metadata?: Record<string, any>;
}

interface CustomerFeedback {
  proposal_id: string;
  customer_id: string;
  feedback_text: string;
  timestamp: Date;
  sentiment?: "positive" | "neutral" | "negative";
}

interface CustomerIntent {
  type: "price_too_high" | "payment_terms" | "add_features" | "remove_features" | "timing" | "other";
  urgency: "low" | "medium" | "high";
  price_sensitivity: number; // 0.0 to 1.0
  negotiation_room: number; // 0.0 to 1.0
  key_objections: string[];
  confidence: number;
}

interface CounterProposal {
  proposal_id: string;
  original_price: number;
  discount_percentage: number;
  new_price: number;
  conditions: string[];
  valid_until: Date;
  agent_confidence: number;
  reasoning: string;
  expected_acceptance: number;
}

interface NegotiationDecision {
  proposal_id: string;
  decision: "counter_offer" | "hold_firm" | "escalate" | "accept_terms";
  discount_offered: number;
  conditions_added: string[];
  reasoning: string;
  timestamp: Date;
  awaiting_feedback: boolean;
}

interface FinancingOption {
  type: "installments" | "lease" | "financing";
  down_payment: number;
  monthly_payment: number;
  term_months: number;
  interest_rate: number;
  total_cost: number;
}

// ================================================================================
// DYNAMIC NEGOTIATION AGENT
// ================================================================================

export class DynamicNegotiationAgent {
  private logger: Logger;
  private maxDiscount: number = 0.15; // 15% max discount
  private minMargin: number = 0.10; // 10% minimum margin

  constructor(logger: Logger, config?: { maxDiscount?: number; minMargin?: number }) {
    this.logger = logger;
    if (config?.maxDiscount) this.maxDiscount = config.maxDiscount;
    if (config?.minMargin) this.minMargin = config.minMargin;
  }

  // ================================================================================
  // MAIN NEGOTIATION METHOD
  // ================================================================================

  async negotiatePriceAutonomously(
    proposal: Proposal,
    customerFeedback: CustomerFeedback
  ): Promise<CounterProposal | null> {
    
    this.logger.info(
      `[Negotiation] 🤝 Starting autonomous negotiation for proposal ${proposal.id}`
    );

    // Step 1: Parse customer intent
    const intent = await this.parseCustomerIntent(customerFeedback);

    this.logger.info(
      `[Negotiation] 📊 Customer intent: ${intent.type} (urgency: ${intent.urgency}, confidence: ${(intent.confidence * 100).toFixed(0)}%)`
    );

    // Step 2: Decide negotiation strategy
    const strategy = this.determineNegotiationStrategy(proposal, intent);

    this.logger.info(`[Negotiation] 🎯 Strategy: ${strategy.action}`);

    // Step 3: Execute strategy
    let counterProposal: CounterProposal | null = null;

    if (strategy.action === "counter_offer") {
      counterProposal = await this.generateCounterOffer(proposal, intent, strategy);
    } else if (strategy.action === "payment_terms") {
      counterProposal = await this.generateFinancingOffer(proposal, intent);
    } else if (strategy.action === "add_value") {
      counterProposal = await this.generateValueAddOffer(proposal, intent);
    } else if (strategy.action === "hold_firm") {
      await this.sendHoldFirmResponse(proposal, intent);
      return null;
    } else if (strategy.action === "escalate") {
      await this.escalateToHuman(proposal, intent, strategy.reason);
      return null;
    }

    // Step 4: Log decision for learning
    if (counterProposal) {
      await this.logNegotiationDecision(proposal, counterProposal, intent);

      // Step 5: Send counter proposal automatically
      await this.sendCounterProposal(proposal.customer_id, counterProposal);

      this.logger.info(
        `[Negotiation] ✅ Counter proposal sent: ` +
        `${counterProposal.discount_percentage.toFixed(1)}% discount, ` +
        `R$ ${counterProposal.new_price.toFixed(2)}`
      );
    }

    return counterProposal;
  }

  // ================================================================================
  // CUSTOMER INTENT PARSING
  // ================================================================================

  private async parseCustomerIntent(feedback: CustomerFeedback): Promise<CustomerIntent> {
    const text = feedback.feedback_text.toLowerCase();

    let type: CustomerIntent["type"] = "other";
    let urgency: CustomerIntent["urgency"] = "medium";
    let priceSensitivity = 0.5;
    let negotiationRoom = 0.5;
    const keyObjections: string[] = [];
    let confidence = 0.6;

    // Pattern matching for intent type
    if (
      text.includes("caro") ||
      text.includes("preço") ||
      text.includes("desconto") ||
      text.includes("expensive") ||
      text.includes("high price")
    ) {
      type = "price_too_high";
      priceSensitivity = 0.8;
      keyObjections.push("Price objection");
      confidence = 0.85;
    }

    if (
      text.includes("pagamento") ||
      text.includes("parcelamento") ||
      text.includes("financiamento") ||
      text.includes("payment") ||
      text.includes("installment")
    ) {
      type = "payment_terms";
      keyObjections.push("Payment flexibility needed");
      confidence = 0.9;
    }

    if (
      text.includes("adicionar") ||
      text.includes("incluir") ||
      text.includes("add") ||
      text.includes("include")
    ) {
      type = "add_features";
      keyObjections.push("Wants additional features");
      confidence = 0.8;
    }

    if (
      text.includes("remover") ||
      text.includes("sem") ||
      text.includes("remove") ||
      text.includes("without")
    ) {
      type = "remove_features";
      keyObjections.push("Wants to reduce scope");
      confidence = 0.8;
    }

    if (
      text.includes("prazo") ||
      text.includes("urgente") ||
      text.includes("rápido") ||
      text.includes("deadline") ||
      text.includes("urgent")
    ) {
      type = "timing";
      urgency = "high";
      keyObjections.push("Timing concerns");
      confidence = 0.85;
    }

    // Urgency detection
    if (
      text.includes("urgente") ||
      text.includes("hoje") ||
      text.includes("agora") ||
      text.includes("imediatamente") ||
      text.includes("urgent") ||
      text.includes("immediately")
    ) {
      urgency = "high";
      negotiationRoom = 0.3; // Less room when urgent
    }

    if (
      text.includes("pensando") ||
      text.includes("analisando") ||
      text.includes("considerando") ||
      text.includes("thinking") ||
      text.includes("considering")
    ) {
      urgency = "low";
      negotiationRoom = 0.7; // More room when not urgent
    }

    // Price sensitivity detection
    if (
      text.includes("orçamento apertado") ||
      text.includes("limitado") ||
      text.includes("tight budget") ||
      text.includes("limited")
    ) {
      priceSensitivity = 0.9;
      negotiationRoom = 0.8;
    }

    if (
      text.includes("flexível") ||
      text.includes("flexible") ||
      text.includes("negociável") ||
      text.includes("negotiable")
    ) {
      negotiationRoom = 0.6;
    }

    return {
      type,
      urgency,
      price_sensitivity: priceSensitivity,
      negotiation_room: negotiationRoom,
      key_objections: keyObjections,
      confidence,
    };
  }

  // ================================================================================
  // NEGOTIATION STRATEGY
  // ================================================================================

  private determineNegotiationStrategy(
    proposal: Proposal,
    intent: CustomerIntent
  ): { action: string; reason: string } {
    
    // Calculate available margin
    const availableMargin = proposal.margin - this.minMargin;
    const maxPossibleDiscount = Math.min(availableMargin, this.maxDiscount);

    this.logger.info(
      `[Negotiation] 💰 Financial position:\n` +
      `  Current margin: ${(proposal.margin * 100).toFixed(1)}%\n` +
      `  Min margin: ${(this.minMargin * 100).toFixed(1)}%\n` +
      `  Available: ${(availableMargin * 100).toFixed(1)}%\n` +
      `  Max discount: ${(maxPossibleDiscount * 100).toFixed(1)}%`
    );

    // Strategy 1: Price objection with room to negotiate
    if (intent.type === "price_too_high" && maxPossibleDiscount > 0.05) {
      return {
        action: "counter_offer",
        reason: "Customer has price objection and we have margin to negotiate",
      };
    }

    // Strategy 2: Price objection but no margin
    if (intent.type === "price_too_high" && maxPossibleDiscount <= 0.05) {
      return {
        action: "add_value",
        reason: "Customer wants discount but margin is tight - offer added value instead",
      };
    }

    // Strategy 3: Payment terms objection
    if (intent.type === "payment_terms") {
      return {
        action: "payment_terms",
        reason: "Customer needs payment flexibility - offer financing options",
      };
    }

    // Strategy 4: Scope change
    if (intent.type === "add_features" || intent.type === "remove_features") {
      return {
        action: "escalate",
        reason: "Scope change requires human review and re-pricing",
      };
    }

    // Strategy 5: High urgency + price sensitivity
    if (intent.urgency === "high" && intent.price_sensitivity > 0.7 && maxPossibleDiscount > 0.03) {
      return {
        action: "counter_offer",
        reason: "Hot lead with price sensitivity - offer small discount with urgency conditions",
      };
    }

    // Strategy 6: Low urgency
    if (intent.urgency === "low") {
      return {
        action: "hold_firm",
        reason: "Customer not urgent - hold price and provide more value justification",
      };
    }

    // Default: Escalate for human review
    return {
      action: "escalate",
      reason: "Intent unclear or complex - requires human judgment",
    };
  }

  // ================================================================================
  // COUNTER OFFER GENERATION
  // ================================================================================

  private async generateCounterOffer(
    proposal: Proposal,
    intent: CustomerIntent,
    strategy: { action: string; reason: string }
  ): Promise<CounterProposal> {
    
    // Calculate discount based on urgency and negotiation room
    const availableMargin = proposal.margin - this.minMargin;
    const maxDiscount = Math.min(availableMargin * 0.7, this.maxDiscount);

    let discountPercentage: number;

    if (intent.urgency === "high") {
      // Hot lead - offer smaller discount
      discountPercentage = maxDiscount * 0.5;
    } else if (intent.urgency === "medium") {
      // Warm lead - offer moderate discount
      discountPercentage = maxDiscount * 0.7;
    } else {
      // Cold lead - offer larger discount to re-engage
      discountPercentage = maxDiscount * 0.9;
    }

    const discountAmount = proposal.total_price * discountPercentage;
    const newPrice = proposal.total_price - discountAmount;

    // Generate conditions
    const conditions: string[] = [];

    if (intent.urgency === "high") {
      conditions.push("Assinatura em até 48 horas");
    } else {
      conditions.push("Assinatura em até 7 dias");
    }

    if (discountPercentage > 0.05) {
      conditions.push("Pagamento à vista ou entrada mínima de 30%");
    }

    if (proposal.total_price > 50000) {
      conditions.push("Cronograma de entrega conforme disponibilidade de estoque");
    }

    // Calculate expected acceptance based on discount and urgency
    let expectedAcceptance = 0.5;
    
    if (intent.urgency === "high" && discountPercentage > 0.03) {
      expectedAcceptance = 0.8;
    } else if (intent.urgency === "medium" && discountPercentage > 0.05) {
      expectedAcceptance = 0.7;
    } else {
      expectedAcceptance = 0.6;
    }

    // Adjust for price sensitivity
    expectedAcceptance = Math.min(
      expectedAcceptance + (intent.price_sensitivity * 0.1),
      0.95
    );

    const validUntil = new Date();
    validUntil.setDate(validUntil.getDate() + (intent.urgency === "high" ? 2 : 5));

    return {
      proposal_id: proposal.id,
      original_price: proposal.total_price,
      discount_percentage: discountPercentage,
      new_price: newPrice,
      conditions,
      valid_until: validUntil,
      agent_confidence: intent.confidence * 0.9,
      reasoning: strategy.reason,
      expected_acceptance: expectedAcceptance,
    };
  }

  // ================================================================================
  // FINANCING OFFER GENERATION
  // ================================================================================

  private async generateFinancingOffer(
    proposal: Proposal,
    intent: CustomerIntent
  ): Promise<CounterProposal> {
    
    this.logger.info(`[Negotiation] 💳 Generating financing options for ${proposal.id}`);

    // Generate multiple financing options
    const options = [
      this.calculateFinancingOption(proposal.total_price, 0.10, 12, 0.0099), // 12x com 0.99% a.m.
      this.calculateFinancingOption(proposal.total_price, 0.20, 24, 0.0089), // 24x com 0.89% a.m.
      this.calculateFinancingOption(proposal.total_price, 0.30, 36, 0.0079), // 36x com 0.79% a.m.
    ];

    // Select best option based on customer profile
    const selectedOption = options[1]; // Default to 24x (middle option)

    const conditions = [
      `Entrada de ${(selectedOption.down_payment / proposal.total_price * 100).toFixed(0)}% (R$ ${selectedOption.down_payment.toFixed(2)})`,
      `${selectedOption.term_months}x de R$ ${selectedOption.monthly_payment.toFixed(2)}`,
      `Taxa de juros: ${(selectedOption.interest_rate * 100).toFixed(2)}% a.m.`,
      `Valor total com juros: R$ ${selectedOption.total_cost.toFixed(2)}`,
      "Sujeito à aprovação de crédito",
    ];

    return {
      proposal_id: proposal.id,
      original_price: proposal.total_price,
      discount_percentage: 0, // No discount, just payment flexibility
      new_price: selectedOption.total_cost,
      conditions,
      valid_until: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
      agent_confidence: 0.85,
      reasoning: "Customer needs payment flexibility - offering financing options",
      expected_acceptance: 0.75,
    };
  }

  private calculateFinancingOption(
    principal: number,
    downPaymentPercent: number,
    termMonths: number,
    monthlyRate: number
  ): FinancingOption {
    
    const downPayment = principal * downPaymentPercent;
    const financed = principal - downPayment;
    
    // Calculate monthly payment using PMT formula
    const monthlyPayment = 
      (financed * monthlyRate * Math.pow(1 + monthlyRate, termMonths)) / 
      (Math.pow(1 + monthlyRate, termMonths) - 1);

    const totalCost = downPayment + (monthlyPayment * termMonths);

    return {
      type: "financing",
      down_payment: downPayment,
      monthly_payment: monthlyPayment,
      term_months: termMonths,
      interest_rate: monthlyRate,
      total_cost: totalCost,
    };
  }

  // ================================================================================
  // VALUE-ADD OFFER GENERATION
  // ================================================================================

  private async generateValueAddOffer(
    proposal: Proposal,
    intent: CustomerIntent
  ): Promise<CounterProposal> {
    
    this.logger.info(`[Negotiation] 🎁 Generating value-add offer for ${proposal.id}`);

    const valueAdds = [
      "Garantia estendida de 12 meses (valor: R$ 1.500)",
      "Monitoramento IoT gratuito por 6 meses (valor: R$ 900)",
      "Seguro premium incluído no primeiro ano (valor: R$ 2.500)",
      "Instalação prioritária (economia de 7-10 dias)",
      "Suporte técnico dedicado por 90 dias",
    ];

    // Select top 2 value-adds
    const selectedValueAdds = valueAdds.slice(0, 2);

    return {
      proposal_id: proposal.id,
      original_price: proposal.total_price,
      discount_percentage: 0,
      new_price: proposal.total_price, // Same price
      conditions: [
        "Preço mantido com benefícios adicionais:",
        ...selectedValueAdds,
        "Válido para assinatura em até 5 dias",
      ],
      valid_until: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000),
      agent_confidence: 0.75,
      reasoning: "Margin is tight - offering added value instead of discount",
      expected_acceptance: 0.65,
    };
  }

  // ================================================================================
  // RESPONSE ACTIONS
  // ================================================================================

  private async sendHoldFirmResponse(proposal: Proposal, intent: CustomerIntent): Promise<void> {
    this.logger.info(`[Negotiation] 🛑 Holding firm on price for ${proposal.id}`);

    const message = 
      `Prezado cliente,\n\n` +
      `Agradecemos seu interesse em nossa proposta.\n\n` +
      `Gostaríamos de reforçar que o preço apresentado reflete:\n` +
      `- Produtos de alta qualidade com certificações internacionais\n` +
      `- Garantia estendida e suporte técnico especializado\n` +
      `- Melhor custo-benefício do mercado considerando todas as variáveis\n\n` +
      `Estamos à disposição para esclarecer qualquer dúvida sobre a composição do valor.\n\n` +
      `Atenciosamente,\nEquipe YSH Solar`;

    await this.sendEmailToCustomer(proposal.customer_id, "Re: Proposta Comercial", message);
  }

  private async escalateToHuman(
    proposal: Proposal,
    intent: CustomerIntent,
    reason: string
  ): Promise<void> {
    
    this.logger.warn(`[Negotiation] 🆙 Escalating ${proposal.id} to human: ${reason}`);

    await this.notifyTeam(
      `🆘 Negotiation Escalation Needed\n\n` +
      `Proposal: ${proposal.id}\n` +
      `Customer: ${proposal.customer_id}\n` +
      `Intent: ${intent.type}\n` +
      `Reason: ${reason}\n\n` +
      `Please review and respond manually.`
    );
  }

  // ================================================================================
  // LOGGING & LEARNING
  // ================================================================================

  private async logNegotiationDecision(
    proposal: Proposal,
    counterProposal: CounterProposal,
    intent: CustomerIntent
  ): Promise<void> {
    
    const decision: NegotiationDecision = {
      proposal_id: proposal.id,
      decision: "counter_offer",
      discount_offered: counterProposal.discount_percentage,
      conditions_added: counterProposal.conditions,
      reasoning: counterProposal.reasoning,
      timestamp: new Date(),
      awaiting_feedback: true,
    };

    this.logger.info(`[Negotiation] 📝 Logged decision for learning: ${JSON.stringify(decision)}`);

    // TODO: Save to database for ML training
  }

  // ================================================================================
  // HELPER METHODS (Stubs)
  // ================================================================================

  private async sendCounterProposal(
    customerId: string,
    counterProposal: CounterProposal
  ): Promise<void> {
    this.logger.info(`[Negotiation] 📧 Sending counter proposal to customer ${customerId}`);
    // TODO: Integrar com sistema de email/CRM
  }

  private async sendEmailToCustomer(
    customerId: string,
    subject: string,
    body: string
  ): Promise<void> {
    this.logger.info(`[Negotiation] 📧 Sending email to ${customerId}: ${subject}`);
    // TODO: Integrar com serviço de email
  }

  private async notifyTeam(message: string): Promise<void> {
    this.logger.info(`[Negotiation] 🔔 Team notification: ${message}`);
    // TODO: Integrar com Slack
  }
}
