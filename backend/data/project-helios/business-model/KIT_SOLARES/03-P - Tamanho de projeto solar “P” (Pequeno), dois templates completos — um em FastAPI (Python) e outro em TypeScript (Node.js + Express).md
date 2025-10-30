A seguir você encontrará, para o **tamanho de projeto solar “P” (Pequeno)**, dois templates completos — um em **FastAPI (Python)** e outro em **TypeScript (Node.js + Express)** — que ilustram passo a passo:

1. **Cálculo automático dos valores** (painéis + inversor) de cada tier de geração (“Padrão”, “Consciente”, “Moderado” e “Acelerado”).
    
2. **Lógica de limitação de parcelas** baseada na bandeira do cartão de crédito: até **21× para Visa e Mastercard** e **até 12× para as demais bandeiras** (conforme documentação Asaas).
    
3. **Payload JSON de cobrança** para envio ao Asaas, incluindo `installmentCount` corretamente ajustado.
    
4. **Comentários explicativos** detalhados em cada trecho de código, sem abreviações, para facilitar leitura e manutenção.
    

Os valores base (para categoria “P”) são:

- **averageKwp** (média de potência): **5,0 kWp**.
    
- **Potência nominal de cada painel**: **400 Wp**.
    
- **Preço por painel (400 Wp)**: **R$ 800,00**.
    
- **Preço por inversor (por kW)**: **R$ 2 000,00**.
    
- **Recomendações de inversor**:
    
    - **Padrão** → 5,8 kW
        
    - **Consciente** → 6,5 kW
        
    - **Moderado** → 7,3 kW
        
    - **Acelerado** → 8,0 kW
        
- **Multiplicadores por tier**:
    
    - **Padrão** → 1.15
        
    - **Consciente** → 1.30
        
    - **Moderado** → 1.45
        
    - **Acelerado** → 1.60
        

Usando essas bases, calculamos:

1. **systemKwp = averageKwp × multiplier**.
    
2. **panelCount = ceil((systemKwp × 1 000) / 400)**.
    
3. **Preço total = (panelCount × 800) + (inverterKw × 2 000)**.
    

A lógica de parcelamento aplica:

- **Visa/Mastercard** → até 21×
    
- **Demais (Elo, Amex, Hipercard, etc.)** → até 12×
    

---

## 1. Template em FastAPI (Python) para “P” (Pequeno)

