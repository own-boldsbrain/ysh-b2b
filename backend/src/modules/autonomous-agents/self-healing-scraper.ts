/**
 * Self-Healing Scraper Agent
 * 
 * Capacidades autônomas:
 * - Auto-correção de seletores quando falham
 * - Descoberta de seletores alternativos
 * - Fallback para cache quando todas tentativas falham
 * - Ajuste dinâmico de delays para evitar rate limiting
 * - Notificação inteligente da equipe
 * 
 * Impacto esperado: -70% em falhas de scraping
 */

import { Logger } from "@medusajs/framework/logger";
import { JSDOM } from "jsdom";
import * as cheerio from "cheerio";
import { promises as fs } from "fs";
import path from "path";

// ================================================================================
// TYPES
// ================================================================================

interface Product {
  sku: string;
  title: string;
  category: string;
  price: number;
  distributor: string;
  [key: string]: any;
}

interface ScraperConfig {
  url: string;
  selectors: {
    productContainer: string;
    title: string;
    price: string;
    sku: string;
    category?: string;
  };
  auth?: {
    username: string;
    password: string;
  };
  delay: number;
  maxRetries: number;
}

interface SelectorDiscoveryResult {
  selector: string;
  confidence: number;
  matchCount: number;
  sampleData: string[];
}

interface ScraperAttemptResult {
  success: boolean;
  products: Product[];
  error?: Error;
  strategy: string;
  qualityScore: number;
}

// ================================================================================
// EXCEPTIONS
// ================================================================================

class SelectorNotFoundException extends Error {
  constructor(public selector: string, message: string) {
    super(message);
    this.name = "SelectorNotFoundException";
  }
}

class LoginFailedException extends Error {
  constructor(message: string) {
    super(message);
    this.name = "LoginFailedException";
  }
}

class RateLimitException extends Error {
  constructor(message: string) {
    super(message);
    this.name = "RateLimitException";
  }
}

class DataQualityException extends Error {
  constructor(message: string) {
    super(message);
    this.name = "DataQualityException";
  }
}

// ================================================================================
// SELF-HEALING SCRAPER AGENT
// ================================================================================

export class SelfHealingScraperAgent {
  private logger: Logger;
  private configs: Map<string, ScraperConfig>;
  private cachePath: string;
  private delays: Map<string, number>;

  constructor(logger: Logger) {
    this.logger = logger;
    this.configs = new Map();
    this.cachePath = path.join(process.cwd(), "output", "cache");
    this.delays = new Map();
  }

  // ================================================================================
  // MAIN SCRAPING METHOD WITH SELF-HEALING
  // ================================================================================

