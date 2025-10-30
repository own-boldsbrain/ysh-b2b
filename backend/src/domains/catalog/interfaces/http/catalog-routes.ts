/**
 * DDD-based catalog route handler
 * 
 * This module integrates the new DDD catalog controller with Medusa routes.
 * Feature flag: CATALOG_DDD_ENABLED
 * 
 * @see ADR-001 (DDD Architecture)
 * @see ADR-002 (CQRS Implementation)
 */

import type { MedusaRequest, MedusaResponse } from '@medusajs/framework';
import { CatalogController } from '@domains/catalog/interfaces/controllers/catalog-controller';
import { ListSKUsHandler } from '@domains/catalog/application/queries/handlers/list-skus-handler';
import { ProductQueryRepository } from '@domains/catalog/infrastructure/repositories/product-query-repository';
import { CacheService } from '@shared/cache';

// Feature flag
const CATALOG_DDD_ENABLED = process.env.CATALOG_DDD_ENABLED === 'true';

/**
 * Initialize DDD catalog controller (singleton)
 */
let catalogController: CatalogController | null = null;

function getCatalogController(container: any): CatalogController {
  if (!catalogController) {
    // Get dependencies from Medusa container
    const dbConnection = container.resolve('manager'); // Database connection
    
    // Initialize Redis cache
    const cache = new CacheService({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379', 10),
      password: process.env.REDIS_PASSWORD,
      db: parseInt(process.env.REDIS_DB || '0', 10)
    });

    // Build DDD layers
    const repository = new ProductQueryRepository(dbConnection);
    const handler = new ListSKUsHandler(repository, cache);
    catalogController = new CatalogController(handler);
  }

  return catalogController;
}

/**
 * GET /store/catalog/skus (DDD version)
 */
export async function handleListSKUs(
  req: MedusaRequest,
  res: MedusaResponse
): Promise<void> {
  const controller = getCatalogController(req.scope);
  return controller.listSKUs(req as any, res);
}

/**
 * Export for use in route.ts
 */
export const dddCatalogHandlers = {
  listSKUs: handleListSKUs,
  isEnabled: CATALOG_DDD_ENABLED
};
