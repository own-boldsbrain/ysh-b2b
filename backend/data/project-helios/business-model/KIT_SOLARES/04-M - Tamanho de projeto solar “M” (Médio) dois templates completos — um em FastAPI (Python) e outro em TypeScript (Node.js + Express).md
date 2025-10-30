A seguir, apresento para o **tamanho de projeto solar “M” (Médio)** dois templates completos — um em **FastAPI (Python)** e outro em **TypeScript (Node.js + Express)** — que ilustram:

1. **Cálculo automático dos valores** (painéis + inversor) de cada tier de geração (“Padrão”, “Consciente”, “Moderado” e “Acelerado”).
    
2. **Lógica de limitação de parcelas** baseada na bandeira do cartão de crédito: até **21× para Visa/Mastercard** e **até 12× para demais bandeiras** (conforme documentação Asaas).
    
3. **Payload JSON de cobrança** para envio ao Asaas, incluindo `installmentCount` corretamente ajustado.
    
4. Comentários explicativos detalhados em cada trecho de código, sem abreviações, para facilitar leitura e manutenção.
    

---

## Informação Base para “M” (Médio)

- **averageKwp** (média de potência): **15,0 kWp**
    
- **Potência nominal de cada painel**: **400 Wp**
    
- **Preço por painel (400 Wp)**: **R$ 800,00**
    
- **Preço por inversor (por kW)**: **R$ 2 000,00**
    
- **Recomendações de inversor para “M”**:
    
    - **Padrão** → 17 kW
        
    - **Consciente** → 20 kW
        
    - **Moderado** → 23 kW
        
    - **Acelerado** → 26 kW
        
- **Multiplicadores por tier**:
    
    - **Padrão** → 1.15
        
    - **Consciente** → 1.30
        
    - **Moderado** → 1.45
        
    - **Acelerado** → 1.60
        

**Como calcular o kit “M” para cada tier**:

1. **systemKwp** = 15 × (multiplier)
    
2. **panelCount** = ceil((systemKwp × 1000) / 400)
    
3. **Preço total** = (panelCount × 800) + (inverterKw × 2 000)
    

**Regras de parcelamento**:

- **Visa/Mastercard** → até 21×
    
- **Demais bandeiras** (Elo, Amex, Hipercard etc.) → até 12×
    

---

## 1. Template em FastAPI (Python) para “M” (Médio)

