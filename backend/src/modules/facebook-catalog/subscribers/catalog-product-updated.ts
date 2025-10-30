import type { SubscriberConfig } from "@medusajs/framework";
import { Modules } from "@medusajs/framework/utils";

/**
 * Subscriber: Catalog Product Updated
 * Trigger: catalog.product.updated, catalog.product.created
 * Action: Sync SKU to Facebook Catalog
 */
export default async function handleCatalogProductUpdated({
    event: { data },
    container,
}: SubscriberConfig) {
    const logger = container.resolve("logger");
    const { syncCatalogToFacebookWorkflow } = await import(
        "../workflows/sync-catalog-to-facebook"
    );

    const catalogId = process.env.FACEBOOK_CATALOG_ID;

    if (!catalogId) {
        logger.warn(
            "[Facebook Sync] FACEBOOK_CATALOG_ID not configured, skipping sync"
        );
        return;
    }

    const skuId = data.id;

    logger.info(`[Facebook Sync] Product updated: ${skuId}, triggering sync...`);

    try {
        // Execute sync workflow for single SKU
        await syncCatalogToFacebookWorkflow(container).run({
            input: {
                catalog_id: catalogId,
                sku_ids: [skuId],
                operation: "UPDATE",
            },
        });

        logger.info(`[Facebook Sync] Product ${skuId} synced successfully`);
    } catch (error) {
        logger.error(`[Facebook Sync] Failed to sync product ${skuId}`, error);
    }
}

export const config: SubscriberConfig = {
    event: ["catalog.product.updated", "catalog.product.created"],
};
