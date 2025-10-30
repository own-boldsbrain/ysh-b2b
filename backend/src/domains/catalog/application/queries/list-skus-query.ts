export interface ListSKUsQueryParams {
  categoryId?: string;
  search?: string;
  inStock?: boolean;
  page?: number;
  limit?: number;
  sort?: string;
}

export class ListSKUsQuery {
  constructor(public readonly params: ListSKUsQueryParams = {}) {}
}
/**
 * Query for listing product SKUs with advanced filters
 * 
 * This query implements the CQRS read side for catalog SKUs.
 * Results are cached in Redis with 1-hour TTL.
 * 
 * @see ADR-002 (CQRS Implementation)
 */

import type { PaginationParams, SortParams } from '@shared/types';

export interface ListSKUsFilters {
  category?: string;
  manufacturerId?: string;
  minPrice?: number;
  maxPrice?: number;
  search?: string;
  isActive?: boolean;
}

export class ListSKUsQuery {
  constructor(
    public readonly filters: ListSKUsFilters = {},
    public readonly pagination: PaginationParams = { limit: 20, offset: 0 },
    public readonly sort: SortParams = { sortBy: 'average_price', sortOrder: 'asc' }
  ) {}

  /**
   * Get offset for database query
   */
  getOffset(): number {
    return this.pagination.offset || 0;
  }

  /**
   * Get limit for database query
   */
  getLimit(): number {
    return this.pagination.limit || 20;
  }

  /**
   * Get cache key for this query
   */
  getCacheKey(): string {
    const filterStr = JSON.stringify(this.filters);
    const paginationStr = `${this.getOffset()}-${this.getLimit()}`;
    const sortStr = `${this.sort.sortBy}-${this.sort.sortOrder}`;
    return `catalog:skus:list:${filterStr}:${paginationStr}:${sortStr}`;
  }
}