```python
# fastapi_m.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import httpx

app = FastAPI(
    title="API de Cobrança de Kit Solar M",
    description=(
        "Este serviço calcula o valor do kit solar para projetos M "
        "e cria a cobrança no Asaas, limitando em até 21 parcelas "
        "para Visa/Mastercard e até 12 parcelas para demais bandeiras."
    ),
    version="1.0.0"
)

#
# === 1) DEFINIÇÃO DOS DADOS DE COMPOSIÇÃO DO KIT M ===
#

# 1.1) Tipos auxiliares
ProjectCategory = Literal["M"]  # Somente "M" neste template
GenerationTierName = Literal["Padrão", "Consciente", "Moderado", "Acelerado"]

class LossFactors(BaseModel):
    """
    Fatores de perda do sistema fotovoltaico (%):
    - temperature: perda por temperatura
    - shading: perda por sombreamento
    - soiling: perda por sujeira/poeira
    - mismatchLidDc: perda combinada (mismatch + LID + fios DC)
    """
    temperature: float = Field(..., description="Perda por temperatura (%)")
    shading: float = Field(..., description="Perda por sombreamento (%)")
    soiling: float = Field(..., description="Perda por sujeira (%)")
    mismatchLidDc: float = Field(..., description="Perda mismatch/LID/DC (%)")

class SolarKitComponent(BaseModel):
    """
    Representa a composição do kit solar M para um determinado tier:
    - category: sempre "M"
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

# 1.3) Lista de tiers de geração M (averageKwp = 15,0 kWp)
#
#   - Multipliers: Padrão=1.15, Consciente=1.30, Moderado=1.45, Acelerado=1.60
#   - Cálculo de panelCount: ceil((systemKwp × 1000) / 400)
#   - Recomendações de inversor (kW): 17, 20, 23, 26
#
generation_tiers: List[SolarKitComponent] = [
    # Tier Padrão: multiplier = 1.15
    SolarKitComponent(
        category="M",
        tier="Padrão",
        systemKwp=round(15.0 * 1.15, 2), # 15,0 × 1.15 = 17,25 kWp
        panelWp=400,
        panelCount=44,                   # ceil(17250 / 400) = ceil(43,125) = 44 módulos
        inverterKw=17.0,                 # recomendado Asaas para M – Padrão
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Consciente: multiplier = 1.30
    SolarKitComponent(
        category="M",
        tier="Consciente",
        systemKwp=round(15.0 * 1.30, 2), # 15,0 × 1.30 = 19,50 kWp
        panelWp=400,
        panelCount=49,                   # ceil(19500 / 400) = ceil(48,75) = 49 módulos
        inverterKw=20.0,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Moderado: multiplier = 1.45
    SolarKitComponent(
        category="M",
        tier="Moderado",
        systemKwp=round(15.0 * 1.45, 2), # 15,0 × 1.45 = 21,75 kWp
        panelWp=400,
        panelCount=55,                   # ceil(21750 / 400) = ceil(54,375) = 55 módulos
        inverterKw=23.0,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Acelerado: multiplier = 1.60
    SolarKitComponent(
        category="M",
        tier="Acelerado",
        systemKwp=round(15.0 * 1.60, 2), # 15,0 × 1.60 = 24,00 kWp
        panelWp=400,
        panelCount=60,                   # ceil(24000 / 400) = ceil(60,0) = 60 módulos
        inverterKw=26.0,
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
    Campos esperados no corpo da requisição para criar cobrança:
    - category: deve ser "M" (este template é específico para M)
    - tier: um dos quatro níveis de geração (Padrão, Consciente, Moderado, Acelerado)
    - customer_id: ID do cliente já cadastrado no Asaas (ex.: "cus_ABC123xyz")
    - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO", "AMEX" etc.)
    - creditCardToken: token de cartão já obtido anteriormente (ex.: "tkn_abc123xyz")
    - installmentCount: número desejado de parcelas (int); será limitado conforme bandeira
    - dueDate: data de vencimento da primeira parcela no formato "AAAA-MM-DD"
    - description (opcional): descrição livre para a cobrança; se não informado, usa padrão interno
    """
    category: ProjectCategory = Field(..., description='Categoria do projeto, neste caso "M"')
    tier: GenerationTierName = Field(..., description="Nível de geração desejado para cálculo do kit")
    customer_id: str = Field(..., description="ID do cliente no Asaas, ex.: 'cus_ABC123xyz'")
    creditCardBrand: str = Field(..., description="Bandeira do cartão, ex.: 'VISA', 'MASTERCARD', 'ELO'")
    creditCardToken: str = Field(..., description="Token de cartão já gerado, ex.: 'tkn_abc123xyz'")
    installmentCount: int = Field(..., description="Número de parcelas solicitado pelo cliente")
    dueDate: str = Field(..., description='Data de vencimento da primeira parcela no formato "AAAA-MM-DD"')
    description: str = Field(
        default="Cobrança de Kit Solar M",
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
    Retorna a composição do kit M para o tier informado.
    Se não encontrar, levanta HTTPException 404.
    """
    for kit in generation_tiers:
        if kit.tier == tier_name:
            return kit
    raise HTTPException(
        status_code=404,
        detail=f"Não foi possível encontrar o kit M para o tier '{tier_name}'."
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
# === 5) ENDPOINT FASTAPI: CRIAR COBRANÇA NO ASAAS PARA KIT M ===
#

@app.post("/m/create_charge")
async def create_m_charge(request: ChargeRequest):
    # 5.1) Validar categoria M (mesmo que Pydantic já imponha, reforçamos aqui)
    if request.category != "M":
        raise HTTPException(
            status_code=400,
            detail="Esta rota só suporta projetos solares de tamanho 'M'."
        )

    # 5.2) Buscar a composição do kit M para o tier solicitado
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
        "billingType": "CREDIT_CARD",                    # Cobrança via cartão de crédito
        "installmentCount": adjusted_installments,       # Parcelas ajustadas
        "value": price_total,                            # Valor total do kit calculado
        "dueDate": request.dueDate,                      # Data de vencimento da 1ª parcela
        "description": f"{request.description} (M - {kit.tier})",
        "externalReference": f"M_{kit.tier}_CHARGE_{request.customer_id}",
        "creditCard": {
            "creditCardToken": request.creditCardToken    # Token do cartão já gerado
        },
        "creditCardHolderInfo": {
            # Dados de titular de cartão; em produção, parametrizar conforme banco de dados
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
        # Se houve erro (ex.: parcelamento não permitido), devolvemos a resposta
        raise HTTPException(
            status_code=response.status_code,
            detail={"error": response.json()}
        )

    # 5.8) Retornar resultado ao cliente
    return {
        "kit_composition": kit.dict(),
        "price_total": price_total,
        "requested_installments": request.installmentCount,
        "adjusted_installments": adjusted_installments,
        "asaas_response": response.json()
    }

#
# === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO M (APENAS CONSULTA) ===
#

@app.get("/m/kits", response_model=List[SolarKitComponent])
async def list_m_kits():
    """
    Retorna a lista completa de composições de kit M para os 4 tiers:
    - Útil para front‐ends que queiram exibir as opções de tier ao usuário.
    """
    return generation_tiers
```

