import { MedusaRequest, MedusaResponse } from "@medusajs/framework/http";

/**
 * POST /admin/facebook-catalog/whatsapp/send-catalog
 * 
 * Envia mensagem do WhatsApp com lista de produtos do catálogo
 * 
 * Body:
 * - to: string (WhatsApp number with country code)
 * - sku_codes: string[] (max 30 products)
 * - header?: string
 * - message?: string
 */
export async function POST(req: MedusaRequest, res: MedusaResponse) {
    const { to, sku_codes, header, message } = req.validatedBody as {
        to: string;
        sku_codes: string[];
        header?: string;
        message?: string;
    };

    const logger = req.scope.resolve("logger");

    try {
        const { WhatsAppCatalogApiClient } = await import(
            "../../../../modules/facebook-catalog/clients/whatsapp-catalog-api"
        );

        // Get config from environment
        const config = {
            app_id: process.env.FACEBOOK_APP_ID || "",
            app_secret: process.env.FACEBOOK_APP_SECRET || "",
            access_token: process.env.FACEBOOK_ACCESS_TOKEN || "",
            catalog_id: process.env.FACEBOOK_CATALOG_ID || "",
            whatsapp_business_account_id: process.env.WHATSAPP_BUSINESS_ACCOUNT_ID,
            whatsapp_phone_number_id: process.env.WHATSAPP_PHONE_NUMBER_ID,
        };

        const whatsappClient = new WhatsAppCatalogApiClient(config);

        // WhatsApp limits: max 30 products per message
        const limitedSkuCodes = sku_codes.slice(0, 30);

        await whatsappClient.sendCatalogMessage(
            to,
            limitedSkuCodes,
            header,
            message
        );

        logger.info(
            `[WhatsApp] Catalog message sent to ${to}: ${limitedSkuCodes.length} products`
        );

        res.json({
            success: true,
            message: "Catalog message sent successfully",
            data: {
                to,
                products_sent: limitedSkuCodes.length,
                products_requested: sku_codes.length,
            },
        });
    } catch (error: any) {
        logger.error("[WhatsApp] Failed to send catalog message", error);

        res.status(500).json({
            success: false,
            error: error.message,
        });
    }
}
