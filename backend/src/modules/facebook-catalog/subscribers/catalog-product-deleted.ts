import type { SubscriberConfig } from "@medusajs/framework";

/**
 * Subscriber: Catalog Product Deleted
 * Trigger: catalog.product.deleted
 * Action: Delete SKU from Facebook Catalog
 */
export default async function handleCatalogProductDeleted({
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
            "[Facebook Sync] FACEBOOK_CATALOG_ID not configured, skipping deletion"
        );
        return;
    }

    const skuId = data.id;

    logger.info(`[Facebook Sync] Product deleted: ${skuId}, removing from Facebook...`);

    try {
        // Execute sync workflow with DELETE operation
        await syncCatalogToFacebookWorkflow(container).run({
            input: {
                catalog_id: catalogId,
                sku_ids: [skuId],
                operation: "DELETE",
            },
        });

        logger.info(`[Facebook Sync] Product ${skuId} deleted from Facebook`);
    } catch (error) {
        logger.error(`[Facebook Sync] Failed to delete product ${skuId}`, error);
    }
}

export const config: SubscriberConfig = {
    event: "catalog.product.deleted",
};
