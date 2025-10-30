import { MedusaService } from "@medusajs/framework/utils";
import {
  DistributorCode,
  NormalizedProduct,
  ScraperExecutionResult,
  MultiDistributorScrapeResult,
  ScrapeRequestDTO,
  ProductMappingConfig,
  DistributorCredentials,
  ScraperAvailability,
  ComparePricesDTO,
  PriceComparisonResult,
  ProductCategory,
  ScraperStatus,
} from "./types";
import * as fs from "fs";
import * as path from "path";
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

/**
 * Scraper Orchestration Module Service
 * 
 * Centraliza gerenciamento de scrapers de distribuidores:
 * - Execução coordenada de múltiplos scrapers
 * - Normalização de produtos de diferentes fontes
 * - Mapeamento de SKUs entre distribuidores
 * - Comparação de preços
 * - Gestão de credenciais
 * - Retry e error handling
 */
export default class ScraperModuleService extends MedusaService({}) {
  private scriptsDir: string;
  private outputDir: string;

  constructor(container) {
    super(arguments[0]);
    this.scriptsDir = path.join(process.cwd(), "scripts");
    this.outputDir = path.join(process.cwd(), "output");
  }

  /**
   * Executa scraping em múltiplos distribuidores simultaneamente
   * 
   * @param request - Configuração de scraping
   * @returns Resultado agregado com produtos normalizados
   */
  async scrapeMultipleDistributors(
    request: ScrapeRequestDTO
  ): Promise<MultiDistributorScrapeResult> {
    const requestId = `scrape-${Date.now()}`;
    const startedAt = new Date();

    console.log(`🚀 Iniciando scraping multi-distribuidor [${requestId}]`);
    console.log(`   Distribuidores: ${request.distributors.join(", ")}`);

    const results: ScraperExecutionResult[] = [];
    const allProducts: NormalizedProduct[] = [];
    const errors: Array<{ distributor: DistributorCode; error: string }> = [];

    // Executar scrapers em paralelo (com limite de concorrência)
    const concurrencyLimit = 3; // 3 scrapers simultâneos
    for (let i = 0; i < request.distributors.length; i += concurrencyLimit) {
      const batch = request.distributors.slice(i, i + concurrencyLimit);

      const batchPromises = batch.map(async (distributor) => {
        try {
          const result = await this.scrapeDistributor(distributor, {
            max_products: request.max_products_per_distributor,
            timeout_ms: request.timeout_ms,
            save_screenshots: request.save_screenshots,
            retry_on_error: request.retry_on_error,
            max_retries: request.max_retries || 2,
          });

          results.push(result);

          // Normalizar produtos
          const products = await this.loadAndNormalizeProducts(
            distributor,
            result.output_file
          );

          allProducts.push(...products);
        } catch (error) {
          console.error(`❌ Erro ao scraper ${distributor}:`, error.message);
          errors.push({
            distributor,
            error: error.message,
          });

          results.push({
            distributor,
            status: "error",
            started_at: new Date(),
            completed_at: new Date(),
            products_found: 0,
            products_normalized: 0,
            products_with_errors: 0,
            error_message: error.message,
          });
        }
      });

      await Promise.all(batchPromises);
    }

    const completedAt = new Date();
    const totalDurationMs = completedAt.getTime() - startedAt.getTime();

    const successfulResults = results.filter((r) => r.status === "completed");
    const failedResults = results.filter((r) => r.status === "error");

    console.log(`✅ Scraping concluído em ${totalDurationMs}ms`);
    console.log(`   Sucessos: ${successfulResults.length}/${request.distributors.length}`);
    console.log(`   Produtos encontrados: ${allProducts.length}`);

    return {
      request_id: requestId,
      started_at: startedAt,
      completed_at: completedAt,
      total_duration_ms: totalDurationMs,
      distributors_requested: request.distributors.length,
      distributors_successful: successfulResults.length,
      distributors_failed: failedResults.length,
      total_products_found: results.reduce((sum, r) => sum + r.products_found, 0),
      total_products_normalized: allProducts.length,
      results,
      products: allProducts,
      errors,
    };
  }

