import { MedusaService } from "@medusajs/framework/utils";
import {
  PriceScoreResult,
  DynamicMarkupResult,
  ChannelPricingResult,
  BundlePricingResult,
  BundleConfiguration,
  FinancingCalculation,
  FinancingTier,
  PriceMatchResult,
  PriceMatchPolicy,
  PsychologicalPricingResult,
  PsychologicalPricingConfig,
  DynamicPricingAdjustments,
  DynamicPricingContext,
  ProjectSplits,
  ProjectPricingResult,
  CalculateProjectPricingDTO,
  PriceCategory,
  CustomerChannel,
  Region,
  Scenario,
} from "./types";

/**
 * Pricing Intelligence Module Service
 * 
 * Centraliza todos os algoritmos de precificação baseados em:
 * - PRICING_STRATEGY_YSH.md (10 seções de estratégia)
 * - BUSINESS_RULES_EXTRACTED.md (regras RN-001 a RN-010)
 * 
 * Responsabilidades:
 * 1. Análise de competitividade de preços
 * 2. Aplicação de markup dinâmico baseado em cenários
 * 3. Precificação por canal (B2C, B2B, Distribuidor, Marketplace)
 * 4. Precificação psicológica (charm pricing, anchor pricing)
 * 5. Precificação dinâmica contextual (tempo, estoque, urgência)
 * 6. Bundles estratégicos
 * 7. Financiamento e parcelas
 * 8. Price matching com competidores
 * 9. Splits de projeto por região e cenário
 * 10. KPIs e métricas de rentabilidade
 */
export default class PricingModuleService extends MedusaService({}) {
  constructor(container) {
    super(arguments[0]);
  }

  /**
   * Calcula score de competitividade de preço
   * 
   * Algoritmo de PRICING_STRATEGY_YSH.md:
   * - Encontra melhor preço entre concorrentes
   * - Calcula delta percentual
   * - Classifica: excellent (≤2%), good (≤5%), average (≤10%), expensive (>10%)
   */
  async calculatePriceScore(
    quotedPrice: number,
    competitorPrices: number[]
  ): Promise<PriceScoreResult> {
    const validPrices = competitorPrices.filter((p) => p > 0);

    if (validPrices.length === 0) {
      return {
        category: "average",
        delta: 0,
        bestPrice: quotedPrice,
        explanation: "Sem preços de competidores para comparação",
      };
    }

    const bestPrice = Math.min(...validPrices);
    const delta = ((quotedPrice - bestPrice) / bestPrice) * 100;

    let category: PriceCategory = "expensive";
    let explanation = "";

    if (delta <= 2) {
      category = "excellent";
      explanation = `Preço excelente, apenas ${delta.toFixed(1)}% acima do melhor mercado`;
    } else if (delta <= 5) {
      category = "good";
      explanation = `Bom preço competitivo, ${delta.toFixed(1)}% acima do melhor mercado`;
    } else if (delta <= 10) {
      category = "average";
      explanation = `Preço médio de mercado, ${delta.toFixed(1)}% acima do melhor`;
    } else {
      category = "expensive";
      explanation = `Preço alto, ${delta.toFixed(1)}% acima do melhor mercado`;
    }

    return { category, delta, bestPrice, explanation };
  }