### Explicação detalhada do código FastAPI para “M”

1. **Composição do Kit M (seção 1)**
    
    - Declaramos `generation_tiers`, com quatro instâncias de `SolarKitComponent`, uma para cada tier em “M”.
        
    - Cada componente armazena:
        
        - `category`: sempre `"M"`.
            
        - `tier`: `"Padrão"`, `"Consciente"`, `"Moderado"` ou `"Acelerado"`.
            
        - `systemKwp`: calculado por `15.0 × multiplier`, arredondado a duas casas. Por exemplo, para “Padrão”: `15.0 × 1.15 = 17.25 kWp`.
            
        - `panelCount`: número de módulos de 400 Wp necessários, calculado como `ceil((systemKwp × 1000) / 400)`. Ex.: `"Padrão"` → `ceil(17 250 / 400) = ceil(43.125) = 44`.
            
        - `inverterKw`: recomendado em kW (`17.0`, `20.0`, `23.0` ou `26.0`).
            
        - `lossFactors`: apenas informativos (4 %, 3 %, 3 %, 4 %).
            
2. **Modelo de requisição `ChargeRequest` (seção 2)**
    
    - Espera receber no JSON:
        
        - `category`: deve ser `"M"` (literal).
            
        - `tier`: um dos quatro níveis.
            
        - `customer_id`: string — ID do cliente já cadastrado no Asaas, por exemplo `"cus_ABC123xyz"`.
            
        - `creditCardBrand`: string — nome da bandeira (ex.: `"VISA"`, `"MASTERCARD"`, `"ELO"` etc.).
            
        - `creditCardToken`: string — token JWT do cartão (já obtido via endpoint de tokenização).
            
        - `installmentCount`: número solicitado de parcelas (int).
            
        - `dueDate`: string no formato `"AAAA-MM-DD"`.
            
        - `description`: string opcional — texto livre para descrição, se não fornecer usa `"Cobrança de Kit Solar M"`.
            
3. **Funções auxiliares (seção 4)**
    
    - `find_kit_for_tier(tier_name)`: itera sobre `generation_tiers` e retorna o `SolarKitComponent` que tenha `tier == tier_name`. Se não achar, lança `HTTPException(status_code=404)`.
        
    - `calculate_kit_price(kit)`: faz `(kit.panelCount × PANEL_COST) + (kit.inverterKw × INVERTER_COST_PER_KW)` e arredonda para duas casas decimais.
        
    - `limit_installments(brand, requested_installments)`: normaliza a `brand` para maiúsculas e retira espaços. Se for `"VISA"` ou `"MASTERCARD"`, retorna `min(requested_installments, 21)`. Caso contrário, retorna `min(requested_installments, 12)`.
        
