import axios, { AxiosInstance } from "axios";
import type {
    FacebookCatalogConfig,
} from "../types/facebook-catalog";

/**
 * Instagram Shopping API Client
 * https://developers.facebook.com/docs/commerce-platform/catalog
 */
export class InstagramShoppingApiClient {
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
     * Conecta Instagram account ao catálogo
     * POST /{catalog-id}/shops
     */
    async connectInstagramAccount(): Promise<void> {
        if (!this.config.instagram_account_id) {
            throw new Error("instagram_account_id is required for Instagram Shopping");
        }

        const endpoint = `/${this.config.catalog_id}/shops`;

        await this.client.post(
            endpoint,
            {
                instagram_account_id: this.config.instagram_account_id,
            },
            {
                params: {
                    access_token: this.config.access_token,
                },
            }
        );
    }

    /**
     * Verifica se Instagram Shopping está configurado
     * GET /{catalog-id}/product_groups
     */
    async checkInstagramShoppingStatus(): Promise<{
        enabled: boolean;
        account_id?: string;
    }> {
        try {
            const endpoint = `/${this.config.catalog_id}/product_groups`;

            const response = await this.client.get(endpoint, {
                params: {
                    access_token: this.config.access_token,
                    fields: "id,retailer_id",
                    limit: 1,
                },
            });

            return {
                enabled: response.data.data.length > 0,
                account_id: this.config.instagram_account_id,
            };
        } catch (error) {
            return { enabled: false };
        }
    }

    /**
     * Habilita produto para Instagram Shopping
     * POST /{product-id}
     * 
     * Nota: Instagram Shopping usa o mesmo catálogo do Facebook.
     * Produtos são automaticamente disponíveis no Instagram se o account estiver conectado.
     */
    async enableProductForInstagram(productId: string): Promise<void> {
        // Instagram Shopping usa o mesmo catálogo
        // Apenas verificar se está conectado
        const status = await this.checkInstagramShoppingStatus();
        
        if (!status.enabled) {
            await this.connectInstagramAccount();
        }
    }

    /**
     * Lista produtos disponíveis no Instagram Shopping
     * GET /{instagram-account-id}/available_catalogs
     */
    async listAvailableCatalogs(): Promise<{
        id: string;
        name: string;
        product_count: number;
    }[]> {
        if (!this.config.instagram_account_id) {
            throw new Error("instagram_account_id is required");
        }

        const endpoint = `/${this.config.instagram_account_id}/available_catalogs`;

        const response = await this.client.get(endpoint, {
            params: {
                access_token: this.config.access_token,
            },
        });

        return response.data.data;
    }
}
