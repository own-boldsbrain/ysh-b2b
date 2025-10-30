import { MedusaRequest, MedusaResponse } from "@medusajs/framework/http";

/**
 * GET /admin/facebook-catalog/mappings
 * 
 * Lista mapeamentos SKU → Facebook Product
 * 
 * Query:
 * - sku_id?: string (filter by SKU)
 * - status?: string (filter by status)
 * - limit?: number (default: 100)
 */
export async function GET(req: MedusaRequest, res: MedusaResponse) {
    const { sku_id, status, limit = 100 } = req.query as {
        sku_id?: string;
        status?: string;
        limit?: number;
    };

    const facebookCatalogService = req.scope.resolve("facebookCatalogService");

    try {
        const mappings = await facebookCatalogService.listFacebookProductMappings({
            filters: {
                ...(sku_id ? { sku_id } : {}),
                ...(status ? { status } : {}),
            },
            config: { take: Number(limit) },
        });

        res.json({
            mappings,
            count: mappings.length,
        });
    } catch (error: any) {
        res.status(500).json({
            error: error.message,
        });
    }
}