4. **Endpoint `/m/create_charge` (seção 5)**
    
    - Valida que `request.category == "M"`. Caso contrário, retorna `HTTPException(400)`.
        
    - Recupera o `kit` correto chamando `find_kit_for_tier(request.tier)`. Se não existir, retorna `404`.
        
    - Calcula `price_total = calculate_kit_price(kit)`.
        
    - Ajusta `installmentCount` usando `limit_installments(request.creditCardBrand, request.installmentCount)`.
        
    - Monta o dicionário `asaas_payload` com todos os campos obrigatórios para o Asaas:
        
        ```jsonc
        {
          "customer": request.customer_id,
          "billingType": "CREDIT_CARD",
          "installmentCount": adjusted_installments,
          "value": price_total,
          "dueDate": request.dueDate,
          "description": "<texto personalizado> (M – <tier>)",
          "externalReference": "M_<tier>_CHARGE_<customer_id>",
          "creditCard": { "creditCardToken": request.creditCardToken },
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
        
    - Envia `POST https://www.asaas.com/api/v3/payments?access_token=<ASAAS_API_TOKEN>` com este JSON.
        
    - Se o Asaas retornar código diferente de `200` ou `201`, repassa o erro para o cliente com `HTTPException(status_code, detail={…})`.
        
    - Se sucesso, devolve JSON contendo:
        
        - `"kit_composition"`: objeto completo do kit (campos de `SolarKitComponent`).
            
        - `"price_total"`: valor calculado total.
            
        - `"requested_installments"`: parcelas originalmente solicitadas pelo usuário.
            
        - `"adjusted_installments"`: parcelas efetivamente enviadas ao Asaas (≤ 21 ou ≤ 12).
            
        - `"asaas_response"`: corpo JSON completo devolvido pelo Asaas.
            
5. **Endpoint `/m/kits` (seção 6)**
    
    - Retorna o array completo `generation_tiers`, permitindo ao front‐end exibir as opções de kit (padrão, consciente, moderado, acelerado) para “M”.
        

---

## 2. Template em TypeScript (Node.js + Express) para “M”

