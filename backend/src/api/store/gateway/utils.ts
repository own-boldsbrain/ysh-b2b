/**
 * YSH B2B Store Gateway - Utility Functions
 * Funções compartilhadas entre os endpoints do gateway
 */

/**
 * Extrai a categoria do produto baseado no SKU
 * @param sku - SKU do produto
 * @returns Categoria do produto
 */
export function extractCategoryFromSKU(sku: string): string {
    const upperSku = sku.toUpperCase();
    
    if (upperSku.includes('KITS')) return 'kits';
    if (upperSku.includes('PAINEL')) return 'panels';
    if (upperSku.includes('INVERSOR')) return 'inverters';
    if (upperSku.includes('BATERIA')) return 'batteries';
    if (upperSku.includes('ESTRUTURA')) return 'structures';
    if (upperSku.includes('CABO')) return 'cables';
    if (upperSku.includes('STRINGBOX')) return 'stringboxes';
    
    return 'accessories';
}

/**
 * Extrai o código do distribuidor do SKU
 * @param sku - SKU do produto
 * @returns Código do distribuidor (primeiros 5 caracteres)
 */
export function extractDistributorFromSKU(sku: string): string {
    return sku.substring(0, 5);
}

/**
 * Formata um número para 2 casas decimais
 * @param value - Valor numérico
 * @returns Número formatado
 */
export function formatDecimal(value: number): number {
    return Number.parseFloat(value.toFixed(2));
}

/**
 * Calcula a média de um array de números
 * @param values - Array de valores
 * @returns Média dos valores
 */
export function calculateAverage(values: number[]): number {
    if (values.length === 0) return 0;
    const sum = values.reduce((acc, val) => acc + val, 0);
    return sum / values.length;
}