  /**
   * Aplica markup dinâmico baseado em competitividade e cenário
   * 
   * PRICING_STRATEGY_YSH.md - Dynamic Markup:
   * - excellent (≤2%): +5% markup adicional
   * - good (≤5%): +2% markup adicional
   * - average (≤10%): -3% markup
   * - expensive (>10%): -8% markup
   * 
   * BUSINESS_RULES_EXTRACTED.md - RN-006:
   * - Otimista: 32-40% margem
   * - Neutro: 25-32% margem
   * - Pessimista: 19-28% margem
   * 
   * RN-008: Margem mínima 15%
   */
  async applyDynamicMarkup(
    costPrice: number,
    priceCategory: PriceCategory,
    scenario: Scenario = "neutro"
  ): Promise<DynamicMarkupResult> {
    // Markup base por cenário
    const baseMarkups = {
      otimista: 35, // 35% base cenário otimista
      neutro: 28, // 28% base cenário neutro
      pessimista: 22, // 22% base cenário pessimista
    };

    // Ajustes por categoria de preço
    const categoryAdjustments = {
      excellent: 5, // +5% quando temos preço excelente
      good: 2, // +2% quando temos bom preço
      average: -3, // -3% quando preço médio
      expensive: -8, // -8% quando preço alto
    };

    const baseMarkup = baseMarkups[scenario];
    const adjustment = categoryAdjustments[priceCategory];
    const finalMarkup = baseMarkup + adjustment;

    // RN-008: Validar margem mínima viável (15%)
    if (finalMarkup < 15) {
      throw new Error(
        `Margem ${finalMarkup.toFixed(1)}% abaixo do mínimo viável (15%). ` +
        `Projeto não rentável com custo R$ ${costPrice.toLocaleString("pt-BR")} ` +
        `e categoria de preço "${priceCategory}".`
      );
    }

    const sellingPrice = costPrice * (1 + finalMarkup / 100);
    
    // Margem bruta: (Preço - Custo) / Preço
    const grossMargin = ((sellingPrice - costPrice) / sellingPrice) * 100;
    
    // Margem líquida: considera custos operacionais (~8-10% do preço)
    const operationalCosts = sellingPrice * 0.09; // 9% média
    const netMargin = ((sellingPrice - costPrice - operationalCosts) / sellingPrice) * 100;

    return {
      costPrice,
      baseMarkup,
      adjustment,
      finalMarkup,
      sellingPrice,
      grossMargin,
      netMargin,
      scenario,
    };
  }

  /**
   * Aplica precificação diferenciada por canal
   * 
   * PRICING_STRATEGY_YSH.md - Channel Pricing:
   * - B2C: 0% desconto (preço cheio)
   * - Integrador B2B: 15% desconto
   * - Distribuidor: 20% desconto
   * - Marketplace: 10% desconto
   * - White-label: 25% desconto
   */
  async applyChannelPricing(
    basePrice: number,
    channel: CustomerChannel
  ): Promise<ChannelPricingResult> {
    const channelConfig = {
      b2c: { discount: 0, commission: 0 },
      integrator_b2b: { discount: 15, commission: 10 },
      distributor: { discount: 20, commission: 15 },
      marketplace: { discount: 10, commission: 12 },
      white_label: { discount: 25, commission: 8 },
    };

    const config = channelConfig[channel] || channelConfig.b2c;
    const channelPrice = basePrice * (1 - config.discount / 100);
    const commission = channelPrice * (config.commission / 100);

    return {
      basePrice,
      channel,
      discount: config.discount,
      channelPrice,
      commission,
    };
  }

  /**
   * Calcula precificação de bundle com desconto estratégico
   * 
   * PRICING_STRATEGY_YSH.md - Bundling Strategy:
   * - Kit Residencial Completo: 12% desconto, manter 28% margem
   * - Sistema Solar + Bateria: 8% desconto, manter 25% margem
   * - Monitoramento IoT: 20% desconto em plano anual
   */
  async calculateBundlePricing(
    config: BundleConfiguration
  ): Promise<BundlePricingResult> {
    const individualTotal = config.components.reduce(
      (sum, item) => sum + item.unit_price * item.quantity,
      0
    );

    const bundleDiscount = config.bundle_discount || 12; // 12% padrão
    const bundlePrice = individualTotal * (1 - bundleDiscount / 100);
    const savings = individualTotal - bundlePrice;

    // Estimar custo assumindo margem original de 30%
    const estimatedCost = individualTotal * 0.70; // 70% do preço = custo
    const margin = ((bundlePrice - estimatedCost) / bundlePrice) * 100;

    // Verificar se mantém margem-alvo (RN-006: mínimo 15%)
    const profitable = margin >= (config.target_margin || 15);

    return {
      individual_total: individualTotal,
      bundle_discount: bundleDiscount,
      bundle_price: bundlePrice,
      savings,
      margin,
      profitable,
    };
  }