```typescript
// server_m.ts

import express, { Request, Response } from "express";
import axios from "axios";
import { body, validationResult } from "express-validator";

const app = express();
app.use(express.json());

/**
 * === 1) TIPOS E DADOS DE COMPOSIÇÃO DO KIT M ===
 *
 * Em M, definimos quatro tiers de geração com seus multiplicadores,
 * potências de inversor recomendadas e fatores de perda.
 */

type ProjectCategory = "M"; // Neste template, apenas "M" é aceito
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
  /** Categoria do projeto, fixo em "M" */
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

// 1.1) Custo de componentes (ajustar conforme valores de mercado)
const PANEL_COST: number = 800.0;            // R$ 800,00 por módulo de 400 Wp
const INVERTER_COST_PER_KW: number = 2000.0; // R$ 2 000,00 por kW de inversor

// 1.2) Lista de composições dos kits M (4 tiers)
//     - averageKwp = 15,0 kWp
//     - Multipliers: Padrão=1.15, Consciente=1.30, Moderado=1.45, Acelerado=1.60
//     - Recomendações de inversor (kW): 17, 20, 23, 26
const mKits: SolarKitComponent[] = [
  {
    category: "M",
    tier: "Padrão",
    systemKwp: parseFloat((15.0 * 1.15).toFixed(2)), // 15,0 × 1.15 = 17,25 kWp
    panelWp: 400,
    panelCount: 44,    // ceil(17 250 / 400) = ceil(43,125) = 44 módulos
    inverterKw: 17.0,  // recomendação Asaas para M – Padrão
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "M",
    tier: "Consciente",
    systemKwp: parseFloat((15.0 * 1.30).toFixed(2)), // 15,0 × 1.30 = 19,50 kWp
    panelWp: 400,
    panelCount: 49,    // ceil(19 500 / 400) = ceil(48,75) = 49 módulos
    inverterKw: 20.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "M",
    tier: "Moderado",
    systemKwp: parseFloat((15.0 * 1.45).toFixed(2)), // 15,0 × 1.45 = 21,75 kWp
    panelWp: 400,
    panelCount: 55,    // ceil(21 750 / 400) = ceil(54,375) = 55 módulos
    inverterKw: 23.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "M",
    tier: "Acelerado",
    systemKwp: parseFloat((15.0 * 1.60).toFixed(2)), // 15,0 × 1.60 = 24,00 kWp
    panelWp: 400,
    panelCount: 60,    // ceil(24 000 / 400) = ceil(60,0) = 60 módulos
    inverterKw: 26.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  }
];

/**
 * === 2) TIPOS E VALIDAÇÕES PARA O BODY DE COBRANÇA ===
 *
 * O front-end deve enviar um JSON contendo:
 * - category: "M"
 * - tier: "Padrão" | "Consciente" | "Moderado" | "Acelerado"
 * - customer_id: ID do cliente Asaas (string)
 * - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO")
 * - creditCardToken: token JWT do cartão (string)
 * - installmentCount: número desejado de parcelas (int)
 * - dueDate: data de vencimento (AAAA-MM-DD)
 * - description (opcional): descrição da cobrança
 */

interface ChargeRequest {
  category: ProjectCategory;
  tier: GenerationTierName;
  customer_id: string;
  creditCardBrand: string;
  creditCardToken: string;
  installmentCount: number;
  dueDate: string;        // Formato "AAAA-MM-DD"
  description?: string;   // Texto livre para descrição (opcional)
}

/**
 * === 3) PARÂMETROS DA API DO ASAAS ===
 *
 * - ASAAS_BASE_URL: endpoint base de produção da Asaas
 * - ASAAS_API_TOKEN: token real fornecido pela Asaas (string)
 * - HEADERS: cabeçalhos padrão para envio JSON
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
 * Retorna a composição do kit M para o tier informado.
 * Se não encontrar, retorna undefined.
 */
function findKitByTier(tierName: GenerationTierName): SolarKitComponent | undefined {
  return mKits.find(kit => kit.tier === tierName);
}

/**
 * Calcula o preço total do kit:
 * (quantidade de módulos × custo unitário de módulo) + (potência de inversor (kW) × custo por kW)
 */
function calculateKitPrice(kit: SolarKitComponent): number {
  const pricePanels = kit.panelCount * PANEL_COST;
  const priceInverter = kit.inverterKw * INVERTER_COST_PER_KW;
  return parseFloat((pricePanels + priceInverter).toFixed(2));
}

/**
 * Limita o número de parcelas conforme bandeira do cartão:
 * - Visa ou Mastercard: até 21×
 * - Demais bandeiras (Elo, Amex, Hipercard etc.): até 12×
 */
function limitInstallments(brand: string, requested: number): number {
  const normalizedBrand = brand.trim().toUpperCase();
  if (normalizedBrand === "VISA" || normalizedBrand === "MASTERCARD") {
    return Math.min(requested, 21);
  }
  return Math.min(requested, 12);
}

/**
 * Valida se uma string segue o padrão AAAA-MM-DD (data)
 */
function isValidDate(dateString: string): boolean {
  const isoDatePattern = /^\d{4}-\d{2}-\d{2}$/;
  return isoDatePattern.test(dateString);
}

/**
 * Regras de validação de campos usando express-validator
 */
const chargeValidationRules = [
  body("category")
    .equals("M").withMessage("category deve ser 'M'"),
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
 * === 5) ENDPOINT Express: CRIAR COBRANÇA NO ASAAS PARA KIT M ===
 */
app.post(
  "/m/create_charge",
  chargeValidationRules,
  async (req: Request, res: Response) => {
    // 5.1) Verificar erros de validação
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // 5.2) Extrair dados do corpo da requisição
    const {
      category,
      tier,
      customer_id,
      creditCardBrand,
      creditCardToken,
      installmentCount,
      dueDate,
      description = "Cobrança de Kit Solar M"
    } = req.body as ChargeRequest;

    // 5.3) Garantir que category seja "M"
    if (category !== "M") {
      return res.status(400).json({
        error: "Para este endpoint, a categoria deve ser 'M'."
      });
    }

    // 5.4) Buscar a composição do kit M para o tier solicitado
    const kit = findKitByTier(tier);
    if (!kit) {
      return res.status(404).json({
        error: `Não encontramos nenhum kit M para o tier '${tier}'.`
      });
    }

    // 5.5) Calcular preço total: módulos + inversor
    const priceTotal = calculateKitPrice(kit);

    // 5.6) Ajustar installmentCount com base na bandeira do cartão
    const adjustedInstallments = limitInstallments(creditCardBrand, installmentCount);

    // 5.7) Montar o payload JSON para a API Asaas
    const asaasPayload = {
      customer: customer_id,                       // ID do cliente no Asaas
      billingType: "CREDIT_CARD",                  // Cobrança via cartão
      installmentCount: adjustedInstallments,      // Parcelas ajustadas
      value: priceTotal,                           // Valor total do kit
      dueDate: dueDate,                            // Data de vencimento da 1ª parcela
      description: `${description} (M - ${kit.tier})`,
      externalReference: `M_${kit.tier}_CHARGE_${customer_id}`,
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

    // 5.8) Enviar requisição para Asaas
    try {
      const asaasUrl = `${ASAAS_BASE_URL}/payments?access_token=${ASAAS_API_TOKEN}`;
      const response = await axios.post(asaasUrl, asaasPayload, { headers: HEADERS });

      // 5.9) Se sucesso, retornar dados completos
      return res.status(201).json({
        kit_composition: kit,
        price_total: priceTotal,
        requested_installments: installmentCount,
        adjusted_installments: adjustedInstallments,
        asaas_response: response.data
      });
    } catch (error: any) {
      // Em caso de erro do Asaas (parcelamento inválido, etc.), repassa o erro
      if (error.response && error.response.data) {
        return res.status(error.response.status).json({ error: error.response.data });
      }
      // Em caso de erro interno de rede ou timeout
      return res.status(500).json({ error: "Erro interno ao chamar a API Asaas." });
    }
  }
);

/**
 * === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO DE KITS M ===
 *
 * GET /m/kits retorna a lista completa dos kits M (4 tiers),
 * permitindo que o front‐end exiba as opções de kit ao usuário.
 */
app.get("/m/kits", (req: Request, res: Response) => {
  return res.json(mKits);
});

// Inicia o servidor na porta 3000 (ou variável de ambiente PORT)
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

### Explicação detalhada do código TypeScript para “M”

1. **Declaração de tipos e array `mKits` (seção 1)**
    
    - Cada objeto contém:
        
        - `category`: fixo em `"M"`.
            
        - `tier`: `"Padrão"`, `"Consciente"`, `"Moderado"` ou `"Acelerado"`.
            
        - `systemKwp`: calculado como `15.0 × multiplier`. Por exemplo, “Padrão” → `15.0 × 1.15 = 17.25 kWp`.
            
        - `panelWp`: sempre `400` (potência do módulo em Watt-Peak).
            
        - `panelCount`: calculado via `ceil((systemKwp × 1000) / 400)`. Ex.: “Padrão” → `ceil(17 250 / 400) = 44` módulos.
            
        - `inverterKw`: potência recomendada (kW) — `17.0`, `20.0`, `23.0`, `26.0`.
            
        - `lossFactors`: informativos (4 %, 3 %, 3 %, 4 %).
            
2. **Modelo de requisição `ChargeRequest` (seção 2)**
    
    - O front‐end deve enviar JSON contendo:
        
        - `category`: `"M"`.
            
        - `tier`: `"Padrão" | "Consciente" | "Moderado" | "Acelerado"`.
            
        - `customer_id`: string (ID do cliente).
            
        - `creditCardBrand`: string (bandeira).
            
        - `creditCardToken`: string (token do cartão).
            
        - `installmentCount`: int (parcelas solicitadas).
            
        - `dueDate`: string no formato `"AAAA-MM-DD"`.
            
        - `description`: string opcional (ex.: `"Cobrança de Kit Solar M"`, se não for enviado).
            
3. **Funções auxiliares (seção 4)**
    
    - `findKitByTier(tierName)`: retorna o kit correspondente pelo campo `tier`. Se não encontrar, retorna `undefined`.
        
    - `calculateKitPrice(kit)`: realiza `(kit.panelCount × PANEL_COST) + (kit.inverterKw × INVERTER_COST_PER_KW)` e arredonda para duas casas.
        
    - `limitInstallments(brand, requested)`:
        
        - Se `brand.toUpperCase()` for `"VISA"` ou `"MASTERCARD"`, retorna `Math.min(requested, 21)`.
            
        - Senão, retorna `Math.min(requested, 12)`.
            
    - `isValidDate(dateString)`: valida regex `^\d{4}-\d{2}-\d{2}$`.
        
4. **Endpoint `POST /m/create_charge` (seção 5)**
    
    - Usa `express-validator` para validar cada campo do JSON:
        
        - `category` deve ser `"M"`.
            
        - `tier` deve estar entre as quatro opções.
            
        - `customer_id`, `creditCardBrand`, `creditCardToken` devem ser strings.
            
        - `installmentCount` deve ser inteiro > 0.
            
        - `dueDate` valida com `isValidDate`.
            
        - `description` é opcional, mas se enviado deve ser string.
            
    - Se houver falhas de validação, retorna `400 Bad Request` com lista de erros.
        
    - Garante que `category === "M"`; senão, retorna `400`.
        
    - Busca kit com `findKitByTier(tier)`. Se `undefined`, retorna `404`.
        
    - Calcula `priceTotal = calculateKitPrice(kit)`.
        
    - Ajusta parcelas com `limitInstallments(creditCardBrand, installmentCount)`.
        
    - Monta `asaasPayload` com campos obrigatórios para Asaas:
        
        ```jsonc
        {
          "customer": customer_id,
          "billingType": "CREDIT_CARD",
          "installmentCount": adjustedInstallments,
          "value": priceTotal,
          "dueDate": dueDate,
          "description": "<desc> (M – <tier>)",
          "externalReference": "M_<tier>_CHARGE_<customer_id>",
          "creditCard": { "creditCardToken": creditCardToken },
          "creditCardHolderInfo": { …dados fixos… }
        }
        ```
        
    - Chama `POST https://www.asaas.com/api/v3/payments?access_token=<ASAAS_API_TOKEN>` com `asaasPayload`.
        
    - Se a resposta tiver status diferente de `200` ou `201`, repassa o JSON de erro do Asaas.
        
    - Se sucesso, retorna `201 Created` com:
        
        - `kit_composition` (objeto completo do kit).
            
        - `price_total`.
            
        - `requested_installments` (parcelas solicitadas).
            
        - `adjusted_installments` (parcelas enviadas ao Asaas).
            
        - `asaas_response` (JSON completo do Asaas).
            
