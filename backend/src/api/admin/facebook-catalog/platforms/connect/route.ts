import { MedusaRequest, MedusaResponse } from "@medusajs/framework/http";

/**
 * POST /admin/facebook-catalog/platforms/connect
 * 
 * Conecta catálogo às plataformas (Instagram e WhatsApp)
 * 
 * Body:
 * - platform: "instagram" | "whatsapp" | "all"
 */
export async function POST(req: MedusaRequest, res: MedusaResponse) {
    const { platform } = req.validatedBody as {
        platform: "instagram" | "whatsapp" | "all";
    };

    const logger = req.scope.resolve("logger");

    try {
        const { InstagramShoppingApiClient } = await import(
            "../../../../modules/facebook-catalog/clients/instagram-shopping-api"
        );
        const { WhatsAppCatalogApiClient } = await import(
            "../../../../modules/facebook-catalog/clients/whatsapp-catalog-api"
        );

        // Get config from environment
        const config = {
            app_id: process.env.FACEBOOK_APP_ID || "",
            app_secret: process.env.FACEBOOK_APP_SECRET || "",
            access_token: process.env.FACEBOOK_ACCESS_TOKEN || "",
            catalog_id: process.env.FACEBOOK_CATALOG_ID || "",
            instagram_account_id: process.env.INSTAGRAM_ACCOUNT_ID,
            whatsapp_business_account_id: process.env.WHATSAPP_BUSINESS_ACCOUNT_ID,
            whatsapp_phone_number_id: process.env.WHATSAPP_PHONE_NUMBER_ID,
        };

        const results: any[] = [];

        // Connect Instagram
        if (platform === "instagram" || platform === "all") {
            try {
                const instagramClient = new InstagramShoppingApiClient(config);
                await instagramClient.connectInstagramAccount();
                
                results.push({
                    platform: "instagram",
                    success: true,
                    message: "Instagram Shopping connected successfully",
                });

                logger.info("[Platform Connect] Instagram Shopping connected");
            } catch (error: any) {
                results.push({
                    platform: "instagram",
                    success: false,
                    error: error.message,
                });

                logger.error("[Platform Connect] Instagram connection failed", error);
            }
        }

        // Connect WhatsApp
        if (platform === "whatsapp" || platform === "all") {
            try {
                const whatsappClient = new WhatsAppCatalogApiClient(config);
                await whatsappClient.connectCatalogToWhatsApp();
                
                results.push({
                    platform: "whatsapp",
                    success: true,
                    message: "WhatsApp Business Catalog connected successfully",
                });

                logger.info("[Platform Connect] WhatsApp Catalog connected");
            } catch (error: any) {
                results.push({
                    platform: "whatsapp",
                    success: false,
                    error: error.message,
                });

                logger.error("[Platform Connect] WhatsApp connection failed", error);
            }
        }

        const allSuccessful = results.every((r) => r.success);

        res.json({
            success: allSuccessful,
            results,
        });
    } catch (error: any) {
        logger.error("[Platform Connect] Failed to connect platforms", error);

        res.status(500).json({
            success: false,
            error: error.message,
        });
    }
}