  async scrapeWithSelfHealing(
    distributor: string,
    config: ScraperConfig,
    maxAttempts: number = 5
  ): Promise<Product[]> {
    this.logger.info(`[SelfHealing] Starting scrape for ${distributor}`);
    
    let attempt = 0;
    let lastError: Error | null = null;
    const strategies: string[] = [];

    while (attempt < maxAttempts) {
      attempt++;
      this.logger.info(`[SelfHealing] Attempt ${attempt}/${maxAttempts} for ${distributor}`);

      try {
        // Strategy 1: Normal scraping
        const result = await this.scrapeDistributor(distributor, config);
        strategies.push("normal");

        // Validate data quality
        const validation = this.validateProducts(result);

        if (validation.qualityScore < 0.7) {
          throw new DataQualityException(
            `Quality score ${validation.qualityScore.toFixed(2)} below threshold 0.70. ` +
            `Issues: ${validation.issues.join(", ")}`
          );
        }

        this.logger.info(
          `[SelfHealing] ✅ Success for ${distributor} - ` +
          `${result.length} products, quality ${validation.qualityScore.toFixed(2)}`
        );

        // Cache successful results
        await this.cacheProducts(distributor, result);

        return result;

      } catch (error) {
        lastError = error as Error;
        this.logger.warn(
          `[SelfHealing] ⚠️ Attempt ${attempt} failed for ${distributor}: ${error.message}`
        );

        // Self-healing logic based on error type
        if (error instanceof SelectorNotFoundException) {
          strategies.push("alternative-selectors");
          
          // Try to discover alternative selectors
          const alternativeSelectors = await this.discoverAlternativeSelectors(
            distributor,
            config,
            error.selector
          );

          if (alternativeSelectors.length > 0) {
            this.logger.info(
              `[SelfHealing] 🔧 Found ${alternativeSelectors.length} alternative selectors`
            );

            // Update config with best alternative
            config.selectors = {
              ...config.selectors,
              productContainer: alternativeSelectors[0].selector,
            };

            this.configs.set(distributor, config);
            continue; // Retry with new selectors
          }

        } else if (error instanceof LoginFailedException) {
          strategies.push("refresh-credentials");
          
          // Try to refresh credentials
          this.logger.info(`[SelfHealing] 🔧 Attempting credential refresh for ${distributor}`);
          const refreshed = await this.refreshCredentials(distributor);

          if (refreshed) {
            await this.sleep(5000); // Wait before retry
            continue;
          }

        } else if (error instanceof RateLimitException) {
          strategies.push("increase-delay");
          
          // Increase delay dynamically
          const currentDelay = this.delays.get(distributor) || config.delay;
          const newDelay = Math.min(currentDelay * 2, 30000); // Max 30s
          this.delays.set(distributor, newDelay);

          this.logger.info(
            `[SelfHealing] 🔧 Rate limit hit - increasing delay to ${newDelay}ms`
          );

          await this.sleep(60000); // Wait 1 minute
          continue;

        } else if (error instanceof DataQualityException) {
          strategies.push("enhanced-parsing");
          
          // Try enhanced parsing strategy
          this.logger.info(`[SelfHealing] 🔧 Trying enhanced parsing strategy`);
          
          const enhancedResult = await this.scrapeWithEnhancedParsing(distributor, config);
          if (enhancedResult.length > 0) {
            await this.cacheProducts(distributor, enhancedResult);
            return enhancedResult;
          }
        }

        // Notify team after 3 failed attempts
        if (attempt >= 3) {
          await this.notifyTeam(
            distributor,
            `Scraper failing repeatedly (attempt ${attempt}/${maxAttempts})`,
            lastError,
            strategies
          );
        }
      }
    }

    // All attempts failed - try fallback strategies
    this.logger.error(
      `[SelfHealing] ❌ All ${maxAttempts} attempts failed for ${distributor}`
    );

    // Strategy: Use cached data
    const cachedProducts = await this.getCachedProducts(distributor);
    if (cachedProducts.length > 0) {
      this.logger.info(
        `[SelfHealing] 📦 Using cached data for ${distributor} (${cachedProducts.length} products)`
      );
      
      await this.notifyTeam(
        distributor,
        `Using cached data - scraper completely failed`,
        lastError,
        strategies
      );

      return cachedProducts;
    }

    // Final fallback: Mark distributor as unavailable
    await this.markDistributorUnavailable(distributor, lastError);

    this.logger.error(
      `[SelfHealing] 🚨 No fallback available for ${distributor} - returning empty array`
    );

    return [];
  }

  // ================================================================================
  // ALTERNATIVE SELECTOR DISCOVERY
  // ================================================================================

  private async discoverAlternativeSelectors(
    distributor: string,
    config: ScraperConfig,
    failedSelector: string
  ): Promise<SelectorDiscoveryResult[]> {
    this.logger.info(`[SelfHealing] 🔍 Discovering alternative selectors for ${failedSelector}`);

    try {
      // Fetch page HTML
      const html = await this.fetchPageHTML(config.url, config.auth);
      const $ = cheerio.load(html);

      // Product container patterns to try
      const patterns = [
        { attr: "class", contains: "product" },
        { attr: "class", contains: "item" },
        { attr: "class", contains: "card" },
        { attr: "data-product", exists: true },
        { attr: "itemprop", value: "product" },
        { attr: "class", contains: "grid-item" },
        { attr: "class", contains: "list-item" },
        { attr: "data-type", value: "product" },
      ];

      const results: SelectorDiscoveryResult[] = [];

      for (const pattern of patterns) {
        let selector = "";
        
        if (pattern.contains) {
          selector = `[${pattern.attr}*="${pattern.contains}"]`;
        } else if (pattern.value) {
          selector = `[${pattern.attr}="${pattern.value}"]`;
        } else if (pattern.exists) {
          selector = `[${pattern.attr}]`;
        }

        const elements = $(selector);
        const matchCount = elements.length;

        // Must have at least 5 matches to be considered valid
        if (matchCount >= 5) {
          // Sample data from first 3 elements
          const sampleData: string[] = [];
          elements.slice(0, 3).each((_, el) => {
            const text = $(el).text().trim().slice(0, 100);
            if (text) sampleData.push(text);
          });

          // Calculate confidence based on match count and data quality
          const confidence = Math.min(
            (matchCount / 20) * 0.6 + (sampleData.length / 3) * 0.4,
            1.0
          );

          results.push({
            selector,
            confidence,
            matchCount,
            sampleData,
          });
        }
      }

      // Sort by confidence descending
      results.sort((a, b) => b.confidence - a.confidence);

      this.logger.info(
        `[SelfHealing] Found ${results.length} alternative selectors (top confidence: ${results[0]?.confidence.toFixed(2) || "N/A"})`
      );

      return results;

    } catch (error) {
      this.logger.error(`[SelfHealing] Failed to discover alternative selectors: ${error.message}`);
      return [];
    }
  }

