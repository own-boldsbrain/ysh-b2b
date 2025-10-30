/**
 * YSH B2B Store Gateway - Facebook Batch API Endpoint
 * Implementa Facebook Catalog Batch API para atualizações em massa
 * 
 * @standard Facebook Commerce Platform Batch API
 * @see https://developers.facebook.com/docs/commerce-platform/catalog/batch-api/
 * @limits 5000 items per request, 100 calls per hour
 */

import { Request, Response, NextFunction } from 'express';
import { loadEnrichedData } from '../../route';
import { extractCategoryFromSKU } from '../../utils';

interface BatchRequest {
    method: 'CREATE' | 'UPDATE' | 'DELETE';
    retailer_id: string;
    data?: {
        id?: string;
        title?: string;
        description?: string;
        availability?: 'in stock' | 'out of stock' | 'preorder' | 'available for order' | 'discontinued';
        condition?: 'new' | 'refurbished' | 'used';
        price?: string;
        link?: string;
        image_link?: string;
        brand?: string;
        gtin?: string;
        mpn?: string;
        sale_price?: string;
        product_type?: string;
        google_product_category?: string;
        [key: string]: any;
    };
}

interface BatchResponse {
    handles: Array<{
        handle: string;
        retailer_id: string;
    }>;
}

const BATCH_LIMIT = 5000;
const REQUIRED_FIELDS = ['id', 'title', 'description', 'price', 'availability', 'condition', 'link', 'image_link', 'brand'];

/**
 * Valida um item do catálogo Facebook
 */
function validateCatalogItem(item: any): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    // Validar campos obrigatórios
    for (const field of REQUIRED_FIELDS) {
        if (!item[field]) {
            errors.push(`Missing required field: ${field}`);
        }
    }
    
    // Validar formato de preço
    if (item.price && !item.price.match(/^\d+\.\d{2}\s[A-Z]{3}$/)) {
        errors.push('Price must be in format "100.00 BRL"');
    }
    
    // Validar availability
    const validAvailability = ['in stock', 'out of stock', 'preorder', 'available for order', 'discontinued'];
    if (item.availability && !validAvailability.includes(item.availability)) {
        errors.push(`Invalid availability. Must be one of: ${validAvailability.join(', ')}`);
    }
    
    // Validar condition
    const validConditions = ['new', 'refurbished', 'used'];
    if (item.condition && !validConditions.includes(item.condition)) {
        errors.push(`Invalid condition. Must be one of: ${validConditions.join(', ')}`);
    }
    
    // Validar título (max 150 chars)
    if (item.title && item.title.length > 150) {
        errors.push('Title exceeds 150 characters');
    }
    
    // Validar descrição (max 5000 chars, sem HTML)
    if (item.description) {
        if (item.description.length > 5000) {
            errors.push('Description exceeds 5000 characters');
        }
        if (/<[^>]*>/.test(item.description)) {
            errors.push('Description cannot contain HTML tags');
        }
    }
    
    // Validar GTIN ou MPN (pelo menos um se for marca conhecida)
    if (item.brand && !item.gtin && !item.mpn) {
        errors.push('Either gtin or mpn is required for branded products');
    }
    
    return {
        valid: errors.length === 0,
        errors
    };
}

/**
 * POST /store/gateway/facebook/batch
 * Processa batch updates para o catálogo Facebook
 */
