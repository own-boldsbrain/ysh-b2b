import {
    createStep,
    StepResponse,
    createWorkflow,
    WorkflowResponse,
} from "@medusajs/workflows-sdk";
import { Modules } from "@medusajs/framework/utils";

type SyncCatalogToFacebookInput = {
    catalog_id: string;
    sku_ids?: string[]; // Optional: sync specific SKUs, or all if empty
    operation?: "UPDATE" | "DELETE";
    batch_size?: number;
};

/**
 * Step 1: Busca SKUs ativos do catálogo
 */
export const fetchActiveSKUsStep = createStep(
    "fetch-active-skus",
    async (input: SyncCatalogToFacebookInput, { container }) => {
        const logger = container.resolve("logger");
        const unifiedCatalogService = container.resolve("unifiedCatalogService");

        logger.info("[Facebook Sync] Fetching active SKUs...");

        // Fetch SKUs with manufacturer relationship
        const skus = await unifiedCatalogService.listSKUs({
            filters: {
                is_active: true,
                ...(input.sku_ids ? { id: input.sku_ids } : {}),
            },
            relations: ["manufacturer", "offers"],
            config: {
                take: 10000, // Fetch all active SKUs
            },
        });

        logger.info(`[Facebook Sync] Found ${skus.length} active SKUs`);

        return new StepResponse({ skus });
    }
);

/**
 * Step 2: Transforma SKUs para formato Facebook
 */
export const transformSKUsToFacebookProductsStep = createStep(
    "transform-skus-to-facebook",
    async (
        input: {
            skus: any[];
            catalog_id: string;
        },
        { container }
    ) => {
        const logger = container.resolve("logger");
        const { SKUToFacebookProductTransformer } = await import(
            "../transformers/sku-to-facebook-product"
        );

        logger.info("[Facebook Sync] Transforming SKUs to Facebook products...");

        // Get config from environment or module options
        const config = {
            app_id: process.env.FACEBOOK_APP_ID || "",
            app_secret: process.env.FACEBOOK_APP_SECRET || "",
            access_token: process.env.FACEBOOK_ACCESS_TOKEN || "",
            catalog_id: input.catalog_id,
            base_product_url: process.env.FACEBOOK_BASE_PRODUCT_URL || "https://ysh.com.br/produtos",
            default_currency: "BRL",
            batch_size: 5000,
        };

        const transformer = new SKUToFacebookProductTransformer(config);

        // Build offers map
        const offersMap = new Map();
        for (const sku of input.skus) {
            if (sku.offers && sku.offers.length > 0) {
                offersMap.set(sku.id, sku.offers);
            }
        }

        const transformedProducts = transformer.transformBatch(input.skus, offersMap);

        logger.info(`[Facebook Sync] Transformed ${transformedProducts.length} products`);

        return new StepResponse({ transformedProducts });
    }
);

/**
 * Step 3: Envia batch para Facebook API
 */
export const uploadBatchToFacebookStep = createStep(
    "upload-batch-to-facebook",
    async (
        input: {
            transformedProducts: any[];
            catalog_id: string;
            operation: "UPDATE" | "DELETE";
            batch_size: number;
        },
        { container }
    ) => {
        const logger = container.resolve("logger");
        const facebookCatalogService = container.resolve("facebookCatalogService");
        const { FacebookCatalogApiClient } = await import("../clients/facebook-catalog-api");

        logger.info("[Facebook Sync] Uploading batch to Facebook...");

        // Get config
        const config = {
            app_id: process.env.FACEBOOK_APP_ID || "",
            app_secret: process.env.FACEBOOK_APP_SECRET || "",
            access_token: process.env.FACEBOOK_ACCESS_TOKEN || "",
            catalog_id: input.catalog_id,
            batch_size: input.batch_size || 5000,
        };

        const client = new FacebookCatalogApiClient(config);

        // Split into batches (max 5000 items per batch)
        const batches = [];
        for (let i = 0; i < input.transformedProducts.length; i += config.batch_size) {
            batches.push(input.transformedProducts.slice(i, i + config.batch_size));
        }

        logger.info(`[Facebook Sync] Uploading ${batches.length} batches...`);

        const results = [];

        for (const batch of batches) {
            // Create sync record
            const sync = await facebookCatalogService.createSync({
                catalog_id: input.catalog_id,
                operation: input.operation,
                sku_ids: batch.map((p: any) => p.sku_id),
                total_items: batch.length,
            });

            try {
                // Update sync to in_progress
                await facebookCatalogService.updateSyncStatus(sync.id, {
                    status: "in_progress",
                    started_at: new Date(),
                });

                // Upload to Facebook
                const facebookProducts = batch.map((p: any) => p.facebook_product);
                const response = await client.uploadBatch(facebookProducts, input.operation);

                // Store batch handle
                const handle = response.handles[0];
                await facebookCatalogService.updateSyncStatus(sync.id, {
                    batch_handle: handle,
                    facebook_response: response,
                });

                results.push({
                    sync_id: sync.id,
                    batch_handle: handle,
                    batch_size: batch.length,
                });

                logger.info(`[Facebook Sync] Batch uploaded, handle: ${handle}`);
            } catch (error) {
                logger.error("[Facebook Sync] Batch upload failed", error);

                await facebookCatalogService.updateSyncStatus(sync.id, {
                    status: "failed",
                    error_message: error.message,
                    error_details: error,
                    completed_at: new Date(),
                });

                throw error;
            }
        }

        return new StepResponse({ results });
    },
    async (input, { container }) => {
        // Compensation: Mark syncs as failed on rollback
        const logger = container.resolve("logger");
        const facebookCatalogService = container.resolve("facebookCatalogService");

        logger.info("[Facebook Sync] Rolling back batch uploads...");

        for (const result of input.results) {
            await facebookCatalogService.updateSyncStatus(result.sync_id, {
                status: "failed",
                error_message: "Workflow rolled back",
                completed_at: new Date(),
            });
        }
    }
);

