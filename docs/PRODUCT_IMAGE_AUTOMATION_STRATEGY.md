# Estratégia de Automação de Imagens de Produtos YSH

## Computer Use Agent + Design System Integration

> **Versão**: 1.0.0  
> **Data**: 2025-01-13  
> **Contexto**: Automatizar captura, normalização e padronização de imagens para 2.914 produtos fotovoltaicos

---

## 📋 Sumário Executivo

### Desafio Atual

- **2.914 produtos base** sem imagens padronizadas
- **16.532 SKUs totais** (com variantes) precisam de assets visuais
- **32 fabricantes** diferentes com sites e formatos variados
- **94.2%** dos produtos sem enriquecimento visual
- Necessidade de imagens para **Meta Commerce Platform** (1200x1200px mínimo)

### Solução Proposta

Implementar um **Computer Use Agent** baseado em Claude Sonnet que:

1. Navega automaticamente nos sites dos fabricantes
2. Captura imagens de produtos usando dados estruturados (SKU, modelo)
3. Normaliza dimensões, qualidade e formato
4. Aplica design system YSH (overlays, watermarks, backgrounds)
5. Gera variações para diferentes canais (web, Meta, print)
6. Organiza assets em CDN com nomenclatura padronizada

---

## 🏗️ Arquitetura da Solução

### Visão Geral do Pipeline

