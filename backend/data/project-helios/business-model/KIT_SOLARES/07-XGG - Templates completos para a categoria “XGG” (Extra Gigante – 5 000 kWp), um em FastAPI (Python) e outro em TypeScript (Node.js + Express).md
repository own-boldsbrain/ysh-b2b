Abaixo seguem dois templates completos para a categoria **“XGG” (Extra Gigante – 5 000 kWp)**, um em **FastAPI (Python)** e outro em **TypeScript (Node.js + Express)**. Ambos utilizam a **chave de API real** fornecida anteriormente e incluem:

1. **Composição de kits “XGG”** para cada um dos quatro tiers de geração (“Padrão”, “Consciente”, “Moderado” e “Acelerado”), com valores pré-calculados de potenciais, número de módulos e inversores recomendados.
    
2. **Cálculo de preço** (módulos + inversor) baseado em:
    
    - R$ 800,00 por módulo de 400 Wp
        
    - R$ 2 000,00 por kW de inversor
        
3. **Lógica de limitação de parcelas**: até **21× para Visa/Mastercard** e até **12× para demais bandeiras** (Elo, Amex, Hipercard etc.).
    
4. **Endpoints**:
    
    - `POST /xgg/create_charge` → cria cobrança no Asaas usando o payload completo, retornando composição do kit, preço, parcelas solicitadas/ajustadas e resposta da Asaas.
        
    - `GET /xgg/kits` → retorna lista completa de composições de kits “XGG” (4 tiers).
        

A chave de API (token) utilizada em ambos os exemplos é a seguinte (conforme histórico de conversa):

```
$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjVjNWI5MGFmLTk2NTMtNGY5Zi1iZTM1LWMxMTFkZDg0NDkxNjo6JGFhY2hfYzRhYmUyZWYtMmU0Zi00NDYwLWFjOWEtMzRjMjEwNDhiZmE2
```

---

## 1. Dados Pré-Calculados para “XGG” (Extra Gigante)

- **AverageKwp**: 5 000 kWp
    
- **Potência de cada painel**: 400 Wp
    
- **Custo por módulo de 400 Wp**: R$ 800,00
    
- **Custo por kW de inversor**: R$ 2 000,00
    
- **Multiplicadores (tiers)**:
    
    - Padrão → 1.15
        
    - Consciente → 1.30
        
    - Moderado → 1.45
        
    - Acelerado → 1.60
        
- **Potências de inversor recomendadas (kW)**:
    
    - Padrão → 5 500 kW
        
    - Consciente → 6 300 kW
        
    - Moderado → 7 250 kW
        
    - Acelerado → 8 000 kW
        

A seguir, a tabela já com todos os valores pré-calculados:

|Tier|systemKwp (kWp)|Carga (Wp)|panelCount|inverterKw (kW)|Custo painéis (R$)|Custo inversor (R$)|Preço total (R$)|
|---|---|---|---|---|---|---|---|
|Padrão|5 750|5 750 000|14 375 → 14 375/400 = 14 375 módulos? (Ajustar abaixo)|5 500|14 375 × 800 = 11 500 000|5 500 × 2 000 = 11 000 000|22 500 000|
|Consciente|6 500|6 500 000|16 250 → 16 250/400 = 16 250 módulos? (Ajustar abaixo)|6 300|16 250 × 800 = 13 000 000|6 300 × 2 000 = 12 600 000|25 600 000|
|Moderado|7 250|7 250 000|18 125 → 18 125/400 = 18 125 módulos? (Ajustar abaixo)|7 250|18 125 × 800 = 14 500 000|7 250 × 2 000 = 14 500 000|29 000 000|
|Acelerado|8 000|8 000 000|20 000 → 20 000/400 = 20 000 módulos? (Ajustar abaixo)|8 000|20 000 × 800 = 16 000 000|8 000 × 2 000 = 16 000 000|32 000 000|

> **Observação sobre panelCount**:
> 
> - Na prática, cada **systemKwp × 1 000 / 400** dá um valor exato quando é múltiplo de 400; caso contrário, arredonda-se sempre para **cima** (função `ceil`).
>     
> - Nos exemplos abaixo, mantivemos panelCount como múltiplos exatos para facilitar (ex.: 5 750 000 / 400 = 14 375 módulos).
>     
> - Se precisar de arredondamento, basta aplicar `ceil((systemKwp × 1 000) / 400)` para obter um número inteiro.
>     

---

## 2. Template em FastAPI (Python) para “XGG”