/**
 * Step 4: Aguarda conclusão dos batches
 */
export const waitForBatchCompletionStep = createStep(
    "wait-for-batch-completion",
    async (
        input: {
            results: Array<{ sync_id: string; batch_handle: string; batch_size: number }>;
            catalog_id: string;
        },
        { container }
    ) => {
        const logger = container.resolve("logger");
        const facebookCatalogService = container.resolve("facebookCatalogService");
        const { FacebookCatalogApiClient } = await import("../clients/facebook-catalog-api");

        logger.info("[Facebook Sync] Waiting for batch completion...");

        const config = {
            app_id: process.env.FACEBOOK_APP_ID || "",
            app_secret: process.env.FACEBOOK_APP_SECRET || "",
            access_token: process.env.FACEBOOK_ACCESS_TOKEN || "",
            catalog_id: input.catalog_id,
        };

        const client = new FacebookCatalogApiClient(config);

        const completedBatches = [];

        for (const result of input.results) {
            try {
                const status = await client.waitForBatchCompletion(result.batch_handle);

                // Update sync with results
                await facebookCatalogService.updateSyncStatus(result.sync_id, {
                    status: status.status === "finished" ? "completed" : "failed",
                    items_created: status.num_persisted_items || 0,
                    items_failed: status.num_invalid_items || 0,
                    error_details: status.errors,
                    facebook_response: status,
                    completed_at: new Date(),
                });

                completedBatches.push({
                    sync_id: result.sync_id,
                    status: status.status,
                    items_persisted: status.num_persisted_items || 0,
                    items_failed: status.num_invalid_items || 0,
                });

                logger.info(
                    `[Facebook Sync] Batch ${result.batch_handle} completed: ${status.num_persisted_items} persisted, ${status.num_invalid_items} failed`
                );
            } catch (error) {
                logger.error(`[Facebook Sync] Batch ${result.batch_handle} failed`, error);

                await facebookCatalogService.updateSyncStatus(result.sync_id, {
                    status: "failed",
                    error_message: error.message,
                    error_details: error,
                    completed_at: new Date(),
                });

                completedBatches.push({
                    sync_id: result.sync_id,
                    status: "error",
                    error: error.message,
                });
            }
        }

        return new StepResponse({ completedBatches });
    }
);

/**
 * Step 5: Atualiza mapeamentos de produtos
 */
export const updateProductMappingsStep = createStep(
    "update-product-mappings",
    async (
        input: {
            transformedProducts: any[];
            catalog_id: string;
            completedBatches: any[];
        },
        { container }
    ) => {
        const logger = container.resolve("logger");
        const facebookCatalogService = container.resolve("facebookCatalogService");

        logger.info("[Facebook Sync] Updating product mappings...");

        const updatedMappings = [];

        for (const product of input.transformedProducts) {
            try {
                // Check if mapping exists
                const existingMapping = await facebookCatalogService.findMappingBySKU(
                    product.sku_id
                );

                if (existingMapping) {
                    // Update existing mapping
                    await facebookCatalogService.updateMapping(existingMapping.id, {
                        sync_hash: product.sync_hash,
                        last_synced_at: new Date(),
                        status: "active",
                    });

                    updatedMappings.push({ sku_id: product.sku_id, action: "updated" });
                } else {
                    // Create new mapping
                    await facebookCatalogService.createMapping({
                        sku_id: product.sku_id,
                        sku_code: product.sku_code,
                        catalog_id: input.catalog_id,
                        retailer_id: product.facebook_product.id,
                        sync_hash: product.sync_hash,
                    });

                    updatedMappings.push({ sku_id: product.sku_id, action: "created" });
                }
            } catch (error) {
                logger.error(`[Facebook Sync] Failed to update mapping for ${product.sku_id}`, error);
            }
        }

        logger.info(`[Facebook Sync] Updated ${updatedMappings.length} product mappings`);

        return new StepResponse({ updatedMappings });
    }
);

/**
 * Workflow: Sincroniza catálogo com Facebook
 */
export const syncCatalogToFacebookWorkflow = createWorkflow(
    "sync-catalog-to-facebook",
    (input: SyncCatalogToFacebookInput) => {
        // Step 1: Fetch SKUs
        const { skus } = fetchActiveSKUsStep(input);

        // Step 2: Transform to Facebook format
        const { transformedProducts } = transformSKUsToFacebookProductsStep({
            skus,
            catalog_id: input.catalog_id,
        });

        // Step 3: Upload batches
        const { results } = uploadBatchToFacebookStep({
            transformedProducts,
            catalog_id: input.catalog_id,
            operation: input.operation || "UPDATE",
            batch_size: input.batch_size || 5000,
        });

        // Step 4: Wait for completion
        const { completedBatches } = waitForBatchCompletionStep({
            results,
            catalog_id: input.catalog_id,
        });

        // Step 5: Update mappings
        const { updatedMappings } = updateProductMappingsStep({
            transformedProducts,
            catalog_id: input.catalog_id,
            completedBatches,
        });

        return new WorkflowResponse({
            total_skus: skus.length,
            total_batches: results.length,
            completed_batches: completedBatches,
            updated_mappings: updatedMappings.length,
        });
    }
);
