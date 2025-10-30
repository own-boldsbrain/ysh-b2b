import { MedusaService } from "@medusajs/framework/utils";
import { FacebookCatalogSync, FacebookProductMapping } from "../models";

/**
 * Facebook Catalog Service
 * Gerencia sincronização com Facebook Commerce Platform
 */
export default class FacebookCatalogService extends MedusaService({
    FacebookCatalogSync,
    FacebookProductMapping,
}) {
    /**
     * Cria registro de sync
     */
    async createSync(data: {
        catalog_id: string;
        operation: string;
        sku_ids: string[];
        total_items: number;
    }) {
        return await this.createFacebookCatalogSyncs(data);
    }

    /**
     * Atualiza status do sync
     */
    async updateSyncStatus(
        syncId: string,
        updates: {
            status?: string;
            batch_handle?: string;
            items_created?: number;
            items_updated?: number;
            items_deleted?: number;
            items_failed?: number;
            error_message?: string;
            error_details?: any;
            facebook_response?: any;
            started_at?: Date;
            completed_at?: Date;
        }
    ) {
        return await this.updateFacebookCatalogSyncs(syncId, updates);
    }

    /**
     * Lista syncs por status
     */
    async listSyncsByStatus(status: string, limit: number = 50) {
        return await this.listFacebookCatalogSyncs({
            filters: { status },
            config: { take: limit },
        });
    }

    /**
     * Cria mapeamento SKU → Facebook Product
     */
    async createMapping(data: {
        sku_id: string;
        sku_code: string;
        catalog_id: string;
        retailer_id: string;
        sync_hash: string;
        facebook_product_id?: string;
    }) {
        return await this.createFacebookProductMappings(data);
    }

    /**
     * Atualiza mapeamento
     */
    async updateMapping(
        mappingId: string,
        updates: {
            last_synced_at?: Date;
            sync_hash?: string;
            status?: string;
            facebook_product_id?: string;
            facebook_errors?: any;
        }
    ) {
        return await this.updateFacebookProductMappings(mappingId, updates);
    }

    /**
     * Busca mapeamento por SKU
     */
    async findMappingBySKU(sku_id: string) {
        const [mapping] = await this.listFacebookProductMappings({
            filters: { sku_id },
            config: { take: 1 },
        });

        return mapping;
    }

    /**
     * Busca mapeamento por retailer_id
     */
    async findMappingByRetailerId(catalog_id: string, retailer_id: string) {
        const [mapping] = await this.listFacebookProductMappings({
            filters: { catalog_id, retailer_id },
            config: { take: 1 },
        });

        return mapping;
    }

    /**
     * Lista produtos que precisam de sync (hash diferente)
     */
    async findProductsNeedingSync(catalog_id: string, limit: number = 100) {
        // This would require custom query - simplified for now
        return await this.listFacebookProductMappings({
            filters: { catalog_id },
            config: { take: limit },
        });
    }

    /**
     * Marca produtos como deletados no Facebook
     */
    async markAsArchived(sku_ids: string[]) {
        // Bulk update - would need custom implementation
        // For now, update one by one
        const updates = [];
        for (const sku_id of sku_ids) {
            const mapping = await this.findMappingBySKU(sku_id);
            if (mapping) {
                updates.push(
                    this.updateMapping(mapping.id, {
                        status: "archived",
                        last_synced_at: new Date(),
                    })
                );
            }
        }

        return await Promise.all(updates);
    }
}