  /**
   * Calcula financiamento com juros
   * 
   * PRICING_STRATEGY_YSH.md - Financing Strategy:
   * - Tier 1: 12× sem juros (CET 4% a.a.)
   * - Tier 2: 24× com 0.99% a.m. (CET 25.9% a.a.)
   * - Tier 3: 60× com 1.49% a.m. (CET 127.2% a.a.)
   */
  async calculateFinancing(
    principal: number,
    installments: number
  ): Promise<FinancingCalculation> {
    const tiers: FinancingTier[] = [
      {
        name: "12× sem juros",
        installments: 12,
        monthly_rate: 0,
        annual_cet: 4.0,
        minimum_purchase: 3000,
        maximum_purchase: 100000,
      },
      {
        name: "24× com juros",
        installments: 24,
        monthly_rate: 0.99,
        annual_cet: 25.9,
        minimum_purchase: 5000,
        maximum_purchase: 200000,
      },
      {
        name: "60× longo prazo",
        installments: 60,
        monthly_rate: 1.49,
        annual_cet: 127.2,
        minimum_purchase: 10000,
        maximum_purchase: 500000,
      },
    ];

    const tier = tiers.find((t) => t.installments === installments) || tiers[0];

    let installmentValue: number;
    let totalAmount: number;

    if (tier.monthly_rate === 0) {
      // Sem juros
      installmentValue = principal / installments;
      totalAmount = principal;
    } else {
      // Com juros - Fórmula Price
      const monthlyRate = tier.monthly_rate / 100;
      installmentValue =
        principal * (monthlyRate * Math.pow(1 + monthlyRate, installments)) /
        (Math.pow(1 + monthlyRate, installments) - 1);
      totalAmount = installmentValue * installments;
    }

    const totalInterest = totalAmount - principal;
    const effectiveRate = (totalInterest / principal) * 100;

    return {
      principal,
      tier,
      installment_value: installmentValue,
      total_amount: totalAmount,
      total_interest: totalInterest,
      effective_rate: effectiveRate,
    };
  }

  /**
   * Avalia solicitação de price matching
   * 
   * PRICING_STRATEGY_YSH.md - Price Matching:
   * - Desconto máximo: 15%
   * - Margem mínima: 12%
   * - Exigir comprovação de preço competidor
   * - Whitelist de competidores válidos
   */
  async evaluatePriceMatch(
    originalPrice: number,
    competitorPrice: number,
    costPrice: number,
    policy?: Partial<PriceMatchPolicy>
  ): Promise<PriceMatchResult> {
    const defaultPolicy: PriceMatchPolicy = {
      max_discount: 15,
      min_margin: 12,
      require_proof: true,
      competitor_whitelist: [
        "Edeltec",
        "Fortlev",
        "Odex",
        "Solfácil",
        "NeoSolar",
        "Blue Sol",
        "Aldo Solar",
      ],
    };

    const finalPolicy = { ...defaultPolicy, ...policy };

    // Calcular desconto necessário
    const discountNeeded = ((originalPrice - competitorPrice) / originalPrice) * 100;

    // Preço igualado
    const matchedPrice = competitorPrice;

    // Margem após match
    const marginAfterMatch = ((matchedPrice - costPrice) / matchedPrice) * 100;

    let approved = true;
    let rejectionReason: string | undefined;

    // Validações
    if (discountNeeded > finalPolicy.max_discount) {
      approved = false;
      rejectionReason = `Desconto necessário (${discountNeeded.toFixed(1)}%) excede máximo permitido (${finalPolicy.max_discount}%)`;
    } else if (marginAfterMatch < finalPolicy.min_margin) {
      approved = false;
      rejectionReason = `Margem após match (${marginAfterMatch.toFixed(1)}%) abaixo do mínimo (${finalPolicy.min_margin}%)`;
    } else if (competitorPrice >= originalPrice) {
      approved = false;
      rejectionReason = "Preço do competidor não é inferior ao nosso";
    }

    return {
      original_price: originalPrice,
      competitor_price: competitorPrice,
      matched_price: approved ? matchedPrice : originalPrice,
      discount_applied: approved ? discountNeeded : 0,
      margin_after_match: marginAfterMatch,
      approved,
      rejection_reason: rejectionReason,
    };
  }