5. **Endpoint `GET /m/kits` (seção 6)**
    
    - Retorna todo o array `mKits`, para que o front‐end exiba os quatro tiers disponíveis.
        

---

## 3. Resumo dos Valores Calculados para “M”

Para cada **tier** em “M” (com `averageKwp = 15,0 kWp`):

|Tier|systemKwp (kWp)|panelCount|inverterKw (kW)|Painéis (R$ = panelCount×800)|Inversor (R$ = inverterKw×2000)|Total (R$)|
|---|---|---|---|---|---|---|
|Padrão|17,25|44|17,0|44 × 800 = 35 200|17 × 2 000 = 34 000|69 200|
|Consciente|19,50|49|20,0|49 × 800 = 39 200|20 × 2 000 = 40 000|79 200|
|Moderado|21,75|55|23,0|55 × 800 = 44 000|23 × 2 000 = 46 000|90 000|
|Acelerado|24,00|60|26,0|60 × 800 = 48 000|26 × 2 000 = 52 000|100 000|

**Como calcular**:

1. `systemKwp = 15,0 × multiplier` (1.15, 1.30, 1.45 ou 1.60).
    
2. `panelCount = ceil((systemKwp × 1000) / 400)`.
    
3. `Preço total = (panelCount × 800) + (inverterKw × 2000)`.
    