```python
# fastapi_p.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import httpx

app = FastAPI(
    title="API de Cobrança de Kit Solar P",
    description=(
        "Este serviço calcula o valor do kit solar para projetos P "
        "e cria a cobrança no Asaas, limitando em até 21 parcelas "
        "para Visa/Mastercard e até 12 parcelas para demais bandeiras."
    ),
    version="1.0.0"
)

#
# === 1) DEFINIÇÃO DOS DADOS DE COMPOSIÇÃO DO KIT P ===
#

# 1.1) Tipos auxiliares
ProjectCategory = Literal["P"]  # Somente "P" neste template
GenerationTierName = Literal["Padrão", "Consciente", "Moderado", "Acelerado"]

class LossFactors(BaseModel):
    """
    Fatores de perda do sistema fotovoltaico (%):
    - temperature: perda por temperatura
    - shading: perda por sombreamento
    - soiling: perda por sujeira
    - mismatchLidDc: perda combinada (mismatch + LID + fios DC)
    """
    temperature: float = Field(..., description="Perda por temperatura (%)")
    shading: float = Field(..., description="Perda por sombreamento (%)")
    soiling: float = Field(..., description="Perda por sujeira (%)")
    mismatchLidDc: float = Field(..., description="Perda mismatch/LID/DC (%)")

class SolarKitComponent(BaseModel):
    """
    Representa a composição do kit solar P para um determinado tier:
    - category: sempre "P"
    - tier: nível de geração (Padrão, Consciente, Moderado, Acelerado)
    - systemKwp: potência total do sistema em kWp (averageKwp × multiplier)
    - panelWp: 400 Wp (módulo padrão)
    - panelCount: quantidade de módulos necessários (arredondado para cima)
    - inverterKw: potência recomendada do inversor em kW
    - lossFactors: fatores de perda padrão (informativo)
    """
    category: ProjectCategory
    tier: GenerationTierName
    systemKwp: float
    panelWp: int
    panelCount: int
    inverterKw: float
    lossFactors: LossFactors

# 1.2) Constantes de precificação
PANEL_COST: float = 800.00            # R$ 800,00 por módulo de 400 Wp
INVERTER_COST_PER_KW: float = 2000.00 # R$ 2.000,00 por kW de inversor

# 1.3) Lista de tiers de geração P (averageKwp = 5,0 kWp)
#
#   - Multipliers: Padrão=1.15, Consciente=1.30, Moderado=1.45, Acelerado=1.60
#   - Cálculo de panelCount: ceil((systemKwp × 1000) / 400)
#   - Recomendações de inversor (kW): 5.8, 6.5, 7.3, 8.0
#
generation_tiers: List[SolarKitComponent] = [
    # Tier Padrão: multiplier = 1.15
    SolarKitComponent(
        category="P",
        tier="Padrão",
        systemKwp=round(5.0 * 1.15, 2),  # 5,0 × 1.15 = 5,75 kWp
        panelWp=400,
        panelCount=15,                   # ceil(5750 / 400) = ceil(14,375) = 15 módulos
        inverterKw=5.8,                  # recomendado Asaas
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Consciente: multiplier = 1.30
    SolarKitComponent(
        category="P",
        tier="Consciente",
        systemKwp=round(5.0 * 1.30, 2),  # 5,0 × 1.30 = 6,50 kWp
        panelWp=400,
        panelCount=17,                   # ceil(6500 / 400) = ceil(16,25) = 17 módulos
        inverterKw=6.5,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Moderado: multiplier = 1.45
    SolarKitComponent(
        category="P",
        tier="Moderado",
        systemKwp=round(5.0 * 1.45, 2),  # 5,0 × 1.45 = 7,25 kWp
        panelWp=400,
        panelCount=19,                   # ceil(7250 / 400) = ceil(18,125) = 19 módulos
        inverterKw=7.3,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Acelerado: multiplier = 1.60
    SolarKitComponent(
        category="P",
        tier="Acelerado",
        systemKwp=round(5.0 * 1.60, 2),  # 5,0 × 1.60 = 8,00 kWp
        panelWp=400,
        panelCount=20,                   # ceil(8000 / 400) = 20 módulos
        inverterKw=8.0,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    )
]

#
# === 2) MODELO DE REQUISIÇÃO (INPUT) PARA O ENDPOINT DE COBRANÇA ===
#

class ChargeRequest(BaseModel):
    """
    Campos esperados no body da requisição para criar cobrança:
    - category: deve ser "P" (este template é específico para P)
    - tier: um dos quatro níveis de geração (Padrão, Consciente, Moderado, Acelerado)
    - customer_id: ID do cliente já cadastrado no Asaas (ex.: "cus_ABC123xyz")
    - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO", "AMEX" etc.)
    - creditCardToken: token de cartão já obtido anteriormente (ex.: "tkn_abc123xyz")
    - installmentCount: número desejado de parcelas (int); será limitado conforme bandeira
    - dueDate: data de vencimento da primeira parcela no formato "AAAA-MM-DD"
    - description (opcional): descrição livre para a cobrança; se não informado, usa padrão interno
    """
    category: ProjectCategory = Field(..., description='Categoria do projeto, neste caso "P"')
    tier: GenerationTierName = Field(..., description="Nível de geração desejado para cálculo do kit")
    customer_id: str = Field(..., description="ID do cliente no Asaas, ex.: 'cus_ABC123xyz'")
    creditCardBrand: str = Field(..., description="Bandeira do cartão, ex.: 'VISA', 'MASTERCARD', 'ELO'")
    creditCardToken: str = Field(..., description="Token de cartão já gerado, ex.: 'tkn_abc123xyz'")
    installmentCount: int = Field(..., description="Número de parcelas solicitado pelo cliente")
    dueDate: str = Field(..., description='Data de vencimento da primeira parcela no formato "AAAA-MM-DD"')
    description: str = Field(
        default="Cobrança de Kit Solar P",
        description="Descrição da cobrança; padrão se não informado"
    )

#
# === 3) PARÂMETROS DA API DO ASAAS ===
#

ASAAS_BASE_URL: str = "https://www.asaas.com/api/v3"
# Sua chave de API Asaas (token real de produção)
ASAAS_API_TOKEN: str = (
    "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6"
    "OjVjNWI5MGFmLTk2NTMtNGY5Zi1iZTM1LWMxMTFkZDg0NDkxNjo6"
    "JGFhY2hfYzRhYmUyZWYtMmU0Zi00NDYwLWFjOWEtMzRjMjEwNDhiZmE2"
)

HEADERS = {
    "Content-Type": "application/json"
}

#
# === 4) FUNÇÕES AUXILIARES ===
#

def find_kit_for_tier(tier_name: GenerationTierName) -> SolarKitComponent:
    """
    Retorna a composição do kit P para o tier informado.
    Se não encontrar, levanta HTTPException 404.
    """
    for kit in generation_tiers:
        if kit.tier == tier_name:
            return kit
    raise HTTPException(
        status_code=404,
        detail=f"Não foi possível encontrar o kit P para o tier '{tier_name}'."
    )

def calculate_kit_price(kit: SolarKitComponent) -> float:
    """
    Calcula o preço total do kit:
    - Total de módulos × Custo unitário de módulo (PANEL_COST)
    - Mais potência de inversor (kW) × Custo por kW de inversor (INVERTER_COST_PER_KW)
    Arredonda para duas casas decimais.
    """
    price_panels = kit.panelCount * PANEL_COST
    price_inverter = kit.inverterKw * INVERTER_COST_PER_KW
    total_price = round(price_panels + price_inverter, 2)
    return total_price

def limit_installments(brand: str, requested_installments: int) -> int:
    """
    Limita o número de parcelas com base na bandeira do cartão:
    - Visa ou Mastercard: até 21×
    - Demais bandeiras (Elo, Amex, Hipercard etc.): até 12×
    Retorna o valor ajustado (se for maior que o permitido, retorna o máximo).
    """
    brand_upper = brand.strip().upper()
    if brand_upper in ["VISA", "MASTERCARD"]:
        return min(requested_installments, 21)
    return min(requested_installments, 12)

#
# === 5) ENDPOINT FASTAPI: CRIAR COBRANÇA NO ASAAS PARA KIT P ===
#

@app.post("/p/create_charge")
async def create_p_charge(request: ChargeRequest):
    # 5.1) Validar category == "P"
    if request.category != "P":
        raise HTTPException(
            status_code=400,
            detail="Esta rota só suporta projetos solares de tamanho 'P'."
        )

    # 5.2) Buscar o kit para o tier solicitado
    kit = find_kit_for_tier(request.tier)

    # 5.3) Calcular preço total do kit (painéis + inversor)
    price_total = calculate_kit_price(kit)

    # 5.4) Ajustar installmentCount com base na bandeira do cartão
    adjusted_installments = limit_installments(
        brand=request.creditCardBrand,
        requested_installments=request.installmentCount
    )

    # 5.5) Montar payload para envio ao Asaas
    asaas_payload = {
        "customer": request.customer_id,                 # ID do cliente Asaas
        "billingType": "CREDIT_CARD",                    # Cobrança via cartão
        "installmentCount": adjusted_installments,       # Parcelas ajustadas
        "value": price_total,                            # Valor total calculado do kit
        "dueDate": request.dueDate,                      # Vencimento da 1ª parcela
        "description": f"{request.description} (P - {kit.tier})",
        "externalReference": f"P_{kit.tier}_CHARGE_{request.customer_id}",
        "creditCard": {
            "creditCardToken": request.creditCardToken    # Token do cartão já gerado
        },
        "creditCardHolderInfo": {
            # Dados fixos de titular de cartão; no real, parametrizar conforme BD
            "name": "NOME DO TITULAR",
            "cpfCnpj": "000.000.000-00",
            "postalCode": "01000-000",
            "address": "Rua Exemplo",
            "addressNumber": "100",
            "complement": "Sala 1",
            "province": "Centro",
            "city": "São Paulo",
            "state": "SP"
        }
    }

    # 5.6) Enviar requisição ao Asaas
    url = f"{ASAAS_BASE_URL}/payments?access_token={ASAAS_API_TOKEN}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=asaas_payload, headers=HEADERS)

    # 5.7) Verificar resposta do Asaas
    if response.status_code not in (200, 201):
        # Se erro (ex.: parcela > permitido), devolvemos JSON de erro
        raise HTTPException(
            status_code=response.status_code,
            detail={"error": response.json()}
        )

    # 5.8) Retornar resultado completo
    return {
        "kit_composition": kit.dict(),
        "price_total": price_total,
        "requested_installments": request.installmentCount,
        "adjusted_installments": adjusted_installments,
        "asaas_response": response.json()
    }

#
# === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO P (APENAS CONSULTA) ===
#

@app.get("/p/kits", response_model=List[SolarKitComponent])
async def list_p_kits():
    """
    Retorna lista completa de composições de kit P para os 4 tiers:
    - Útil para front-ends exibirem opções ao usuário.
    """
    return generation_tiers
```

