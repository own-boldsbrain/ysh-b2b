import { ListSKUsHandler } from '../../../application/queries/handlers/list-skus-handler';
import { ListSKUsQuery } from '../../../application/queries/list-skus-query';
import type { Request, Response } from 'express';

export class CatalogController {
  constructor(private readonly handler: ListSKUsHandler) {}

  async listSKUs(req: Request, res: Response): Promise<void> {
    const params = {
      categoryId: req.query.categoryId as string | undefined,
      search: req.query.search as string | undefined,
      inStock: req.query.inStock ? req.query.inStock === 'true' : undefined,
      page: req.query.page ? Number(req.query.page) : undefined,
      limit: req.query.limit ? Number(req.query.limit) : undefined,
      sort: req.query.sort as string | undefined
    };

    const query = new ListSKUsQuery(params);
    const result = await this.handler.execute(query);
    res.json(result);
  }
}
/**
 * CatalogController
 * 
 * HTTP interface layer for catalog operations.
 * Translates HTTP requests to domain queries (CQRS read side).
 * 
 * @see ADR-001 (DDD Architecture)
 * @see ADR-002 (CQRS Implementation)
 */

import type { MedusaRequest, MedusaResponse } from '@medusajs/framework';
import { ValidationError } from '@shared/errors';
import { ListSKUsQuery } from '../../application/queries/list-skus-query';
import type { ListSKUsHandler } from '../../application/queries/handlers/list-skus-handler';
import { ProductSKU } from '../../domain/entities/product-sku';

export interface ListSKUsRequestQuery {
  category?: string;
  manufacturer_id?: string;
  min_price?: string | number;
  max_price?: string | number;
  search?: string;
  limit?: string | number;
  offset?: string | number;
  sort_field?: string;
  sort_order?: string;
}

export class CatalogController {
  constructor(
    private readonly listSKUsHandler: ListSKUsHandler
  ) {}

  /**
   * Parse query parameter as number
   */
  private parseNumber(value: any, defaultValue?: number): number | undefined {
    if (value === undefined || value === null) {
      return defaultValue;
    }
    if (typeof value === 'number') {
      return value;
    }
    if (typeof value === 'string') {
      const parsed = parseFloat(value);
      return isNaN(parsed) ? defaultValue : parsed;
    }
    return defaultValue;
  }

  /**
   * Parse query parameter as string
   */
  private parseString(value: any): string | undefined {
    if (value === undefined || value === null) {
      return undefined;
    }
    if (typeof value === 'string') {
      return value;
    }
    if (Array.isArray(value) && value.length > 0) {
      return String(value[0]);
    }
    return undefined;
  }

  /**
   * GET /store/catalog/skus
   * List product SKUs with advanced filters
   */
  async listSKUs(
    req: MedusaRequest<ListSKUsRequestQuery>,
    res: MedusaResponse
  ): Promise<void> {
    try {
      // 1. Parse and validate query parameters
      const {
        category,
        manufacturer_id,
        min_price,
        max_price,
        search,
        limit = 20,
        offset = 0,
        sort_field = 'average_price',
        sort_order = 'ASC'
      } = req.query;

      // 2. Parse and validate numeric parameters
      const limitNum = this.parseNumber(limit, 20) ?? 20;
      const offsetNum = this.parseNumber(offset, 0) ?? 0;
      const minPriceNum = min_price !== undefined ? this.parseNumber(min_price) : undefined;
      const maxPriceNum = max_price !== undefined ? this.parseNumber(max_price) : undefined;

      if (limitNum < 1 || limitNum > 100) {
        throw new ValidationError(
          'Limit must be between 1 and 100',
          { limit: limitNum }
        );
      }

      if (offsetNum < 0) {
        throw new ValidationError(
          'Offset must be non-negative',
          { offset: offsetNum }
        );
      }

      // 3. Build query
      const categoryStr = this.parseString(category);
      const manufacturerIdStr = this.parseString(manufacturer_id);
      const searchStr = this.parseString(search);
      const sortFieldStr = this.parseString(sort_field) || 'average_price';
      const sortOrderStr = (sort_order === 'desc' || sort_order === 'DESC') ? 'desc' : 'asc';

      const query = new ListSKUsQuery(
        {
          category: categoryStr,
          manufacturerId: manufacturerIdStr,
          minPrice: minPriceNum,
          maxPrice: maxPriceNum,
          search: searchStr,
          isActive: true // Only show active products in store API
        },
        { limit: limitNum, offset: offsetNum },
        { 
          sortBy: sortFieldStr, 
          sortOrder: sortOrderStr as 'asc' | 'desc'
        }
      );

      // 4. Execute query
      const result = await this.listSKUsHandler.execute(query);

      // 5. Format response
      const pagination = result.pagination;
      res.json({
        skus: result.data.map((sku: ProductSKU) => sku.toJSON()),
        count: pagination.total,
        limit: pagination.limit,
        offset: pagination.offset,
        has_more: pagination.hasMore,
        next_offset: pagination.nextOffset
      });

    } catch (error) {
      // Let error middleware handle it
      throw error;
    }
  }

  /**
   * Health check endpoint
   */
  async health(_req: MedusaRequest, res: MedusaResponse): Promise<void> {
    res.json({
      status: 'healthy',
      service: 'catalog',
      timestamp: new Date().toISOString()
    });
  }
}
