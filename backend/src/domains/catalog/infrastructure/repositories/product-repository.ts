import type { PaginatedResponse } from '@shared/types';
import { ProductSKU } from '../../domain/entities/product-sku';

export interface ListSKUsOptions {
  categoryId?: string;
  search?: string;
  inStock?: boolean;
  offset?: number;
  limit?: number;
  sort?: string;
}

export class ProductRepository {
  constructor(private readonly db: any) {}

  async listSKUs(options: ListSKUsOptions): Promise<PaginatedResponse<ProductSKU>> {
    // Minimal stub: return empty data with pagination metadata
    const data: ProductSKU[] = [];
    const pagination = {
      total: 0,
      limit: options.limit ?? 20,
      offset: options.offset ?? 0,
      hasMore: false,
      nextOffset: undefined
    };

    return {
      data,
      pagination
    } as unknown as PaginatedResponse<ProductSKU>;
  }
}