  /**
   * Aplica precificação psicológica
   * 
   * PRICING_STRATEGY_YSH.md - Psychological Pricing:
   * - Charm pricing: terminações .99 ou .95
   * - Anchor pricing: mostrar preço "De/Por"
   * - Urgência: "Últimas unidades", "Oferta por tempo limitado"
   */
  async applyPsychologicalPricing(
    basePrice: number,
    config?: Partial<PsychologicalPricingConfig>
  ): Promise<PsychologicalPricingResult> {
    const defaultConfig: PsychologicalPricingConfig = {
      use_charm_pricing: true,
      use_anchor_pricing: true,
      anchor_multiplier: 1.25, // Mostrar 25% acima como "De"
      urgency_message: false,
      scarcity_threshold: 10,
    };

    const finalConfig = { ...defaultConfig, ...config };

    let charmPrice = basePrice;
    let anchorPrice: number | undefined;
    let displaySavings: number | undefined;
    let urgencyTag: string | undefined;

    // Charm pricing
    if (finalConfig.use_charm_pricing) {
      // Arredondar para .99
      charmPrice = Math.ceil(basePrice) - 0.01;
      
      // Se diferença for muito pequena, usar .95
      if (charmPrice - basePrice < 1) {
        charmPrice = Math.floor(basePrice) + 0.95;
      }
    }

    // Anchor pricing
    if (finalConfig.use_anchor_pricing) {
      anchorPrice = charmPrice * finalConfig.anchor_multiplier;
      displaySavings = anchorPrice - charmPrice;
    }

    // Urgência
    if (finalConfig.urgency_message) {
      urgencyTag = "⚡ Oferta por tempo limitado";
    }

    return {
      original_price: basePrice,
      charm_price: charmPrice,
      anchor_price: anchorPrice,
      display_savings: displaySavings,
      urgency_tag: urgencyTag,
    };
  }

  /**
   * Calcula ajustes de precificação dinâmica contextual
   * 
   * PRICING_STRATEGY_YSH.md - Dynamic Pricing:
   * Considera 7 fatores:
   * 1. Horário do dia
   * 2. Dia da semana
   * 3. Sazonalidade
   * 4. Nível de estoque
   * 5. Competição
   * 6. Segmento do cliente
   * 7. Urgência do cliente
   */
  async calculateDynamicAdjustments(
    context: Partial<DynamicPricingContext>
  ): Promise<DynamicPricingAdjustments> {
    let timeAdjustment = 0;
    let inventoryAdjustment = 0;
    let competitionAdjustment = 0;
    let segmentAdjustment = 0;
    let urgencyAdjustment = 0;

    // Horário do dia
    if (context.time_of_day === "evening" || context.time_of_day === "night") {
      timeAdjustment = -2; // -2% fora do horário comercial
    } else if (context.time_of_day === "morning") {
      timeAdjustment = 1; // +1% pico manhã
    }

    // Estoque
    if (context.inventory_level === "high") {
      inventoryAdjustment = -5; // -5% para escoar estoque
    } else if (context.inventory_level === "low") {
      inventoryAdjustment = 3; // +3% escassez
    }

    // Competição
    if (context.competition_level === "high") {
      competitionAdjustment = -5; // -5% mercado competitivo
    } else if (context.competition_level === "low") {
      competitionAdjustment = 2; // +2% pouca competição
    }

    // Segmento cliente
    if (context.customer_segment === "vip") {
      segmentAdjustment = 5; // +5% cliente premium
    } else if (context.customer_segment === "new") {
      segmentAdjustment = -10; // -10% aquisição
    }

    // Urgência
    if (context.urgency === "high") {
      urgencyAdjustment = -15; // -15% fechar rápido
    } else if (context.urgency === "low") {
      urgencyAdjustment = 0; // Sem ajuste
    }

    const totalAdjustment =
      timeAdjustment +
      inventoryAdjustment +
      competitionAdjustment +
      segmentAdjustment +
      urgencyAdjustment;

    return {
      time_adjustment: timeAdjustment,
      inventory_adjustment: inventoryAdjustment,
      competition_adjustment: competitionAdjustment,
      segment_adjustment: segmentAdjustment,
      urgency_adjustment: urgencyAdjustment,
      total_adjustment: totalAdjustment,
    };
  }

