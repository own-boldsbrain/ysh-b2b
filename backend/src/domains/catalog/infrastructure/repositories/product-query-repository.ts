/**
 * ProductQueryRepository
 * 
 * Read-only repository for product queries (CQRS read side).
 * Optimized for fast reads with proper indexing.
 * 
 * @see ADR-002 (CQRS Implementation)
 */

import type { PaginatedResponse } from '@shared/types';
import type { ListSKUsFilters } from '../../application/queries/list-skus-query';
import { ProductSKU } from '../../domain/entities/product-sku';

export interface IProductQueryRepository {
  /**
   * List SKUs with filters and pagination
   */
  listSKUs(
    filters: ListSKUsFilters,
    pagination: { offset: number; limit: number },
    sort: { field: string; order: 'ASC' | 'DESC' }
  ): Promise<PaginatedResponse<ProductSKU>>;
}

/**
 * Implementation using raw SQL for optimal performance
 */
export class ProductQueryRepository implements IProductQueryRepository {
  constructor(private readonly db: any) {}

  async listSKUs(
    filters: ListSKUsFilters,
    pagination: { offset: number; limit: number },
    sort: { field: string; order: 'ASC' | 'DESC' }
  ): Promise<PaginatedResponse<ProductSKU>> {
    const { offset, limit } = pagination;

    // Build WHERE clause
    const conditions: string[] = [];
    const params: any[] = [];
    let paramIndex = 1;

    if (filters.category) {
      conditions.push(`p.category = $${paramIndex++}`);
      params.push(filters.category);
    }

    if (filters.manufacturerId) {
      conditions.push(`p.manufacturer_id = $${paramIndex++}`);
      params.push(filters.manufacturerId);
    }

    if (filters.minPrice !== undefined) {
      conditions.push(`p.price_brl >= $${paramIndex++}`);
      params.push(filters.minPrice);
    }

    if (filters.maxPrice !== undefined) {
      conditions.push(`p.price_brl <= $${paramIndex++}`);
      params.push(filters.maxPrice);
    }

    if (filters.search) {
      conditions.push(`(
        p.name ILIKE $${paramIndex} OR 
        p.ysh_sku ILIKE $${paramIndex} OR 
        p.brand ILIKE $${paramIndex}
      )`);
      params.push(`%${filters.search}%`);
      paramIndex++;
    }

    if (filters.isActive !== undefined) {
      conditions.push(`p.is_active = $${paramIndex++}`);
      params.push(filters.isActive);
    }

    const whereClause = conditions.length > 0 
      ? `WHERE ${conditions.join(' AND ')}`
      : '';

    // Map sort field to database column
    const sortFieldMap: Record<string, string> = {
      'average_price': 'p.price_brl',
      'name': 'p.name',
      'created_at': 'p.created_at',
      'updated_at': 'p.updated_at'
    };
    const sortColumn = sortFieldMap[sort.field] || 'p.price_brl';
    const sortOrder = sort.order === 'DESC' ? 'DESC' : 'ASC';

    // Count query
    const countQuery = `
      SELECT COUNT(*) as total
      FROM ysh_catalog.products p
      ${whereClause}
    `;

    // Data query
    const dataQuery = `
      SELECT 
        p.id,
        p.ysh_sku,
        p.name,
        p.description,
        p.category,
        p.manufacturer_id,
        m.name as manufacturer_name,
        p.brand,
        p.model,
        p.price_brl as average_price,
        p.price_brl as min_price,
        p.price_brl as max_price,
        p.is_active,
        p.image_url,
        p.specifications,
        p.created_at,
        p.updated_at
      FROM ysh_catalog.products p
      LEFT JOIN ysh_catalog.manufacturers m ON p.manufacturer_id = m.id
      ${whereClause}
      ORDER BY ${sortColumn} ${sortOrder}
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `;

    params.push(limit, offset);

    try {
      // Execute queries in parallel
      const [countResult, dataResult] = await Promise.all([
        this.db.query(countQuery, params.slice(0, -2)),
        this.db.query(dataQuery, params)
      ]);

      const total = parseInt(countResult.rows[0]?.total || '0', 10);
      const items = dataResult.rows.map((row: any) => 
        ProductSKU.fromPersistence(row)
      );

      const hasMore = offset + limit < total;
      const nextOffset = hasMore ? offset + limit : undefined;

      return {
        data: items,
        pagination: {
          total,
          limit,
          offset,
          hasMore,
          nextOffset
        }
      };
    } catch (error) {
      console.error('[ProductQueryRepository] Error listing SKUs:', error);
      throw error;
    }
  }
}
