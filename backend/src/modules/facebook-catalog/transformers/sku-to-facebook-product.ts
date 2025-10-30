import { createHash } from "crypto";
import type { SKU, Manufacturer } from "../../unified-catalog/models";
import type {
    FacebookProductItem,
    FacebookProductAvailability,
    FacebookProductCondition,
    FacebookCatalogConfig,
    SKUToFacebookProductTransform,
} from "../types/facebook-catalog";

/**
 * Category to Google Product Taxonomy Mapping
 * https://support.google.com/merchants/answer/6324436
 */
const CATEGORY_TO_GOOGLE_TAXONOMY: Record<string, string> = {
    panels: "1279", // Electronics > Electronics Accessories > Solar Panels
    inverters: "1801", // Electronics > Electronics Accessories > Power Inverters
    batteries: "505371", // Electronics > Electronics Accessories > Power > Batteries
    charge_controllers: "1801", // Electronics > Electronics Accessories > Power
    structures: "632", // Hardware > Building Materials
    monitoring: "1801", // Electronics > Electronics Accessories
    cables: "238", // Electronics > Electronics Accessories > Cables
    connectors: "238", // Electronics > Electronics Accessories
    accessories: "1801", // Electronics > Electronics Accessories
    protection: "1801", // Electronics > Electronics Accessories
    tools: "632", // Hardware > Tools
    kits: "1279", // Electronics > Electronics Accessories
    other: "1801", // Electronics > Electronics Accessories
};

/**
 * Transforma SKU do YSH para formato Facebook Product
 */
export class SKUToFacebookProductTransformer {
    constructor(private config: FacebookCatalogConfig) {}

    /**
     * Transforma um único SKU
     */
    transform(
        sku: SKU & { manufacturer?: Manufacturer },
        offers?: Array<{ price: number; stock_quantity?: number }>
    ): SKUToFacebookProductTransform {
        const facebookProduct = this.buildFacebookProduct(sku, offers);
        const syncHash = this.generateSyncHash(facebookProduct);

        return {
            sku_id: sku.id,
            sku_code: sku.sku_code,
            facebook_product: facebookProduct,
            sync_hash,
        };
    }

    /**
     * Transforma múltiplos SKUs
     */
    transformBatch(
        skus: Array<SKU & { manufacturer?: Manufacturer }>,
        offersMap?: Map<string, Array<{ price: number; stock_quantity?: number }>>
    ): SKUToFacebookProductTransform[] {
        return skus.map((sku) => {
            const offers = offersMap?.get(sku.id);
            return this.transform(sku, offers);
        });
    }

    /**
     * Constrói objeto FacebookProductItem
     */
    private buildFacebookProduct(
        sku: SKU & { manufacturer?: Manufacturer },
        offers?: Array<{ price: number; stock_quantity?: number }>
    ): FacebookProductItem {
        const baseUrl = this.config.base_product_url || "https://ysh.com.br/produtos";
        const currency = this.config.default_currency || "BRL";

        // Calculate availability and price
        const { availability, price, salePrice, inventory } = this.calculatePricingAndAvailability(
            sku,
            offers,
            currency
        );

        // Build product item
        const product: FacebookProductItem = {
            // Required fields
            id: sku.sku_code,
            title: this.buildTitle(sku),
            description: this.buildDescription(sku),
            availability,
            condition: this.config.default_condition || FacebookProductCondition.NEW,
            price,
            link: `${baseUrl}/${sku.sku_code}`,
            image_link: this.getMainImageUrl(sku),
            brand: sku.manufacturer?.name || "YSH Solar",

            // Recommended fields
            google_product_category: CATEGORY_TO_GOOGLE_TAXONOMY[sku.category] || "1801",
            product_type: this.buildProductType(sku),

            // Additional fields
            additional_image_link: this.getAdditionalImages(sku),
            sale_price: salePrice,

            // Identifiers
            mpn: sku.model_number,

            // Custom labels (for segmentation)
            custom_label_0: sku.category, // Category
            custom_label_1: sku.manufacturer?.tier || "unknown", // Manufacturer tier
            custom_label_2: this.getPowerRating(sku), // Power rating (if applicable)
            custom_label_3: sku.warranty_years ? `${sku.warranty_years}y warranty` : undefined,

            // Inventory
            inventory,
        };

        // Add category-specific fields
        this.addCategorySpecificFields(product, sku);

        return product;
    }