### Explicação detalhada do código FastAPI para “P”

1. **Composição do Kit P (seção 1)**
    
    - Definimos `generation_tiers` com quatro instâncias de `SolarKitComponent`, uma para cada tier de geração em “P”.
        
    - Cada objeto inclui:
        
        - `category`: fixo `"P"`.
            
        - `tier`: `"Padrão"`, `"Consciente"`, `"Moderado"` ou `"Acelerado"`.
            
        - `systemKwp`: resultante de `5,0 × multiplier`. Ex.: “Padrão” → `5.0 × 1.15 = 5.75 kWp`.
            
        - `panelCount`: calculado em função de `systemKwp × 1 000 / 400`, arredondado para cima.
            
        - `inverterKw`: potência recomendada (5.8 kW para “Padrão”).
            
        - `lossFactors`: apenas informativos (4 %, 3 %, 3 %, 4 %).
            
2. **Modelo de requisição `ChargeRequest` (seção 2)**
    
    - Recebe:
        
        - `category` (deve ser “P”),
            
        - `tier` (um dos quatro tiers),
            
        - `customer_id` (ID do cliente Asaas, ex.: “cus_ABC123xyz”),
            
        - `creditCardBrand` (ex.: “VISA”),
            
        - `creditCardToken` (string JWT),
            
        - `installmentCount` (int),
            
        - `dueDate` (“AAAA-MM-DD”),
            
        - `description` (opcional, padrão “Cobrança de Kit Solar P”).
            
