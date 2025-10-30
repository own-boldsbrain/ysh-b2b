import { MedusaRequest, MedusaResponse } from "@medusajs/framework/http";

/**
 * GET /admin/facebook-catalog/platforms/status
 * 
 * Verifica status de integração com cada plataforma
 * (Facebook Shops, Instagram Shopping, WhatsApp Business Catalog)
 */
export async function GET(req: MedusaRequest, res: MedusaResponse) {
    const logger = req.scope.resolve("logger");

    try {
        const { FacebookCatalogApiClient } = await import(
            "../../../../modules/facebook-catalog/clients/facebook-catalog-api"
        );
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

        // Check Facebook Catalog
        const facebookClient = new FacebookCatalogApiClient(config);
        let facebookStatus = {
            platform: "facebook",
            enabled: false,
            catalog_info: null as any,
            error: null as string | null,
        };

        try {
            const catalogInfo = await facebookClient.getCatalogInfo();
            facebookStatus.enabled = true;
            facebookStatus.catalog_info = catalogInfo;
        } catch (error: any) {
            facebookStatus.error = error.message;
        }

        // Check Instagram Shopping
        const instagramClient = new InstagramShoppingApiClient(config);
        let instagramStatus = {
            platform: "instagram",
            enabled: false,
            connected: false,
            account_id: config.instagram_account_id,
            error: null as string | null,
        };

        try {
            if (config.instagram_account_id) {
                const status = await instagramClient.checkInstagramShoppingStatus();
                instagramStatus.enabled = status.enabled;
                instagramStatus.connected = status.enabled;
            } else {
                instagramStatus.error = "instagram_account_id not configured";
            }
        } catch (error: any) {
            instagramStatus.error = error.message;
        }

        // Check WhatsApp Catalog
        const whatsappClient = new WhatsAppCatalogApiClient(config);
        let whatsappStatus = {
            platform: "whatsapp",
            enabled: false,
            connected: false,
            business_account_id: config.whatsapp_business_account_id,
            phone_number_id: config.whatsapp_phone_number_id,
            error: null as string | null,
        };

        try {
            if (config.whatsapp_business_account_id) {
                const status = await whatsappClient.checkWhatsAppCatalogStatus();
                whatsappStatus.enabled = status.connected;
                whatsappStatus.connected = status.connected;
            } else {
                whatsappStatus.error = "whatsapp_business_account_id not configured";
            }
        } catch (error: any) {
            whatsappStatus.error = error.message;
        }

        res.json({
            platforms: {
                facebook: facebookStatus,
                instagram: instagramStatus,
                whatsapp: whatsappStatus,
            },
            summary: {
                total_platforms: 3,
                enabled_platforms: [facebookStatus, instagramStatus, whatsappStatus].filter(
                    (p) => p.enabled
                ).length,
                catalog_id: config.catalog_id,
            },
        });
    } catch (error: any) {
        logger.error("[Platform Status] Failed to check platform status", error);

        res.status(500).json({
            error: error.message,
        });
    }
}
