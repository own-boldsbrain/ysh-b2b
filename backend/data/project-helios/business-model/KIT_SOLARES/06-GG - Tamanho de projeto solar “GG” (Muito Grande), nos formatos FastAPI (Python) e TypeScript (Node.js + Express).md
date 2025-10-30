A seguir estão os templates completos para o **tamanho de projeto solar “GG” (Muito Grande)**, nos formatos **FastAPI (Python)** e **TypeScript (Node.js + Express)**. Ambos incluem:

1. **Cálculo automático** dos valores (painéis + inversor) de cada tier de geração (“Padrão”, “Consciente”, “Moderado” e “Acelerado”).
    
2. **Limitação de parcelas** conforme bandeira do cartão: até **21× para Visa/Mastercard** e **12× para demais bandeiras**.
    
3. **Payload JSON de cobrança** para envio ao Asaas, contendo `installmentCount` ajustado.
    
4. Comentários detalhados em cada trecho de código, sem abreviações, para facilitar manutenção.
    

---

## 1. Informações Base para “GG” (Muito Grande)

- **averageKwp** (média de geração recomendada): **300,0 kWp**
    
- **Potência nominal de cada painel**: **400 Wp**
    
- **Preço por painel (400 Wp)**: **R$ 800,00**
    
- **Preço por inversor (por kW)**: **R$ 2 000,00**
    
- **Recomendações de inversor para “GG”**:
    
    - **Padrão** → 330 kW
        
    - **Consciente** → 380 kW
        
    - **Moderado** → 435 kW
        
    - **Acelerado** → 480 kW
        
- **Multiplicadores por tier**:
    
    - **Padrão** → 1.15
        
    - **Consciente** → 1.30
        
    - **Moderado** → 1.45
        
    - **Acelerado** → 1.60
        

### Como calcular cada kit “GG”:

1. **systemKwp** = 300 kWp × (multiplier).
    
2. **Carga total (Wp)** = systemKwp × 1 000.
    
3. **panelCount** = ceil((systemKwp × 1 000) / 400).
    
4. **Custo dos painéis** = panelCount × R$ 800.
    
5. **Custo do inversor** = inverterKw × R$ 2 000.
    
6. **Preço total do kit** = (custo painéis) + (custo inversor).
    

### Regras de parcelamento (Asaas):

- **Visa / Mastercard**: até **21 vezes**.
    
- **Demais bandeiras (Elo, Amex, Hipercard etc.)**: até **12 vezes**.
    

---

## 2. Cálculos Pré-Gerados para “GG”

|Tier|systemKwp (kWp)|Carga (Wp)|panelCount|inverterKw (kW)|Custo painéis (R$)|Custo inversor (R$)|Preço total (R$)|
|---|---|---|---|---|---|---|---|
|Padrão|345,00|345 000|863|330,0|863 × 800 = 690 400|330 × 2 000 = 660 000|1 350 400|
|Consciente|390,00|390 000|975|380,0|975 × 800 = 780 000|380 × 2 000 = 760 000|1 540 000|
|Moderado|435,00|435 000|1 088|435,0|1 088 × 800 = 870 400|435 × 2 000 = 870 000|1 740 400|
|Acelerado|480,00|480 000|1 200|480,0|1 200 × 800 = 960 000|480 × 2 000 = 960 000|1 920 000|

- **Cálculo de panelCount**:
    
    - Padrão: ceil(345 000 / 400) = 863 módulos.
        
    - Consciente: ceil(390 000 / 400) = 975 módulos.
        
    - Moderado: ceil(435 000 / 400) = 1 088 módulos.
        
    - Acelerado: ceil(480 000 / 400) = 1 200 módulos.
        

Estes valores já estão pré-calculados e serão carregados diretamente nos arrays abaixo.

---

## 3. Template em FastAPI (Python) para “GG”