3. **Funções auxiliares (seção 4)**
    
    - `find_kit_for_tier(tier_name)`: retorna o objeto de `generation_tiers` correspondente ao `tier_name`, ou 404 se não encontrar.
        
    - `calculate_kit_price(kit)`: `(kit.panelCount × 800) + (kit.inverterKw × 2000)`, arredondado a duas casas decimais.
        
    - `limit_installments(brand, requested_installments)`:
        
        - Se bandeira for “VISA” ou “MASTERCARD”, retorna `min(requested_installments, 21)`.
            
        - Caso contrário (ELO, AMEX, HIPERCARD, etc.), retorna `min(requested_installments, 12)`.
            
4. **Endpoint `/p/create_charge` (seção 5)**
    
    - Verifica se `category` é exatamente `"P"`.
        
    - Recupera composição do kit via `find_kit_for_tier(request.tier)`.
        
    - Calcula `price_total = calculate_kit_price(kit)`.
        
    - Ajusta `installmentCount` com `limit_installments(request.creditCardBrand, request.installmentCount)`.
        
    - Monta o dicionário `asaas_payload` para envio ao Asaas, incluindo `customer`, `billingType`, `installmentCount`, `value`, `dueDate`, `description`, `externalReference`, `creditCard` (token) e `creditCardHolderInfo` (dados fixos).
        
    - Envia `POST https://www.asaas.com/api/v3/payments?access_token={ASAAS_API_TOKEN}` com o payload JSON.
        
    - Se a resposta não for 200 ou 201, devolve HTTPException com o JSON de erro do Asaas.
        
    - Se for sucesso, retorna:
        
        - `"kit_composition"`: dict completo com todos os campos do kit.
            
        - `"price_total"`: valor calculado.
            
        - `"requested_installments"`: parcelas originalmente solicitadas.
            
        - `"adjusted_installments"`: parcelas ajustadas (≤21 ou ≤12).
            
        - `"asaas_response"`: JSON completo retornado pelo Asaas.
            
5. **Endpoint `/p/kits` (seção 6)**
    
    - Retorna `generation_tiers` para consulta, permitindo listar as composições dos kits em um front-end.
        

---

## 2. Template em TypeScript (Node.js + Express) para “P”

