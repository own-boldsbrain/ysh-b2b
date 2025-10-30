import { Router } from 'express';
import { CatalogController } from '@domains/catalog/interfaces/controllers/catalog-controller';
import { ListSKUsHandler } from '@domains/catalog/application/queries/handlers/list-skus-handler';
import { CacheService } from '@shared/cache';
import { ProductRepository } from '@domains/catalog/infrastructure/repositories/product-repository';

export function mountCatalogDDD(router: Router, deps: { cache: CacheService; db: any }) {
  const repo = new ProductRepository(deps.db);
  const handler = new ListSKUsHandler(repo, deps.cache);
  const controller = new CatalogController(handler);

  router.get('/store/catalog/skus', async (req, res, next) => {
    try {
      if (process.env.CATALOG_DDD_ENABLED !== 'true') return next();
      await controller.listSKUs(req, res);
    } catch (err) {
      next(err);
    }
  });
}