    /**
     * Calcula preço e disponibilidade baseado em offers
     */
    private calculatePricingAndAvailability(
        sku: SKU,
        offers?: Array<{ price: number; stock_quantity?: number }>,
        currency: string = "BRL"
    ): {
        availability: FacebookProductAvailability;
        price: string;
        salePrice?: string;
        inventory: number;
    } {
        if (!offers || offers.length === 0) {
            return {
                availability: this.config.default_availability || FacebookProductAvailability.OUT_OF_STOCK,
                price: sku.lowest_price ? `${sku.lowest_price.toFixed(2)} ${currency}` : "0.00 BRL",
                inventory: 0,
            };
        }

        // Calculate total inventory
        const totalInventory = offers.reduce((sum, offer) => sum + (offer.stock_quantity || 0), 0);

        // Determine availability
        const availability =
            totalInventory > 0
                ? FacebookProductAvailability.IN_STOCK
                : FacebookProductAvailability.OUT_OF_STOCK;

        // Use lowest price as regular price
        const lowestPrice = Math.min(...offers.map((o) => o.price));
        const highestPrice = Math.max(...offers.map((o) => o.price));

        // If there's significant price variation, use highest as regular and lowest as sale
        const priceVariation = ((highestPrice - lowestPrice) / highestPrice) * 100;
        const useSalePrice = priceVariation > 10; // More than 10% difference

        return {
            availability,
            price: `${highestPrice.toFixed(2)} ${currency}`,
            salePrice: useSalePrice ? `${lowestPrice.toFixed(2)} ${currency}` : undefined,
            inventory: totalInventory,
        };
    }

    /**
     * Constrói título otimizado
     */
    private buildTitle(sku: SKU): string {
        // Format: "Brand Model - Power/Specs - Category"
        const parts: string[] = [];

        if (sku.manufacturer?.name) {
            parts.push(sku.manufacturer.name);
        }

        parts.push(sku.model_number);

        const powerRating = this.getPowerRating(sku);
        if (powerRating) {
            parts.push(powerRating);
        }

        return parts.join(" - ");
    }

    /**
     * Constrói descrição
     */
    private buildDescription(sku: SKU): string {
        if (sku.description) {
            return sku.description;
        }

        // Build basic description
        const parts: string[] = [
            `${sku.name} - ${sku.model_number}`,
            sku.manufacturer?.name ? `Fabricante: ${sku.manufacturer.name}` : "",
            sku.warranty_years ? `Garantia: ${sku.warranty_years} anos` : "",
        ];

        return parts.filter(Boolean).join(" | ");
    }

    /**
     * Constrói hierarquia de categoria customizada
     */
    private buildProductType(sku: SKU): string {
        const categoryMap: Record<string, string> = {
            panels: "Energia Solar > Painéis Solares",
            inverters: "Energia Solar > Inversores",
            batteries: "Energia Solar > Baterias",
            charge_controllers: "Energia Solar > Controladores de Carga",
            structures: "Energia Solar > Estruturas de Montagem",
            monitoring: "Energia Solar > Monitoramento",
            cables: "Energia Solar > Cabos e Conectores",
            connectors: "Energia Solar > Cabos e Conectores",
            accessories: "Energia Solar > Acessórios",
            protection: "Energia Solar > Proteção",
            tools: "Energia Solar > Ferramentas",
            kits: "Energia Solar > Kits Completos",
            other: "Energia Solar > Outros",
        };

        return categoryMap[sku.category] || "Energia Solar";
    }

    /**
     * Obtém URL da imagem principal
     */
    private getMainImageUrl(sku: SKU): string {
        if (sku.image_urls && Array.isArray(sku.image_urls) && sku.image_urls.length > 0) {
            return sku.image_urls[0];
        }

        // Fallback placeholder
        return "https://via.placeholder.com/800x800.png?text=YSH+Solar";
    }

    /**
     * Obtém imagens adicionais (max 10)
     */
    private getAdditionalImages(sku: SKU): string[] | undefined {
        if (!sku.image_urls || !Array.isArray(sku.image_urls) || sku.image_urls.length <= 1) {
            return undefined;
        }

        return sku.image_urls.slice(1, 11); // Max 10 additional images
    }

    /**
     * Extrai potência nominal das specs técnicas
     */
    private getPowerRating(sku: SKU): string | undefined {
        if (!sku.technical_specs) return undefined;

        const specs = sku.technical_specs as Record<string, any>;

        // For panels
        if (sku.category === "panels" && specs.nominal_power_w) {
            return `${specs.nominal_power_w}W`;
        }

        // For inverters
        if (sku.category === "inverters" && specs.rated_power_w) {
            return `${specs.rated_power_w}W`;
        }

        // For batteries
        if (sku.category === "batteries" && specs.capacity_ah) {
            return `${specs.capacity_ah}Ah`;
        }

        return undefined;
    }

    /**
     * Adiciona campos específicos por categoria
     */
    private addCategorySpecificFields(product: FacebookProductItem, sku: SKU): void {
        const specs = (sku.technical_specs as Record<string, any>) || {};

        // Panels: Add color and material
        if (sku.category === "panels") {
            product.material = specs.cell_type || "Silício";
            product.color = "Preto"; // Most solar panels are black
        }

        // Add shipping weight if available
        if (specs.weight_kg) {
            product.shipping_weight = `${specs.weight_kg} kg`;
        }
    }

    /**
     * Gera hash para detectar mudanças
     */
    private generateSyncHash(product: FacebookProductItem): string {
        // Create deterministic string from critical fields
        const criticalFields = {
            title: product.title,
            description: product.description,
            price: product.price,
            availability: product.availability,
            brand: product.brand,
            image_link: product.image_link,
        };

        const hashInput = JSON.stringify(criticalFields, Object.keys(criticalFields).sort());
        return createHash("sha256").update(hashInput).digest("hex");
    }
}