```typescript
// server_p.ts

import express, { Request, Response } from "express";
import axios from "axios";
import { body, validationResult } from "express-validator";

const app = express();
app.use(express.json());

/**
 * === 1) TIPOS E DADOS DE COMPOSIÇÃO DO KIT P ===
 *
 * Em P, definimos quatro tiers de geração com seus multiplicadores,
 * potências de inversor recomendadas e fatores de perda.
 */

type ProjectCategory = "P"; // Neste template, apenas "P" é aceito
type GenerationTierName = "Padrão" | "Consciente" | "Moderado" | "Acelerado";

interface LossFactors {
  /** Perda de energia por temperatura (%) */
  temperature: number;
  /** Perda de energia por sombreamento (%) */
  shading: number;
  /** Perda de energia por sujidade (%) */
  soiling: number;
  /** Perda combinada (mismatch + LID + fios DC) (%) */
  mismatchLidDc: number;
}

interface SolarKitComponent {
  /** Categoria do projeto solar, fixo em "P" */
  category: ProjectCategory;
  /** Tier de geração (um dos quatro) */
  tier: GenerationTierName;
  /** Potência total do sistema em kWp (averageKwp × multiplier) */
  systemKwp: number;
  /** Potência nominal de cada painel (400 Wp) */
  panelWp: number;
  /** Quantidade de módulos de 400 Wp necessários (arredondado para cima) */
  panelCount: number;
  /** Potência do inversor recomendada em kW */
  inverterKw: number;
  /** Fatores de perda padrão (informativo) */
  lossFactors: LossFactors;
}

// 1.1) Custo de componentes (ajustar conforme cenário real)
const PANEL_COST: number = 800.0;            // R$ 800,00 por módulo de 400 Wp
const INVERTER_COST_PER_KW: number = 2000.0; // R$ 2 000,00 por kW de inversor

// 1.2) Lista de composições dos kits P (4 tiers)
//     - averageKwp = 5,0 kWp
//     - Multiplers: Padrão=1.15, Consciente=1.30, Moderado=1.45, Acelerado=1.60
//     - Recomendações inversor (kW): 5.8, 6.5, 7.3, 8.0
const pKits: SolarKitComponent[] = [
  {
    category: "P",
    tier: "Padrão",
    systemKwp: parseFloat((5.0 * 1.15).toFixed(2)), // 5,0 × 1.15 = 5.75 kWp
    panelWp: 400,
    panelCount: 15,     // ceil(5750 / 400) = ceil(14,375) = 15 módulos
    inverterKw: 5.8,    // recomendado Asaas
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "P",
    tier: "Consciente",
    systemKwp: parseFloat((5.0 * 1.30).toFixed(2)), // 5,0 × 1.30 = 6.50 kWp
    panelWp: 400,
    panelCount: 17,     // ceil(6500 / 400) = ceil(16,25) = 17 módulos
    inverterKw: 6.5,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "P",
    tier: "Moderado",
    systemKwp: parseFloat((5.0 * 1.45).toFixed(2)), // 5,0 × 1.45 = 7.25 kWp
    panelWp: 400,
    panelCount: 19,     // ceil(7250 / 400) = ceil(18,125) = 19 módulos
    inverterKw: 7.3,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "P",
    tier: "Acelerado",
    systemKwp: parseFloat((5.0 * 1.60).toFixed(2)), // 5,0 × 1.60 = 8.00 kWp
    panelWp: 400,
    panelCount: 20,     // ceil(8000 / 400) = ceil(20,0) = 20 módulos
    inverterKw: 8.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  }
];

/**
 * === 2) TIPOS E VALIDAÇÕES PARA O BODY DE COBRANÇA ===
 *
 * O front-end deve enviar um JSON contendo:
 * - category: "P"
 * - tier: "Padrão" | "Consciente" | "Moderado" | "Acelerado"
 * - customer_id: ID do cliente Asaas (string)
 * - creditCardBrand: bandeira (ex.: "VISA", "MASTERCARD", "ELO")
 * - creditCardToken: token JWT do cartão (string)
 * - installmentCount: número de parcelas (int)
 * - dueDate: data de vencimento (AAAA-MM-DD)
 * - description (opcional): texto livre para descrição
 */

interface ChargeRequest {
  category: ProjectCategory;
  tier: GenerationTierName;
  customer_id: string;
  creditCardBrand: string;
  creditCardToken: string;
  installmentCount: number;
  dueDate: string;        // Formato "AAAA-MM-DD"
  description?: string;   // Texto de descrição (opcional)
}

/**
 * === 3) PARÂMETROS DA API DO ASAAS ===
 *
 * - ASAAS_BASE_URL: endpoint base produção Asaas
 * - ASAAS_API_TOKEN: token real Asaas (produção)
 * - HEADERS: cabeçalhos para requisição JSON
 */
const ASAAS_BASE_URL: string = "https://www.asaas.com/api/v3";
const ASAAS_API_TOKEN: string =
  "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6" +
  "OjVjNWI5MGFmLTk2NTMtNGY5Zi1iZTM1LWMxMTFkZDg0NDkxNjo6" +
  "JGFhY2hfYzRhYmUyZWYtMmU0Zi00NDYwLWFjOWEtMzRjMjEwNDhiZmE2";

const HEADERS = {
  "Content-Type": "application/json"
};

/**
 * === 4) FUNÇÕES AUXILIARES ===
 */

/**
 * Retorna a composição do kit P para o tier informado.
 * Se não encontrar, retorna undefined.
 */
function findKitByTier(tierName: GenerationTierName): SolarKitComponent | undefined {
  return pKits.find(kit => kit.tier === tierName);
}

/**
 * Calcula o preço total do kit:
 * (quantidade de módulos × custo de módulo) + (potência de inversor (kW) × custo por kW)
 */
function calculateKitPrice(kit: SolarKitComponent): number {
  const pricePanels = kit.panelCount * PANEL_COST;
  const priceInverter = kit.inverterKw * INVERTER_COST_PER_KW;
  return parseFloat((pricePanels + priceInverter).toFixed(2));
}

/**
 * Limita o número de parcelas conforme bandeira:
 * - Visa ou Mastercard: até 21×
 * - Demais bandeiras: até 12×
 */
function limitInstallments(brand: string, requested: number): number {
  const normalizedBrand = brand.trim().toUpperCase();
  if (normalizedBrand === "VISA" || normalizedBrand === "MASTERCARD") {
    return Math.min(requested, 21);
  }
  return Math.min(requested, 12);
}

/**
 * Valida se string é data no formato AAAA-MM-DD
 */
function isValidDate(dateString: string): boolean {
  const isoDatePattern = /^\d{4}-\d{2}-\d{2}$/;
  return isoDatePattern.test(dateString);
}

/**
 * Validação de campos com express-validator
 */
const chargeValidationRules = [
  body("category")
    .equals("P").withMessage("category deve ser 'P'"),
  body("tier")
    .isIn(["Padrão", "Consciente", "Moderado", "Acelerado"])
    .withMessage("tier inválido"),
  body("customer_id")
    .isString().withMessage("customer_id deve ser string"),
  body("creditCardBrand")
    .isString().withMessage("creditCardBrand deve ser string"),
  body("creditCardToken")
    .isString().withMessage("creditCardToken deve ser string"),
  body("installmentCount")
    .isInt({ gt: 0 }).withMessage("installmentCount deve ser inteiro positivo"),
  body("dueDate")
    .custom((value) => isValidDate(value))
    .withMessage("dueDate deve estar no formato 'AAAA-MM-DD'"),
  body("description")
    .optional().isString().withMessage("description deve ser string")
];

/**
 * === 5) ENDPOINT Express: CRIAR COBRANÇA NO ASAAS PARA KIT P ===
 */
app.post(
  "/p/create_charge",
  chargeValidationRules,
  async (req: Request, res: Response) => {
    // 5.1) Verificar erros de validação
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // 5.2) Extrair dados do corpo
    const {
      category,
      tier,
      customer_id,
      creditCardBrand,
      creditCardToken,
      installmentCount,
      dueDate,
      description = "Cobrança de Kit Solar P"
    } = req.body as ChargeRequest;

    // 5.3) Garantir que category seja "P"
    if (category !== "P") {
      return res.status(400).json({
        error: "Para este endpoint, a categoria deve ser 'P'."
      });
    }

    // 5.4) Buscar a composição do kit P para o tier solicitado
    const kit = findKitByTier(tier);
    if (!kit) {
      return res.status(404).json({
        error: `Não encontramos nenhum kit P para o tier '${tier}'.`
      });
    }

    // 5.5) Calcular preço total: módulos + inversor
    const priceTotal = calculateKitPrice(kit);

    // 5.6) Ajustar installmentCount com base na bandeira
    const adjustedInstallments = limitInstallments(creditCardBrand, installmentCount);

    // 5.7) Montar payload JSON para o Asaas
    const asaasPayload = {
      customer: customer_id,                       // ID do cliente no Asaas
      billingType: "CREDIT_CARD",                  // Cobrança via cartão
      installmentCount: adjustedInstallments,      // Parcelas ajustadas
      value: priceTotal,                           // Valor total do kit
      dueDate: dueDate,                            // Data de vencimento 1ª parcela
      description: `${description} (P - ${kit.tier})`,
      externalReference: `P_${kit.tier}_CHARGE_${customer_id}`,
      creditCard: {
        creditCardToken: creditCardToken           // Token do cartão já gerado
      },
      creditCardHolderInfo: {
        // Dados fixos de titular de cartão (parametrizar em produção)
        name: "NOME DO TITULAR",
        cpfCnpj: "000.000.000-00",
        postalCode: "01000-000",
        address: "Rua Exemplo",
        addressNumber: "100",
        complement: "Sala 1",
        province: "Centro",
        city: "São Paulo",
        state: "SP"
      }
    };

    // 5.8) Chamar API Asaas
    try {
      const asaasUrl = `${ASAAS_BASE_URL}/payments?access_token=${ASAAS_API_TOKEN}`;
      const response = await axios.post(asaasUrl, asaasPayload, { headers: HEADERS });

      // 5.9) Se sucesso, retornar dados
      return res.status(201).json({
        kit_composition: kit,
        price_total: priceTotal,
        requested_installments: installmentCount,
        adjusted_installments: adjustedInstallments,
        asaas_response: response.data
      });
    } catch (error: any) {
      // Se Asaas retornar erro (parcelas > permitido, etc.), repassamos
      if (error.response && error.response.data) {
        return res.status(error.response.status).json({ error: error.response.data });
      }
      // Erro interno
      return res.status(500).json({ error: "Erro interno ao chamar a API Asaas." });
    }
  }
);

/**
 * === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO DE KITS P ===
 *
 * GET /p/kits retorna lista completa dos 4 tiers de kit P.
 */
app.get("/p/kits", (req: Request, res: Response) => {
  return res.json(pKits);
});

// Inicia servidor na porta 3000 (ou variável de ambiente PORT)
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

### Explicação detalhada do código TypeScript para “P”

1. **Declaração de tipos e array `pKits` (seção 1)**
    
    - Cada objeto possui:
        
        - `category`: `"P"`.
            
        - `tier`: `"Padrão"`, `"Consciente"`, `"Moderado"` ou `"Acelerado"`.
            
        - `systemKwp`: `5.0 × multiplier`. Ex.: “Padrão” → 5.0 × 1.15 = 5.75 kWp.
            
        - `panelCount`: `ceil((systemKwp × 1000) / 400)`. Ex.: “Padrão” → `ceil(5750 / 400) = 15` módulos.
            
        - `inverterKw`: 5.8 kW para “Padrão”, 6.5 para “Consciente”, 7.3 para “Moderado” e 8.0 para “Acelerado”.
            
        - `lossFactors`: informativos (4 %, 3 %, 3 %, 4 %).
            
2. **Modelo de requisição `ChargeRequest` (seção 2)**
    
    - O front-end manda JSON com:
        
        - `category` (fixo “P”),
            
        - `tier` (um dos quatro tiers),
            
        - `customer_id` (string),
            
        - `creditCardBrand` (string),
            
        - `creditCardToken` (string),
            
        - `installmentCount` (int),
            
        - `dueDate` (“AAAA-MM-DD”),
            
        - `description` (opcional).
            
3. **Funções auxiliares (seção 4)**
    
    - `findKitByTier(tierName)`: retorna o kit correspondente a `tierName`, ou `undefined` se não achar.
        
    - `calculateKitPrice(kit)`: `(kit.panelCount × 800) + (kit.inverterKw × 2000)`, arredondado a duas casas.
        
    - `limitInstallments(brand, requested)`:
        
        - Se `brand` é “VISA” ou “MASTERCARD”, retorna `min(requested, 21)`.
            
        - Senão (Elo, Amex, Hipercard, etc.), retorna `min(requested, 12)`.
            
    - `isValidDate(dateString)`: valida formato “AAAA-MM-DD”.
        
4. **Endpoint `POST /p/create_charge` (seção 5)**
    
    - Usa `express-validator` para validar e sanitizar:
        
        - `category == "P"`;
            
        - `tier` em lista válida;
            
        - `customer_id`, `creditCardBrand`, `creditCardToken` como strings;
            
        - `installmentCount` como inteiro > 0;
            
        - `dueDate` no formato “AAAA-MM-DD”.
            
    - Se `category !== "P"`, retorna 400.
        
    - Recupera kit com `findKitByTier()`. Se `undefined`, retorna 404.
        
    - Calcula `priceTotal = calculateKitPrice(kit)`.
        
    - Ajusta parcelas com `limitInstallments(creditCardBrand, installmentCount)`.
        
    - Monta `asaasPayload` com `customer`, `billingType`, `installmentCount`, `value`, `dueDate`, `description`, `externalReference`, `creditCard` (token) e `creditCardHolderInfo` (dados fixos).
        
    - Chama `POST https://www.asaas.com/api/v3/payments?access_token={ASAAS_API_TOKEN}` com payload JSON.
        
    - Se retornar erro (status != 200/201), devolve o JSON de erro do Asaas.
        
    - Se sucesso, devolve JSON com:
        
        - `kit_composition` (objeto kit),
            
        - `price_total`,
            
        - `requested_installments`,
            
        - `adjusted_installments`,
            
        - `asaas_response` (JSON completo do Asaas).
            