**Exemplos de parcelamento**:

- Se bandeira for **VISA** e cliente pedir `installmentCount = 25`, ajusta para `21`.
    
- Se bandeira for **ELO** e cliente pedir `installmentCount = 13`, ajusta para `12`.
    

---

### Exemplos de Requisição

#### 3.1. Criar cobrança “M – Padrão” com 21× em Mastercard

```bash
POST /m/create_charge
Host: localhost:3000
Content-Type: application/json

{
  "category": "M",
  "tier": "Padrão",
  "customer_id": "cus_EXEMPLO_CLIENTE_M",
  "creditCardBrand": "MASTERCARD",
  "creditCardToken": "tkn_EXEMPLO_TOKEN_CLIENTE",
  "installmentCount": 21,
  "dueDate": "2025-07-01",
  "description": "Kit M – Padrão – 21x"
}
```

**Fluxo interno**:

1. `findKitByTier("Padrão")` → kit com `systemKwp=17.25`, `panelCount=44`, `inverterKw=17.0`.
    
2. `calculateKitPrice(...)` → (44 × 800) + (17 × 2000) = 35 200 + 34 000 = 69 200.
    
3. `limitInstallments("MASTERCARD", 21)` → 21 (já dentro do limite).
    
4. Monta payload:
    
    ```jsonc
    {
      "customer": "cus_EXEMPLO_CLIENTE_M",
      "billingType": "CREDIT_CARD",
      "installmentCount": 21,
      "value": 69200.00,
      "dueDate": "2025-07-01",
      "description": "Kit M – Padrão – 21x (M – Padrão)",
      "externalReference": "M_Padrão_CHARGE_cus_EXEMPLO_CLIENTE_M",
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
    
5. O Asaas retornará JSON com dados da cobrança. Nosso endpoint retorna esse JSON junto com composição e preços.
    

#### 3.2. Criar cobrança “M – Moderado” com 15× em Elo

```bash
POST /m/create_charge
Host: localhost:3000
Content-Type: application/json