  /**
   * Calcula splits de projeto por região e cenário
   * 
   * BUSINESS_RULES_EXTRACTED.md - Seção 5:
   * - Equipamentos: 55-65% (varia por cenário)
   * - Mão de Obra: 10-15% (Sudeste +20%, Nordeste -15%)
   * - Projeto: 6-9%
   * - ART/TRT: 2%
   * - Homologação: 3-5%
   * - Comissão: 4-6%
   * - Logística: 3-7% (Norte +50%, Sul +20%)
   * - Margem/Contingência: 2-11%
   */
  async calculateProjectSplits(
    totalValue: number,
    region: Region,
    scenario: Scenario
  ): Promise<ProjectSplits> {
    // Percentuais base por cenário
    const scenarioSplits = {
      otimista: {
        equipments: 55,
        labor: 15,
        engineering: 9,
        art_trt: 2,
        homologation: 3,
        commission: 6,
        logistics: 4,
        margin: 8,
      },
      neutro: {
        equipments: 60,
        labor: 13,
        engineering: 7,
        art_trt: 2,
        homologation: 4,
        commission: 5,
        logistics: 4,
        margin: 5,
      },
      pessimista: {
        equipments: 65,
        labor: 10,
        engineering: 6,
        art_trt: 2,
        homologation: 5,
        commission: 4,
        logistics: 6,
        margin: 2,
      },
    };

    const baseSplits = scenarioSplits[scenario];

    // Ajustes regionais
    let laborAdjustment = 0;
    let logisticsAdjustment = 0;

    if (region === "nordeste") {
      laborAdjustment = -15; // -15% mão de obra no Nordeste
      logisticsAdjustment = 0;
    } else if (region === "sul") {
      laborAdjustment = 0;
      logisticsAdjustment = 20; // +20% logística no Sul
    } else if (region === "norte") {
      laborAdjustment = 0;
      logisticsAdjustment = 50; // +50% logística no Norte
    }

    const labor = baseSplits.labor * (1 + laborAdjustment / 100);
    const logistics = baseSplits.logistics * (1 + logisticsAdjustment / 100);

    // Calcular valores absolutos
    const splits: ProjectSplits = {
      scenario,
      region,
      total_value: totalValue,
      equipments: {
        percentage: baseSplits.equipments,
        value: (totalValue * baseSplits.equipments) / 100,
      },
      labor: {
        percentage: labor,
        value: (totalValue * labor) / 100,
      },
      engineering: {
        percentage: baseSplits.engineering,
        value: (totalValue * baseSplits.engineering) / 100,
      },
      art_trt: {
        percentage: baseSplits.art_trt,
        value: (totalValue * baseSplits.art_trt) / 100,
      },
      homologation: {
        percentage: baseSplits.homologation,
        value: (totalValue * baseSplits.homologation) / 100,
      },
      commission: {
        percentage: baseSplits.commission,
        value: (totalValue * baseSplits.commission) / 100,
      },
      logistics: {
        percentage: logistics,
        value: (totalValue * logistics) / 100,
      },
      margin: {
        percentage: baseSplits.margin,
        value: (totalValue * baseSplits.margin) / 100,
      },
    };

    return splits;
  }

