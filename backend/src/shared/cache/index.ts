/**
 * Shared Cache Utilities
 * 
 * Redis wrapper com suporte a namespaces, TTLs por domínio,
 * versionamento de chaves e invalidação precisa.
 */

import Redis from "ioredis";
import { createHash } from "crypto";

/**
 * Cache Configuration
 */
export interface CacheConfig {
  host: string;
  port: number;
  password?: string;
  db?: number;
  keyPrefix?: string;
}

export interface CacheOptions {
  ttl?: number; // TTL in seconds
  namespace?: string;
  version?: string;
}

/**
 * Cache Service
 */
export class CacheService {
  private client: Redis;
  private readonly defaultTTL: number = 3600; // 1 hour
  private readonly keyPrefix: string;

  constructor(config: CacheConfig) {
    this.client = new Redis({
      host: config.host,
      port: config.port,
      password: config.password,
      db: config.db || 0,
      keyPrefix: config.keyPrefix || "ysh:",
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
    });

    this.keyPrefix = config.keyPrefix || "ysh:";

    this.client.on("error", (error) => {
      console.error("Redis connection error:", error);
    });

    this.client.on("connect", () => {
      console.log("Redis connected successfully");
    });
  }

  /**
   * Generate Cache Key
   */
  private generateKey(
    key: string,
    namespace?: string,
    version: string = "v1"
  ): string {
    const parts = [version];
    if (namespace) parts.push(namespace);
    parts.push(key);
    return parts.join(":");
  }

  /**
   * Generate Hash Key (for complex filters)
   */
  generateHashKey(data: any): string {
    const str = JSON.stringify(data, Object.keys(data).sort());
    return createHash("md5").update(str).digest("hex");
  }

  /**
   * Get
   */
  async get<T>(key: string, options?: CacheOptions): Promise<T | null> {
    const fullKey = this.generateKey(key, options?.namespace, options?.version);
    const value = await this.client.get(fullKey);

    if (!value) return null;

    try {
      return JSON.parse(value) as T;
    } catch {
      return value as T;
    }
  }

  /**
   * Set
   */
  async set<T>(
    key: string,
    value: T,
    options?: CacheOptions
  ): Promise<void> {
    const fullKey = this.generateKey(key, options?.namespace, options?.version);
    const ttl = options?.ttl || this.defaultTTL;
    const serialized = typeof value === "string" ? value : JSON.stringify(value);

    await this.client.setex(fullKey, ttl, serialized);
  }

  /**
   * Delete
   */
  async delete(key: string, options?: CacheOptions): Promise<void> {
    const fullKey = this.generateKey(key, options?.namespace, options?.version);
    await this.client.del(fullKey);
  }

  /**
   * Delete by Pattern
   */
  async deleteByPattern(pattern: string): Promise<void> {
    const fullPattern = `${this.keyPrefix}${pattern}`;
    const stream = this.client.scanStream({
      match: fullPattern,
      count: 100,
    });

    const keys: string[] = [];

    stream.on("data", (resultKeys: string[]) => {
      keys.push(...resultKeys);
    });

    await new Promise((resolve, reject) => {
      stream.on("end", resolve);
      stream.on("error", reject);
    });

    if (keys.length > 0) {
      // Remove prefix before deleting (ioredis adds it automatically)
      const keysWithoutPrefix = keys.map((k) =>
        k.replace(this.keyPrefix, "")
      );
      await this.client.del(...keysWithoutPrefix);
    }
  }

  /**
   * Exists
   */
  async exists(key: string, options?: CacheOptions): Promise<boolean> {
    const fullKey = this.generateKey(key, options?.namespace, options?.version);
    const result = await this.client.exists(fullKey);
    return result === 1;
  }

  /**
   * Get or Set (Cache-aside pattern)
   */
  async getOrSet<T>(
    key: string,
    factory: () => Promise<T>,
    options?: CacheOptions
  ): Promise<T> {
    const cached = await this.get<T>(key, options);

    if (cached !== null) {
      return cached;
    }

    const value = await factory();
    await this.set(key, value, options);

    return value;
  }

  /**
   * Increment
   */
  async increment(
    key: string,
    amount: number = 1,
    options?: CacheOptions
  ): Promise<number> {
    const fullKey = this.generateKey(key, options?.namespace, options?.version);
    return await this.client.incrby(fullKey, amount);
  }

  /**
   * Decrement
   */
  async decrement(
    key: string,
    amount: number = 1,
    options?: CacheOptions
  ): Promise<number> {
    const fullKey = this.generateKey(key, options?.namespace, options?.version);
    return await this.client.decrby(fullKey, amount);
  }

  /**
   * Set with Expire
   */
  async setWithExpire(
    key: string,
    value: any,
    ttl: number,
    options?: Omit<CacheOptions, "ttl">
  ): Promise<void> {
    await this.set(key, value, { ...options, ttl });
  }

  /**
   * Get TTL
   */
  async getTTL(key: string, options?: CacheOptions): Promise<number> {
    const fullKey = this.generateKey(key, options?.namespace, options?.version);
    return await this.client.ttl(fullKey);
  }

  /**
   * Flush All (use with caution)
   */
  async flushAll(): Promise<void> {
    await this.client.flushdb();
  }

  /**
   * Close connection
   */
  async disconnect(): Promise<void> {
    await this.client.quit();
  }

  /**
   * Health Check
   */
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.ping();
      return true;
    } catch {
      return false;
    }
  }
}

/**
 * Domain-specific TTLs
 */
export const DomainTTLs = {
  catalog: 3600, // 1 hour
  pricing: 300, // 5 minutes
  quotes: 1800, // 30 minutes
  approvals: 600, // 10 minutes
  company: 3600, // 1 hour
  solar: 86400, // 24 hours
  tariff: 43200, // 12 hours
} as const;

/**
 * Cache Key Patterns
 */
export const CachePatterns = {
  catalog: {
    product: (id: string) => `product:${id}`,
    productList: (filters: any) => `product:list:${filters}`,
    category: (id: string) => `category:${id}`,
  },
  pricing: {
    price: (skuId: string, context: string) => `price:${skuId}:${context}`,
    promotion: (id: string) => `promotion:${id}`,
  },
  quotes: {
    quote: (id: string) => `quote:${id}`,
    quotesByCustomer: (customerId: string) => `quotes:customer:${customerId}`,
  },
  solar: {
    simulation: (params: any) => `simulation:${params}`,
  },
} as const;

/**
 * Factory function
 */
export function createCacheService(config: CacheConfig): CacheService {
  return new CacheService(config);
}