```python
# fastapi_xgg.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import httpx

app = FastAPI(
    title="API de Cobrança de Kit Solar XGG",
    description=(
        "Este serviço calcula o valor do kit solar para projetos XGG "
        "e cria a cobrança no Asaas, limitando em até 21 parcelas "
        "para Visa/Mastercard e até 12 parcelas para demais bandeiras."
    ),
    version="1.0.0"
)

#
# === 1) DEFINIÇÃO DOS DADOS DE COMPOSIÇÃO DO KIT XGG ===
#

# 1.1) Tipos auxiliares
ProjectCategory = Literal["XGG"]                       # Apenas "XGG" neste módulo
GenerationTierName = Literal["Padrão", "Consciente", "Moderado", "Acelerado"]

class LossFactors(BaseModel):
    """
    Fatores de perda do sistema (%):
    - temperature: perda por temperatura (%)
    - shading: perda por sombreamento (%)
    - soiling: perda por sujeira/poeira (%)
    - mismatchLidDc: perda combinada (mismatch + LID + fios DC) (%)
    """
    temperature: float = Field(
        ...,
        description="Perda de potência por temperatura (%)"
    )
    shading: float = Field(
        ...,
        description="Perda de potência por sombreamento (%)"
    )
    soiling: float = Field(
        ...,
        description="Perda de potência por sujeira/poeira (%)"
    )
    mismatchLidDc: float = Field(
        ...,
        description="Perda de potência mismatch + LID + fios DC (%)"
    )

class SolarKitComponent(BaseModel):
    """
    Representa a composição do kit solar XGG para um determinado tier:
    - category: sempre "XGG"
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

# 1.3) Lista fixa com as composições dos kits XGG (4 tiers)
#
#   Valores calculados a partir de:
#     averageKwp = 5 000 kWp
#     Multipliers: Padrão=1.15, Consciente=1.30, Moderado=1.45, Acelerado=1.60
#     Potências de inversor (kW): 5 500.0, 6 300.0, 7 250.0, 8 000.0
#   Cálculo de panelCount: 
#     ceil((systemKwp × 1 000) / 400) 
#     (aqui todos já resultam em múltiplos exatos para evitar arredondamentos)
generation_tiers: List[SolarKitComponent] = [
    # Tier Padrão: systemKwp = 5 000 × 1.15 = 5 750.00 kWp
    SolarKitComponent(
        category="XGG",
        tier="Padrão",
        systemKwp=5750.00,     # pré-calculado
        panelWp=400,
        panelCount=14375,      # ceil(5 750 000 / 400) = 14 375 módulos
        inverterKw=5500.0,      # recomendado pelo Asaas
        lossFactors=LossFactors(
            temperature=4.0,
            shading=3.0,
            soiling=3.0,
            mismatchLidDc=4.0
        )
    ),
    # Tier Consciente: systemKwp = 5 000 × 1.30 = 6 500.00 kWp
    SolarKitComponent(
        category="XGG",
        tier="Consciente",
        systemKwp=6500.00,
        panelWp=400,
        panelCount=16250,      # ceil(6 500 000 / 400) = 16 250 módulos
        inverterKw=6300.0,
        lossFactors=LossFactors(
            temperature=4.0,
            shading=3.0,
            soiling=3.0,
            mismatchLidDc=4.0
        )
    ),
    # Tier Moderado: systemKwp = 5 000 × 1.45 = 7 250.00 kWp
    SolarKitComponent(
        category="XGG",
        tier="Moderado",
        systemKwp=7250.00,
        panelWp=400,
        panelCount=18125,      # ceil(7 250 000 / 400) = 18 125 módulos
        inverterKw=7250.0,
        lossFactors=LossFactors(
            temperature=4.0,
            shading=3.0,
            soiling=3.0,
            mismatchLidDc=4.0
        )
    ),
    # Tier Acelerado: systemKwp = 5 000 × 1.60 = 8 000.00 kWp
    SolarKitComponent(
        category="XGG",
        tier="Acelerado",
        systemKwp=8000.00,
        panelWp=400,
        panelCount=20000,      # ceil(8 000 000 / 400) = 20 000 módulos
        inverterKw=8000.0,
        lossFactors=LossFactors(
            temperature=4.0,
            shading=3.0,
            soiling=3.0,
            mismatchLidDc=4.0
        )
    )
]

#
# === 2) MODELO DE REQUISIÇÃO (INPUT) PARA O ENDPOINT DE COBRANÇA ===
#

class ChargeRequest(BaseModel):
    """
    Campos esperados no body da requisição para criar cobrança:
    - category: deve ser "XGG" (este template é específico para XGG)
    - tier: um dos quatro níveis de geração (Padrão, Consciente, Moderado, Acelerado)
    - customer_id: ID do cliente já cadastrado no Asaas (ex.: "cus_ABC123xyz")
    - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO", "AMEX" etc.)
    - creditCardToken: token de cartão já obtido previamente (ex.: "tkn_abc123xyz")
    - installmentCount: número desejado de parcelas (int); será limitado conforme bandeira
    - dueDate: data de vencimento da primeira parcela no formato "AAAA-MM-DD"
    - description (opcional): texto livre para a cobrança; se não informado, usa padrão interno
    """
    category: ProjectCategory = Field(..., description='Categoria do projeto: "XGG"')
    tier: GenerationTierName = Field(..., description="Tier de geração desejado para cálculo do kit")
    customer_id: str = Field(..., description="ID do cliente no Asaas, ex.: 'cus_ABC123xyz'")
    creditCardBrand: str = Field(..., description="Bandeira do cartão, ex.: 'VISA', 'MASTERCARD', 'ELO'")
    creditCardToken: str = Field(..., description="Token do cartão já gerado, ex.: 'tkn_abc123xyz'")
    installmentCount: int = Field(..., description="Número de parcelas solicitado pelo cliente")
    dueDate: str = Field(..., description='Data de vencimento da primeira parcela no formato "AAAA-MM-DD"')
    description: str = Field(
        default="Cobrança de Kit Solar XGG",
        description="Descrição da cobrança; padrão se não informado"
    )

#
# === 3) PARÂMETROS DA API DO ASAAS ===
#

ASAAS_BASE_URL: str = "https://www.asaas.com/api/v3"
# Chave de API real (token de produção), conforme histórico de conversa
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
    Retorna a composição do kit XGG para o tier informado.
    Se não encontrar, levanta HTTPException 404.
    """
    for kit in generation_tiers:
        if kit.tier == tier_name:
            return kit
    raise HTTPException(
        status_code=404,
        detail=f"Kit XGG para o tier '{tier_name}' não encontrado."
    )

def calculate_kit_price(kit: SolarKitComponent) -> float:
    """
    Calcula o preço total do kit XGG:
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
# === 5) ENDPOINT FASTAPI: CRIAR COBRANÇA NO ASAAS PARA KIT XGG ===
#

@app.post("/xgg/create_charge")
async def create_xgg_charge(request: ChargeRequest):
    # 5.1) Validar que category == "XGG"
    if request.category != "XGG":
        raise HTTPException(
            status_code=400,
            detail="Esta rota só suporta projetos solares de tamanho 'XGG'."
        )

    # 5.2) Buscar composição do kit XGG para o tier solicitado
    kit = find_kit_for_tier(request.tier)

    # 5.3) Calcular preço total do kit (painéis + inversor)
    price_total = calculate_kit_price(kit)

    # 5.4) Ajustar installmentCount conforme bandeira
    adjusted_installments = limit_installments(
        brand=request.creditCardBrand,
        requested_installments=request.installmentCount
    )

    # 5.5) Montar payload JSON para a API Asaas
    asaas_payload = {
        "customer": request.customer_id,                 # ID do cliente Asaas
        "billingType": "CREDIT_CARD",                    # Cobrança via cartão
        "installmentCount": adjusted_installments,       # Parcelas ajustadas
        "value": price_total,                            # Valor total do kit XGG
        "dueDate": request.dueDate,                      # Data de vencimento da 1ª parcela
        "description": f"{request.description} (XGG - {kit.tier})",
        "externalReference": f"XGG_{kit.tier}_CHARGE_{request.customer_id}",
        "creditCard": {
            "creditCardToken": request.creditCardToken    # Token do cartão já obtido
        },
        "creditCardHolderInfo": {
            # Dados de titular de cartão (em produção, buscar do banco de dados)
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

    # 5.7) Tratar resposta do Asaas
    if response.status_code not in (200, 201):
        # Em caso de erro (parcelamento acima do permitido, dados inválidos etc.),
        # devolve o JSON de erro retornado pelo Asaas
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
# === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO XGG (APENAS CONSULTA) ===
#

@app.get("/xgg/kits", response_model=List[SolarKitComponent])
async def list_xgg_kits():
    """
    Retorna a lista completa de composições de kit XGG para os 4 tiers:
    - Útil para front-ends exibirem as opções disponíveis ao usuário.
    """
    return generation_tiers
```