```tsx
┌─────────────────────────────────────────────────────────────────┐
│              Inventário YSH (2.914 produtos)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Neosolar    │  │   Fortlev    │  │   Solfacil   │          │
│  │  (850 SKUs)  │  │  (420 SKUs)  │  │  (520 SKUs)  │  ...     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│          Computer Use Agent (Claude Sonnet 4.5)                  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │  Web Navigation & Scraping Engine                       │     │
│  │  • Playwright + Anthropic Computer Use                  │     │
│  │  • Navegação inteligente em sites de fabricantes        │     │
│  │  • OCR para extração de especificações                  │     │
│  │  • Download de imagens de alta resolução                │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────────┐     │
│  │  Image Processing & Normalization                       │     │
│  │  • Sharp.js (resize, crop, optimize)                    │     │
│  │  • Background removal (rembg/remove.bg API)             │     │
│  │  • Quality enhancement (AI upscaling)                   │     │
│  │  • Format conversion (PNG → WebP, AVIF)                 │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────────┐     │
│  │  Design System Application (YSH Branding)               │     │
│  │  • Canvas API / Fabric.js                               │     │
│  │  • Overlay de marca YSH                                 │     │
│  │  • Watermark + selo "Produto Certificado"              │     │
│  │  • Background gradiente (brand colors)                  │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────────┐     │
│  │  Multi-Channel Export                                   │     │
│  │  • Web (800x800, WebP)                                  │     │
│  │  • Meta Commerce (1200x1200, JPEG)                      │     │
│  │  • Thumbnails (300x300, WebP)                           │     │
│  │  • Print (2400x2400, PNG)                               │     │
│  └────────────────┬───────────────────────────────────────┘     │
└───────────────────┼──────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│              CDN Storage & Metadata Database                     │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Cloudflare  │  │   S3 Bucket  │  │   PostgreSQL │          │
│  │   R2/Images  │  │  (raw assets)│  │  (metadata)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  Estrutura de URLs:                                              │
│  https://cdn.ysh.com.br/products/{sku}/                         │
│    ├─ hero.webp (800x800)                                       │
│    ├─ meta.jpg (1200x1200)                                      │
│    ├─ thumb.webp (300x300)                                      │
│    ├─ print.png (2400x2400)                                     │
│    └─ gallery/                                                  │
│       ├─ angle-1.webp                                           │
│       ├─ angle-2.webp                                           │
│       └─ detail-closeup.webp                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Local AI Models - Especificação (Docker Desktop)

### Modelos Disponíveis

Baseado nos modelos disponíveis localmente no Docker Desktop:

| Modelo | Tamanho | Uso na Pipeline |
|--------|---------|-----------------|
| **ai/gemma3-gpt-latest** | 2.36 GiB | Análise de páginas web, extração de URLs de imagens |
| **ai/smollm2-latest** | 256.35 MiB | Classificação de imagens, detecção de qualidade |
| **ai/qwen3-coder-latest** | 16.45 GiB | Geração de scripts de scraping, automação |
| **ai/gpt-cos-latest** | N/A | Processamento de texto em páginas de produtos |

### Job-to-be-Done (JTBD)

**Quando** tenho um produto no inventário sem imagem,  
**Eu quero** que o sistema capture automaticamente imagens de alta qualidade usando modelos locais,  
**Para que** eu possa exibir produtos profissionalmente sem depender de APIs externas pagas.

### Inputs do Agent

```json
{
  "product": {
    "sku": "NEO-INV-DEYE-SUN-8K-SG04LP3-EU",
    "name": "Inversor Deye SUN-8K-SG04LP3-EU",
    "manufacturer": {
      "name": "Deye",
      "website": "https://www.deyeinverter.com",
      "search_pattern": "SUN-8K-SG04LP3"
    },
    "distributor": {
      "name": "Neosolar",
      "product_url": "https://www.neosolar.com.br/loja/...",
      "fallback": true
    },
    "category": "inversores",
    "specifications": {
      "power": "8kW",
      "type": "Híbrido",
      "phases": "Monofásico"
    }
  },
  "target_outputs": [
    "hero_image",
    "gallery_images",
    "detail_closeups",
    "datasheet_cover"
  ],
  "quality_requirements": {
    "min_resolution": "1200x1200",
    "format": "PNG",
    "background": "transparent_preferred"
  }
}
```

### Outputs do Agent

```json
{
  "status": "success",
  "images_captured": 5,
  "processing_time_ms": 12500,
  "results": [
    {
      "type": "hero",
      "source_url": "https://www.deyeinverter.com/images/sun-8k-front.jpg",
      "original": {
        "path": "s3://ysh-raw-assets/deye/sun-8k/original-hero.jpg",
        "size_bytes": 2457600,
        "dimensions": "2000x2000",
        "format": "JPEG"
      },
      "processed": [
        {
          "variant": "web",
          "path": "https://cdn.ysh.com.br/products/NEO-INV-DEYE-SUN-8K/hero.webp",
          "size_bytes": 45000,
          "dimensions": "800x800",
          "format": "WebP",
          "quality": 85
        },
        {
          "variant": "meta_commerce",
          "path": "https://cdn.ysh.com.br/products/NEO-INV-DEYE-SUN-8K/meta.jpg",
          "size_bytes": 120000,
          "dimensions": "1200x1200",
          "format": "JPEG",
          "quality": 90
        },
        {
          "variant": "thumbnail",
          "path": "https://cdn.ysh.com.br/products/NEO-INV-DEYE-SUN-8K/thumb.webp",
          "size_bytes": 12000,
          "dimensions": "300x300",
          "format": "WebP",
          "quality": 80
        },
        {
          "variant": "print",
          "path": "https://cdn.ysh.com.br/products/NEO-INV-DEYE-SUN-8K/print.png",
          "size_bytes": 850000,
          "dimensions": "2400x2400",
          "format": "PNG"
        }
      ],
      "metadata": {
        "has_transparent_bg": true,
        "branding_applied": true,
        "watermark": "YSH_certified",
        "ai_enhanced": false
      }
    },
    {
      "type": "gallery",
      "count": 3,
      "items": [
        {
          "angle": "lateral",
          "path": "https://cdn.ysh.com.br/products/NEO-INV-DEYE-SUN-8K/gallery/angle-1.webp"
        },
        {
          "angle": "back",
          "path": "https://cdn.ysh.com.br/products/NEO-INV-DEYE-SUN-8K/gallery/angle-2.webp"
        },
        {
          "angle": "detail_display",
          "path": "https://cdn.ysh.com.br/products/NEO-INV-DEYE-SUN-8K/gallery/detail-closeup.webp"
        }
      ]
    }
  ],
  "quality_score": 9.2,
  "manual_review_required": false
}
```

---

## 🛠️ Stack Tecnológico

### Local AI Agent (Docker Models)

```typescript
// backend/src/automation/local-ai-agent/product-image-scraper.ts
import { Browser, Page } from "playwright";
import Dockerode from "dockerode";

interface LocalAIConfig {
  dockerHost: string; // Docker Desktop connection
  maxImagesPerProduct: number;
  timeoutMs: number;
  headless: boolean;
}

export class LocalProductImageScraper {
  private docker: Dockerode;
  private config: LocalAIConfig;
  
  constructor(config: LocalAIConfig) {
    this.docker = new Dockerode({ socketPath: config.dockerHost });
    this.config = config;
  }
  
