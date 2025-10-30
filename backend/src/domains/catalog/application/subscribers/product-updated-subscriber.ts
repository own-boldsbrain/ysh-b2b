/**
 * ProductUpdatedSubscriber
 * 
 * Event subscriber for cache invalidation when products are updated.
 * Implements idempotency as per ADR-003 (Event-Driven Integration).
 * 
 * To register in Medusa:
 * - Create subscriber file in src/subscribers/catalog-cache-invalidation.ts
 * - Export default async function(eventBusService, cacheService) { ... }
 * 
 * @see ADR-003 - Event-Driven Integration
 */

import { CacheService } from '@shared/cache';

interface ProductUpdatedEvent {
  id: string;
  eventName: 'catalog.product.updated';
  metadata: {
    productId: string;
    category?: string;
    manufacturerId?: string;
    changeType: 'price' | 'stock' | 'availability' | 'metadata';
  };
  occurredAt: string;
}

/**
 * Handler function for catalog.product.updated event
 * This should be registered with Medusa's eventBusService in a subscriber
 */
export async function handleProductUpdated(
  event: ProductUpdatedEvent,
  cache: CacheService
): Promise<void> {
  const { metadata } = event;
  
  console.log(`[ProductUpdatedSubscriber] Processing event for product ${metadata.productId}`);

  // Invalidate all catalog list caches (selective invalidation)
  const patterns = [
    'catalog:skus:list:*', // All list queries
  ];

  // If category changed, invalidate category-specific caches
  if (metadata.category) {
    patterns.push(`catalog:skus:category:${metadata.category}:*`);
  }

  // If manufacturer changed, invalidate manufacturer-specific caches
  if (metadata.manufacturerId) {
    patterns.push(`catalog:skus:manufacturer:${metadata.manufacturerId}:*`);
  }

  // Invalidate caches
  for (const pattern of patterns) {
    await cache.deleteByPattern(pattern);
    console.log(`[ProductUpdatedSubscriber] Invalidated cache pattern: ${pattern}`);
  }

  console.log(`[ProductUpdatedSubscriber] Cache invalidation complete for product ${metadata.productId}`);
}
