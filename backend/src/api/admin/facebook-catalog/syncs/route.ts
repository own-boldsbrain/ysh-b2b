import { MedusaRequest, MedusaResponse } from "@medusajs/framework/http";

/**
 * GET /admin/facebook-catalog/syncs
 * 
 * Lista histórico de sincronizações
 * 
 * Query:
 * - status?: string (filter by status)
 * - limit?: number (default: 50)
 */
export async function GET(req: MedusaRequest, res: MedusaResponse) {
    const { status, limit = 50 } = req.query as {
        status?: string;
        limit?: number;
    };

    const facebookCatalogService = req.scope.resolve("facebookCatalogService");

    try {
        const syncs = status
            ? await facebookCatalogService.listSyncsByStatus(status, Number(limit))
            : await facebookCatalogService.listFacebookCatalogSyncs({
                  config: { take: Number(limit) },
              });

        res.json({
            syncs,
            count: syncs.length,
        });
    } catch (error: any) {
        res.status(500).json({
            error: error.message,
        });
    }
}