  async scrapeProductImages(input: ProductImageInput): Promise<ProductImageOutput> {
    const browser = await this.launchBrowser();
    const page = await browser.newPage();
    
    try {
      // 1. Navegar para página do fabricante
      await this.navigateToManufacturerPage(page, input);
      
      // 2. Usar Gemma3 GPT para extrair conteúdo e URLs
      const pageContent = await this.extractPageContent(page);
      const imageUrls = await this.findImagesWithGemma3(pageContent, input);
      
      // 3. Download de imagens
      const rawImages = await this.downloadImages(imageUrls);
      
      // 4. Usar SmolLM2 para classificar qualidade
      const qualityImages = await this.filterByQuality(rawImages);
      
      // 5. Processar e normalizar
      const processedImages = await this.processImages(qualityImages, input);
      
      // 6. Aplicar design system
      const brandedImages = await this.applyBranding(processedImages);
      
      // 7. Upload para CDN
      const cdnUrls = await this.uploadToCDN(brandedImages, input.product.sku);
      
      return {
        status: "success",
        images_captured: imageUrls.length,
        results: cdnUrls,
      };
    } finally {
      await browser.close();
    }
  }
  
  private async findImagesWithGemma3(
    pageContent: string,
    input: ProductImageInput
  ): Promise<string[]> {
    // Executar Gemma3 GPT via Docker
    const container = await this.docker.createContainer({
      Image: "ai/gemma3-gpt-latest",
      Cmd: ["run"],
      HostConfig: {
        AutoRemove: true,
      },
    });
    
    await container.start();
    
    const prompt = `Analyze this HTML content from a manufacturer website and extract all product image URLs for "${input.product.name}" (Model: ${input.manufacturer.search_pattern}).

HTML Content:
${pageContent.substring(0, 5000)} // Limitar contexto

REQUIREMENTS:
1. Extract only high-quality product photo URLs (JPG, PNG, WebP)
2. Avoid thumbnails, icons, logos
3. Prefer images with product model number in filename
4. Return as JSON array of URLs

Response format: ["url1", "url2", ...]`;
    
    // Enviar prompt via stdin
    const exec = await container.exec({
      Cmd: ["sh", "-c", `echo '${prompt}' | /app/model-runner`],
      AttachStdout: true,
      AttachStderr: true,
    });
    
    const stream = await exec.start({ hijack: true, stdin: true });
    
    // Coletar resposta
    let response = "";
    stream.on("data", (chunk: Buffer) => {
      response += chunk.toString();
    });
    
    await new Promise((resolve) => stream.on("end", resolve));
    
    // Parsear JSON
    const imageUrls = this.parseImageUrlsFromResponse(response);
    
    return imageUrls;
  }
  
  private async filterByQuality(images: Buffer[]): Promise<Buffer[]> {
    // Usar SmolLM2 (leve e rápido) para classificar qualidade
    const container = await this.docker.createContainer({
      Image: "ai/smollm2-latest",
      Cmd: ["classify"],
      HostConfig: {
        AutoRemove: true,
      },
    });
    
    await container.start();
    
    const qualityScores = await Promise.all(
      images.map(async (img) => {
        // Converter imagem para base64
        const base64 = img.toString("base64");
        
        const prompt = `Classify this product image quality (0-10 scale).
Criteria:
- Resolution >= 1200x1200: +3
- Clear focus: +2
- White/transparent background: +2
- No text overlays: +2
- Professional lighting: +1

Image: data:image/png;base64,${base64.substring(0, 1000)}...

Return only the numeric score.`;
        
        // Executar classificação
        const score = await this.runSmolLM2(container, prompt);
        return { image: img, score: parseFloat(score) };
      })
    );
    
    // Filtrar apenas imagens com score >= 7
    return qualityScores
      .filter((item) => item.score >= 7.0)
      .map((item) => item.image);
  }
  
  private async downloadImages(urls: string[]): Promise<Buffer[]> {
    const downloads = await Promise.all(
      urls.map(async (url) => {
        const response = await fetch(url);
        return Buffer.from(await response.arrayBuffer());
      })
    );
    return downloads;
  }
  
  private async extractPageContent(page: Page): Promise<string> {
    return await page.content();
  }
  
  private parseImageUrlsFromResponse(response: string): string[] {
    try {
      const jsonMatch = response.match(/\[.*\]/s);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return [];
    } catch {
      return [];
    }
  }
  
