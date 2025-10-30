import { MedusaService } from "@medusajs/framework/utils";
import { ComparativeQuoteRequest, SupplierQuoteResponse } from "./models/comparative-quote";
import { SCRAPER_MODULE } from "../scraper";
import { PROPOSAL_MODULE } from "../proposal";
import {
  CreateComparativeQuoteRequestDTO,
  PublishComparativeQuoteDTO,
  SubmitSupplierQuoteDTO,
  EvaluateQuoteDTO,
  SelectQuoteDTO,
  GenerateComparisonDTO,
  ComparisonResultDTO,
} from "./types";

type InjectedDependencies = {
  // Add dependencies like scraperService, proposalService, etc.
};

/**
 * ComparativeQuoteModuleService
 * 
 * Sistema de cotação inteligente multi-fornecedor que integra:
 * - Web scraping de distribuidores (Edeltec, Fortlev, Odex, Solfácil, Fotus, Dynamis, NeoSolar)
 * - Inteligência de precificação (PRICING_STRATEGY_YSH.md)
 * - Regras de negócio YSH (BUSINESS_RULES_EXTRACTED.md)
 * - Geração de propostas comerciais profissionais
 */
export default class ComparativeQuoteModuleService extends MedusaService({
  ComparativeQuoteRequest,
  SupplierQuoteResponse,
}) {
  constructor(container: InjectedDependencies) {
    super(arguments[0]);
  }

  /**
   * Cria uma nova requisição de cotação comparativa
   * 
   * Aplica regras:
   * - RN-002: Classificação por porte (Microgeração ≤75kWp, Minigeração 76-3000kWp)
   * - RN-004: Tier padrão Consciente (130%) para dimensionamento
   * - RN-005: Ajuste regional de geração (Nordeste 1.09x, Sul 0.91x, Sudeste 1.00x)
   */
  async createRequest(
    data: CreateComparativeQuoteRequestDTO
  ): Promise<ComparativeQuoteRequest> {
    const requestNumber = await this.generateRequestNumber();

    // Calcular potência necessária baseado em consumo e tier
    const tierFactors = {
      moderado: 1.15,
      consciente: 1.30, // Recomendado (RN-004)
      acelerado: 1.45,
      ultra: 1.60,
    };

    const regionalFactors = {
      nordeste: 1.09,
      centro_oeste: 1.07,
      sudeste: 1.00, // Base (RN-005)
      norte: 0.98,
      sul: 0.91,
    };

    const tierFactor = tierFactors[data.generation_tier || "consciente"];
    const regionalFactor = regionalFactors[data.region?.toLowerCase() || "sudeste"];

    // Fórmula: potenciaNecessaria = (consumoMensal * fatorGeracao) / (150 / fatorRegional)
    const divisorRegional = 150 / regionalFactor;
    const potenciaEstimada = (data.monthly_consumption_kwh * tierFactor) / divisorRegional;

    // Classificar porte do projeto (RN-002)
    let projectCategory = "P"; // Default
    if (potenciaEstimada <= 2.0) projectCategory = "XPP";
    else if (potenciaEstimada <= 4.0) projectCategory = "PP";
    else if (potenciaEstimada <= 10.0) projectCategory = "P";
    else if (potenciaEstimada <= 25.0) projectCategory = "M";
    else if (potenciaEstimada <= 75.0) projectCategory = "G";
    else if (potenciaEstimada <= 500.0) projectCategory = "XG";
    else projectCategory = "XXG";

    const request = await this.createComparativeQuoteRequest({
      request_number: requestNumber,
      customer_id: data.customer_id,
      customer_type: data.customer_type,
      region: data.region,
      project_category: projectCategory,
      estimated_power_kwp: potenciaEstimada,
      monthly_consumption_kwh: data.monthly_consumption_kwh,
      generation_tier: data.generation_tier || "consciente",
      technical_specifications: {
        ...data.technical_specifications,
        calculated_power_kwp: potenciaEstimada,
        tier_factor: tierFactor,
        regional_factor: regionalFactor,
      },
      evaluation_criteria: data.evaluation_criteria || {
        price_weight: 0.4, // 40% peso preço
        quality_weight: 0.25, // 25% peso qualidade
        delivery_weight: 0.2, // 20% peso entrega
        warranty_weight: 0.15, // 15% peso garantia
      },
      invited_suppliers: data.invited_suppliers,
      deadline: data.deadline || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 dias padrão
      status: "draft",
      created_at: new Date(),
      updated_at: new Date(),
    });

    return request;
  }

  /**
   * Publica requisição e dispara scrapers para fornecedores convidados
   * 
   * Workflow:
   * 1. Muda status para "published"
   * 2. Notifica fornecedores convidados
   * 3. Dispara web scrapers para coletar preços atuais
   * 4. Aguarda respostas até deadline
   */
  async publishRequest(
    requestId: string,
    data?: PublishComparativeQuoteDTO
  ): Promise<ComparativeQuoteRequest> {
    const request = await this.retrieveComparativeQuoteRequest(requestId);

    if (request.status !== "draft") {
      throw new Error(`Requisição ${request.request_number} não está em rascunho`);
    }

    // Atualizar status
    const updated = await this.updateComparativeQuoteRequest(requestId, {
      status: "published",
      published_at: new Date(),
      updated_at: new Date(),
    });

    // Disparar scrapers para fornecedores convidados via Scraper Module
    if (data?.trigger_scrapers !== false) {
      try {
        const scraperService = this.container.resolve(SCRAPER_MODULE);
        await scraperService.scrapeMultipleDistributors({
          distributors: request.invited_suppliers as any[],
          max_products_per_distributor: 100,
          timeout_ms: 300000, // 5 minutos
          save_screenshots: true,
          retry_on_error: true,
          max_retries: 2,
        });
      } catch (error) {
        console.error("Erro ao disparar scrapers:", error.message);
        // Não falhar a publicação se scrapers falharem
      }
    }

    // TODO: Enviar notificações para fornecedores
    // await this.notifyInvitedSuppliers(request);

    return updated;
  }

  /**
   * Coleta respostas dos fornecedores via web scraping
   * 
   * Integra com scrapers:
   * - backend/scripts/extract-edeltec.ts (1000 produtos)
   * - backend/scripts/extract-fortlev.ts (9 produtos validados)
   * - backend/scripts/extract-odex.ts (login OK, extração pendente)
   * - backend/scripts/extract-solfacil.ts (SSO OK, extração pendente)
   * - backend/scripts/extract-fotus.ts
   * - backend/scripts/extract-dynamis.ts
   * - backend/scripts/extract-neosolar.ts
   */
  async collectResponses(requestId: string): Promise<SupplierQuoteResponse[]> {
    const request = await this.retrieveComparativeQuoteRequest(requestId);

    if (request.status !== "published" && request.status !== "receiving_quotes") {
      throw new Error(
        `Requisição ${request.request_number} não está publicada ou recebendo cotações`
      );
    }

    // Atualizar status se necessário
    if (request.status === "published") {
      await this.updateComparativeQuoteRequest(requestId, {
        status: "receiving_quotes",
        updated_at: new Date(),
      });
    }

    const responses: SupplierQuoteResponse[] = [];
    const scraperService = this.container.resolve(SCRAPER_MODULE);

    // Executar scraping para todos os fornecedores convidados
    const scrapeResult = await scraperService.scrapeMultipleDistributors({
      distributors: request.invited_suppliers as any[],
      max_products_per_distributor: 100,
      timeout_ms: 300000,
      save_screenshots: true,
      retry_on_error: true,
      max_retries: 2,
    });

    // Para cada fornecedor com dados raspados, criar SupplierQuoteResponse
    for (const result of scrapeResult.results) {
      if (result.status !== "completed" || result.products_found === 0) {
        console.warn(`Fornecedor ${result.distributor} não retornou produtos`);
        continue;
      }

      try {
        // Buscar produtos raspados deste fornecedor
        const supplierProducts = scrapeResult.products.filter(
          (p) => p.distributor === result.distributor
        );

        if (supplierProducts.length === 0) {
          continue;
        }

        // Calcular preço médio ou somar produtos relacionados ao projeto
        const relevantProducts = this.filterRelevantProducts(
          supplierProducts,
          request.technical_specifications
        );

        const totalPrice = relevantProducts.reduce((sum, p) => sum + p.price, 0);
        const avgDelivery = 15; // Estimativa padrão
        const avgWarranty = relevantProducts[0]?.specifications?.warranty_years || 10;

        const response = await this.createSupplierQuoteResponse({
          comparative_quote_request_id: requestId,
          supplier_id: result.distributor,
          supplier_name: this.getSupplierName(result.distributor),
          quoted_price: totalPrice,
          items: relevantProducts.map((p) => ({
            product_id: p.sku,
            name: p.name,
            quantity: 1,
            unit_price: p.price,
            category: p.category,
          })),
          delivery_time_days: avgDelivery,
          warranty_years: avgWarranty,
          additional_info: {
            products_found: result.products_found,
            scrape_duration_ms: result.duration_ms,
          },
          is_selected: false,
          submitted_at: new Date(),
          created_at: new Date(),
          updated_at: new Date(),
        });

        responses.push(response);
      } catch (error) {
        console.error(`Erro ao processar fornecedor ${result.distributor}:`, error);
      }
    }

    console.log(`✅ ${responses.length} respostas coletadas de ${request.invited_suppliers.length} fornecedores`);

    return responses;
  }

  /**
   * Filtra produtos relevantes para o projeto baseado em especificações técnicas
   */
  private filterRelevantProducts(products: any[], technicalSpecs: any): any[] {
    // Por enquanto, retornar primeiros 5 produtos
    // TODO: Implementar filtro inteligente baseado em potência, categoria, etc
    return products.slice(0, 5);
  }

  /**
   * Calcula score de preço baseado em competitividade
   * 
   * Algoritmo de PRICING_STRATEGY_YSH.md (linhas 18-50):
   * - Encontrar melhor preço entre fornecedores
   * - Calcular delta percentual vs melhor preço
   * - Classificar: excellent (≤2%), good (≤5%), average (≤10%), expensive (>10%)
   * 
   * @returns Categoria de preço e delta percentual
   */
  async calculatePriceScore(
    quotedPrice: number,
    allPrices: number[]
  ): Promise<{ category: string; delta: number; bestPrice: number }> {
    const bestPrice = Math.min(...allPrices.filter((p) => p > 0));
    const delta = ((quotedPrice - bestPrice) / bestPrice) * 100;

    let category = "expensive";
    if (delta <= 2) category = "excellent";
    else if (delta <= 5) category = "good";
    else if (delta <= 10) category = "average";

    return { category, delta, bestPrice };
  }

  /**
   * Aplica markup dinâmico baseado em competitividade
   * 
   * Estratégia de PRICING_STRATEGY_YSH.md (linhas 58-74):
   * - excellent_deal (≤2%): +5% markup adicional (27% margem final)
   * - good_price (≤5%): +2% markup adicional (24% margem final)
   * - average (≤10%): -3% markup (19% margem final)
   * - expensive (>10%): -8% markup (14% margem final)
   * 
   * Regras de negócio:
   * - RN-006: Margem-alvo 25-35%
   * - RN-008: Margem mínima 15% (rejeitar se abaixo)
   */
  async applyDynamicMarkup(
    costPrice: number,
    priceCategory: string,
    baseMarkup: number = 22 // 22% base padrão
  ): Promise<{ finalPrice: number; appliedMarkup: number; margin: number }> {
    const markupAdjustments = {
      excellent: 5, // +5% quando temos preço excelente
      good: 2, // +2% quando temos bom preço
      average: -3, // -3% quando preço médio
      expensive: -8, // -8% quando preço caro
    };

    const adjustment = markupAdjustments[priceCategory] || 0;
    const appliedMarkup = baseMarkup + adjustment;

    // RN-008: Verificar margem mínima viável (15%)
    if (appliedMarkup < 15) {
      throw new Error(
        `Margem ${appliedMarkup}% abaixo do mínimo viável (15%). Projeto não rentável.`
      );
    }

    const finalPrice = costPrice * (1 + appliedMarkup / 100);
    const margin = (appliedMarkup / (100 + appliedMarkup)) * 100;

    return { finalPrice, appliedMarkup, margin };
  }

  /**
   * Aplica ajustes de precificação por canal
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
    channel: string
  ): Promise<{ channelPrice: number; discount: number }> {
    const channelDiscounts = {
      b2c: 0,
      integrator_b2b: 15,
      distributor: 20,
      marketplace: 10,
      white_label: 25,
    };

    const discount = channelDiscounts[channel?.toLowerCase()] || 0;
    const channelPrice = basePrice * (1 - discount / 100);

    return { channelPrice, discount };
  }

  /**
   * Avalia cotação de fornecedor e calcula score final
   * 
   * Score = (price_score * price_weight) + 
   *         (quality_score * quality_weight) +
   *         (delivery_score * delivery_weight) +
   *         (warranty_score * warranty_weight)
   * 
   * Normaliza cada componente para escala 0-100
   */
  async evaluateQuote(
    quoteId: string,
    data: EvaluateQuoteDTO
  ): Promise<SupplierQuoteResponse> {
    const quote = await this.retrieveSupplierQuoteResponse(quoteId);
    const request = await this.retrieveComparativeQuoteRequest(
      quote.comparative_quote_request_id
    );

    // Obter todas as cotações para calcular scores relativos
    const allQuotes = await this.listSupplierQuoteResponse({
      filters: { comparative_quote_request_id: request.id },
    });

    const allPrices = allQuotes.map((q) => q.quoted_price);
    const priceScore = await this.calculatePriceScore(quote.quoted_price, allPrices);

    // Normalizar scores (0-100)
    const priceScoreNormalized = this.normalizePriceScore(priceScore.category);
    const qualityScoreNormalized = data.quality_score || 70; // Default médio
    const deliveryScoreNormalized = this.normalizeDeliveryScore(quote.delivery_time_days);
    const warrantyScoreNormalized = this.normalizeWarrantyScore(quote.warranty_years);

    // Calcular score final ponderado
    const criteria = request.evaluation_criteria;
    const finalScore =
      priceScoreNormalized * (criteria.price_weight || 0.4) +
      qualityScoreNormalized * (criteria.quality_weight || 0.25) +
      deliveryScoreNormalized * (criteria.delivery_weight || 0.2) +
      warrantyScoreNormalized * (criteria.warranty_weight || 0.15);

    const updated = await this.updateSupplierQuoteResponse(quoteId, {
      score: Math.round(finalScore),
      price_category: priceScore.category,
      price_delta_percent: priceScore.delta,
      evaluation_notes: data.evaluation_notes || "",
      evaluated_at: new Date(),
      updated_at: new Date(),
    });

    return updated;
  }

  /**
   * Gera matriz de comparação entre fornecedores
   * 
   * Retorna:
   * - Comparação detalhada de preços, scores, prazos
   * - Recomendação de melhor fornecedor
   * - Análise de trade-offs (preço vs qualidade vs prazo)
   * - Aplicação de regras de margem (RN-006, RN-008)
   */
  async generateComparison(
    requestId: string,
    data?: GenerateComparisonDTO
  ): Promise<ComparisonResultDTO> {
    const request = await this.retrieveComparativeQuoteRequest(requestId);

    const quotes = await this.listSupplierQuoteResponse({
      filters: { comparative_quote_request_id: requestId },
    });

    if (quotes.length === 0) {
      throw new Error(`Nenhuma cotação encontrada para requisição ${request.request_number}`);
    }

    // Avaliar todas as cotações se ainda não foram avaliadas
    for (const quote of quotes) {
      if (!quote.score) {
        await this.evaluateQuote(quote.id, {});
      }
    }

    // Recarregar cotações com scores atualizados
    const evaluatedQuotes = await this.listSupplierQuoteResponse({
      filters: { comparative_quote_request_id: requestId },
    });

    // Ordenar por score (maior = melhor)
    const rankedQuotes = evaluatedQuotes.sort((a, b) => (b.score || 0) - (a.score || 0));

    // Identificar melhor fornecedor
    const bestQuote = rankedQuotes[0];

    // Calcular estatísticas
    const allPrices = rankedQuotes.map((q) => q.quoted_price);
    const avgPrice = allPrices.reduce((a, b) => a + b, 0) / allPrices.length;
    const minPrice = Math.min(...allPrices);
    const maxPrice = Math.max(...allPrices);

    // Aplicar margem e gerar preços finais
    const customerType = request.customer_type || "b2c";
    const pricingResults = await Promise.all(
      rankedQuotes.map(async (quote) => {
        const priceScore = await this.calculatePriceScore(quote.quoted_price, allPrices);
        const markup = await this.applyDynamicMarkup(
          quote.quoted_price,
          priceScore.category,
          data?.base_markup
        );
        const channelPrice = await this.applyChannelPricing(markup.finalPrice, customerType);

        return {
          supplier_id: quote.supplier_id,
          supplier_name: quote.supplier_name,
          cost_price: quote.quoted_price,
          price_category: priceScore.category,
          price_delta: priceScore.delta,
          applied_markup: markup.appliedMarkup,
          margin: markup.margin,
          final_price: channelPrice.channelPrice,
          channel_discount: channelPrice.discount,
          score: quote.score,
          delivery_days: quote.delivery_time_days,
          warranty_years: quote.warranty_years,
        };
      })
    );

    // Atualizar status da requisição
    await this.updateComparativeQuoteRequest(requestId, {
      status: "evaluation",
      updated_at: new Date(),
    });

    return {
      request_number: request.request_number,
      total_quotes: rankedQuotes.length,
      best_supplier: {
        supplier_id: bestQuote.supplier_id,
        supplier_name: bestQuote.supplier_name,
        score: bestQuote.score,
        quoted_price: bestQuote.quoted_price,
        final_price: pricingResults[0].final_price,
        margin: pricingResults[0].margin,
      },
      price_statistics: {
        average: avgPrice,
        minimum: minPrice,
        maximum: maxPrice,
        spread_percent: ((maxPrice - minPrice) / minPrice) * 100,
      },
      ranked_suppliers: pricingResults,
      recommendation: this.generateRecommendation(pricingResults, request),
      generated_at: new Date(),
    };
  }

  /**
   * Seleciona fornecedor vencedor e dispara geração de proposta
   * 
   * Workflow:
   * 1. Marca cotação como selecionada
   * 2. Atualiza status da requisição para "selected"
   * 3. Dispara geração de proposta comercial (ProposalModule)
   * 4. Notifica fornecedor vencedor
   */
  async selectQuote(requestId: string, data: SelectQuoteDTO): Promise<ComparativeQuoteRequest> {
    const request = await this.retrieveComparativeQuoteRequest(requestId);

    if (request.status !== "evaluation") {
      throw new Error(
        `Requisição ${request.request_number} não está em fase de avaliação`
      );
    }

    // Desmarcar qualquer cotação previamente selecionada
    const allQuotes = await this.listSupplierQuoteResponse({
      filters: { comparative_quote_request_id: requestId },
    });

    for (const quote of allQuotes) {
      if (quote.is_selected) {
        await this.updateSupplierQuoteResponse(quote.id, {
          is_selected: false,
          updated_at: new Date(),
        });
      }
    }

    // Marcar nova cotação como selecionada
    await this.updateSupplierQuoteResponse(data.quote_id, {
      is_selected: true,
      selection_reason: data.selection_reason,
      selected_at: new Date(),
      updated_at: new Date(),
    });

    // Atualizar requisição
    const updated = await this.updateComparativeQuoteRequest(requestId, {
      status: "selected",
      selected_quote_id: data.quote_id,
      updated_at: new Date(),
    });

    // Disparar geração de proposta comercial
    if (data.create_proposal !== false) {
      try {
        const proposalService = this.container.resolve(PROPOSAL_MODULE);
        const selectedQuote = await this.retrieveSupplierQuoteResponse(data.quote_id);
        
        await proposalService.createProposal({
          customer_id: request.customer_id,
          quote_id: requestId,
          supplier_id: selectedQuote.supplier_id,
          supplier_name: selectedQuote.supplier_name,
          items: selectedQuote.items,
          subtotal: selectedQuote.quoted_price,
          discount: 0,
          tax: 0,
          total: selectedQuote.quoted_price,
          delivery_terms: `Entrega em ${selectedQuote.delivery_time_days} dias úteis`,
          warranty_terms: `Garantia de ${selectedQuote.warranty_years} anos`,
          payment_terms: "Conforme negociação",
          validity_days: 15,
          notes: data.selection_reason,
          metadata: {
            comparative_quote_id: requestId,
            selected_quote_id: data.quote_id,
            project_category: request.project_category,
            estimated_power_kwp: request.estimated_power_kwp,
          },
        });
        
        console.log(`✅ Proposta comercial criada para cotação ${requestId}`);
      } catch (error) {
        console.error("Erro ao criar proposta:", error.message);
        // Não falhar a seleção se proposta falhar
      }
    }

    // TODO: Notificar fornecedor vencedor
    // await this.notifySelectedSupplier(data.quote_id);

    return updated;
  }

  /**
   * Gera número de requisição único: CQR-YYYY-####
   */
  private async generateRequestNumber(): Promise<string> {
    const year = new Date().getFullYear();
    const count = await this.listComparativeQuoteRequest({
      filters: {
        created_at: {
          $gte: new Date(year, 0, 1),
          $lt: new Date(year + 1, 0, 1),
        },
      },
    });

    const sequence = String(count.length + 1).padStart(4, "0");
    return `CQR-${year}-${sequence}`;
  }

  /**
   * Mapeia ID de fornecedor para nome
   */
  private getSupplierName(supplierId: string): string {
    const supplierNames = {
      edeltec: "Edeltec",
      fortlev: "Fortlev",
      odex: "Odex",
      solfacil: "Solfácil",
      fotus: "Fotus",
      dynamis: "Dynamis",
      neosolar: "NeoSolar",
    };

    return supplierNames[supplierId.toLowerCase()] || supplierId;
  }

  /**
   * Normaliza score de preço para escala 0-100
   */
  private normalizePriceScore(category: string): number {
    const scores = {
      excellent: 100,
      good: 80,
      average: 60,
      expensive: 30,
    };

    return scores[category] || 50;
  }

  /**
   * Normaliza score de prazo de entrega para escala 0-100
   * Quanto menor o prazo, maior o score
   */
  private normalizeDeliveryScore(deliveryDays: number): number {
    if (deliveryDays <= 7) return 100;
    if (deliveryDays <= 15) return 80;
    if (deliveryDays <= 30) return 60;
    if (deliveryDays <= 45) return 40;
    return 20;
  }

  /**
   * Normaliza score de garantia para escala 0-100
   */
  private normalizeWarrantyScore(warrantyYears: number): number {
    if (warrantyYears >= 25) return 100;
    if (warrantyYears >= 20) return 90;
    if (warrantyYears >= 15) return 80;
    if (warrantyYears >= 10) return 70;
    if (warrantyYears >= 5) return 60;
    return 40;
  }

  /**
   * Gera recomendação inteligente baseada em análise multi-critério
   */
  private generateRecommendation(
    pricingResults: any[],
    request: ComparativeQuoteRequest
  ): string {
    const best = pricingResults[0];

    let recommendation = `Fornecedor recomendado: ${best.supplier_name}\n`;
    recommendation += `Score: ${best.score}/100 | `;
    recommendation += `Preço: R$ ${best.final_price.toLocaleString("pt-BR", {
      minimumFractionDigits: 2,
    })} | `;
    recommendation += `Margem: ${best.margin.toFixed(1)}%\n\n`;

    // Análise de preço
    if (best.price_category === "excellent") {
      recommendation += `✅ Excelente oportunidade de preço (${best.price_delta.toFixed(
        1
      )}% acima do melhor)\n`;
    } else if (best.price_category === "good") {
      recommendation += `✅ Bom preço competitivo (${best.price_delta.toFixed(1)}% acima do melhor)\n`;
    }

    // Análise de margem (RN-006)
    if (best.margin >= 32) {
      recommendation += `✅ Margem excelente (${best.margin.toFixed(
        1
      )}%) - Cenário Otimista\n`;
    } else if (best.margin >= 25) {
      recommendation += `✅ Margem saudável (${best.margin.toFixed(
        1
      )}%) - Cenário Neutro\n`;
    } else if (best.margin >= 19) {
      recommendation += `⚠️ Margem justa (${best.margin.toFixed(
        1
      )}%) - Cenário Pessimista\n`;
    } else if (best.margin >= 15) {
      recommendation += `⚠️ Margem mínima (${best.margin.toFixed(1)}%) - Atenção!\n`;
    }

    // Análise de prazo
    if (best.delivery_days <= 15) {
      recommendation += `✅ Prazo de entrega rápido (${best.delivery_days} dias)\n`;
    }

    // Análise de garantia
    if (best.warranty_years >= 20) {
      recommendation += `✅ Garantia premium (${best.warranty_years} anos)\n`;
    }

    return recommendation;
  }
}