  /**
   * Orquestra cálculo completo de precificação de projeto
   * 
   * Integra todos os algoritmos:
   * 1. Price score (se houver competidores)
   * 2. Dynamic markup baseado em competitividade
   * 3. Channel pricing
   * 4. Psychological pricing
   * 5. Dynamic adjustments contextuais
   * 6. Project splits regionais
   * 7. Validação de KPIs
   */
  async calculateProjectPricing(
    data: CalculateProjectPricingDTO
  ): Promise<ProjectPricingResult> {
    const {
      cost_price,
      region = "sudeste",
      customer_channel = "b2c",
      competitor_prices = [],
      scenario = "neutro",
      apply_psychological_pricing = true,
      dynamic_context = {},
    } = data;

    // 1. Price score (se houver competidores)
    let priceScore: PriceScoreResult | undefined;
    let priceCategory: PriceCategory = "average";

    if (competitor_prices.length > 0) {
      priceScore = await this.calculatePriceScore(cost_price, competitor_prices);
      priceCategory = priceScore.category;
    }

    // 2. Dynamic markup
    const dynamicMarkup = await this.applyDynamicMarkup(
      cost_price,
      priceCategory,
      scenario
    );

    // 3. Channel pricing
    const channelPricing = await this.applyChannelPricing(
      dynamicMarkup.sellingPrice,
      customer_channel
    );

    // 4. Ajustes regionais de geração (RN-005)
    const regionalFactors = {
      nordeste: 1.09,
      centro_oeste: 1.07,
      sudeste: 1.00,
      norte: 0.98,
      sul: 0.91,
    };

    const regionalAdjustments = {
      generation_factor: regionalFactors[region],
      cost_factor: 1.0, // Simplificado, poderia variar por região
    };

    // 5. Dynamic adjustments contextuais
    let dynamicAdjustments: DynamicPricingAdjustments | undefined;
    let adjustedPrice = channelPricing.channelPrice;

    if (Object.keys(dynamic_context).length > 0) {
      dynamicAdjustments = await this.calculateDynamicAdjustments(dynamic_context);
      adjustedPrice = channelPricing.channelPrice * (1 + dynamicAdjustments.total_adjustment / 100);
    }

    // 6. Psychological pricing
    let psychologicalPricing: PsychologicalPricingResult | undefined;
    let recommendedPrice = adjustedPrice;

    if (apply_psychological_pricing) {
      psychologicalPricing = await this.applyPsychologicalPricing(adjustedPrice);
      recommendedPrice = psychologicalPricing.charm_price;
    }

    // 7. Project splits
    const projectSplits = await this.calculateProjectSplits(
      recommendedPrice,
      region,
      scenario
    );

    // 8. Validação de KPIs
    const grossMargin = dynamicMarkup.grossMargin;
    const netMargin = dynamicMarkup.netMargin;
    const meetsTarget = grossMargin >= 25 && netMargin >= 15; // RN-006

    return {
      cost_price,
      price_score: priceScore,
      dynamic_markup: dynamicMarkup,
      channel_pricing: channelPricing,
      regional_adjustments: regionalAdjustments,
      psychological_pricing: psychologicalPricing,
      dynamic_adjustments: dynamicAdjustments,
      project_splits: projectSplits,
      final_price: adjustedPrice,
      recommended_price: recommendedPrice,
      kpis: {
        gross_margin: grossMargin,
        net_margin: netMargin,
        meets_target: meetsTarget,
      },
    };
  }
}