5. **Endpoint `GET /p/kits` (seção 6)**
    
    - Retorna o array `pKits`, permitindo ao front‐end mostrar ao cliente todas as opções de tier disponíveis.
        

---

## 3. Resumo dos Valores Calculados para “P”

Para cada **tier** em “P” (baseado em `averageKwp = 5,0 kWp`):

|Tier|systemKwp (kWp)|panelCount|inverterKw (kW)|Painéis (R$ = panelCount×800)|Inversor (R$ = inverterKw×2000)|Total (R$)|
|---|---|---|---|---|---|---|
|Padrão|5,75|15|5,8|15 × 800 = 12 000|5,8 × 2 000 = 11 600|23 600|
|Consciente|6,50|17|6,5|17 × 800 = 13 600|6,5 × 2 000 = 13 000|26 600|
|Moderado|7,25|19|7,3|19 × 800 = 15 200|7,3 × 2 000 = 14 600|29 800|
|Acelerado|8,00|20|8,0|20 × 800 = 16 000|8,0 × 2 000 = 16 000|32 000|

- **Cálculo**:
    
    1. `systemKwp = 5,0 × multiplier`.
        
    2. `panelCount = ceil((systemKwp × 1000) / 400)`.
        
    3. `Preço total = (panelCount × 800) + (inverterKw × 2000)`.
        