  private async runSmolLM2(container: Dockerode.Container, prompt: string): Promise<string> {
    const exec = await container.exec({
      Cmd: ["sh", "-c", `echo '${prompt}' | /app/classifier`],
      AttachStdout: true,
    });
    
    const stream = await exec.start({ hijack: true });
    let output = "";
    stream.on("data", (chunk: Buffer) => {
      output += chunk.toString();
    });
    
    await new Promise((resolve) => stream.on("end", resolve));
    return output.trim();
  }
}
```

### Image Processing Pipeline

```typescript
// backend/src/automation/image-processing/normalizer.ts
import sharp from "sharp";
import { RemoveBgClient } from "removebg-api";

export class ImageNormalizer {
  private removeBgClient: RemoveBgClient;
  
  async normalize(
    rawImage: Buffer, 
    targetDimensions: { width: number; height: number }
  ): Promise<Buffer> {
    // 1. Remove background (se necessário)
    const noBg = await this.removeBackground(rawImage);
    
    // 2. Resize mantendo aspect ratio
    const resized = await sharp(noBg)
      .resize(targetDimensions.width, targetDimensions.height, {
        fit: "contain",
        background: { r: 0, g: 0, b: 0, alpha: 0 },
      })
      .toBuffer();
    
    // 3. Enhance quality (AI upscaling se < min resolution)
    const enhanced = await this.enhanceIfNeeded(resized);
    
    return enhanced;
  }
  
  private async removeBackground(image: Buffer): Promise<Buffer> {
    try {
      const result = await this.removeBgClient.removeBackground(image);
      return result;
    } catch (error) {
      console.warn("Background removal failed, using original:", error);
      return image;
    }
  }
}
```

### Design System Overlay

```typescript
// backend/src/automation/image-processing/branding.ts
import { createCanvas, loadImage, Canvas } from "canvas";
import { readFile } from "fs/promises";

interface YSHBrandingConfig {
  logo: string; // path to YSH logo
  watermark: string; // path to watermark
  colors: {
    primary: string; // #FFD700 (yellow)
    secondary: string; // #1E3A8A (blue)
    accent: string; // #10B981 (green)
  };
  gradients: {
    hero: string[]; // gradient stops
  };
}

export class BrandingEngine {
  private config: YSHBrandingConfig;
  
  async applyBranding(
    productImage: Buffer, 
    variant: "hero" | "gallery" | "thumbnail"
  ): Promise<Buffer> {
    const canvas = createCanvas(1200, 1200);
    const ctx = canvas.getContext("2d");
    
    // 1. Desenhar background gradiente (opcional)
    if (variant === "hero") {
      this.drawGradientBackground(ctx, canvas);
    }
    
    // 2. Desenhar imagem do produto centralizada
    const productImg = await loadImage(productImage);
    const { x, y, width, height } = this.calculateCenteredPosition(
      productImg,
      canvas.width,
      canvas.height
    );
    ctx.drawImage(productImg, x, y, width, height);
    
    // 3. Adicionar watermark YSH
    await this.addWatermark(ctx, canvas);
    
    // 4. Adicionar selo "Produto Certificado"
    if (variant === "hero") {
      await this.addCertificationBadge(ctx, canvas);
    }
    
    // 5. Converter para buffer
    return canvas.toBuffer("image/png");
  }
  
  private drawGradientBackground(ctx: CanvasRenderingContext2D, canvas: Canvas) {
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, this.config.colors.primary + "10"); // 10% opacity
    gradient.addColorStop(1, this.config.colors.secondary + "10");
    
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
  
  private async addWatermark(ctx: CanvasRenderingContext2D, canvas: Canvas) {
    const watermark = await loadImage(this.config.watermark);
    const size = 80; // watermark size
    const margin = 20;
    
    ctx.globalAlpha = 0.3; // semi-transparent
    ctx.drawImage(
      watermark,
      canvas.width - size - margin,
      canvas.height - size - margin,
      size,
      size
    );
    ctx.globalAlpha = 1.0;
  }
  