  // ================================================================================
  // DATA QUALITY VALIDATION
  // ================================================================================

  private validateProducts(products: Product[]): { 
    qualityScore: number; 
    issues: string[] 
  } {
    if (products.length === 0) {
      return { qualityScore: 0, issues: ["No products extracted"] };
    }

    const issues: string[] = [];
    let scoreDeductions = 0;

    // Check 1: Minimum product count (expect at least 10)
    if (products.length < 10) {
      issues.push(`Low product count (${products.length} < 10)`);
      scoreDeductions += 0.2;
    }

    // Check 2: Required fields present
    const requiredFields = ["sku", "title", "price", "distributor"];
    let missingFieldCount = 0;

    for (const product of products) {
      for (const field of requiredFields) {
        if (!product[field] || product[field] === "" || product[field] === 0) {
          missingFieldCount++;
        }
      }
    }

    const missingFieldRate = missingFieldCount / (products.length * requiredFields.length);
    if (missingFieldRate > 0.1) {
      issues.push(`High missing field rate (${(missingFieldRate * 100).toFixed(1)}%)`);
      scoreDeductions += missingFieldRate;
    }

    // Check 3: Price validity (should be > 0)
    const invalidPrices = products.filter(p => !p.price || p.price <= 0).length;
    const invalidPriceRate = invalidPrices / products.length;
    
    if (invalidPriceRate > 0.3) {
      issues.push(`High invalid price rate (${(invalidPriceRate * 100).toFixed(1)}%)`);
      scoreDeductions += invalidPriceRate * 0.5;
    }

    // Check 4: Duplicate SKUs (shouldn't exceed 5%)
    const skus = products.map(p => p.sku).filter(Boolean);
    const uniqueSkus = new Set(skus);
    const duplicateRate = (skus.length - uniqueSkus.size) / skus.length;

    if (duplicateRate > 0.05) {
      issues.push(`High duplicate SKU rate (${(duplicateRate * 100).toFixed(1)}%)`);
      scoreDeductions += duplicateRate;
    }

    const qualityScore = Math.max(1 - scoreDeductions, 0);

    return { qualityScore, issues };
  }

  // ================================================================================
  // ENHANCED PARSING STRATEGY
  // ================================================================================

  private async scrapeWithEnhancedParsing(
    distributor: string,
    config: ScraperConfig
  ): Promise<Product[]> {
    this.logger.info(`[SelfHealing] Trying enhanced parsing for ${distributor}`);

    try {
      const html = await this.fetchPageHTML(config.url, config.auth);
      const $ = cheerio.load(html);

      // Try multiple extraction strategies
      const strategies = [
        () => this.extractFromMicrodata($),
        () => this.extractFromJSONLD($),
        () => this.extractFromDataAttributes($),
        () => this.extractFromTableStructure($),
      ];

      for (const strategy of strategies) {
        try {
          const products = strategy();
          if (products.length >= 5) {
            this.logger.info(
              `[SelfHealing] ✅ Enhanced parsing found ${products.length} products`
            );
            return products;
          }
        } catch (error) {
          continue; // Try next strategy
        }
      }

      return [];

    } catch (error) {
      this.logger.error(`[SelfHealing] Enhanced parsing failed: ${error.message}`);
      return [];
    }
  }

  private extractFromMicrodata($: cheerio.CheerioAPI): Product[] {
    const products: Product[] = [];
    
    $('[itemtype*="Product"]').each((_, el) => {
      const $el = $(el);
      
      const product: Product = {
        sku: $el.find('[itemprop="sku"]').text().trim(),
        title: $el.find('[itemprop="name"]').text().trim(),
        price: parseFloat($el.find('[itemprop="price"]').attr("content") || "0"),
        category: $el.find('[itemprop="category"]').text().trim(),
        distributor: "unknown",
      };

      if (product.sku && product.title) {
        products.push(product);
      }
    });

    return products;
  }

  private extractFromJSONLD($: cheerio.CheerioAPI): Product[] {
    const products: Product[] = [];

    $('script[type="application/ld+json"]').each((_, el) => {
      try {
        const data = JSON.parse($(el).html() || "{}");
        
        if (data["@type"] === "Product" || data.itemListElement) {
          const items = Array.isArray(data.itemListElement) 
            ? data.itemListElement 
            : [data];

          for (const item of items) {
            if (item.sku || item.name) {
              products.push({
                sku: item.sku || "",
                title: item.name || "",
                price: parseFloat(item.offers?.price || "0"),
                category: item.category || "",
                distributor: "unknown",
              });
            }
          }
        }
      } catch (error) {
        // Invalid JSON - skip
      }
    });

    return products;
  }