```python
# fastapi_gg.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import httpx

app = FastAPI(
    title="API de Cobrança de Kit Solar GG",
    description=(
        "Este serviço calcula o valor do kit solar para projetos GG "
        "e cria a cobrança no Asaas, limitando em até 21 parcelas "
        "para Visa/Mastercard e até 12 parcelas para demais bandeiras."
    ),
    version="1.0.0"
)

#
# === 1) DEFINIÇÃO DOS DADOS DE COMPOSIÇÃO DO KIT GG ===
#

# 1.1) Tipos auxiliares para validação
ProjectCategory = Literal["GG"]                       # Somente "GG" neste template
GenerationTierName = Literal["Padrão", "Consciente", "Moderado", "Acelerado"]

class LossFactors(BaseModel):
    """
    Fatores de perda do sistema (%):
    - temperature: perda por temperatura (%)
    - shading: perda por sombreamento (%)
    - soiling: perda por sujeira/poeira (%)
    - mismatchLidDc: perda combinada (mismatch + LID + fios DC) (%)
    """
    temperature: float = Field(..., description="Perda por temperatura (%)")
    shading: float = Field(..., description="Perda por sombreamento (%)")
    soiling: float = Field(..., description="Perda por sujeira (%)")
    mismatchLidDc: float = Field(..., description="Perda mismatch/LID/DC (%)")

class SolarKitComponent(BaseModel):
    """
    Representa a composição do kit solar GG para um determinado tier:
    - category: sempre "GG"
    - tier: nível de geração (Padrão, Consciente, Moderado, Acelerado)
    - systemKwp: potência total projetada (pré-calculada)
    - panelWp: 400 Wp (módulo padrão)
    - panelCount: número de módulos necessários (pré-calculado)
    - inverterKw: potência recomendada do inversor em kW (pré-calculado)
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
PANEL_COST: float = 800.00              # R$ 800,00 por módulo de 400 Wp
INVERTER_COST_PER_KW: float = 2000.00   # R$ 2.000,00 por kW de inversor

# 1.3) Lista fixa das composições dos kits GG (pré-calculadas)
#
#   Valores obtidos a partir de:
#     averageKwp = 300,0 kWp
#     Multipliers: Padrão=1.15, Consciente=1.30, Moderado=1.45, Acelerado=1.60
#     Recomendações inversor (kW): 330.0, 380.0, 435.0, 480.0
#
generation_tiers: List[SolarKitComponent] = [
    # Tier Padrão: systemKwp = 300 × 1.15 = 345.00 kWp
    SolarKitComponent(
        category="GG",
        tier="Padrão",
        systemKwp=345.00,    # pré-calculado
        panelWp=400,
        panelCount=863,      # ceil(345 000 / 400) = 863 módulos
        inverterKw=330.0,    # recomendado pelo Asaas
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Consciente: systemKwp = 300 × 1.30 = 390.00 kWp
    SolarKitComponent(
        category="GG",
        tier="Consciente",
        systemKwp=390.00,
        panelWp=400,
        panelCount=975,      # ceil(390 000 / 400) = 975 módulos
        inverterKw=380.0,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Moderado: systemKwp = 300 × 1.45 = 435.00 kWp
    SolarKitComponent(
        category="GG",
        tier="Moderado",
        systemKwp=435.00,
        panelWp=400,
        panelCount=1088,     # ceil(435 000 / 400) = 1088 módulos
        inverterKw=435.0,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Acelerado: systemKwp = 300 × 1.60 = 480.00 kWp
    SolarKitComponent(
        category="GG",
        tier="Acelerado",
        systemKwp=480.00,
        panelWp=400,
        panelCount=1200,     # ceil(480 000 / 400) = 1200 módulos
        inverterKw=480.0,
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
    - category: deve ser "GG" (este template é específico para GG)
    - tier: um dos quatro níveis de geração (Padrão, Consciente, Moderado, Acelerado)
    - customer_id: ID do cliente já cadastrado no Asaas (ex.: "cus_ABC123xyz")
    - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO", "AMEX" etc.)
    - creditCardToken: token de cartão já obtido previamente (ex.: "tkn_abc123xyz")
    - installmentCount: número desejado de parcelas (int); será limitado conforme bandeira
    - dueDate: data de vencimento da primeira parcela no formato "AAAA-MM-DD"
    - description (opcional): texto livre para a cobrança; se não informado, usa padrão interno
    """
    category: ProjectCategory = Field(..., description='Categoria do projeto: "GG"')
    tier: GenerationTierName = Field(..., description="Tier de geração do kit")
    customer_id: str = Field(..., description="ID do cliente no Asaas")
    creditCardBrand: str = Field(..., description="Bandeira do cartão de crédito")
    creditCardToken: str = Field(..., description="Token do cartão já obtido")
    installmentCount: int = Field(..., description="Número de parcelas solicitado")
    dueDate: str = Field(..., description='Data de vencimento (formato "AAAA-MM-DD")')
    description: str = Field(
        default="Cobrança de Kit Solar GG",
        description="Descrição da cobrança; padrão se não informado"
    )

#
# === 3) PARÂMETROS DA API DO ASAAS ===
#

ASAAS_BASE_URL: str = "https://www.asaas.com/api/v3"
# Substitua por sua chave de API Asaas (token real de produção)
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
    Retorna a composição do kit GG para o tier informado.
    Se não encontrar, levanta HTTPException 404.
    """
    for kit in generation_tiers:
        if kit.tier == tier_name:
            return kit
    raise HTTPException(
        status_code=404,
        detail=f"Kit GG para o tier '{tier_name}' não encontrado."
    )

def calculate_kit_price(kit: SolarKitComponent) -> float:
    """
    Calcula o preço total do kit GG:
    - Custo dos painéis = panelCount × PANEL_COST
    - Custo do inversor = inverterKw × INVERTER_COST_PER_KW
    Retorna valor arredondado para duas casas decimais.
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
    Retorna o valor ajustado (não ultrapassa o máximo permitido).
    """
    brand_upper = brand.strip().upper()
    if brand_upper in ["VISA", "MASTERCARD"]:
        return min(requested_installments, 21)
    return min(requested_installments, 12)

#
# === 5) ENDPOINT FASTAPI: CRIAR COBRANÇA NO ASAAS PARA KIT GG ===
#

@app.post("/gg/create_charge")
async def create_gg_charge(request: ChargeRequest):
    # 5.1) Validar category == "GG"
    if request.category != "GG":
        raise HTTPException(
            status_code=400,
            detail="Esta rota só suporta projetos solares de tamanho 'GG'."
        )

    # 5.2) Buscar composição do kit GG para o tier solicitado
    kit = find_kit_for_tier(request.tier)

    # 5.3) Calcular preço total do kit (painéis + inversor)
    price_total = calculate_kit_price(kit)

    # 5.4) Ajustar número de parcelas conforme bandeira
    adjusted_installments = limit_installments(
        brand=request.creditCardBrand,
        requested_installments=request.installmentCount
    )

    # 5.5) Montar payload para envio ao Asaas
    asaas_payload = {
        "customer": request.customer_id,                 # ID do cliente no Asaas
        "billingType": "CREDIT_CARD",                    # Cobrança via cartão de crédito
        "installmentCount": adjusted_installments,       # Parcelas ajustadas
        "value": price_total,                            # Valor total do kit GG
        "dueDate": request.dueDate,                      # Data de vencimento da 1ª parcela
        "description": f"{request.description} (GG - {kit.tier})",
        "externalReference": f"GG_{kit.tier}_CHARGE_{request.customer_id}",
        "creditCard": {
            "creditCardToken": request.creditCardToken    # Token do cartão já obtido
        },
        "creditCardHolderInfo": {
            # Dados de titular de cartão (em produção, buscar no banco de dados)
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

    # 5.6) Enviar requisição ao Asaas para criar cobrança
    url = f"{ASAAS_BASE_URL}/payments?access_token={ASAAS_API_TOKEN}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=asaas_payload, headers=HEADERS)

    # 5.7) Verificar resposta do Asaas
    if response.status_code not in (200, 201):
        # Se houve erro (parcelamento não permitido, dados inválidos, etc.),
        # devolvemos o JSON de erro retornado pelo Asaas
        raise HTTPException(
            status_code=response.status_code,
            detail={"error": response.json()}
        )

    # 5.8) Retornar resultado completo ao cliente
    return {
        "kit_composition": kit.dict(),
        "price_total": price_total,
        "requested_installments": request.installmentCount,
        "adjusted_installments": adjusted_installments,
        "asaas_response": response.json()
    }

#
# === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO GG (APENAS CONSULTA) ===
#

@app.get("/gg/kits", response_model=List[SolarKitComponent])
async def list_gg_kits():
    """
    Retorna a lista completa de composições de kit GG para os 4 tiers:
    - Útil para front-ends que queiram exibir as opções de tier ao usuário.
    """
    return generation_tiers
```