  private async addCertificationBadge(
    ctx: CanvasRenderingContext2D, 
    canvas: Canvas
  ) {
    const badgeSize = 100;
    const margin = 30;
    
    // Desenhar círculo amarelo com texto "CERTIFICADO"
    ctx.fillStyle = this.config.colors.primary;
    ctx.beginPath();
    ctx.arc(margin + badgeSize / 2, margin + badgeSize / 2, badgeSize / 2, 0, Math.PI * 2);
    ctx.fill();
    
    // Texto
    ctx.fillStyle = this.config.colors.secondary;
    ctx.font = "bold 14px Arial";
    ctx.textAlign = "center";
    ctx.fillText("CERTIFICADO", margin + badgeSize / 2, margin + badgeSize / 2);
  }
}
```

---

## 🔄 Workflows de Automação

### Workflow 1: Scraping em Lote (Huginn/n8n)

```yaml
# n8n workflow: product-image-batch-scraper.json
name: "YSH Product Image Batch Scraper"
nodes:
  - id: trigger
    type: n8n-nodes-base.schedule
    parameters:
      rule:
        interval:
          - cron: "0 2 * * *" # Roda diariamente às 2h AM
  
  - id: fetch_products_without_images
    type: n8n-nodes-base.postgres
    parameters:
      operation: executeQuery
      query: |
        SELECT 
          p.id, 
          p.external_id as sku, 
          p.title as name,
          p.metadata->>'manufacturer' as manufacturer_name,
          p.metadata->>'manufacturer_url' as manufacturer_url,
          p.metadata->>'model_number' as search_pattern
        FROM product p
        WHERE NOT EXISTS (
          SELECT 1 FROM product_image pi 
          WHERE pi.product_id = p.id
        )
        LIMIT 50 -- Processar 50 produtos por execução
  
  - id: scrape_each_product
    type: n8n-nodes-base.function
    parameters:
      functionCode: |
        const results = [];
        for (const product of items) {
          const scraperInput = {
            product: {
              sku: product.json.sku,
              name: product.json.name,
              manufacturer: {
                name: product.json.manufacturer_name,
                website: product.json.manufacturer_url,
                search_pattern: product.json.search_pattern
              }
            }
          };
          
          // Chamar Computer Use Agent via HTTP
          const response = await $http.request({
            method: 'POST',
            url: 'http://localhost:3001/api/scrape-product-images',
            body: scraperInput
          });
          
          results.push({
            product_id: product.json.id,
            images: response.data.results
          });
        }
        return results;
  
  - id: save_to_database
    type: n8n-nodes-base.postgres
    parameters:
      operation: insert
      table: product_image
      columns: product_id, url, type, metadata
```

### Workflow 2: Processamento Incremental

```typescript
// backend/src/workflows/image-processing/process-product-image.workflow.ts
import { createWorkflow, createStep, WorkflowResponse } from "@medusajs/workflows-sdk";
import { ProductImageScraper } from "@/automation/computer-use-agent/product-image-scraper";
import { ImageNormalizer } from "@/automation/image-processing/normalizer";
import { BrandingEngine } from "@/automation/image-processing/branding";

const scrapeImagesStep = createStep(
  "scrape-product-images",
  async ({ productId }, { container }) => {
    const productService = container.resolve("product");
    const product = await productService.retrieve(productId);
    
    const scraper = new ProductImageScraper({
      anthropicApiKey: process.env.ANTHROPIC_API_KEY,
      maxImagesPerProduct: 5,
      timeoutMs: 60000,
      headless: true,
    });
    
    const result = await scraper.scrapeProductImages({
      product: {
        sku: product.external_id,
        name: product.title,
        manufacturer: {
          name: product.metadata.manufacturer,
          website: product.metadata.manufacturer_url,
          search_pattern: product.metadata.model_number,
        },
      },
    });
    
    return new StepResponse(result, { productId });
  }
);

const normalizeImagesStep = createStep(
  "normalize-images",
  async ({ rawImages }, { container }) => {
    const normalizer = new ImageNormalizer();
    
    const variants = [
      { name: "web", width: 800, height: 800, format: "webp", quality: 85 },
      { name: "meta", width: 1200, height: 1200, format: "jpeg", quality: 90 },
      { name: "thumb", width: 300, height: 300, format: "webp", quality: 80 },
      { name: "print", width: 2400, height: 2400, format: "png", quality: 100 },
    ];
    
    const normalized = await Promise.all(
      rawImages.map(async (img) => {
        const processed = {};
        for (const variant of variants) {
          processed[variant.name] = await normalizer.normalize(img, variant);
        }
        return processed;
      })
    );
    
    return new StepResponse(normalized);
  }
);

const applyBrandingStep = createStep(
  "apply-branding",
  async ({ normalizedImages }, { container }) => {
    const branding = new BrandingEngine({
      logo: "./assets/ysh-logo.png",
      watermark: "./assets/ysh-watermark.png",
      colors: {
        primary: "#FFD700",
        secondary: "#1E3A8A",
        accent: "#10B981",
      },
    });
    
    const branded = await Promise.all(
      normalizedImages.map((img) => branding.applyBranding(img, "hero"))
    );
    
    return new StepResponse(branded);
  }
);