  /**
   * Executa scraper de um distribuidor específico
   */
  private async scrapeDistributor(
    distributor: DistributorCode,
    options: {
      max_products?: number;
      timeout_ms?: number;
      save_screenshots?: boolean;
      retry_on_error?: boolean;
      max_retries?: number;
    }
  ): Promise<ScraperExecutionResult> {
    const startedAt = new Date();

    console.log(`🔍 Scraping ${distributor}...`);

    // Mapear distribuidor para script
    const scriptMap: Record<DistributorCode, string> = {
      edeltec: "extract-edeltec-deep.ts",
      fortlev: "extract-fortlev-final.ts",
      odex: "extract-odex-fixed.ts",
      solfacil: "extract-solfacil-fixed.ts",
      fotus: "extract-fotus-final.ts",
      dynamis: "extract-dynamis-custom.ts",
      neosolar: "extract-neosolar-production.ts",
    };

    const scriptName = scriptMap[distributor];
    if (!scriptName) {
      throw new Error(`Script não encontrado para distribuidor: ${distributor}`);
    }

    const scriptPath = path.join(this.scriptsDir, scriptName);

    // Verificar se script existe
    if (!fs.existsSync(scriptPath)) {
      throw new Error(`Script não existe: ${scriptPath}`);
    }

    // Executar script com timeout
    const timeout = options.timeout_ms || 300000; // 5 minutos default
    let attempt = 0;
    let lastError: Error | null = null;

    while (attempt <= (options.max_retries || 0)) {
      try {
        attempt++;
        if (attempt > 1) {
          console.log(`   Tentativa ${attempt}/${options.max_retries! + 1}...`);
        }

        const { stdout, stderr } = await this.executeWithTimeout(
          `npx tsx ${scriptPath}`,
          timeout
        );

        if (stderr && !stderr.includes("Debugger attached")) {
          console.warn(`   ⚠️ Warnings: ${stderr.substring(0, 200)}`);
        }

        // Extrair informações do output
        const productsMatch = stdout.match(/(\d+) produtos/i);
        const productsFound = productsMatch ? parseInt(productsMatch[1]) : 0;

        // Encontrar arquivo de output mais recente
        const outputFile = await this.findLatestOutputFile(distributor);

        const completedAt = new Date();
        const durationMs = completedAt.getTime() - startedAt.getTime();

        console.log(`   ✅ Concluído: ${productsFound} produtos em ${durationMs}ms`);

        return {
          distributor,
          status: "completed",
          started_at: startedAt,
          completed_at: completedAt,
          duration_ms: durationMs,
          products_found: productsFound,
          products_normalized: 0, // Será atualizado depois
          products_with_errors: 0,
          output_file: outputFile,
        };
      } catch (error) {
        lastError = error;
        if (!options.retry_on_error || attempt > (options.max_retries || 0)) {
          break;
        }
        await new Promise((resolve) => setTimeout(resolve, 5000)); // 5s entre tentativas
      }
    }

    // Se chegou aqui, todas as tentativas falharam
    throw lastError || new Error(`Scraping falhou após ${attempt} tentativas`);
  }