- **Exemplo de parcelamento**:
    
    - Se bandeira for **VISA** e cliente pedir `installmentCount = 25`, ajusta para `21`.
        
    - Se bandeira for **ELO** e cliente pedir `installmentCount = 14`, ajusta para `12`.
        

---

### Exemplos de Requisição

#### 3.1. Requisição para “P – Moderado” com 24× em Visa

```bash
POST /p/create_charge
Host: localhost:3000
Content-Type: application/json

{
  "category": "P",
  "tier": "Moderado",
  "customer_id": "cus_EXEMPLO_CLIENTE_P",
  "creditCardBrand": "VISA",
  "creditCardToken": "tkn_EXEMPLO_TOKEN_CLIENTE",
  "installmentCount": 24,
  "dueDate": "2025-06-10",
  "description": "Kit P – Moderado – 24x"
}
```

- **Fluxo**:
    
    1. `findKitByTier("Moderado")` → kit com `systemKwp=7,25`, `panelCount=19`, `inverterKw=7,3`.
        
    2. `calculateKitPrice(...)` → `(19×800)+(7,3×2000)=15 200+14 600=29 800`.
        
    3. `limitInstallments("VISA", 24)` → `min(24,21)=21`.
        
    4. Monta payload e chama Asaas:
        
        ```jsonc
        {
          "customer": "cus_EXEMPLO_CLIENTE_P",
          "billingType": "CREDIT_CARD",
          "installmentCount": 21,
          "value": 29800.00,
          "dueDate": "2025-06-10",
          "description": "Kit P – Moderado – 21x (ajustado) (P – Moderado)",
          "externalReference": "P_Moderado_CHARGE_cus_EXEMPLO_CLIENTE_P",
          "creditCard": {
            "creditCardToken": "tkn_EXEMPLO_TOKEN_CLIENTE"
          },
          "creditCardHolderInfo": {
            "name": "NOME DO TITULAR",
            "cpfCnpj": "000.000.000-00",
            "postalCode": "01000-000",
            "address": "Rua Exemplo",
            "addressNumber": "100",
            "complement": "Sala 1",
            "province": "Centro",
            "city": "São Paulo",
            "state": "SP"
          }
        }
        ```
        
    5. Retorna JSON com composição, preço e resposta Asaas.
        