const uploadToCDNStep = createStep(
  "upload-to-cdn",
  async ({ images, productSku }, { container }) => {
    const s3Service = container.resolve("s3");
    
    const uploads = await Promise.all(
      images.map(async (img, idx) => {
        const key = `products/${productSku}/image-${idx}.webp`;
        await s3Service.upload({
          bucket: "ysh-product-images",
          key,
          body: img,
          contentType: "image/webp",
        });
        return `https://cdn.ysh.com.br/${key}`;
      })
    );
    
    return new StepResponse(uploads);
  }
);

const saveToProductStep = createStep(
  "save-to-product",
  async ({ productId, imageUrls }, { container }) => {
    const productService = container.resolve("product");
    
    await productService.update(productId, {
      images: imageUrls.map((url, idx) => ({
        url,
        metadata: {
          position: idx,
          type: idx === 0 ? "hero" : "gallery",
        },
      })),
    });
    
    return new StepResponse({ updated: true });
  }
);

export const processProductImageWorkflow = createWorkflow(
  "process-product-image",
  function (input: { productId: string }) {
    const scraped = scrapeImagesStep(input);
    const normalized = normalizeImagesStep(scraped);
    const branded = applyBrandingStep(normalized);
    const uploaded = uploadToCDNStep({ images: branded, productSku: input.productId });
    const saved = saveToProductStep({ productId: input.productId, imageUrls: uploaded });
    
    return new WorkflowResponse(saved);
  }
);
```

---

## 📊 Estratégia de Priorização

### Fase 1: Produtos de Alta Prioridade (Semana 1-2)

**Critérios**:

- Top 100 produtos mais vendidos
- Produtos sem imagem alguma
- Fabricantes com sites bem estruturados (Deye, DAH Solar, EPever)

**Método**: Computer Use Agent manual + validação humana

**Output esperado**: 100 produtos com imagens hero + 2-3 gallery

---

### Fase 2: Categorias Principais (Semana 3-6)

**Critérios**:

- Inversores (850 produtos)
- Painéis solares (620 produtos)
- Baterias (380 produtos)

**Método**: Workflow automatizado em lote (n8n + Huginn)

**Output esperado**: 1.850 produtos com imagens completas

---

### Fase 3: Long Tail + Variantes (Semana 7-12)

**Critérios**:

- Acessórios, cabos, estruturas
- Variantes de produtos já processados

**Método**: Scraping agressivo + fallback para distribuidores

**Output esperado**: 2.914 produtos totalmente cobertos

---

## 🎨 Design System YSH - Especificações

### Paleta de Cores

```scss
// YSH Brand Colors
$ysh-primary: #FFD700; // Amarelo solar
$ysh-secondary: #1E3A8A; // Azul escuro
$ysh-accent: #10B981; // Verde energia
$ysh-neutral-100: #F9FAFB;
$ysh-neutral-900: #111827;
```

### Overlays & Badges

```typescript
interface YSHImageOverlay {
  // Hero image overlay (opcional)
  gradient: {
    enabled: boolean;
    colors: [string, string];
    opacity: number; // 0.1 = 10%
  };
  
  // Watermark (obrigatório)
  watermark: {
    position: "bottom-right" | "bottom-left";
    size: number; // pixels
    opacity: number; // 0.3 = 30%
  };
  
  // Certification badge (produtos certificados)
  badge: {
    enabled: boolean;
    position: "top-left" | "top-right";
    text: "CERTIFICADO" | "PREMIUM" | "BESTSELLER";
    color: string;
  };
  
