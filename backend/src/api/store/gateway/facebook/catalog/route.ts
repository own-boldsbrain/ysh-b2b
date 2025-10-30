/**
 * YSH B2B Store Gateway - Facebook Catalog Product Feed
 * Exporta produtos no formato Facebook Commerce Platform
 * 
 * @standard Facebook Commerce Platform Product Feed
 * @see https://developers.facebook.com/docs/commerce-platform/catalog/
 */

import { Request, Response, NextFunction } from 'express';
import { loadEnrichedData } from '../../route';

/**
 * Helper: Extrair categoria do SKU
 */
function extractCategory(sku: string): string {
    if (sku.includes('KITS')) return 'kits';
    if (sku.includes('PAINEL')) return 'panels';
    if (sku.includes('INVERSOR')) return 'inverters';
    if (sku.includes('BATERIA')) return 'batteries';
    if (sku.includes('ESTRUTURA')) return 'structures';
    if (sku.includes('CABO')) return 'cables';
    if (sku.includes('STRINGBOX')) return 'stringboxes';
    return 'accessories';
}

/**
 * Helper: Gerar título descritivo do produto
 */
function generateTitle(product: any): string {
    const category = extractCategory(product.sku);
    const power = product.sku.match(/(\d+)KWP?/i)?.[1] || '';
    
    if (category === 'kits' && power) {
        return `Kit Solar ${power}kWp - Sistema Completo`;
    }
    
    return `${category.charAt(0).toUpperCase() + category.slice(1)} - ${product.sku}`;
}

/**
 * Helper: Gerar descrição do produto
 */
function generateDescription(product: any): string {
    const category = extractCategory(product.sku);
    const price = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(product.final_price);
    
    let description = `Produto: ${product.sku}\n`;
    description += `Categoria: ${category}\n`;
    description += `Preço: ${price}\n`;
    description += `Margem Líquida: ${product.dynamic_markup.netMargin}%\n`;
    description += `\nProduto novo, com garantia do fabricante.`;
    
    if (product.kpis?.confidence) {
        description += `\nConfiança: ${product.kpis.confidence}`;
    }
    
    return description.substring(0, 5000); // Facebook limit
}

/**
 * Helper: Converter produto para formato Facebook Catalog
 */
function toFacebookCatalogFormat(product: any): any {
    const category = extractCategory(product.sku);
    const manufacturer = product.sku.substring(0, 5); // Extract from SKU
    
    return {
        // Required fields
        id: product.sku,
        title: generateTitle(product).substring(0, 150), // Facebook limit
        description: generateDescription(product),
        availability: 'in stock', // TODO: Integrar com estoque real
        condition: 'new',
        price: `${product.final_price.toFixed(2)} BRL`,
        link: `https://yshsolar.com.br/products/${product.sku}`, // TODO: URL real
        image_link: product.images?.[0] || 'https://yshsolar.com.br/placeholder.jpg',
        brand: manufacturer,
        
        // Conditionally required
        gtin: product.gtin || undefined,
        mpn: product.mpn || product.sku,
        
        // Optional but recommended
        sale_price: product.channel_pricing?.discount > 0 
            ? `${(product.final_price * (1 - product.channel_pricing.discount / 100)).toFixed(2)} BRL`
            : undefined,
        product_type: `Solar > ${category}`,
        google_product_category: category === 'kits' ? '2082' : '2082', // "Solar Panels" category
        
        // Custom labels for campaign optimization
        custom_label_0: product.dynamic_markup.scenario, // neutro/agressivo/premium
        custom_label_1: `margin_${Math.round(product.dynamic_markup.netMargin)}`, // margin bucket
        custom_label_2: category,
        custom_label_3: product.psychological_pricing?.charm_applied ? 'charm_pricing' : 'standard',
        custom_label_4: product.price_score?.category || 'average',
        
        // Additional images
        additional_image_link: product.images?.slice(1, 11).join(',') || undefined,
        
        // Inventory
        quantity_to_sell_on_facebook: 999, // TODO: Integrar estoque real
        
        // Rich description
        rich_text_description: generateDescription(product)
    };
}