  /**
   * Executa comando com timeout
   */
  private executeWithTimeout(
    command: string,
    timeoutMs: number
  ): Promise<{ stdout: string; stderr: string }> {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Timeout após ${timeoutMs}ms`));
      }, timeoutMs);

      execAsync(command, { cwd: this.scriptsDir })
        .then((result) => {
          clearTimeout(timer);
          resolve(result);
        })
        .catch((error) => {
          clearTimeout(timer);
          reject(error);
        });
    });
  }

  /**
   * Encontra arquivo de output mais recente de um distribuidor
   */
  private async findLatestOutputFile(distributor: DistributorCode): Promise<string | undefined> {
    const distributorDir = path.join(this.outputDir, distributor);

    if (!fs.existsSync(distributorDir)) {
      return undefined;
    }

    const files = fs.readdirSync(distributorDir)
      .filter((f) => f.endsWith(".json") && f.includes("products"))
      .map((f) => ({
        name: f,
        path: path.join(distributorDir, f),
        mtime: fs.statSync(path.join(distributorDir, f)).mtime,
      }))
      .sort((a, b) => b.mtime.getTime() - a.mtime.getTime());

    return files.length > 0 ? files[0].path : undefined;
  }

  /**
   * Carrega e normaliza produtos de um arquivo JSON
   */
  private async loadAndNormalizeProducts(
    distributor: DistributorCode,
    filePath?: string
  ): Promise<NormalizedProduct[]> {
    if (!filePath || !fs.existsSync(filePath)) {
      console.warn(`   ⚠️ Arquivo não encontrado: ${filePath}`);
      return [];
    }

    try {
      const rawData = JSON.parse(fs.readFileSync(filePath, "utf-8"));
      const products = Array.isArray(rawData) ? rawData : [];

      console.log(`   📦 Normalizando ${products.length} produtos de ${distributor}...`);

      const normalized = products
        .map((raw) => this.normalizeProduct(distributor, raw))
        .filter((p): p is NormalizedProduct => p !== null);

      console.log(`   ✅ ${normalized.length} produtos normalizados`);

      return normalized;
    } catch (error) {
      console.error(`   ❌ Erro ao normalizar produtos:`, error.message);
      return [];
    }
  }

  /**
   * Normaliza produto de formato bruto para formato padronizado
   */
  private normalizeProduct(
    distributor: DistributorCode,
    raw: any
  ): NormalizedProduct | null {
    try {
      // Extrair SKU
      const sku = raw.sku || raw.SKU || raw.codigo || raw.id || "UNKNOWN";

      // Extrair nome
      const name = raw.name || raw.nome || raw.title || raw.descricao || "";

      // Extrair preço
      let price = 0;
      if (typeof raw.price === "number") {
        price = raw.price;
      } else if (typeof raw.price === "string") {
        price = parseFloat(raw.price.replace(/[^\d,.-]/g, "").replace(",", "."));
      } else if (raw.preco) {
        price = parseFloat(String(raw.preco).replace(/[^\d,.-]/g, "").replace(",", "."));
      }

      if (!name || price <= 0) {
        return null; // Produto inválido
      }

      // Classificar categoria baseado no nome
      const category = this.classifyProductCategory(name);

      // Determinar disponibilidade
      const availability = this.determineAvailability(raw);

      // Extrair especificações técnicas
      const specifications = this.extractSpecifications(name, raw);

      return {
        distributor,
        sku,
        name: name.trim(),
        category,
        price,
        currency: "BRL",
        availability,
        stock_quantity: raw.stock || raw.estoque || undefined,
        specifications,
        image_url: raw.image || raw.imagem || raw.photo || undefined,
        product_url: raw.url || raw.link || undefined,
        last_updated: new Date(),
        scrape_session_id: `session-${Date.now()}`,
      };
    } catch (error) {
      console.warn(`   ⚠️ Erro ao normalizar produto:`, error.message);
      return null;
    }
  }

  /**
   * Classifica categoria do produto baseado no nome
   */
  private classifyProductCategory(name: string): ProductCategory {
    const nameLower = name.toLowerCase();

    if (nameLower.includes("painel") || nameLower.includes("placa") || nameLower.includes("módulo")) {
      return "painel_solar";
    }
    if (nameLower.includes("inversor") || nameLower.includes("inverter")) {
      return "inversor";
    }
    if (nameLower.includes("bateria") || nameLower.includes("battery")) {
      return "bateria";
    }
    if (nameLower.includes("estrutura") || nameLower.includes("suporte")) {
      return "estrutura";
    }
    if (nameLower.includes("string box") || nameLower.includes("quadro")) {
      return "string_box";
    }
    if (nameLower.includes("cabo") || nameLower.includes("fio")) {
      return "cabo";
    }
    if (nameLower.includes("conector") || nameLower.includes("mc4")) {
      return "conector";
    }

    return "outros";
  }

  /**
   * Determina disponibilidade do produto
   */
  private determineAvailability(raw: any): "in_stock" | "out_of_stock" | "limited" | "unknown" {
    const availabilityText = (
      raw.availability ||
      raw.disponibilidade ||
      raw.status ||
      ""
    ).toLowerCase();

    if (availabilityText.includes("disponível") || availabilityText.includes("estoque")) {
      return "in_stock";
    }
    if (availabilityText.includes("indisponível") || availabilityText.includes("esgotado")) {
      return "out_of_stock";
    }
    if (availabilityText.includes("limitado") || availabilityText.includes("poucos")) {
      return "limited";
    }

    // Se tem quantidade em estoque
    if (raw.stock > 0 || raw.estoque > 0) {
      return raw.stock < 5 || raw.estoque < 5 ? "limited" : "in_stock";
    }

    return "unknown";
  }

  /**
   * Extrai especificações técnicas do produto
   */
  private extractSpecifications(name: string, raw: any): any {
    const specs: any = {};

    // Potência (Watts)
    const powerMatch = name.match(/(\d+)\s*w/i);
    if (powerMatch) {
      specs.power_watts = parseInt(powerMatch[1]);
    }

    // Voltagem
    const voltageMatch = name.match(/(\d+)\s*v/i);
    if (voltageMatch) {
      specs.voltage = `${voltageMatch[1]}V`;
    }

    // Marca
    const brands = ["canadian", "jinko", "trina", "risen", "odex", "fortlev", "fronius", "growatt", "goodwe"];
    for (const brand of brands) {
      if (name.toLowerCase().includes(brand)) {
        specs.brand = brand.charAt(0).toUpperCase() + brand.slice(1);
        break;
      }
    }

    // Copiar outras especificações do raw
    if (raw.specifications) {
      Object.assign(specs, raw.specifications);
    }

    return Object.keys(specs).length > 0 ? specs : undefined;
  }

  /**
   * Compara preços de um produto entre distribuidores
   */
  async comparePrices(data: ComparePricesDTO): Promise<PriceComparisonResult> {
    console.log(`💰 Comparando preços: ${data.product_name_or_sku}`);

    const distributors = data.distributors || [
      "edeltec",
      "fortlev",
      "odex",
      "solfacil",
      "fotus",
      "dynamis",
      "neosolar",
    ];

    const matchedProducts: PriceComparisonResult["matched_products"] = [];

    // Buscar produto em cada distribuidor
    for (const distributor of distributors) {
      const products = await this.searchProducts(distributor, data.product_name_or_sku);

      for (const product of products) {
        if (!data.include_out_of_stock && product.availability === "out_of_stock") {
          continue;
        }

        const matchScore = this.calculateMatchScore(
          data.product_name_or_sku,
          product.name,
          product.sku
        );

        if (matchScore >= 50) {
          // Mínimo 50% de similaridade
          matchedProducts.push({
            distributor,
            product,
            price: product.price,
            availability: product.availability,
            match_score: matchScore,
          });
        }
      }
    }

    // Ordenar por score de match
    matchedProducts.sort((a, b) => b.match_score - a.match_score);

    // Encontrar melhor preço
    const bestPrice = matchedProducts.reduce(
      (best, current) =>
        !best || current.price < best.price ? current : best,
      null as any
    );

    // Calcular estatísticas de preço
    const prices = matchedProducts.map((m) => m.price);
    const priceStatistics = {
      min: Math.min(...prices),
      max: Math.max(...prices),
      average: prices.reduce((a, b) => a + b, 0) / prices.length,
      median: this.calculateMedian(prices),
      spread_percent: prices.length > 0
        ? ((Math.max(...prices) - Math.min(...prices)) / Math.min(...prices)) * 100
        : 0,
    };

    // Resumo de disponibilidade
    const availabilitySummary = {
      in_stock: matchedProducts.filter((m) => m.availability === "in_stock").length,
      out_of_stock: matchedProducts.filter((m) => m.availability === "out_of_stock").length,
      limited: matchedProducts.filter((m) => m.availability === "limited").length,
      unknown: matchedProducts.filter((m) => m.availability === "unknown").length,
    };

    console.log(`   ✅ ${matchedProducts.length} produtos encontrados`);
    console.log(`   💵 Melhor preço: R$ ${bestPrice.price} (${bestPrice.distributor})`);

    return {
      search_query: data.product_name_or_sku,
      matched_products: matchedProducts,
      best_price: {
        distributor: bestPrice.distributor,
        price: bestPrice.price,
        product: bestPrice.product,
      },
      price_statistics: priceStatistics,
      availability_summary: availabilitySummary,
    };
  }

  /**
   * Busca produtos de um distribuidor por nome ou SKU
   */
  private async searchProducts(
    distributor: DistributorCode,
    query: string
  ): Promise<NormalizedProduct[]> {
    const outputFile = await this.findLatestOutputFile(distributor);
    if (!outputFile) {
      return [];
    }

    const products = await this.loadAndNormalizeProducts(distributor, outputFile);
    const queryLower = query.toLowerCase();

    return products.filter(
      (p) =>
        p.name.toLowerCase().includes(queryLower) ||
        p.sku.toLowerCase().includes(queryLower)
    );
  }

  /**
   * Calcula score de similaridade entre query e produto
   */
  private calculateMatchScore(query: string, name: string, sku: string): number {
    const queryLower = query.toLowerCase();
    const nameLower = name.toLowerCase();
    const skuLower = sku.toLowerCase();

    // Match exato de SKU = 100%
    if (queryLower === skuLower) {
      return 100;
    }

    // Match parcial de SKU = 90%
    if (skuLower.includes(queryLower) || queryLower.includes(skuLower)) {
      return 90;
    }

    // Calcular similaridade de nome (palavras em comum)
    const queryWords = queryLower.split(/\s+/);
    const nameWords = nameLower.split(/\s+/);

    const commonWords = queryWords.filter((word) =>
      nameWords.some((nw) => nw.includes(word) || word.includes(nw))
    );

    const similarityPercent = (commonWords.length / queryWords.length) * 100;

    return Math.round(similarityPercent);
  }

  /**
   * Calcula mediana de array de números
   */
  private calculateMedian(numbers: number[]): number {
    const sorted = [...numbers].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 === 0
      ? (sorted[mid - 1] + sorted[mid]) / 2
      : sorted[mid];
  }

  /**
   * Retorna status de disponibilidade de scrapers
   */
  async getScraperAvailability(): Promise<ScraperAvailability[]> {
    const distributors: DistributorCode[] = [
      "edeltec",
      "fortlev",
      "odex",
      "solfacil",
      "fotus",
      "dynamis",
      "neosolar",
    ];

    const availabilities: ScraperAvailability[] = [];

    for (const distributor of distributors) {
      const scriptMap: Record<DistributorCode, string> = {
        edeltec: "extract-edeltec-deep.ts",
        fortlev: "extract-fortlev-final.ts",
        odex: "extract-odex-fixed.ts",
        solfacil: "extract-solfacil-fixed.ts",
        fotus: "extract-fotus-final.ts",
        dynamis: "extract-dynamis-custom.ts",
        neosolar: "extract-neosolar-production.ts",
      };

      const scriptPath = path.join(this.scriptsDir, scriptMap[distributor]);
      const isAvailable = fs.existsSync(scriptPath);

      // Verificar credenciais
      const hasCredentials = this.hasCredentials(distributor);

      // Verificar último arquivo
      const outputFile = await this.findLatestOutputFile(distributor);
      let lastSuccessfulRun: Date | undefined;
      let averageProducts: number | undefined;

      if (outputFile) {
        const stats = fs.statSync(outputFile);
        lastSuccessfulRun = stats.mtime;

        try {
          const products = JSON.parse(fs.readFileSync(outputFile, "utf-8"));
          averageProducts = Array.isArray(products) ? products.length : 0;
        } catch (error) {
          // Ignore
        }
      }

      availabilities.push({
        distributor,
        is_available: isAvailable,
        has_credentials: hasCredentials,
        last_successful_run: lastSuccessfulRun,
        average_products_per_run: averageProducts,
      });
    }

    return availabilities;
  }

  /**
   * Verifica se distribuidor tem credenciais configuradas
   */
  private hasCredentials(distributor: DistributorCode): boolean {
    const envVars = {
      edeltec: ["EDELTEC_EMAIL", "EDELTEC_PASSWORD"],
      fortlev: ["FORTLEV_EMAIL", "FORTLEV_PASSWORD"],
      odex: ["ODEX_EMAIL", "ODEX_PASSWORD"],
      solfacil: ["SOLFACIL_EMAIL", "SOLFACIL_PASSWORD"],
      fotus: ["FOTUS_EMAIL", "FOTUS_PASSWORD"],
      dynamis: ["DYNAMIS_EMAIL", "DYNAMIS_PASSWORD"],
      neosolar: ["NEOSOLAR_EMAIL", "NEOSOLAR_PASSWORD"],
    };

    const required = envVars[distributor] || [];
    return required.every((key) => !!process.env[key]);
  }
}