  // Category tag
  tag: {
    enabled: boolean;
    text: string; // "Inversor", "Painel", etc
    position: "top-center";
    backgroundColor: string;
  };
}
```

### Templates por Categoria

```typescript
const imageTemplates: Record<string, YSHImageOverlay> = {
  "inversores": {
    gradient: { enabled: true, colors: ["#FFD700", "#1E3A8A"], opacity: 0.1 },
    watermark: { position: "bottom-right", size: 80, opacity: 0.3 },
    badge: { enabled: true, position: "top-left", text: "CERTIFICADO", color: "#FFD700" },
    tag: { enabled: true, text: "INVERSOR", position: "top-center", backgroundColor: "#1E3A8A" },
  },
  "paineis-solares": {
    gradient: { enabled: true, colors: ["#10B981", "#FFD700"], opacity: 0.1 },
    watermark: { position: "bottom-right", size: 80, opacity: 0.3 },
    badge: { enabled: false },
    tag: { enabled: true, text: "PAINEL SOLAR", position: "top-center", backgroundColor: "#10B981" },
  },
  "baterias": {
    gradient: { enabled: true, colors: ["#1E3A8A", "#10B981"], opacity: 0.1 },
    watermark: { position: "bottom-right", size: 80, opacity: 0.3 },
    badge: { enabled: true, position: "top-right", text: "PREMIUM", color: "#10B981" },
    tag: { enabled: true, text: "BATERIA", position: "top-center", backgroundColor: "#1E3A8A" },
  },
  // ... outros
};
```

---

## 🔍 Controle de Qualidade

### Validação Automática

```typescript
interface ImageQualityValidation {
  min_resolution: { width: number; height: number };
  max_file_size_kb: number;
  allowed_formats: string[];
  has_transparent_bg: boolean;
  aspect_ratio_tolerance: number; // 0.1 = 10%
  brightness_range: [number, number]; // 0-255
  contrast_min: number;
}

export class QualityValidator {
  async validate(image: Buffer, rules: ImageQualityValidation): Promise<ValidationResult> {
    const metadata = await sharp(image).metadata();
    
    const checks = {
      resolution_ok: metadata.width >= rules.min_resolution.width,
      size_ok: image.length <= rules.max_file_size_kb * 1024,
      format_ok: rules.allowed_formats.includes(metadata.format),
      // ... outros checks
    };
    
    const score = this.calculateQualityScore(checks);
    
    return {
      passed: score >= 7.0,
      score,
      checks,
      needs_manual_review: score < 5.0,
    };
  }
}
```

### Dashboard de Monitoramento

```sql
-- Query para dashboard de progresso
SELECT 
  category,
  COUNT(*) as total_products,
  COUNT(CASE WHEN images.url IS NOT NULL THEN 1 END) as with_images,
  ROUND(
    COUNT(CASE WHEN images.url IS NOT NULL THEN 1 END)::numeric / COUNT(*)::numeric * 100, 
    2
  ) as coverage_pct,
  AVG(CASE WHEN images.metadata->>'quality_score' IS NOT NULL 
      THEN (images.metadata->>'quality_score')::numeric 
      END) as avg_quality_score
FROM product p
LEFT JOIN product_image images ON p.id = images.product_id
GROUP BY category
ORDER BY coverage_pct ASC;

-- Output exemplo:
-- category         | total | with_images | coverage_pct | avg_quality_score
-- -----------------|-------|-------------|--------------|------------------
-- cabos            |  180  |     12      |    6.67%     |      8.2
-- acessorios       |  240  |     28      |   11.67%     |      7.9
-- estruturas       |  220  |     45      |   20.45%     |      8.5
-- baterias         |  380  |    210      |   55.26%     |      9.1
-- inversores       |  850  |    680      |   80.00%     |      9.3
-- paineis-solares  |  620  |    580      |   93.55%     |      9.4
-- kits-solares     |  424  |    412      |   97.17%     |      9.2
```

---

## 💰 Estimativa de Custos

### Custos de Infraestrutura (por 1.000 produtos)

| Recurso | Uso | Custo Unitário | Total |
|---------|-----|----------------|-------|
| **Docker Desktop** (modelos locais) | Incluído - 0 custo de API | $0 | $0 |
| **Rembg Local** (Background Removal) | Roda em container Docker | $0 | $0 |
| **Cloudflare R2 Storage** | 5GB storage + bandwidth | $0.015/GB | $5 |
| **Computação** (servidor local/VPS) | 24h de processamento | ~$10-20 | $15 |
| **Total por 1.000 produtos** | | | **~$20** |

### Custo Total para 2.914 Produtos

```tsx
2.914 produtos × ($20 / 1.000) = $58.28

Arredondando com margem de segurança: ~$100

