/**
 * Metrics endpoint for catalog DDD implementation
 * Returns handler metrics for monitoring
 */

import type { MedusaRequest, MedusaResponse } from '@medusajs/framework/http';
import { getHandlerMetrics } from '@domains/catalog/application/queries/handlers/list-skus-handler';

export async function GET(
  req: MedusaRequest,
  res: MedusaResponse
): Promise<void> {
  try {
    const metrics = getHandlerMetrics();
    
    res.json({
      success: true,
      data: {
        ...metrics,
        timestamp: new Date().toISOString(),
        info: {
          target_p95: '150ms',
          cache_ttl: '3600s (1 hour)',
          feature_flag: process.env.CATALOG_DDD_ENABLED === 'true'
        }
      }
    });
  } catch (error) {
    console.error('[CatalogMetrics] Error fetching metrics:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch metrics'
    });
  }
}