  private extractFromDataAttributes($: cheerio.CheerioAPI): Product[] {
    const products: Product[] = [];

    $('[data-product], [data-item], [data-sku]').each((_, el) => {
      const $el = $(el);
      
      const product: Product = {
        sku: $el.attr("data-sku") || $el.attr("data-product-id") || "",
        title: $el.attr("data-title") || $el.attr("data-name") || $el.text().trim(),
        price: parseFloat($el.attr("data-price") || "0"),
        category: $el.attr("data-category") || "",
        distributor: "unknown",
      };

      if (product.sku && product.title) {
        products.push(product);
      }
    });

    return products;
  }

  private extractFromTableStructure($: cheerio.CheerioAPI): Product[] {
    const products: Product[] = [];

    $('table tbody tr').each((_, row) => {
      const cells = $(row).find("td");
      
      if (cells.length >= 3) {
        // Assume first 3 columns are: SKU, Title, Price
        const product: Product = {
          sku: $(cells[0]).text().trim(),
          title: $(cells[1]).text().trim(),
          price: parseFloat($(cells[2]).text().replace(/[^\d.,]/g, "").replace(",", ".")),
          category: cells.length >= 4 ? $(cells[3]).text().trim() : "",
          distributor: "unknown",
        };

        if (product.sku && product.title && product.price > 0) {
          products.push(product);
        }
      }
    });

    return products;
  }

  // ================================================================================
  // CACHE MANAGEMENT
  // ================================================================================

  private async cacheProducts(distributor: string, products: Product[]): Promise<void> {
    try {
      await fs.mkdir(this.cachePath, { recursive: true });
      
      const cacheFile = path.join(this.cachePath, `${distributor}-cache.json`);
      const cacheData = {
        distributor,
        cachedAt: new Date().toISOString(),
        productCount: products.length,
        products,
      };

      await fs.writeFile(cacheFile, JSON.stringify(cacheData, null, 2));
      
      this.logger.info(`[SelfHealing] 📦 Cached ${products.length} products for ${distributor}`);
    } catch (error) {
      this.logger.warn(`[SelfHealing] Failed to cache products: ${error.message}`);
    }
  }

  private async getCachedProducts(distributor: string): Promise<Product[]> {
    try {
      const cacheFile = path.join(this.cachePath, `${distributor}-cache.json`);
      const data = await fs.readFile(cacheFile, "utf-8");
      const cache = JSON.parse(data);

      // Check cache age (max 7 days)
      const cachedAt = new Date(cache.cachedAt);
      const ageInDays = (Date.now() - cachedAt.getTime()) / (1000 * 60 * 60 * 24);

      if (ageInDays <= 7) {
        this.logger.info(
          `[SelfHealing] Using cache from ${cache.cachedAt} (${ageInDays.toFixed(1)} days old)`
        );
        return cache.products;
      }

      this.logger.warn(`[SelfHealing] Cache too old (${ageInDays.toFixed(1)} days) - ignoring`);
      return [];

    } catch (error) {
      return [];
    }
  }

  // ================================================================================
  // HELPER METHODS (Stubs - implementar com lógica real)
  // ================================================================================

  private async scrapeDistributor(
    distributor: string,
    config: ScraperConfig
  ): Promise<Product[]> {
    // Implementar lógica real de scraping aqui
    // Este é apenas um stub
    throw new Error("Not implemented - integrate with actual scraper");
  }

  private async fetchPageHTML(url: string, auth?: { username: string; password: string }): Promise<string> {
    // Implementar fetch real aqui
    throw new Error("Not implemented");
  }

  private async refreshCredentials(distributor: string): Promise<boolean> {
    this.logger.info(`[SelfHealing] Attempting to refresh credentials for ${distributor}`);
    // Implementar lógica de refresh de credenciais
    return false;
  }

  private async notifyTeam(
    distributor: string,
    message: string,
    error: Error | null,
    strategies: string[]
  ): Promise<void> {
    this.logger.warn(
      `[SelfHealing] 🔔 TEAM NOTIFICATION: ${distributor} - ${message}\n` +
      `Error: ${error?.message || "N/A"}\n` +
      `Strategies tried: ${strategies.join(", ")}`
    );
    
    // TODO: Integrar com Slack/Email
  }

  private async markDistributorUnavailable(
    distributor: string,
    error: Error | null
  ): Promise<void> {
    this.logger.error(
      `[SelfHealing] 🚫 Marking ${distributor} as UNAVAILABLE\n` +
      `Last error: ${error?.message || "Unknown"}`
    );
    
    // TODO: Atualizar banco de dados com status
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