---

## 3. Template em TypeScript (Node.js + Express) para “XGG”

```typescript
// server_xgg.ts

import express, { Request, Response } from "express";
import axios from "axios";
import { body, validationResult } from "express-validator";

const app = express();
app.use(express.json());

/**
 * === 1) TIPOS E DADOS DE COMPOSIÇÃO DO KIT XGG ===
 *
 * Cada objeto representa um tier de geração com dados pré-calculados:
 * - systemKwp: potência total (kWp)
 * - panelCount: quantidade de módulos de 400 Wp
 * - inverterKw: potência do inversor (kW)
 */
type ProjectCategory = "XGG"; // Apenas "XGG" é aceito aqui
type GenerationTierName = "Padrão" | "Consciente" | "Moderado" | "Acelerado";

interface LossFactors {
  /** Perda por temperatura (%) */
  temperature: number;
  /** Perda por sombreamento (%) */
  shading: number;
  /** Perda por sujeira (%) */
  soiling: number;
  /** Perda combinada (mismatch + LID + fios DC) (%) */
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

// 1.1) Custos unitários (ajustar conforme cenário real)
const PANEL_COST: number = 800.0;            // R$ 800,00 por módulo de 400 Wp
const INVERTER_COST_PER_KW: number = 2000.0; // R$ 2 000,00 por kW de inversor

// 1.2) Array fixo das composições dos kits XGG (4 tiers)
//     averageKwp = 5 000 kWp
//     Multipliers: 1.15, 1.30, 1.45, 1.60
//     Potências de inversor (kW): 5 500.0, 6 300.0, 7 250.0, 8 000.0
//     Cálculo de panelCount: ceil((systemKwp × 1 000) / 400)
const xggKits: SolarKitComponent[] = [
  {
    category: "XGG",
    tier: "Padrão",
    systemKwp: parseFloat((5000.0 * 1.15).toFixed(2)), // 5 750.00 kWp
    panelWp: 400,
    panelCount: 14375,       // ceil(5 750 000 / 400) = 14 375 módulos
    inverterKw: 5500.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "XGG",
    tier: "Consciente",
    systemKwp: parseFloat((5000.0 * 1.30).toFixed(2)), // 6 500.00 kWp
    panelWp: 400,
    panelCount: 16250,       // ceil(6 500 000 / 400) = 16 250 módulos
    inverterKw: 6300.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "XGG",
    tier: "Moderado",
    systemKwp: parseFloat((5000.0 * 1.45).toFixed(2)), // 7 250.00 kWp
    panelWp: 400,
    panelCount: 18125,       // ceil(7 250 000 / 400) = 18 125 módulos
    inverterKw: 7250.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "XGG",
    tier: "Acelerado",
    systemKwp: parseFloat((5000.0 * 1.60).toFixed(2)), // 8 000.00 kWp
    panelWp: 400,
    panelCount: 20000,       // ceil(8 000 000 / 400) = 20 000 módulos
    inverterKw: 8000.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  }
];

/**
 * === 2) TIPOS E VALIDAÇÕES PARA O BODY DE COBRANÇA ===
 *
 * O front-end deve enviar um JSON contendo:
 * - category: "XGG"
 * - tier: "Padrão" | "Consciente" | "Moderado" | "Acelerado"
 * - customer_id: ID do cliente Asaas (string)
 * - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO")
 * - creditCardToken: token JWT do cartão (string)
 * - installmentCount: número de parcelas (int)
 * - dueDate: data de vencimento (AAAA-MM-DD)
 * - description (opcional): texto livre para descrição da cobrança
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
 * - ASAAS_BASE_URL: endpoint base em produção
 * - ASAAS_API_TOKEN: token real fornecido pela Asaas
 * - HEADERS: cabeçalhos padrão para JSON
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
 * Retorna a composição do kit XGG para o tier informado.
 * Se não encontrar, retorna undefined.
 */
function findKitByTier(tierName: GenerationTierName): SolarKitComponent | undefined {
  return xggKits.find(kit => kit.tier === tierName);
}

/**
 * Calcula o preço total do kit:
 * (quantidade de módulos × custo de módulo) + (potência do inversor (kW) × custo por kW)
 */
function calculateKitPrice(kit: SolarKitComponent): number {
  const pricePanels = kit.panelCount * PANEL_COST;
  const priceInverter = kit.inverterKw * INVERTER_COST_PER_KW;
  return parseFloat((pricePanels + priceInverter).toFixed(2));
}

/**
 * Limita o número de parcelas conforme bandeira:
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
    .equals("XGG").withMessage("category deve ser 'XGG'"),
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
 * === 5) ENDPOINT Express: CRIAR COBRANÇA NO ASAAS PARA KIT XGG ===
 */
app.post(
  "/xgg/create_charge",
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
      description = "Cobrança de Kit Solar XGG"
    } = req.body as ChargeRequest;

    // 5.3) Garantir que category seja "XGG"
    if (category !== "XGG") {
      return res.status(400).json({
        error: "Para este endpoint, a categoria deve ser 'XGG'."
      });
    }

    // 5.4) Buscar composição do kit XGG para o tier solicitado
    const kit = findKitByTier(tier);
    if (!kit) {
      return res.status(404).json({
        error: `Não encontramos nenhum kit XGG para o tier '${tier}'.`
      });
    }

    // 5.5) Calcular preço total: (módulos + inversor)
    const priceTotal = calculateKitPrice(kit);

    // 5.6) Ajustar installmentCount conforme bandeira
    const adjustedInstallments = limitInstallments(creditCardBrand, installmentCount);

    // 5.7) Montar payload JSON para a API Asaas
    const asaasPayload = {
      customer: customer_id,                       // ID do cliente no Asaas
      billingType: "CREDIT_CARD",                  // Cobrança via cartão de crédito
      installmentCount: adjustedInstallments,      // Parcelas ajustadas
      value: priceTotal,                           // Valor total do kit XGG
      dueDate: dueDate,                            // Data de vencimento da 1ª parcela
      description: `${description} (XGG - ${kit.tier})`,
      externalReference: `XGG_${kit.tier}_CHARGE_${customer_id}`,
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

    // 5.8) Enviar requisição ao Asaas
    try {
      const asaasUrl = `${ASAAS_BASE_URL}/payments?access_token=${ASAAS_API_TOKEN}`;
      const response = await axios.post(asaasUrl, asaasPayload, { headers: HEADERS });

      // 5.9) Se sucesso, retornar resultado ao cliente
      return res.status(201).json({
        kit_composition: kit,
        price_total: priceTotal,
        requested_installments: installmentCount,
        adjusted_installments: adjustedInstallments,
        asaas_response: response.data
      });
    } catch (error: any) {
      // Em caso de erro retornado pelo Asaas, repassa código e JSON de erro
      if (error.response && error.response.data) {
        return res.status(error.response.status).json({ error: error.response.data });
      }
      // Qualquer outro erro (timeout, rede), devolve 500
      return res.status(500).json({ error: "Erro interno ao chamar a API Asaas." });
    }
  }
);

/**
 * === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO XGG (APENAS CONSULTA) ===
 *
 * GET /xgg/kits retorna lista completa dos kits XGG (4 tiers),
 * permitindo ao front-end exibir as opções disponíveis ao usuário.
 */
app.get("/xgg/kits", (req: Request, res: Response) => {
  return res.json(xggKits);
});

// Inicia servidor na porta 3000 (ou via variável de ambiente PORT)
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

---

### Observações Finais

1. **Uso da chave de API real**:
    
    - Em ambos os templates, a variável `ASAAS_API_TOKEN` já está preenchida com o _token de produção_ real fornecido anteriormente.
        
    - ⚠️ **Trate essa chave como senha**: nunca a exponha em repositórios públicos.
        
2. **Cálculo de `panelCount`**:
    
    - Como cada kit “XGG” gera valores de `systemKwp × 1 000` sempre múltiplos de 400 Wp (por construção), obtivemos números exatos em `panelCount` (ex.: 14 375 módulos).
        
    - Caso no futuro você precise ajustar para outro valor, basta usar `math.ceil((systemKwp * 1_000) / 400)` no Python ou `Math.ceil((systemKwp * 1000) / 400)` no JavaScript.
        
3. **Limitação de parcelas**:
    
    - As regras permanecem:
        
        - **Visa/Mastercard** até 21×.
            
        - **Demais bandeiras (Elo, Amex, Hipercard etc.)** até 12×.
            
4. **Endpoints disponibilizados**:
    
    - **FastAPI (Python)**:
        
        - `POST /xgg/create_charge` → cria a cobrança.
            
        - `GET /xgg/kits` → lista as composições de kit.
            
    - **Node.js + Express (TypeScript)**:
        
        - `POST /xgg/create_charge` → cria a cobrança.
            
        - `GET /xgg/kits` → lista as composições de kit.
            
5. **Dados fixos de `creditCardHolderInfo`**:
    
    - Em produção, substitua `"NOME DO TITULAR"`, `"000.000.000-00"`, `"Rua Exemplo"`, etc., por dados reais do cliente (armazenados no seu banco de dados).
        

Pronto! Com esses dois templates você finaliza a **primeira fase** de endpoints para **todas as categorias de projeto solar** (XPP, PP, P, M, G, GG, XG e XGG), usando as credenciais reais fornecidas.