#### 3.2. Requisição para “P – Consciente” com 10× em Hipercard

```bash
POST /p/create_charge
Host: localhost:3000
Content-Type: application/json

{
  "category": "P",
  "tier": "Consciente",
  "customer_id": "cus_EXEMPLO_CLIENTE_P",
  "creditCardBrand": "HIPERCARD",
  "creditCardToken": "tkn_EXEMPLO_TOKEN_CLIENTE",
  "installmentCount": 10,
  "dueDate": "2025-06-15",
  "description": "Kit P – Consciente – 10x"
}
```

- **Fluxo**:
    
    1. `findKitByTier("Consciente")` → kit com `systemKwp=6,50`, `panelCount=17`, `inverterKw=6,5`.
        
    2. `calculateKitPrice(...)` → `(17×800)+(6,5×2000)=13 600+13 000=26 600`.
        
    3. `limitInstallments("HIPERCARD", 10)` → `min(10,12)=10` (não ajusta).
        
    4. Monta payload:
        
        ```jsonc
        {
          "customer": "cus_EXEMPLO_CLIENTE_P",
          "billingType": "CREDIT_CARD",
          "installmentCount": 10,
          "value": 26600.00,
          "dueDate": "2025-06-15",
          "description": "Kit P – Consciente – 10x (P – Consciente)",
          "externalReference": "P_Consciente_CHARGE_cus_EXEMPLO_CLIENTE_P",
          "creditCard": {
            "creditCardToken": "tkn_EXEMPLO_TOKEN_CLIENTE"
          },
          "creditCardHolderInfo": {
            "name": "NOME DO TITULAR",
            "cpfCnpj": "000.000.000-00",
            "postalCode": "01000-000",
            "address": "Rua Exemplo",
            "addressNumber": "100",
            "complement": "Sala 1",
            "province": "Centro",
            "city": "São Paulo",
            "state": "SP"
          }
        }
        ```
        
    5. Retorna JSON com detalhes.
        

---

### 4. Sumário Final dos Kits “P”

|Tier|systemKwp|panelCount|inverterKw|Painéis (R$)|Inversor (R$)|Total (R$)|
|---|---|---|---|---|---|---|
|Padrão|5,75|15|5,8|15 × 800 = 12 000|5,8 × 2 000 = 11 600|23 600|
|Consciente|6,50|17|6,5|17 × 800 = 13 600|6,5 × 2 000 = 13 000|26 600|
|Moderado|7,25|19|7,3|19 × 800 = 15 200|7,3 × 2 000 = 14 600|29 800|
|Acelerado|8,00|20|8,0|20 × 800 = 16 000|8,0 × 2 000 = 16 000|32 000|

- **Parcelamento Visa/Mastercard** ≤ 21×.
    
- **Parcelamento demais bandeiras** ≤ 12×.
    

Com isso, você tem a base pronta para automatizar cobranças Asaas para **kits solares “P”**, respeitando integralmente as regras de parcelas definidos pela plataforma.