/**
 * GET /store/gateway/facebook/catalog
 * Retorna catálogo no formato Facebook Commerce Platform
 */
export const GET = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const { format = 'json', limit, offset = 0 } = req.query as any;
        
        const enrichedData = await loadEnrichedData();
        
        // Aplicar paginação se especificado
        const start = parseInt(offset) || 0;
        const end = limit ? start + parseInt(limit) : enrichedData.length;
        const paginatedData = enrichedData.slice(start, end);
        
        // Converter para formato Facebook
        const catalogItems = paginatedData.map(toFacebookCatalogFormat);
        
        // Responder no formato solicitado
        if (format === 'csv') {
            // CSV Format
            const headers = Object.keys(catalogItems[0]);
            let csv = headers.join(',') + '\n';
            
            for (const item of catalogItems) {
                const row = headers.map(header => {
                    const value = item[header] || '';
                    // Escape commas and quotes
                    return typeof value === 'string' && value.includes(',') 
                        ? `"${value.replace(/"/g, '""')}"` 
                        : value;
                });
                csv += row.join(',') + '\n';
            }
            
            res.setHeader('Content-Type', 'text/csv');
            res.setHeader('Content-Disposition', `attachment; filename="ysh-catalog-${Date.now()}.csv"`);
            res.send(csv);
            
        } else if (format === 'xml') {
            // RSS XML Format
            let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
            xml += '<rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">\n';
            xml += '  <channel>\n';
            xml += '    <title>YSH Solar Product Catalog</title>\n';
            xml += '    <link>https://yshsolar.com.br</link>\n';
            xml += '    <description>Catálogo de produtos solares YSH</description>\n';
            
            for (const item of catalogItems) {
                xml += '    <item>\n';
                xml += `      <g:id>${item.id}</g:id>\n`;
                xml += `      <g:title><![CDATA[${item.title}]]></g:title>\n`;
                xml += `      <g:description><![CDATA[${item.description}]]></g:description>\n`;
                xml += `      <g:link>${item.link}</g:link>\n`;
                xml += `      <g:image_link>${item.image_link}</g:image_link>\n`;
                xml += `      <g:availability>${item.availability}</g:availability>\n`;
                xml += `      <g:price>${item.price}</g:price>\n`;
                xml += `      <g:brand>${item.brand}</g:brand>\n`;
                xml += `      <g:condition>${item.condition}</g:condition>\n`;
                
                if (item.sale_price) {
                    xml += `      <g:sale_price>${item.sale_price}</g:sale_price>\n`;
                }
                if (item.gtin) {
                    xml += `      <g:gtin>${item.gtin}</g:gtin>\n`;
                }
                if (item.mpn) {
                    xml += `      <g:mpn>${item.mpn}</g:mpn>\n`;
                }
                if (item.product_type) {
                    xml += `      <g:product_type>${item.product_type}</g:product_type>\n`;
                }
                if (item.google_product_category) {
                    xml += `      <g:google_product_category>${item.google_product_category}</g:google_product_category>\n`;
                }
                
                // Custom labels
                for (let i = 0; i <= 4; i++) {
                    const label = (item as any)[`custom_label_${i}`];
                    if (label) {
                        xml += `      <g:custom_label_${i}>${label}</g:custom_label_${i}>\n`;
                    }
                }
                
                xml += '    </item>\n';
            }
            
            xml += '  </channel>\n';
            xml += '</rss>';
            
            res.setHeader('Content-Type', 'application/xml');
            res.setHeader('Content-Disposition', `attachment; filename="ysh-catalog-${Date.now()}.xml"`);
            res.send(xml);
            
        } else {
            // JSON Format (default)
            res.status(200).json({
                data: catalogItems,
                paging: {
                    cursors: {
                        before: start > 0 ? start - (parseInt(limit) || 50) : null,
                        after: end < enrichedData.length ? end : null
                    }
                },
                summary: {
                    total_count: enrichedData.length,
                    returned_count: catalogItems.length
                }
            });
        }
        
    } catch (error: any) {
        console.error('[Gateway] Facebook catalog error:', error);
        error.statusCode = error.statusCode || 500;
        next(error);
    }
};
