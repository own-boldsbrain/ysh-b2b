import { model } from "@medusajs/framework/utils";

export enum CommercePlatform {
    FACEBOOK = "facebook",
    INSTAGRAM = "instagram",
    WHATSAPP = "whatsapp",
    ALL = "all",
}

export enum FacebookProductStatus {
    ACTIVE = "active",
    ARCHIVED = "archived",
    STAGED = "staged",
}

/**
 * FacebookProductMapping Model
 * Mapeia SKUs do YSH para produtos no Facebook Catalog
 */
export const FacebookProductMapping = model.define("facebook_product_mapping", {
    id: model.id({ prefix: "fbprod" }).primaryKey(),
    
    // YSH SKU reference
    sku_id: model.text(),
    sku_code: model.text(),
    
    // Facebook identifiers
    catalog_id: model.text(),
    retailer_id: model.text(), // ID único no Facebook (geralmente sku_code)
    
    // Multi-platform tracking
    synced_platforms: model.json().nullable(), // CommercePlatform[] - Onde o produto está disponível
    
    // Facebook product data
    product_group_id: model.text().nullable(), // Para variações
    status: model.enum(FacebookProductStatus).default(FacebookProductStatus.ACTIVE),
    
    // Sync tracking
    last_synced_at: model.dateTime().nullable(),
    sync_hash: model.text().nullable(), // Hash do conteúdo para detectar mudanças
    
    // Facebook response metadata
    facebook_product_id: model.text().nullable(),
    facebook_errors: model.json().nullable(),
    
    metadata: model.json().nullable(),
}).indexes([
    {
        name: "IDX_fb_mapping_sku_id",
        on: ["sku_id"],
    },
    {
        name: "IDX_fb_mapping_catalog_retailer",
        on: ["catalog_id", "retailer_id"],
        unique: true,
    },
    {
        name: "IDX_fb_mapping_status",
        on: ["status"],
    },
]);
