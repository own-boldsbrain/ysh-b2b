import axios, { AxiosInstance } from "axios";
import type {
    FacebookProductItem,
    FacebookCatalogConfig,
} from "../types/facebook-catalog";

/**
 * WhatsApp Business Catalog API Client
 * https://developers.facebook.com/docs/whatsapp/business-management-api/manage-catalogs
 */
export class WhatsAppCatalogApiClient {
    private client: AxiosInstance;
    private config: FacebookCatalogConfig;

    constructor(config: FacebookCatalogConfig) {
        this.config = config;
        this.client = axios.create({
            baseURL: "https://graph.facebook.com/v21.0",
            timeout: 60000,
            headers: {
                "Content-Type": "application/json",
            },
        });
    }

    /**
     * Conecta catálogo ao WhatsApp Business Account
     * POST /{whatsapp-business-account-id}/product_catalogs
     */
    async connectCatalogToWhatsApp(): Promise<void> {
        if (!this.config.whatsapp_business_account_id) {
            throw new Error("whatsapp_business_account_id is required for WhatsApp Catalog");
        }

        const endpoint = `/${this.config.whatsapp_business_account_id}/product_catalogs`;

        await this.client.post(
            endpoint,
            {
                catalog_id: this.config.catalog_id,
            },
            {
                params: {
                    access_token: this.config.access_token,
                },
            }
        );
    }

    /**
     * Lista catálogos conectados ao WhatsApp
     * GET /{whatsapp-business-account-id}/product_catalogs
     */
    async listConnectedCatalogs(): Promise<{
        id: string;
        name: string;
        product_count: number;
    }[]> {
        if (!this.config.whatsapp_business_account_id) {
            throw new Error("whatsapp_business_account_id is required");
        }

        const endpoint = `/${this.config.whatsapp_business_account_id}/product_catalogs`;

        const response = await this.client.get(endpoint, {
            params: {
                access_token: this.config.access_token,
            },
        });

        return response.data.data;
    }

    /**
     * Verifica se catálogo está conectado ao WhatsApp
     */
    async checkWhatsAppCatalogStatus(): Promise<{
        connected: boolean;
        catalog_id?: string;
    }> {
        try {
            const catalogs = await this.listConnectedCatalogs();
            const connected = catalogs.some((cat) => cat.id === this.config.catalog_id);

            return {
                connected,
                catalog_id: connected ? this.config.catalog_id : undefined,
            };
        } catch (error) {
            return { connected: false };
        }
    }

    /**
     * Envia mensagem do WhatsApp com produto do catálogo
     * POST /{whatsapp-phone-number-id}/messages
     */
    async sendProductMessage(
        to: string,
        productRetailerId: string,
        bodyText?: string
    ): Promise<void> {
        if (!this.config.whatsapp_phone_number_id) {
            throw new Error("whatsapp_phone_number_id is required");
        }

        const endpoint = `/${this.config.whatsapp_phone_number_id}/messages`;

        await this.client.post(
            endpoint,
            {
                messaging_product: "whatsapp",
                recipient_type: "individual",
                to,
                type: "interactive",
                interactive: {
                    type: "product",
                    body: {
                        text: bodyText || "Confira este produto!",
                    },
                    action: {
                        catalog_id: this.config.catalog_id,
                        product_retailer_id: productRetailerId,
                    },
                },
            },
            {
                params: {
                    access_token: this.config.access_token,
                },
            }
        );
    }

    /**
     * Envia mensagem do WhatsApp com múltiplos produtos (catálogo)
     * POST /{whatsapp-phone-number-id}/messages
     */
    async sendCatalogMessage(
        to: string,
        productRetailerIds: string[],
        headerText?: string,
        bodyText?: string
    ): Promise<void> {
        if (!this.config.whatsapp_phone_number_id) {
            throw new Error("whatsapp_phone_number_id is required");
        }

        const endpoint = `/${this.config.whatsapp_phone_number_id}/messages`;

        await this.client.post(
            endpoint,
            {
                messaging_product: "whatsapp",
                recipient_type: "individual",
                to,
                type: "interactive",
                interactive: {
                    type: "product_list",
                    header: {
                        type: "text",
                        text: headerText || "Nossos Produtos",
                    },
                    body: {
                        text: bodyText || "Escolha um produto abaixo:",
                    },
                    action: {
                        catalog_id: this.config.catalog_id,
                        sections: [
                            {
                                title: "Produtos Solares",
                                product_items: productRetailerIds.map((id) => ({
                                    product_retailer_id: id,
                                })),
                            },
                        ],
                    },
                },
            },
            {
                params: {
                    access_token: this.config.access_token,
                },
            }
        );
    }

    /**
     * Atualiza configurações do catálogo no WhatsApp
     * POST /{catalog-id}
     */
    async updateCatalogSettings(settings: {
        is_catalog_visible?: boolean;
    }): Promise<void> {
        const endpoint = `/${this.config.catalog_id}`;

        await this.client.post(endpoint, settings, {
            params: {
                access_token: this.config.access_token,
            },
        });
    }
}