### Explicação do Código FastAPI para “GG”

1. **Composição do Kit GG (seção 1)**
    
    - Declaração de `generation_tiers`, lista com quatro instâncias de `SolarKitComponent`, uma para cada tier.
        
    - Cada componente contém:
        
        - `category`: sempre `"GG"`.
            
        - `tier`: `"Padrão"`, `"Consciente"`, `"Moderado"` ou `"Acelerado"`.
            
        - `systemKwp`: valor pré-calculado (por ex., 345.00 kWp para “Padrão”).
            
        - `panelWp`: potência nominal do módulo (400 Wp).
            
        - `panelCount`: número de módulos (863, 975, 1088, 1200).
            
        - `inverterKw`: potência do inversor em kW (330.0, 380.0, 435.0, 480.0).
            
        - `lossFactors`: informativos (4 %, 3 %, 3 %, 4 %).
            
2. **Modelo de requisição `ChargeRequest` (seção 2)**
    
    - Espera receber no JSON:
        
        - `category`: `"GG"`
            
        - `tier`: `"Padrão" | "Consciente" | "Moderado" | "Acelerado"`
            
        - `customer_id`: string (ID do cliente Asaas)
            
        - `creditCardBrand`: string (bandeira do cartão)
            
        - `creditCardToken`: string (token do cartão)
            
        - `installmentCount`: integer (número de parcelas solicitadas)
            
        - `dueDate`: string (formato `"AAAA-MM-DD"`)
            
        - `description`: string opcional (padrão `"Cobrança de Kit Solar GG"`)
            
