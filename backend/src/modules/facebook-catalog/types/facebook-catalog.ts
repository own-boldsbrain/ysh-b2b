/**
 * Facebook Commerce Platform API Types
 * Supports: Facebook Shops, Instagram Shopping, WhatsApp Business Catalog
 * Based on: https://developers.facebook.com/docs/commerce-platform/catalog
 */

export enum CommercePlatform {
    FACEBOOK = "facebook",
    INSTAGRAM = "instagram",
    WHATSAPP = "whatsapp",
    ALL = "all", // Sync to all platforms
}

export enum FacebookProductAvailability {
    IN_STOCK = "in stock",
    OUT_OF_STOCK = "out of stock",
    PREORDER = "preorder",
    AVAILABLE_FOR_ORDER = "available for order",
    DISCONTINUED = "discontinued",
}

export enum FacebookProductCondition {
    NEW = "new",
    REFURBISHED = "refurbished",
    USED = "used",
}

/**
 * Facebook Product Item
 * https://developers.facebook.com/docs/marketing-api/catalog/reference
 */
export interface FacebookProductItem {
    // Required fields
    id: string; // Unique retailer ID (sku_code)
    title: string;
    description: string;
    availability: FacebookProductAvailability;
    condition: FacebookProductCondition;
    price: string; // Format: "1000.00 BRL" or "1000.00 USD"
    link: string; // URL to product page
    image_link: string;
    brand: string;

    // Recommended fields
    google_product_category?: string; // Google Product Taxonomy ID
    product_type?: string; // Custom category hierarchy
    
    // Additional fields
    additional_image_link?: string[]; // Up to 10 additional images
    sale_price?: string; // Format: "800.00 BRL"
    sale_price_effective_date?: string; // ISO 8601 date range
    
    // Identifiers
    gtin?: string; // Global Trade Item Number (EAN/UPC)
    mpn?: string; // Manufacturer Part Number
    
    // Specifications
    item_group_id?: string; // For product variants
    color?: string;
    size?: string;
    material?: string;
    pattern?: string;
    age_group?: "adult" | "kids" | "toddler" | "infant" | "newborn";
    gender?: "male" | "female" | "unisex";
    
    // Shipping
    shipping?: FacebookShipping[];
    shipping_weight?: string; // Format: "1.5 kg" or "3.3 lb"
    
    // Custom labels (for segmentation)
    custom_label_0?: string;
    custom_label_1?: string;
    custom_label_2?: string;
    custom_label_3?: string;
    custom_label_4?: string;
    
    // Additional metadata
    inventory?: number;
    override?: string; // Override specific attributes
}

export interface FacebookShipping {
    country: string; // ISO 3166-1 alpha-2 country code
    service: string; // Shipping service name
    price: string; // Format: "10.00 BRL"
}

/**
 * Facebook Batch Request
 * https://developers.facebook.com/docs/marketing-api/catalog/guides/manage-catalog-items/catalog-batch-api
 */
export interface FacebookBatchRequest {
    method: "UPDATE" | "DELETE";
    data: FacebookProductItem[];
}

/**
 * Facebook Batch Response
 */
export interface FacebookBatchResponse {
    handles: string[]; // Batch handles for status checking
    validation_status: FacebookValidationStatus[];
}

export interface FacebookValidationStatus {
    handle: string;
    status: "finished" | "in_progress" | "error";
    errors?: FacebookBatchError[];
    warnings?: FacebookBatchWarning[];
    num_detected_items?: number;
    num_persisted_items?: number;
    num_invalid_items?: number;
}

export interface FacebookBatchError {
    error_type: string;
    error_message: string;
    line_number?: number;
    samples?: string[];
}

export interface FacebookBatchWarning {
    warning_type: string;
    warning_message: string;
    line_number?: number;
}

/**
 * Facebook Commerce Platform Catalog Config
 * Supports: Facebook Shops, Instagram Shopping, WhatsApp Business Catalog
 */
export interface FacebookCatalogConfig {
    app_id: string;
    app_secret: string;
    access_token: string;
    catalog_id: string;
    
    // Multi-platform settings
    platforms?: CommercePlatform[]; // Default: ["all"]
    
    // Instagram Shopping specific
    instagram_account_id?: string; // Required for Instagram Shopping
    
    // WhatsApp Business specific
    whatsapp_business_account_id?: string; // Required for WhatsApp Catalog
    whatsapp_phone_number_id?: string;
    
    // Optional configs
    default_availability?: FacebookProductAvailability;
    default_condition?: FacebookProductCondition;
    default_currency?: string; // BRL, USD, etc.
    base_product_url?: string; // Base URL for product links
    
    // Batch settings
    batch_size?: number; // Max 5000 items per batch
    retry_attempts?: number;
    retry_delay_ms?: number;
}

/**
 * SKU to Facebook Product Transformer
 */
export interface SKUToFacebookProductTransform {
    sku_id: string;
    sku_code: string;
    facebook_product: FacebookProductItem;
    sync_hash: string; // For change detection
}