{
  "category": "M",
  "tier": "Moderado",
  "customer_id": "cus_EXEMPLO_CLIENTE_M",
  "creditCardBrand": "ELO",
  "creditCardToken": "tkn_EXEMPLO_TOKEN_CLIENTE",
  "installmentCount": 15,
  "dueDate": "2025-07-10",
  "description": "Kit M – Moderado – 15x"
}
```

**Fluxo interno**:

1. `findKitByTier("Moderado")` → kit com `systemKwp=21.75`, `panelCount=55`, `inverterKw=23.0`.
    
2. `calculateKitPrice(...)` → (55 × 800) + (23 × 2000) = 44 000 + 46 000 = 90 000.
    
3. `limitInstallments("ELO", 15)` → 12 (ajustado para 12, pois Elo não admite 15×).
    
4. Monta payload:
    
    ```jsonc
    {
      "customer": "cus_EXEMPLO_CLIENTE_M",
      "billingType": "CREDIT_CARD",
      "installmentCount": 12,          // ajustado
      "value": 90000.00,
      "dueDate": "2025-07-10",
      "description": "Kit M – Moderado – 12x (ajustado) (M – Moderado)",
      "externalReference": "M_Moderado_CHARGE_cus_EXEMPLO_CLIENTE_M",
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
    
5. O endpoint retorna JSON com composição, preços e resposta do Asaas.
    

---

### 4. Resumo Final dos Kits “M”

|Tier|systemKwp|panelCount|inverterKw|Painéis (R$)|Inversor (R$)|Total (R$)|
|---|---|---|---|---|---|---|
|Padrão|17,25|44|17,0|44 × 800 = 35 200|17 × 2 000 = 34 000|69 200|
|Consciente|19,50|49|20,0|49 × 800 = 39 200|20 × 2 000 = 40 000|79 200|
|Moderado|21,75|55|23,0|55 × 800 = 44 000|23 × 2 000 = 46 000|90 000|
|Acelerado|24,00|60|26,0|60 × 800 = 48 000|26 × 2 000 = 52 000|100 000|

- **Parcelamento**:
    
    - **Visa/Mastercard** → até 21×.
        
    - **Demais bandeiras** → até 12×.
        
- **Endpoints principais**:
    
    - `POST /m/create_charge` → cria cobrança parcelada no Asaas, aplicando regras de cálculo e limite de parcelas.
        
    - `GET /m/kits` → retorna lista de composições de kits “M” para cada tier.
        

---

Com esses dois templates (FastAPI e TypeScript/Express), você tem toda a base necessária para gerar endpoints de cobrança para **kits solares “M”**, garantindo que só Visa e Mastercard possam parcelar em até 21 vezes e que as demais bandeiras fiquem limitadas a 12 parcelas, exatamente conforme as políticas do Asaas.