ECONOMIA vs. APIs externas: $850 - $100 = $750 (87.5% de redução)
```

### ROI - Retorno sobre Investimento

**Custo evitado** (trabalho manual):

- Tempo médio por produto: 15 minutos (buscar, baixar, editar, salvar)
- Total de horas: 2.914 × 15 min = 728 horas
- Custo de designer @ R$ 50/h: R$ 36.400

**Benefício da automação** (com modelos Docker locais):

- Custo: $100 (≈ R$ 500)
- **Economia líquida: R$ 35.900**
- **ROI: 7.180%** 🚀

---

## 📅 Roadmap de Implementação

### Sprint 1: Setup & Proof of Concept (Semana 1)

- [ ] Pull de modelos Docker (Gemma3, SmolLM2, Qwen3-coder)
- [ ] Setup Docker Compose stack com modelos AI
- [ ] Implementar `LocalProductImageScraper` básico
- [ ] Testar scraping com Gemma3 em 10 produtos Deye
- [ ] Validar qualidade das imagens com SmolLM2

### Sprint 2: Image Processing Pipeline (Semana 2)

- [ ] Implementar `ImageNormalizer` (Sharp.js)
- [ ] Setup Rembg container local para background removal
- [ ] Implementar `BrandingEngine` com overlays YSH
- [ ] Gerar variações (web, meta, thumb, print)
- [ ] Otimizar modelos Docker para paralelização

### Sprint 3: Batch Automation (Semana 3-4)

- [ ] Criar Docker Compose orchestration para pipeline completo
- [ ] Criar workflow n8n integrado com containers Docker
- [ ] Setup Cloudflare R2 para storage
- [ ] Implementar CDN URL generation
- [ ] Processar 500 produtos (inversores + painéis)

### Sprint 4: Quality & Scale (Semana 5-6)

- [ ] Implementar `QualityValidator`
- [ ] Dashboard de monitoramento (Grafana/Metabase)
- [ ] Processar restante dos produtos (1.500+)
- [ ] Manual review para produtos low-score

### Sprint 5: Integration & Optimization (Semana 7-8)

- [ ] Integrar com Meta Commerce Platform
- [ ] Otimizar performance (parallel processing)
- [ ] Implementar retry logic para falhas
- [ ] Documentação completa

---

## 🎯 Métricas de Sucesso

| Métrica | Baseline | Alvo |
|---------|----------|------|
| Cobertura de Imagens | 5.8% | 95%+ |
| Qualidade Média (score) | N/A | 8.5/10 |
| Tempo Médio de Processamento | 15 min/manual | < 2 min/auto |
| Taxa de Sucesso de Scraping | N/A | > 85% |
| Taxa de Aprovação Automática | N/A | > 90% |
| Custo por Produto | R$ 12.50 | < R$ 0.20 (local) |

---

## 📚 Recursos & Referências

### Documentação Técnica

- [Anthropic Computer Use Guide](https://docs.anthropic.com/claude/docs/computer-use)
- [Sharp.js Image Processing](https://sharp.pixelplumbing.com/)
- [Remove.bg API](https://www.remove.bg/api)
- [Cloudflare R2 Storage](https://developers.cloudflare.com/r2/)
- [n8n Workflow Automation](https://docs.n8n.io/)

### Recursos YSH

- [Product Inventory Blueprint](../backend/data/products-inventory/INVENTORY_BLUEPRINT_360.md)
- [Meta Commerce Integration](./META_COMMERCE_INTEGRATION_BLUEPRINT.md)
- [Solar Automation Handbook](../../Computer%20Use%20Agent%20Handbook.md)

---

## 🚀 Próximos Passos Imediatos

1. **Setup inicial** (hoje):
   - Pull modelos Docker: `docker pull ai/gemma3-gpt-latest`, `docker pull ai/smollm2-latest`
   - Setup Rembg local: `docker pull danielgatis/rembg`
   - Configurar Cloudflare R2 bucket

2. **Proof of Concept** (esta semana):
   - Implementar scraper com Gemma3 para 10 produtos Deye
   - Testar classificação de qualidade com SmolLM2
   - Validar tempo de processamento local
   - Medir uso de recursos (RAM, CPU, GPU se disponível)

3. **Sprint Planning** (próxima semana):
   - Criar Docker Compose stack completo
   - Definir prioridades de categorias
   - Alocar recursos (developer + infraestrutura)
   - Kickoff Sprint 1

---

**Versão**: 1.0.0  
**Data**: 2025-01-13  
**Status**: ✅ Estratégia Completa - Pronto para Implementação  
**Owner**: YSH Automation Team  

> 💡 **Nota**: Este documento é uma estratégia executável. Para detalhes de implementação técnica, consulte o [Computer Use Agent Handbook](../../Computer%20Use%20Agent%20Handbook.md).
