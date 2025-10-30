import { ListSKUsQuery } from '../list-skus-query';
import { CacheService } from '@shared/cache';
import type { PaginatedResponse } from '@shared/types';
import { ProductSKU } from '../../../domain/entities/product-sku';
import type { IProductQueryRepository } from '../../../infrastructure/repositories/product-query-repository';

/**
 * Simple metrics collector (in-memory)
 * In production, replace with Prometheus client
 */
class MetricsCollector {
  private metrics = {
    cacheHits: 0,
    cacheMisses: 0,
    queriesTotal: 0,
    queryDurations: [] as number[],
  };

  recordCacheHit(): void {
    this.metrics.cacheHits++;
    this.metrics.queriesTotal++;
  }

  recordCacheMiss(): void {
    this.metrics.cacheMisses++;
    this.metrics.queriesTotal++;
  }

  recordQueryDuration(durationMs: number): void {
    this.metrics.queryDurations.push(durationMs);
    
    // Keep only last 1000 measurements
    if (this.metrics.queryDurations.length > 1000) {
      this.metrics.queryDurations.shift();
    }
  }

  getMetrics() {
    const durations = this.metrics.queryDurations;
    const avgDuration = durations.length > 0
      ? durations.reduce((a, b) => a + b, 0) / durations.length
      : 0;
    
    const sortedDurations = [...durations].sort((a, b) => a - b);
    const p50 = sortedDurations[Math.floor(sortedDurations.length * 0.50)] || 0;
    const p95 = sortedDurations[Math.floor(sortedDurations.length * 0.95)] || 0;
    const p99 = sortedDurations[Math.floor(sortedDurations.length * 0.99)] || 0;

    const cacheHitRate = this.metrics.queriesTotal > 0
      ? (this.metrics.cacheHits / this.metrics.queriesTotal) * 100
      : 0;

    return {
      ...this.metrics,
      avgDuration: Math.round(avgDuration * 10) / 10,
      p50Duration: p50,
      p95Duration: p95,
      p99Duration: p99,
      cacheHitRate: Math.round(cacheHitRate * 10) / 10,
    };
  }

  reset(): void {
    this.metrics = {
      cacheHits: 0,
      cacheMisses: 0,
      queriesTotal: 0,
      queryDurations: [],
    };
  }
}

const metricsCollector = new MetricsCollector();

/**
 * Get current metrics (for monitoring endpoint)
 */
export function getHandlerMetrics() {
  return metricsCollector.getMetrics();
}

/**
 * Reset metrics (useful for testing)
 */
export function resetHandlerMetrics() {
  metricsCollector.reset();
}

/**
 * ListSKUsHandler
 * Query handler for listing product SKUs (CQRS read side).
 * Uses ProductSKU read model and CacheService.
 * Performance target: <150ms P95
 */
export class ListSKUsHandler {
  constructor(
    private readonly repository: IProductQueryRepository,
    private readonly cache: CacheService
  ) {}

  private buildCacheKey(query: ListSKUsQuery): string {
    const keyData = {
      params: query.params
    };
    return `catalog:skus:list:${Buffer.from(JSON.stringify(keyData)).toString('base64')}`;
  }

  async execute(query: ListSKUsQuery): Promise<PaginatedResponse<ProductSKU>> {
    const startTime = Date.now();

    const cacheKey = this.buildCacheKey(query);

    // Try cache first
    const cached = await this.cache.get<PaginatedResponse<any>>(cacheKey);
    if (cached) {
      const duration = Date.now() - startTime;
      metricsCollector.recordCacheHit();
      metricsCollector.recordQueryDuration(duration);
      
      console.log(`[ListSKUsHandler] Cache HIT - ${duration}ms`);
      
      return {
        ...cached,
        data: cached.data.map((item: any) => ProductSKU.fromPersistence(item))
      } as PaginatedResponse<ProductSKU>;
    }

    metricsCollector.recordCacheMiss();
    console.log(`[ListSKUsHandler] Cache MISS - querying DB`);

    // Map pagination params
    const page = query.params.page ?? 1;
    const limit = query.params.limit ?? 20;
    const offset = (page - 1) * limit;

    const result = await this.repository.listSKUs(
      {
        categoryId: query.params.categoryId,
        search: query.params.search,
        inStock: query.params.inStock
      },
      {
        offset,
        limit
      },
      {
        field: query.params.sort ?? 'average_price',
        order: 'ASC'
      }
    );

    // Cache plain objects (TTL: 1 hour)
    const cacheData = {
      data: result.data.map((sku: ProductSKU) => sku.toJSON()),
      pagination: result.pagination
    };
    await this.cache.set(cacheKey, cacheData, 3600);

    const duration = Date.now() - startTime;
    metricsCollector.recordQueryDuration(duration);
    
    console.log(`[ListSKUsHandler] Query completed - ${duration}ms (${result.data.length} items, P95: ${metricsCollector.getMetrics().p95Duration}ms)`);

    return result;
  }
}
