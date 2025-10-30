import { MedusaRequest, MedusaResponse } from "@medusajs/framework/http";
import { syncCatalogToFacebookWorkflow } from "../../../modules/facebook-catalog/workflows/sync-catalog-to-facebook";

/**
 * POST /admin/facebook-catalog/sync
 * 
 * Sincroniza catálogo YSH com Facebook Commerce Platform
 * 
 * Body:
 * - catalog_id: string (required)
 * - sku_ids?: string[] (optional: sync specific SKUs)
 * - operation?: "UPDATE" | "DELETE" (default: "UPDATE")
 * - batch_size?: number (default: 5000)
 */
export async function POST(req: MedusaRequest, res: MedusaResponse) {
    const { catalog_id, sku_ids, operation, batch_size } = req.validatedBody as {
        catalog_id: string;
        sku_ids?: string[];
        operation?: "UPDATE" | "DELETE";
        batch_size?: number;
    };

    const logger = req.scope.resolve("logger");

    logger.info(`[Facebook Sync] Manual sync triggered for catalog ${catalog_id}`);

    try {
        const { result } = await syncCatalogToFacebookWorkflow(req.scope).run({
            input: {
                catalog_id,
                sku_ids,
                operation: operation || "UPDATE",
                batch_size: batch_size || 5000,
            },
        });

        logger.info(`[Facebook Sync] Sync completed successfully`);

        res.json({
            success: true,
            data: result,
        });
    } catch (error: any) {
        logger.error("[Facebook Sync] Sync failed", error);

        res.status(500).json({
            success: false,
            error: error.message,
            details: error,
        });
    }
}
