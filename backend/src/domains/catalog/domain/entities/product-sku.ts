/**
 * ProductSKU Entity
 * 
 * Represents a Stock Keeping Unit (SKU) in the catalog domain.
 * This is a read-optimized entity for catalog queries (CQRS read model).
 * 
 * @see ADR-001 (DDD Architecture)
 */

import type { UUID, Money } from '@shared/types';

export interface ProductSKUProps {
  id: UUID;
  yshSku: string;
  name: string;
  description?: string;
  category: string;
  manufacturerId?: string;
  manufacturerName?: string;
  brand?: string;
  model?: string;
  averagePrice: Money;
  minPrice?: Money;
  maxPrice?: Money;
  isActive: boolean;
  imageUrl?: string;
  specifications?: Record<string, unknown>;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * ProductSKU Entity - Immutable read model
 */
export class ProductSKU {
  private constructor(private readonly props: ProductSKUProps) {}

  /**
   * Factory method to create ProductSKU from database row
   */
  static fromPersistence(data: any): ProductSKU {
    return new ProductSKU({
      id: data.id,
      yshSku: data.ysh_sku,
      name: data.name,
      description: data.description,
      category: data.category,
      manufacturerId: data.manufacturer_id,
      manufacturerName: data.manufacturer_name,
      brand: data.brand,
      model: data.model,
      averagePrice: {
        amount: parseFloat(data.average_price || data.price_brl || '0'),
        currency: 'BRL'
      },
      minPrice: data.min_price ? {
        amount: parseFloat(data.min_price),
        currency: 'BRL'
      } : undefined,
      maxPrice: data.max_price ? {
        amount: parseFloat(data.max_price),
        currency: 'BRL'
      } : undefined,
      isActive: data.is_active ?? true,
      imageUrl: data.image_url,
      specifications: data.specifications,
      createdAt: new Date(data.created_at),
      updatedAt: new Date(data.updated_at || data.created_at)
    });
  }

  // Getters
  get id(): UUID { return this.props.id; }
  get yshSku(): string { return this.props.yshSku; }
  get name(): string { return this.props.name; }
  get description(): string | undefined { return this.props.description; }
  get category(): string { return this.props.category; }
  get manufacturerId(): string | undefined { return this.props.manufacturerId; }
  get manufacturerName(): string | undefined { return this.props.manufacturerName; }
  get brand(): string | undefined { return this.props.brand; }
  get model(): string | undefined { return this.props.model; }
  get averagePrice(): Money { return this.props.averagePrice; }
  get minPrice(): Money | undefined { return this.props.minPrice; }
  get maxPrice(): Money | undefined { return this.props.maxPrice; }
  get isActive(): boolean { return this.props.isActive; }
  get imageUrl(): string | undefined { return this.props.imageUrl; }
  get specifications(): Record<string, unknown> | undefined { return this.props.specifications; }
  get createdAt(): Date { return this.props.createdAt; }
  get updatedAt(): Date { return this.props.updatedAt; }

  /**
   * Convert to plain object (for API responses)
   */
  toJSON(): Record<string, unknown> {
    return {
      id: this.id,
      ysh_sku: this.yshSku,
      name: this.name,
      description: this.description,
      category: this.category,
      manufacturer_id: this.manufacturerId,
      manufacturer_name: this.manufacturerName,
      brand: this.brand,
      model: this.model,
      average_price: this.averagePrice,
      min_price: this.minPrice,
      max_price: this.maxPrice,
      is_active: this.isActive,
      image_url: this.imageUrl,
      specifications: this.specifications,
      created_at: this.createdAt.toISOString(),
      updated_at: this.updatedAt.toISOString()
    };
  }
}
