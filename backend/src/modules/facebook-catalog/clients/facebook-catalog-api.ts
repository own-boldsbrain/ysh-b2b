import axios, { AxiosInstance } from "axios";
import type {
    FacebookBatchRequest,
    FacebookBatchResponse,
    FacebookCatalogConfig,
    FacebookProductItem,
    FacebookValidationStatus,
} from "../types/facebook-catalog";

/**
 * Facebook Catalog API Client
 * https://developers.facebook.com/docs/marketing-api/catalog
 */
export class FacebookCatalogApiClient {
    private client: AxiosInstance;
    private config: FacebookCatalogConfig;

    constructor(config: FacebookCatalogConfig) {
        this.config = config;
        this.client = axios.create({
            baseURL: "https://graph.facebook.com/v21.0",
            timeout: 60000, // 60s timeout
            headers: {
                "Content-Type": "application/json",
            },
        });
    }

    /**
     * Envia batch de produtos para o catálogo
     * POST /{catalog-id}/items_batch
     */
    async uploadBatch(
        products: FacebookProductItem[],
        operation: "UPDATE" | "DELETE" = "UPDATE"
    ): Promise<FacebookBatchResponse> {
        const endpoint = `/${this.config.catalog_id}/items_batch`;

        const request: FacebookBatchRequest = {
            method: operation,
            data: products,
        };

        const response = await this.client.post(endpoint, request, {
            params: {
                access_token: this.config.access_token,
            },
        });

        return response.data;
    }

    /**
     * Verifica status de um batch request
     * GET /{catalog-id}/check_batch_request_status
     */
    async checkBatchStatus(handle: string): Promise<FacebookValidationStatus> {
        const endpoint = `/${this.config.catalog_id}/check_batch_request_status`;

        const response = await this.client.get(endpoint, {
            params: {
                access_token: this.config.access_token,
                handle,
            },
        });

        return response.data.data[0]; // API returns array with single item
    }

    /**
     * Aguarda conclusão do batch com polling
     */
    async waitForBatchCompletion(
        handle: string,
        maxAttempts: number = 30,
        delayMs: number = 2000
    ): Promise<FacebookValidationStatus> {
        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            const status = await this.checkBatchStatus(handle);

            if (status.status === "finished" || status.status === "error") {
                return status;
            }

            // Wait before next poll
            await this.sleep(delayMs);
        }

        throw new Error(`Batch ${handle} did not complete after ${maxAttempts} attempts`);
    }

    /**
     * Lista produtos do catálogo
     * GET /{catalog-id}/products
     */
    async listProducts(limit: number = 100, after?: string): Promise<{
        data: FacebookProductItem[];
        paging: { cursors: { before: string; after: string }; next?: string };
    }> {
        const endpoint = `/${this.config.catalog_id}/products`;

        const response = await this.client.get(endpoint, {
            params: {
                access_token: this.config.access_token,
                limit,
                after,
            },
        });

        return response.data;
    }

    /**
     * Obtém informações do catálogo
     * GET /{catalog-id}
     */
    async getCatalogInfo(): Promise<{
        id: string;
        name: string;
        product_count: number;
        vertical: string;
    }> {
        const endpoint = `/${this.config.catalog_id}`;

        const response = await this.client.get(endpoint, {
            params: {
                access_token: this.config.access_token,
                fields: "id,name,product_count,vertical",
            },
        });

        return response.data;
    }

    /**
     * Deleta produto individual
     * DELETE /{catalog-id}/products
     */
    async deleteProduct(retailerId: string): Promise<void> {
        const endpoint = `/${this.config.catalog_id}/products`;

        await this.client.delete(endpoint, {
            params: {
                access_token: this.config.access_token,
                retailer_id: retailerId,
            },
        });
    }

    /**
     * Helper: Sleep
     */
    private sleep(ms: number): Promise<void> {
        return new Promise((resolve) => setTimeout(resolve, ms));
    }
}
