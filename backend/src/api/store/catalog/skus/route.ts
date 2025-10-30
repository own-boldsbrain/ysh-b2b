import { AuthenticatedMedusaRequest, MedusaResponse } from "@medusajs/framework";
import {
    StoreGetCatalogSKUsParams,
    StoreGetCatalogSKUsParamsType,
} from "../validators";
import { UNIFIED_CATALOG_MODULE } from "../../../../modules/unified-catalog";
import { dddCatalogHandlers } from "../../../../domains/catalog/interfaces/http/catalog-routes";

/**
 * GET /store/catalog/skus
 * Lista SKUs com filtros avançados
 * 
 * Feature flag: CATALOG_DDD_ENABLED
 * - true: Use new DDD/CQRS implementation with Redis cache
 * - false: Use legacy Unified Catalog module
 */
export const GET = async (
    req: MedusaRequest<StoreGetCatalogSKUsParamsType>,
    res: MedusaResponse
) => {
    // Route to DDD implementation if feature flag enabled
    if (dddCatalogHandlers.isEnabled) {
        return dddCatalogHandlers.listSKUs(req, res);
    }

    // Legacy implementation (Unified Catalog)
    const catalogService = req.scope.resolve(UNIFIED_CATALOG_MODULE) as any;

    const validatedQuery = StoreGetCatalogSKUsParams.parse(req.query);

    const { limit, offset, ...filters } = validatedQuery;

    // Buscar SKUs
    const [skus, count] = await (catalogService as any).listAndCountSKUs(
        {
            ...(filters.category && { category: filters.category }),
            ...(filters.manufacturer_id && {
                manufacturer_id: filters.manufacturer_id,
            }),
            ...(filters.min_price && {
                average_price: { $gte: filters.min_price },
            }),
            ...(filters.max_price && {
                average_price: { $lte: filters.max_price },
            }),
            is_active: true,
        },
        {
            skip: offset,
            take: limit,
            order: { average_price: "ASC" },
        }
    );

    res.json({
        skus,
        count,
        limit,
        offset,
    });
};
