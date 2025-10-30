import { model } from "@medusajs/framework/utils";

export enum CommercePlatform {
    FACEBOOK = "facebook",
    INSTAGRAM = "instagram",
    WHATSAPP = "whatsapp",
    ALL = "all",
}

export enum FacebookSyncStatus {
    PENDING = "pending",
    IN_PROGRESS = "in_progress",
    COMPLETED = "completed",
    FAILED = "failed",
    PARTIAL = "partial",
}

export enum FacebookSyncOperation {
    CREATE = "create",
    UPDATE = "update",
    DELETE = "delete",
}

/**
 * FacebookCatalogSync Model
 * Rastreia sincronizações de catálogo com Facebook Commerce Platform
 */
export const FacebookCatalogSync = model.define("facebook_catalog_sync", {
    id: model.id({ prefix: "fbsync" }).primaryKey(),
    
    // Facebook API identifiers
    catalog_id: model.text(),
    batch_handle: model.text().nullable(), // Handle retornado pela API
    
    // Multi-platform tracking
    platforms: model.json(), // CommercePlatform[] - Plataformas sincronizadas
    
    // Sync metadata
    operation: model.enum(FacebookSyncOperation),
    status: model.enum(FacebookSyncStatus).default(FacebookSyncStatus.PENDING),
    
    // SKU tracking
    sku_ids: model.json(), // string[] - SKUs incluídos neste batch
    total_items: model.number().default(0),
    
    // Results
    items_created: model.number().default(0),
    items_updated: model.number().default(0),
    items_deleted: model.number().default(0),
    items_failed: model.number().default(0),
    
    // Error tracking
    error_message: model.text().nullable(),
    error_details: model.json().nullable(),
    
    // API response
    facebook_response: model.json().nullable(),
    
    // Timestamps
    started_at: model.dateTime().nullable(),
    completed_at: model.dateTime().nullable(),
    
    metadata: model.json().nullable(),
}).indexes([
    {
        name: "IDX_fb_sync_catalog_id",
        on: ["catalog_id"],
    },
    {
        name: "IDX_fb_sync_status",
        on: ["status"],
    },
    {
        name: "IDX_fb_sync_batch_handle",
        on: ["batch_handle"],
    },
]);
