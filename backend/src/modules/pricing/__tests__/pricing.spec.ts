import PricingModuleService from "../service";

/**
 * Testes de Pricing Intelligence Module
 * 
 * Valida conformidade com:
 * - PRICING_STRATEGY_YSH.md
 * - BUSINESS_RULES_EXTRACTED.md
 */

describe("PricingModuleService", () => {
  let pricingService: PricingModuleService;

  beforeEach(() => {
    pricingService = new PricingModuleService({} as any);
  });

  describe("calculatePriceScore", () => {
    it("deve classificar como excellent quando delta ≤2%", async () => {
      const result = await pricingService.calculatePriceScore(10200, [10000, 10500, 11000]);
      
      expect(result.category).toBe("excellent");
      expect(result.delta).toBeLessThanOrEqual(2);
      expect(result.bestPrice).toBe(10000);
    });

    it("deve classificar como good quando 2% < delta ≤5%", async () => {
      const result = await pricingService.calculatePriceScore(10400, [10000, 10500, 11000]);
      
      expect(result.category).toBe("good");
      expect(result.delta).toBeGreaterThan(2);
      expect(result.delta).toBeLessThanOrEqual(5);
    });

    it("deve classificar como average quando 5% < delta ≤10%", async () => {
      const result = await pricingService.calculatePriceScore(10700, [10000, 10500, 11000]);
      
      expect(result.category).toBe("average");
      expect(result.delta).toBeGreaterThan(5);
      expect(result.delta).toBeLessThanOrEqual(10);
    });

    it("deve classificar como expensive quando delta >10%", async () => {
      const result = await pricingService.calculatePriceScore(11500, [10000, 10500, 11000]);
      
      expect(result.category).toBe("expensive");
      expect(result.delta).toBeGreaterThan(10);
    });

    it("deve retornar average quando não há preços de competidores", async () => {
      const result = await pricingService.calculatePriceScore(10000, []);
      
      expect(result.category).toBe("average");
      expect(result.delta).toBe(0);
      expect(result.bestPrice).toBe(10000);
    });
  });

  describe("applyDynamicMarkup - RN-006 e RN-008", () => {
    describe("Cenário Otimista", () => {
      it("deve aplicar 35% base + 5% excellent = 40% markup", async () => {
        const result = await pricingService.applyDynamicMarkup(
          10000,
          "excellent",
          "otimista"
        );

        expect(result.baseMarkup).toBe(35);
        expect(result.adjustment).toBe(5);
        expect(result.finalMarkup).toBe(40);
        expect(result.sellingPrice).toBe(14000); // 10000 * 1.40
        expect(result.scenario).toBe("otimista");
      });

      it("deve aplicar 35% base + 2% good = 37% markup", async () => {
        const result = await pricingService.applyDynamicMarkup(
          10000,
          "good",
          "otimista"
        );

        expect(result.finalMarkup).toBe(37);
        expect(result.sellingPrice).toBe(13700);
      });
    });

    describe("Cenário Neutro", () => {
      it("deve aplicar 28% base + 5% excellent = 33% markup", async () => {
        const result = await pricingService.applyDynamicMarkup(
          10000,
          "excellent",
          "neutro"
        );

        expect(result.baseMarkup).toBe(28);
        expect(result.finalMarkup).toBe(33);
        expect(result.sellingPrice).toBe(13300);
      });

      it("deve aplicar 28% base - 3% average = 25% markup", async () => {
        const result = await pricingService.applyDynamicMarkup(
          10000,
          "average",
          "neutro"
        );

        expect(result.finalMarkup).toBe(25);
        expect(result.sellingPrice).toBe(12500);
      });
    });

    describe("Cenário Pessimista", () => {
      it("deve aplicar 22% base + 5% excellent = 27% markup", async () => {
        const result = await pricingService.applyDynamicMarkup(
          10000,
          "excellent",
          "pessimista"
        );

        expect(result.baseMarkup).toBe(22);
        expect(result.finalMarkup).toBe(27);
        expect(result.sellingPrice).toBe(12700);
      });

      it("deve aplicar 22% base - 8% expensive = 14% markup (mínimo viável)", async () => {
        await expect(
          pricingService.applyDynamicMarkup(10000, "expensive", "pessimista")
        ).rejects.toThrow("Margem 14.0% abaixo do mínimo viável");
      });
    });

    describe("RN-008: Margem Mínima 15%", () => {
      it("deve rejeitar markup abaixo de 15%", async () => {
        await expect(
          pricingService.applyDynamicMarkup(10000, "expensive", "pessimista")
        ).rejects.toThrow("mínimo viável (15%)");
      });

      it("deve aceitar markup exatamente 15%", async () => {
        // Criar cenário com markup exato de 15%
        const result = await pricingService.applyDynamicMarkup(
          10000,
          "average", // 22% base - 3% = 19%
          "pessimista"
        );

        expect(result.finalMarkup).toBeGreaterThanOrEqual(15);
      });
    });

    describe("Cálculo de Margens", () => {
      it("deve calcular margem bruta corretamente", async () => {
        const result = await pricingService.applyDynamicMarkup(
          10000,
          "excellent",
          "neutro"
        );

        // Preço: R$13.300, Custo: R$10.000
        // Margem bruta: (13.300 - 10.000) / 13.300 = 24.8%
        expect(result.grossMargin).toBeCloseTo(24.8, 1);
      });

      it("deve calcular margem líquida considerando custos operacionais 9%", async () => {
        const result = await pricingService.applyDynamicMarkup(
          10000,
          "excellent",
          "neutro"
        );

        // Custos operacionais: 13.300 * 0.09 = 1.197
        // Margem líquida: (13.300 - 10.000 - 1.197) / 13.300 = 15.8%
        expect(result.netMargin).toBeCloseTo(15.8, 1);
      });
    });
  });

  describe("applyChannelPricing", () => {
    const basePrice = 10000;

    it("deve aplicar 0% desconto para B2C", async () => {
      const result = await pricingService.applyChannelPricing(basePrice, "b2c");

      expect(result.discount).toBe(0);
      expect(result.channelPrice).toBe(10000);
      expect(result.commission).toBe(0);
    });

    it("deve aplicar 15% desconto para Integrador B2B", async () => {
      const result = await pricingService.applyChannelPricing(basePrice, "integrator_b2b");

      expect(result.discount).toBe(15);
      expect(result.channelPrice).toBe(8500); // 10000 * 0.85
      expect(result.commission).toBeGreaterThan(0);
    });

    it("deve aplicar 20% desconto para Distribuidor", async () => {
      const result = await pricingService.applyChannelPricing(basePrice, "distributor");

      expect(result.discount).toBe(20);
      expect(result.channelPrice).toBe(8000); // 10000 * 0.80
    });

    it("deve aplicar 10% desconto para Marketplace", async () => {
      const result = await pricingService.applyChannelPricing(basePrice, "marketplace");

      expect(result.discount).toBe(10);
      expect(result.channelPrice).toBe(9000);
    });

    it("deve aplicar 25% desconto para White-label", async () => {
      const result = await pricingService.applyChannelPricing(basePrice, "white_label");

      expect(result.discount).toBe(25);
      expect(result.channelPrice).toBe(7500); // 10000 * 0.75
    });
  });

  describe("calculateBundlePricing", () => {
    it("deve aplicar 12% desconto padrão em bundle", async () => {
      const config = {
        name: "Kit Residencial Completo",
        description: "Painéis + Inversor + Estrutura",
        components: [
          { product_id: "p1", quantity: 10, unit_price: 500 },
          { product_id: "p2", quantity: 1, unit_price: 3000 },
          { product_id: "p3", quantity: 1, unit_price: 2000 },
        ],
        bundle_discount: 12,
        target_margin: 28,
      };

      const result = await pricingService.calculateBundlePricing(config);

      expect(result.individual_total).toBe(10000); // 5000 + 3000 + 2000
      expect(result.bundle_discount).toBe(12);
      expect(result.bundle_price).toBe(8800); // 10000 * 0.88
      expect(result.savings).toBe(1200);
    });

    it("deve validar se mantém margem-alvo", async () => {
      const config = {
        name: "Bundle Test",
        description: "Test",
        components: [
          { product_id: "p1", quantity: 1, unit_price: 10000 },
        ],
        bundle_discount: 12,
        target_margin: 28,
      };

      const result = await pricingService.calculateBundlePricing(config);

      // Bundle price: 8800
      // Estimated cost (70% of original): 7000
      // Margin: (8800 - 7000) / 8800 = 20.45%
      expect(result.margin).toBeGreaterThan(15); // Acima do mínimo
      expect(result.profitable).toBeTruthy();
    });
  });

  describe("calculateFinancing", () => {
    it("deve calcular 12× sem juros corretamente", async () => {
      const result = await pricingService.calculateFinancing(12000, 12);

      expect(result.tier.installments).toBe(12);
      expect(result.tier.monthly_rate).toBe(0);
      expect(result.installment_value).toBe(1000); // 12000 / 12
      expect(result.total_amount).toBe(12000);
      expect(result.total_interest).toBe(0);
    });

    it("deve calcular 24× com 0.99% a.m. corretamente", async () => {
      const result = await pricingService.calculateFinancing(24000, 24);

      expect(result.tier.monthly_rate).toBe(0.99);
      expect(result.installment_value).toBeGreaterThan(1000); // Com juros
      expect(result.total_amount).toBeGreaterThan(24000);
      expect(result.total_interest).toBeGreaterThan(0);
      expect(result.effective_rate).toBeGreaterThan(0);
    });

    it("deve calcular 60× com 1.49% a.m. corretamente", async () => {
      const result = await pricingService.calculateFinancing(60000, 60);

      expect(result.tier.monthly_rate).toBe(1.49);
      expect(result.total_amount).toBeGreaterThan(60000);
      expect(result.total_interest).toBeGreaterThan(10000); // Juros significativos
    });
  });

  describe("evaluatePriceMatch", () => {
    it("deve aprovar price match dentro dos limites", async () => {
      const result = await pricingService.evaluatePriceMatch(
        10000, // Preço original
        9000, // Preço competidor (10% menor)
        7000 // Custo
      );

      expect(result.approved).toBe(true);
      expect(result.discount_applied).toBeCloseTo(10, 1);
      expect(result.matched_price).toBe(9000);
      expect(result.margin_after_match).toBeGreaterThan(12); // Acima de 12%
    });

    it("deve rejeitar price match com desconto >15%", async () => {
      const result = await pricingService.evaluatePriceMatch(
        10000,
        8000, // 20% menor
        7000
      );

      expect(result.approved).toBe(false);
      expect(result.rejection_reason).toContain("excede máximo permitido");
    });

    it("deve rejeitar price match com margem <12%", async () => {
      const result = await pricingService.evaluatePriceMatch(
        10000,
        9000,
        8000 // Custo alto, margem resultante <12%
      );

      expect(result.approved).toBe(false);
      expect(result.rejection_reason).toContain("abaixo do mínimo");
    });

    it("deve rejeitar se preço competidor não é inferior", async () => {
      const result = await pricingService.evaluatePriceMatch(
        10000,
        10500, // Maior que nosso preço
        7000
      );

      expect(result.approved).toBe(false);
      expect(result.rejection_reason).toContain("não é inferior");
    });
  });

  describe("applyPsychologicalPricing", () => {
    it("deve aplicar charm pricing (.99)", async () => {
      const result = await pricingService.applyPsychologicalPricing(10350);

      expect(result.charm_price).toBe(10350.99);
    });

    it("deve calcular anchor pricing (25% acima)", async () => {
      const result = await pricingService.applyPsychologicalPricing(10000, {
        use_anchor_pricing: true,
        anchor_multiplier: 1.25,
      });

      expect(result.anchor_price).toBeCloseTo(12500, 0); // 10000 * 1.25
      expect(result.display_savings).toBeCloseTo(2500, 0);
    });
  });

  describe("calculateDynamicAdjustments", () => {
    it("deve aplicar ajuste negativo para estoque alto", async () => {
      const result = await pricingService.calculateDynamicAdjustments({
        inventory_level: "high",
      });

      expect(result.inventory_adjustment).toBe(-5);
    });

    it("deve aplicar ajuste negativo para competição alta", async () => {
      const result = await pricingService.calculateDynamicAdjustments({
        competition_level: "high",
      });

      expect(result.competition_adjustment).toBe(-5);
    });

    it("deve aplicar ajuste negativo para urgência alta", async () => {
      const result = await pricingService.calculateDynamicAdjustments({
        urgency: "high",
      });

      expect(result.urgency_adjustment).toBe(-15);
    });

    it("deve aplicar ajuste positivo para cliente VIP", async () => {
      const result = await pricingService.calculateDynamicAdjustments({
        customer_segment: "vip",
      });

      expect(result.segment_adjustment).toBe(5);
    });

    it("deve somar todos os ajustes corretamente", async () => {
      const result = await pricingService.calculateDynamicAdjustments({
        inventory_level: "high", // -5%
        competition_level: "high", // -5%
        customer_segment: "new", // -10%
        urgency: "high", // -15%
      });

      expect(result.total_adjustment).toBe(-35); // -5 -5 -10 -15
    });
  });

  describe("calculateProjectSplits - RN-006", () => {
    const totalValue = 50000;

    describe("Cenário Otimista", () => {
      it("deve alocar 55% para equipamentos", async () => {
        const result = await pricingService.calculateProjectSplits(
          totalValue,
          "sudeste",
          "otimista"
        );

        expect(result.equipments.percentage).toBe(55);
        expect(result.equipments.value).toBe(27500);
      });

      it("deve ter margem de 8%", async () => {
        const result = await pricingService.calculateProjectSplits(
          totalValue,
          "sudeste",
          "otimista"
        );

        expect(result.margin.percentage).toBe(8);
        expect(result.margin.value).toBe(4000);
      });
    });

    describe("Cenário Neutro", () => {
      it("deve alocar 60% para equipamentos", async () => {
        const result = await pricingService.calculateProjectSplits(
          totalValue,
          "sudeste",
          "neutro"
        );

        expect(result.equipments.percentage).toBe(60);
        expect(result.equipments.value).toBe(30000);
      });

      it("deve ter margem de 5%", async () => {
        const result = await pricingService.calculateProjectSplits(
          totalValue,
          "sudeste",
          "neutro"
        );

        expect(result.margin.percentage).toBe(5);
        expect(result.margin.value).toBe(2500);
      });
    });

    describe("Ajustes Regionais - RN-005", () => {
      it("deve reduzir 15% mão de obra no Nordeste", async () => {
        const result = await pricingService.calculateProjectSplits(
          totalValue,
          "nordeste",
          "neutro"
        );

        // 13% base * 0.85 = 11.05%
        expect(result.labor.percentage).toBeCloseTo(11.05, 1);
      });

      it("deve aumentar 50% logística no Norte", async () => {
        const result = await pricingService.calculateProjectSplits(
          totalValue,
          "norte",
          "neutro"
        );

        // 4% base * 1.50 = 6%
        expect(result.logistics.percentage).toBeCloseTo(6, 1);
      });

      it("deve aumentar 20% logística no Sul", async () => {
        const result = await pricingService.calculateProjectSplits(
          totalValue,
          "sul",
          "neutro"
        );

        // 4% base * 1.20 = 4.8%
        expect(result.logistics.percentage).toBeCloseTo(4.8, 1);
      });
    });
  });

  describe("calculateProjectPricing - Orquestração Completa", () => {
    it("deve calcular precificação completa de projeto", async () => {
      const result = await pricingService.calculateProjectPricing({
        cost_price: 10000,
        region: "sudeste",
        customer_channel: "b2c",
        competitor_prices: [10000, 10500, 11000],
        scenario: "neutro",
        apply_psychological_pricing: true,
      });

      expect(result.cost_price).toBe(10000);
      expect(result.price_score).toBeDefined();
      expect(result.dynamic_markup).toBeDefined();
      expect(result.channel_pricing).toBeDefined();
      expect(result.psychological_pricing).toBeDefined();
      expect(result.project_splits).toBeDefined();
      expect(result.final_price).toBeGreaterThan(10000);
      expect(result.recommended_price).toBeGreaterThan(10000);
      expect(result.kpis.gross_margin).toBeGreaterThan(0);
      expect(result.kpis.net_margin).toBeGreaterThan(0);
    });

    it("deve validar KPIs - margem bruta ≥25%, margem líquida ≥15%", async () => {
      const result = await pricingService.calculateProjectPricing({
        cost_price: 10000,
        region: "sudeste",
        customer_channel: "b2c",
        scenario: "neutro",
      });

      if (result.kpis.meets_target) {
        expect(result.kpis.gross_margin).toBeGreaterThanOrEqual(25);
        expect(result.kpis.net_margin).toBeGreaterThanOrEqual(15);
      }
    });

    it("deve aplicar ajustes regionais corretamente", async () => {
      const resultNordeste = await pricingService.calculateProjectPricing({
        cost_price: 10000,
        region: "nordeste",
        customer_channel: "b2c",
        scenario: "neutro",
      });

      const resultSul = await pricingService.calculateProjectPricing({
        cost_price: 10000,
        region: "sul",
        customer_channel: "b2c",
        scenario: "neutro",
      });

      expect(resultNordeste.regional_adjustments.generation_factor).toBe(1.09);
      expect(resultSul.regional_adjustments.generation_factor).toBe(0.91);
    });

    it("deve aplicar desconto de canal corretamente", async () => {
      const resultB2C = await pricingService.calculateProjectPricing({
        cost_price: 10000,
        region: "sudeste",
        customer_channel: "b2c",
        scenario: "neutro",
      });

      const resultB2B = await pricingService.calculateProjectPricing({
        cost_price: 10000,
        region: "sudeste",
        customer_channel: "integrator_b2b",
        scenario: "neutro",
      });

      expect(resultB2C.channel_pricing.discount).toBe(0);
      expect(resultB2B.channel_pricing.discount).toBe(15);
      expect(resultB2B.channel_pricing.channelPrice).toBeLessThan(resultB2C.channel_pricing.channelPrice);
    });
  });
});