3. **Funções auxiliares (seção 4)**
    
    - `find_kit_for_tier(tier_name)`: busca o objeto em `generation_tiers` cujo `tier` corresponda a `tier_name`. Se não encontrar, lança `HTTPException(status_code=404)`.
        
    - `calculate_kit_price(kit)`: calcula `(kit.panelCount × 800) + (kit.inverterKw × 2000)`, retorna valor arredondado a duas casas.
        
    - `limit_installments(brand, requested_installments)`:
        
        - Se `brand` for `"VISA"` ou `"MASTERCARD"`, retorna `min(requested_installments, 21)`.
            
        - Caso contrário, retorna `min(requested_installments, 12)`.
            
4. **Endpoint `/gg/create_charge` (seção 5)**
    
    - Verifica se `request.category == "GG"`. Se não, retorna `HTTPException(400)`.
        
    - Recupera o `kit` usando `find_kit_for_tier(request.tier)`.
        
    - Calcula `price_total = calculate_kit_price(kit)`.
        
    - Ajusta `installmentCount` com `limit_installments(request.creditCardBrand, request.installmentCount)`.
        
    - Monta o JSON `asaas_payload` com:
        
        - `customer`: ID do cliente.
            
        - `billingType`: `"CREDIT_CARD"`.
            
        - `installmentCount`: parcelas ajustadas.
            
        - `value`: valor total calculado.
            
        - `dueDate`: data de vencimento da 1ª parcela.
            
        - `description`: concatenação do texto padrão ou fornecido + “(GG – )”.
            
        - `externalReference`: string de controle, ex.: `"GG_Padrão_CHARGE_<customer_id>"`.
            
        - `creditCard`: com `creditCardToken`.
            
        - `creditCardHolderInfo`: dados fixos do titular do cartão (substituir por dados reais em produção).
            
    - Faz `POST` a `https://www.asaas.com/api/v3/payments?access_token=<token>`.
        
    - Se Asaas retornar código diferente de 200 ou 201, devolve `HTTPException` com corpo de erro.
        
    - Em sucesso, retorna JSON com:
        
        ```json
        {
          "kit_composition": { ...dados do kit GG... },
          "price_total": <valor>,
          "requested_installments": <int>,
          "adjusted_installments": <int>,
          "asaas_response": { ...JSON Asaas completo... }
        }
        ```
        
5. **Endpoint `/gg/kits` (seção 6)**
    
    - Retorna o array `generation_tiers`, com as quatro composições de kit “GG”.
        

---

## 4. Template em TypeScript (Node.js + Express) para “GG”

