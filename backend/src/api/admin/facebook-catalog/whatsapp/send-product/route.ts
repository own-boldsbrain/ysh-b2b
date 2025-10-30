import { MedusaRequest, MedusaResponse } from "@medusajs/framework/http";

/**
 * POST /admin/facebook-catalog/whatsapp/send-product
 * 
 * Envia mensagem do WhatsApp com produto do catálogo
 * 
 * Body:
 * - to: string (WhatsApp number with country code)
 * - sku_code: string
 * - message?: string
 */
export async function POST(req: MedusaRequest, res: MedusaResponse) {
    const { to, sku_code, message } = req.validatedBody as {
        to: string;
        sku_code: string;
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

        await whatsappClient.sendProductMessage(to, sku_code, message);

        logger.info(`[WhatsApp] Product message sent to ${to}: ${sku_code}`);

        res.json({
            success: true,
            message: "Product message sent successfully",
            data: {
                to,
                sku_code,
            },
        });
    } catch (error: any) {
        logger.error("[WhatsApp] Failed to send product message", error);

        res.status(500).json({
            success: false,
            error: error.message,
        });
    }
}