export const POST = async (
    req: Request,
    res: Response,
    next: NextFunction
) => {
    try {
        const { requests } = req.body as { requests: BatchRequest[] };
        
        // Validar payload
        if (!requests || !Array.isArray(requests)) {
            const error: any = new Error('Invalid request format. Expected { requests: BatchRequest[] }');
            error.statusCode = 400;
            throw error;
        }
        
        // Validar limite de batch
        if (requests.length > BATCH_LIMIT) {
            const error: any = new Error(`Batch size exceeds limit. Maximum ${BATCH_LIMIT} items per request`);
            error.statusCode = 400;
            throw error;
        }
        
        if (requests.length === 0) {
            const error: any = new Error('Empty batch request');
            error.statusCode = 400;
            throw error;
        }
        
        const enrichedData = await loadEnrichedData();
        const results: Array<{
            handle: string;
            retailer_id: string;
            status: 'success' | 'error';
            errors?: string[];
        }> = [];
        
        // Processar cada item do batch
        for (let i = 0; i < requests.length; i++) {
            const batchItem = requests[i];
            const handle = `batch_${Date.now()}_${i}`;
            
            try {
                // Validar método
                if (!['CREATE', 'UPDATE', 'DELETE'].includes(batchItem.method)) {
                    results.push({
                        handle,
                        retailer_id: batchItem.retailer_id,
                        status: 'error',
                        errors: [`Invalid method: ${batchItem.method}`]
                    });
                    continue;
                }
                
                // Validar retailer_id
                if (!batchItem.retailer_id) {
                    results.push({
                        handle,
                        retailer_id: '',
                        status: 'error',
                        errors: ['Missing retailer_id']
                    });
                    continue;
                }
                
                // Para DELETE, apenas verificar se existe
                if (batchItem.method === 'DELETE') {
                    const exists = enrichedData.find((p: any) => p.sku === batchItem.retailer_id);
                    if (!exists) {
                        results.push({
                            handle,
                            retailer_id: batchItem.retailer_id,
                            status: 'error',
                            errors: ['Product not found']
                        });
                    } else {
                        results.push({
                            handle,
                            retailer_id: batchItem.retailer_id,
                            status: 'success'
                        });
                    }
                    continue;
                }
                
                // Para CREATE/UPDATE, validar dados
                if (!batchItem.data) {
                    results.push({
                        handle,
                        retailer_id: batchItem.retailer_id,
                        status: 'error',
                        errors: ['Missing data field']
                    });
                    continue;
                }
                
                // Validar item do catálogo
                const validation = validateCatalogItem(batchItem.data);
                if (!validation.valid) {
                    results.push({
                        handle,
                        retailer_id: batchItem.retailer_id,
                        status: 'error',
                        errors: validation.errors
                    });
                    continue;
                }
                
                // Se CREATE, verificar se já existe
                if (batchItem.method === 'CREATE') {
                    const exists = enrichedData.find((p: any) => p.sku === batchItem.retailer_id);
                    if (exists) {
                        results.push({
                            handle,
                            retailer_id: batchItem.retailer_id,
                            status: 'error',
                            errors: ['Product already exists. Use UPDATE instead.']
                        });
                        continue;
                    }
                }
                
                // Se UPDATE, verificar se existe
                if (batchItem.method === 'UPDATE') {
                    const exists = enrichedData.find((p: any) => p.sku === batchItem.retailer_id);
                    if (!exists) {
                        results.push({
                            handle,
                            retailer_id: batchItem.retailer_id,
                            status: 'error',
                            errors: ['Product not found. Use CREATE instead.']
                        });
                        continue;
                    }
                }
                
                // Item válido
                results.push({
                    handle,
                    retailer_id: batchItem.retailer_id,
                    status: 'success'
                });
                
            } catch (itemError: any) {
                results.push({
                    handle,
                    retailer_id: batchItem.retailer_id,
                    status: 'error',
                    errors: [itemError.message || 'Unknown error']
                });
            }
        }
        
        // Calcular estatísticas
        const successCount = results.filter(r => r.status === 'success').length;
        const errorCount = results.filter(r => r.status === 'error').length;
        
        res.status(200).json({
            data: results,
            summary: {
                total_items: requests.length,
                successful: successCount,
                failed: errorCount,
                success_rate: Number.parseFloat((successCount / requests.length * 100).toFixed(2))
            },
            timestamp: new Date().toISOString()
        });
        
    } catch (error: any) {
        console.error('[Gateway Facebook Batch] Error:', error);
        error.statusCode = error.statusCode || 500;
        next(error);
    }
};