```typescript
// server_gg.ts

import express, { Request, Response } from "express";
import axios from "axios";
import { body, validationResult } from "express-validator";

const app = express();
app.use(express.json());

/**
 * === 1) TIPOS E DADOS DE COMPOSIÇÃO DO KIT GG ===
 *
 * Cada objeto representa um tier de geração com dados pré-calculados:
 * - systemKwp: potência total (kWp)
 * - panelCount: quantidade de módulos de 400 Wp
 * - inverterKw: potência do inversor (kW)
 */

type ProjectCategory = "GG"; // Apenas "GG" é aceito aqui
type GenerationTierName = "Padrão" | "Consciente" | "Moderado" | "Acelerado";

interface LossFactors {
  /** Perda por temperatura (%) */
  temperature: number;
  /** Perda por sombreamento (%) */
  shading: number;
  /** Perda por sujeira (%) */
  soiling: number;
  /** Perda combinada mismatch/LID/DC (%) */
  mismatchLidDc: number;
}

interface SolarKitComponent {
  category: ProjectCategory;
  tier: GenerationTierName;
  systemKwp: number;
  panelWp: number;
  panelCount: number;
  inverterKw: number;
  lossFactors: LossFactors;
}

// 1.1) Custos unitários
const PANEL_COST: number = 800.0;            // R$ 800,00 por módulo de 400 Wp
const INVERTER_COST_PER_KW: number = 2000.0; // R$ 2 000,00 por kW de inversor

// 1.2) Array fixo de composições para GG
//     averageKwp = 300,0 kWp
//     Multipliers: 1.15, 1.30, 1.45, 1.60
//     Recomendações de inversor: 330.0, 380.0, 435.0, 480.0
const ggKits: SolarKitComponent[] = [
  {
    category: "GG",
    tier: "Padrão",
    systemKwp: parseFloat((300.0 * 1.15).toFixed(2)), // 345.00 kWp
    panelWp: 400,
    panelCount: 863,        // ceil(345 000 / 400) = 863
    inverterKw: 330.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "GG",
    tier: "Consciente",
    systemKwp: parseFloat((300.0 * 1.30).toFixed(2)), // 390.00 kWp
    panelWp: 400,
    panelCount: 975,        // ceil(390 000 / 400) = 975
    inverterKw: 380.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "GG",
    tier: "Moderado",
    systemKwp: parseFloat((300.0 * 1.45).toFixed(2)), // 435.00 kWp
    panelWp: 400,
    panelCount: 1088,       // ceil(435 000 / 400) = 1088
    inverterKw: 435.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "GG",
    tier: "Acelerado",
    systemKwp: parseFloat((300.0 * 1.60).toFixed(2)), // 480.00 kWp
    panelWp: 400,
    panelCount: 1200,       // ceil(480 000 / 400) = 1200
    inverterKw: 480.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  }
];

/**
 * === 2) TIPOS E VALIDAÇÕES PARA O BODY DE COBRANÇA ===
 *
 * O front-end deve enviar um JSON contendo:
 * - category: "GG"
 * - tier: "Padrão" | "Consciente" | "Moderado" | "Acelerado"
 * - customer_id: ID do cliente no Asaas (string)
 * - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO")
 * - creditCardToken: token JWT do cartão (string)
 * - installmentCount: número de parcelas (int)
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
  description?: string;   // Opcional
}

/**
 * === 3) PARÂMETROS DA API DO ASAAS ===
 *
 * - ASAAS_BASE_URL: endpoint base da Asaas em produção
 * - ASAAS_API_TOKEN: token real fornecido pela Asaas
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
 * Retorna a composição do kit GG para o tier informado.
 * Se não encontrar, retorna undefined.
 */
function findKitByTier(tierName: GenerationTierName): SolarKitComponent | undefined {
  return ggKits.find(kit => kit.tier === tierName);
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
 * Limita o número de parcelas conforme bandeira:
 * - Visa ou Mastercard:até 21×
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
 * Valida se string está no formato YYYY-MM-DD
 */
function isValidDate(dateString: string): boolean {
  const isoPattern = /^\d{4}-\d{2}-\d{2}$/;
  return isoPattern.test(dateString);
}

/**
 * Regras de validação usando express-validator
 */
const chargeValidationRules = [
  body("category")
    .equals("GG").withMessage("category deve ser 'GG'"),
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
 * === 5) ENDPOINT Express: CRIAR COBRANÇA NO ASAAS PARA KIT GG ===
 */
app.post(
  "/gg/create_charge",
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
      description = "Cobrança de Kit Solar GG"
    } = req.body as ChargeRequest;

    // 5.3) Garantir que category seja "GG"
    if (category !== "GG") {
      return res.status(400).json({
        error: "Para este endpoint, a categoria deve ser 'GG'."
      });
    }

    // 5.4) Buscar composição do kit GG para o tier solicitado
    const kit = findKitByTier(tier);
    if (!kit) {
      return res.status(404).json({
        error: `Não encontramos nenhum kit GG para o tier '${tier}'.`
      });
    }

    // 5.5) Calcular preço total: módulos + inversor
    const priceTotal = calculateKitPrice(kit);

    // 5.6) Ajustar número de parcelas conforme bandeira
    const adjustedInstallments = limitInstallments(creditCardBrand, installmentCount);

    // 5.7) Montar payload JSON para a API Asaas
    const asaasPayload = {
      customer: customer_id,                       // ID do cliente no Asaas
      billingType: "CREDIT_CARD",                  // Cobrança via cartão de crédito
      installmentCount: adjustedInstallments,      // Parcelas ajustadas
      value: priceTotal,                           // Preço total do kit GG
      dueDate: dueDate,                            // Data de vencimento da 1ª parcela
      description: `${description} (GG - ${kit.tier})`,
      externalReference: `GG_${kit.tier}_CHARGE_${customer_id}`,
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

    // 5.8) Chamar API Asaas para criar cobrança
    try {
      const asaasUrl = `${ASAAS_BASE_URL}/payments?access_token=${ASAAS_API_TOKEN}`;
      const response = await axios.post(asaasUrl, asaasPayload, { headers: HEADERS });

      // 5.9) Se sucesso, retornar dados ao cliente
      return res.status(201).json({
        kit_composition: kit,
        price_total: priceTotal,
        requested_installments: installmentCount,
        adjusted_installments: adjustedInstallments,
        asaas_response: response.data
      });
    } catch (error: any) {
      // Se Asaas retornar erro, repassar o código e JSON de erro
      if (error.response && error.response.data) {
        return res.status(error.response.status).json({ error: error.response.data });
      }
      // Caso contrário (erro interno), retornar erro 500
      return res.status(500).json({ error: "Erro interno ao chamar a API Asaas." });
    }
  }
);

/**
 * === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO GG (APENAS CONSULTA) ===
 *
 * GET /gg/kits retorna lista completa dos kits GG (4 tiers),
 * permitindo ao front-end exibir as opções disponíveis ao usuário.
 */
app.get("/gg/kits", (req: Request, res: Response) => {
  return res.json(ggKits);
});

// Inicia servidor na porta 3000 (ou variável de ambiente PORT)
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

### Explicação do Código TypeScript para “GG”

1. **Declaração de tipos e array `ggKits` (seção 1)**
    
    - Cada objeto em `ggKits` contém:
        
        - `category`: **"GG"**
            
        - `tier`: **"Padrão"**, **"Consciente"**, **"Moderado"** ou **"Acelerado"**
            
        - `systemKwp`: potência total em kWp (345.00, 390.00, 435.00, 480.00)
            
        - `panelWp`: **400** (Wp por módulo)
            
        - `panelCount`: quantidade de módulos (863, 975, 1088, 1200)
            
        - `inverterKw`: potência do inversor (330.0, 380.0, 435.0, 480.0)
            
        - `lossFactors`: valores informativos (4 %, 3 %, 3 %, 4 %)
            
2. **Modelo de requisição `ChargeRequest` (seção 2)**
    
    - Campos esperados no JSON enviado pelo front-end:
        
        - `category`: **"GG"**
            
        - `tier`: **"Padrão" | "Consciente" | "Moderado" | "Acelerado"**
            
        - `customer_id`: string (ID do cliente Asaas)
            
        - `creditCardBrand`: string (bandeira do cartão)
            
        - `creditCardToken`: string (token do cartão)
            
        - `installmentCount`: integer (parcelas solicitadas)
            
        - `dueDate`: string no formato `"AAAA-MM-DD"`
            
        - `description`: string opcional
            
3. **Funções auxiliares (seção 4)**
    
    - `findKitByTier(tierName)`: retorna o objeto cujo campo `tier` bate com `tierName`, ou `undefined` se não existir.
        
    - `calculateKitPrice(kit)`: executa `(kit.panelCount × 800) + (kit.inverterKw × 2000)`, arredonda para duas casas.
        
    - `limitInstallments(brand, requested)`:
        
        - Se `brand` é `"VISA"` ou `"MASTERCARD"`, retorna `min(requested, 21)`.
            
        - Senão, retorna `min(requested, 12)`.
            
    - `isValidDate(dateString)`: valida o formato `"YYYY-MM-DD"` via regex.
        
4. **Endpoint `POST /gg/create_charge` (seção 5)**
    
    - Aplica validações com `express-validator`:
        
        - `category` deve ser `"GG"`.
            
        - `tier` deve estar entre as quatro opções.
            
        - `customer_id`, `creditCardBrand`, `creditCardToken` devem ser strings.
            
        - `installmentCount` deve ser inteiro > 0.
            
        - `dueDate` deve obedecer ao padrão `"YYYY-MM-DD"`.
            
        - `description` é opcional, mas se informado deve ser string.
            
    - Se houver falhas de validação, retorna `400 Bad Request` com a lista de erros.
        
    - Verifica se `category === "GG"`; caso contrário, devolve `400`.
        
    - Busca o `kit` correspondente via `findKitByTier(tier)`; se não achar, devolve `404`.
        
    - Calcula `priceTotal = calculateKitPrice(kit)`.
        
    - Ajusta `installmentCount` usando `limitInstallments(creditCardBrand, installmentCount)`.
        
    - Monta `asaasPayload` com:
        
        ```jsonc
        {
          "customer": "<customer_id>",
          "billingType": "CREDIT_CARD",
          "installmentCount": <adjustedInstallments>,
          "value": <priceTotal>,
          "dueDate": "<dueDate>",
          "description": "<description> (GG – <tier>)",
          "externalReference": "GG_<tier>_CHARGE_<customer_id>",
          "creditCard": {
            "creditCardToken": "<creditCardToken>"
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
        
    - Executa `POST` em `https://www.asaas.com/api/v3/payments?access_token=<ASAAS_API_TOKEN>` com o payload JSON.
        
    - Se Asaas retornar status diferente de `200` ou `201`, responde com o JSON de erro e o mesmo código de status.
        
    - Se sucesso, responde `201 Created` com:
        
        ```json
        {
          "kit_composition": { ...dados do kit GG... },
          "price_total": <valor calculado>,
          "requested_installments": <int solicitado>,
          "adjusted_installments": <int ajustado>,
          "asaas_response": { ...JSON completo retornado pelo Asaas... }
        }
        ```
        
5. **Endpoint `GET /gg/kits` (seção 6)**
    
    - Retorna `ggKits`, permitindo ao front-end exibir as quatro opções de kit “GG”.
        

---

## 5. Resumo dos Valores para “GG”

|Tier|systemKwp|panelCount|inverterKw|Custo painéis (R$)|Custo inversor (R$)|Total (R$)|
|---|---|---|---|---|---|---|
|Padrão|345 kWp|863|330 kW|863 × 800 = 690 400|330 × 2 000 = 660 000|1 350 400|
|Consciente|390 kWp|975|380 kW|975 × 800 = 780 000|380 × 2 000 = 760 000|1 540 000|
|Moderado|435 kWp|1 088|435 kW|1 088 × 800 = 870 400|435 × 2 000 = 870 000|1 740 400|
|Acelerado|480 kWp|1 200|480 kW|1 200 × 800 = 960 000|480 × 2 000 = 960 000|1 920 000|

- **Cálculo de panelCount**:
    
    - Padrão: ceil(345 000 / 400) = 863.
        
    - Consciente: ceil(390 000 / 400) = 975.
        
    - Moderado: ceil(435 000 / 400) = 1 088.
        
    - Acelerado: ceil(480 000 / 400) = 1 200.
        
- **Parcelamento**:
    
    - **Visa/Mastercard** ≤ 21×.
        
    - **Demais bandeiras** ≤ 12×.
        

Com estes dois templates (FastAPI e TypeScript/Express), você tem a estrutura completa para gerar endpoints de cobrança para **kits solares “GG”**, assegurando que as regras de parcelamento do Asaas sejam rigorosamente aplicadas.