A seguir estão os templates completos para o **tamanho de projeto solar “G” (Grande)**, em **FastAPI (Python)** e em **TypeScript (Node.js + Express)**. Ambos incluem:

1. **Cálculo automático** dos valores (painéis + inversor) de cada tier de geração (“Padrão”, “Consciente”, “Moderado” e “Acelerado”).
    
2. **Limitação de parcelas**: até **21× para Visa/Mastercard** e até **12× para demais bandeiras** (Elo, Amex, Hipercard etc.).
    
3. **Payload JSON** de cobrança para envio ao Asaas, contendo o `installmentCount` ajustado conforme a bandeira.
    
4. **Comentários detalhados** em cada trecho de código, sem abreviações, para facilitar entendimento e manutenção.
    

---

## 1. Informações Base para “G” (Grande)

- **averageKwp** (média de geração recomendada): **50,0 kWp**
    
- **Potência nominal de cada painel**: **400 Wp**
    
- **Preço por painel (400 Wp)**: **R$ 800,00**
    
- **Preço por inversor (por kW)**: **R$ 2 000,00**
    
- **Recomendações de inversor para “G”**:
    
    - **Padrão** → 55 kW
        
    - **Consciente** → 63 kW
        
    - **Moderado** → 72 kW
        
    - **Acelerado** → 80 kW
        
- **Multiplicadores por tier**:
    
    - **Padrão** → 1.15
        
    - **Consciente** → 1.30
        
    - **Moderado** → 1.45
        
    - **Acelerado** → 1.60
        

### Como calcular cada kit “G”:

1. **systemKwp** = 50,0 kWp × (multiplier).
    
2. **Carga total (Wp)** = systemKwp × 1 000.
    
3. **panelCount** = ceil((systemKwp × 1 000) / 400).
    
4. **Preço dos painéis** = panelCount × R$ 800,00.
    
5. **Preço do inversor** = inverterKw × R$ 2 000,00.
    
6. **Preço total do kit** = (painéis) + (inversor).
    

### Limitação de Parcelas pelo Asaas:

- **Visa / Mastercard**: até **21 vezes** (conforme documentação Asaas).
    
- **Demais bandeiras (Elo, Amex, Hipercard etc.)**: até **12 vezes**.
    

---

## 2. Cálculos Detalhados Pré-Gerados para “G”

A tabela abaixo mostra, para cada tier em “G”, os valores pré-calculados:

|Tier|systemKwp (kWp)|Carga (Wp)|panelCount|inverterKw (kW)|Custo painéis (R$)|Custo inversor (R$)|Preço total (R$)|
|---|---|---|---|---|---|---|---|
|Padrão|57,50|57 500|144|55,0|144 × 800 = 115 200|55 × 2 000 = 110 000|225 200|
|Consciente|65,00|65 000|163|63,0|163 × 800 = 130 400|63 × 2 000 = 126 000|256 400|
|Moderado|72,50|72 500|182|72,0|182 × 800 = 145 600|72 × 2 000 = 144 000|289 600|
|Acelerado|80,00|80 000|200|80,0|200 × 800 = 160 000|80 × 2 000 = 160 000|320 000|

- **Cálculo de panelCount**:
    
    - Padrão: ceil(57 500 / 400) = ceil(143,75) = 144 módulos.
        
    - Consciente: ceil(65 000 / 400) = ceil(162,5) = 163 módulos.
        
    - Moderado: ceil(72 500 / 400) = ceil(181,25) = 182 módulos.
        
    - Acelerado: ceil(80 000 / 400) = ceil(200,0) = 200 módulos.
        

A partir desses valores fixos, os templates apenas os carregam diretamente em arrays, evitando cálculos repetitivos em tempo de execução. Você também pode, se preferir, fazer o cálculo dinâmico (como nos exemplos anteriores), mas aqui optamos por pré-gerar para clareza.

---

## 3. Template em FastAPI (Python)

```python
# fastapi_g.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import httpx

app = FastAPI(
    title="API de Cobrança de Kit Solar G",
    description=(
        "Este serviço calcula o valor do kit solar para projetos G "
        "e cria a cobrança no Asaas, limitando em até 21 parcelas "
        "para Visa/Mastercard e até 12 parcelas para demais bandeiras."
    ),
    version="1.0.0"
)

#
# === 1) DEFINIÇÃO DOS DADOS DE COMPOSIÇÃO DO KIT G ===
#

# 1.1) Tipos auxiliares para validação
ProjectCategory = Literal["G"]                      # Apenas "G" neste template
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
    Representa a composição do kit solar G para um determinado tier:
    - category: sempre "G"
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
PANEL_COST: float = 800.00             # R$ 800,00 por módulo de 400 Wp
INVERTER_COST_PER_KW: float = 2000.00  # R$ 2.000,00 por kW de inversor

# 1.3) Lista fixa das composições dos kits G
#
#   Valores pré-gerados de acordo com:
#     averageKwp = 50,0 kWp
#     Multipliers: Padrão=1.15, Consciente=1.30, Moderado=1.45, Acelerado=1.60
#     Recomendações inversor (kW): 55.0, 63.0, 72.0, 80.0
#
generation_tiers: List[SolarKitComponent] = [
    # Tier Padrão: systemKwp = 50 × 1.15 = 57.50 kWp
    SolarKitComponent(
        category="G",
        tier="Padrão",
        systemKwp=57.50,    # pré-calculado
        panelWp=400,
        panelCount=144,     # ceil(57 500 / 400) = 144 módulos
        inverterKw=55.0,    # recomendado pelo Asaas
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Consciente: systemKwp = 50 × 1.30 = 65.00 kWp
    SolarKitComponent(
        category="G",
        tier="Consciente",
        systemKwp=65.00,
        panelWp=400,
        panelCount=163,     # ceil(65 000 / 400) = 163 módulos
        inverterKw=63.0,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Moderado: systemKwp = 50 × 1.45 = 72.50 kWp
    SolarKitComponent(
        category="G",
        tier="Moderado",
        systemKwp=72.50,
        panelWp=400,
        panelCount=182,     # ceil(72 500 / 400) = 182 módulos
        inverterKw=72.0,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Acelerado: systemKwp = 50 × 1.60 = 80.00 kWp
    SolarKitComponent(
        category="G",
        tier="Acelerado",
        systemKwp=80.00,
        panelWp=400,
        panelCount=200,     # ceil(80 000 / 400) = 200 módulos
        inverterKw=80.0,
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
    - category: deve ser "G" (este template é específico para G)
    - tier: um dos quatro níveis de geração (Padrão, Consciente, Moderado, Acelerado)
    - customer_id: ID do cliente já cadastrado no Asaas (ex.: "cus_ABC123xyz")
    - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO", "AMEX" etc.)
    - creditCardToken: token de cartão já obtido previamente (ex.: "tkn_abc123xyz")
    - installmentCount: número desejado de parcelas (int); será limitado conforme bandeira
    - dueDate: data de vencimento da primeira parcela no formato "AAAA-MM-DD"
    - description (opcional): texto livre para a cobrança; se não informado, usa padrão interno
    """
    category: ProjectCategory = Field(..., description='Categoria do projeto, neste caso "G"')
    tier: GenerationTierName = Field(..., description="Nível de geração desejado para cálculo do kit")
    customer_id: str = Field(..., description="ID do cliente no Asaas, ex.: 'cus_ABC123xyz'")
    creditCardBrand: str = Field(..., description="Bandeira do cartão, ex.: 'VISA', 'MASTERCARD', 'ELO'")
    creditCardToken: str = Field(..., description="Token de cartão já gerado, ex.: 'tkn_abc123xyz'")
    installmentCount: int = Field(..., description="Número de parcelas solicitado pelo cliente")
    dueDate: str = Field(..., description='Data de vencimento da primeira parcela no formato "AAAA-MM-DD"')
    description: str = Field(
        default="Cobrança de Kit Solar G",
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
    Retorna a composição do kit G para o tier informado.
    Se não encontrar, levanta HTTPException 404.
    """
    for kit in generation_tiers:
        if kit.tier == tier_name:
            return kit
    raise HTTPException(
        status_code=404,
        detail=f"Não foi possível encontrar o kit G para o tier '{tier_name}'."
    )

def calculate_kit_price(kit: SolarKitComponent) -> float:
    """
    Calcula o preço total do kit G:
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
    Retorna o valor ajustado (se for maior que o permitido, retorna o máximo).
    """
    brand_upper = brand.strip().upper()
    if brand_upper in ["VISA", "MASTERCARD"]:
        return min(requested_installments, 21)
    return min(requested_installments, 12)

#
# === 5) ENDPOINT FASTAPI: CRIAR COBRANÇA NO ASAAS PARA KIT G ===
#

@app.post("/g/create_charge")
async def create_g_charge(request: ChargeRequest):
    # 5.1) Validar categoria G (embora Pydantic já assegure, reforçamos aqui)
    if request.category != "G":
        raise HTTPException(
            status_code=400,
            detail="Esta rota só suporta projetos solares de tamanho 'G'."
        )

    # 5.2) Buscar a composição do kit G para o tier solicitado
    kit = find_kit_for_tier(request.tier)

    # 5.3) Calcular preço total do kit (painéis + inversor)
    price_total = calculate_kit_price(kit)

    # 5.4) Ajustar installmentCount conforme bandeira do cartão
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
        "dueDate": request.dueDate,                      # Data de vencimento da 1ª parcela
        "description": f"{request.description} (G - {kit.tier})",
        "externalReference": f"G_{kit.tier}_CHARGE_{request.customer_id}",
        "creditCard": {
            "creditCardToken": request.creditCardToken    # Token do cartão já gerado
        },
        "creditCardHolderInfo": {
            # Dados de titular de cartão (em produção, trazer do banco de dados)
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
        # Se houver erro (parcelamento acima do permitido, dados inválidos, etc.),
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
# === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO G (APENAS CONSULTA) ===
#

@app.get("/g/kits", response_model=List[SolarKitComponent])
async def list_g_kits():
    """
    Retorna a lista completa de composições de kit G para os 4 tiers:
    - Útil para front-ends que queiram exibir as opções de tier ao usuário.
    """
    return generation_tiers
```

### Explicação do Código FastAPI para “G”

1. **Composição do Kit G (seção 1)**
    
    - Criamos uma lista fixa `generation_tiers` com quatro `SolarKitComponent`, um para cada tier (“Padrão”, “Consciente”, “Moderado” e “Acelerado”).
        
    - Cada entrada contém:
        
        - `category`: sempre `"G"`.
            
        - `tier`: um dos quatro níveis de geração.
            
        - `systemKwp`: valor pré-calculado (por ex., 57,50 kWp para “Padrão”).
            
        - `panelWp`: potência do módulo (400 Wp).
            
        - `panelCount`: quantidade de módulos calculada (por ex., 144 para “Padrão”).
            
        - `inverterKw`: potência do inversor recomendada (55 kW para “Padrão”).
            
        - `lossFactors`: fatores de perda padrão (4 %, 3 %, 3 %, 4 %), só para referência.
            
2. **Modelo de Requisição `ChargeRequest` (seção 2)**
    
    - Espera receber os seguintes campos no JSON:
        
        - `category`: fixo `"G"`.
            
        - `tier`: escolher entre “Padrão” | “Consciente” | “Moderado” | “Acelerado”.
            
        - `customer_id`: string, ID do cliente já cadastrado no Asaas.
            
        - `creditCardBrand`: string, nome da bandeira (ex.: `"VISA"`, `"MASTERCARD"`, `"ELO"`).
            
        - `creditCardToken`: string, token JWT do cartão (já gerado pelo endpoint de tokenização).
            
        - `installmentCount`: integer, número de parcelas que o cliente deseja.
            
        - `dueDate`: string no formato `"AAAA-MM-DD"`.
            
        - `description`: string opcional; se não fornecido, usa `"Cobrança de Kit Solar G"`.
            
3. **Funções Auxiliares (seção 4)**
    
    - `find_kit_for_tier(tier_name)`: percorre `generation_tiers` e retorna o objeto cujo `tier` coincida com `tier_name`. Se não encontrar, lança `HTTPException(404)`.
        
    - `calculate_kit_price(kit)`: calcula `(kit.panelCount × 800) + (kit.inverterKw × 2 000)` e arredonda para duas casas. Retorna o **preço total** do kit.
        
    - `limit_installments(brand, requested_installments)`: normaliza a `brand` para maiúsculas.
        
        - Se for `"VISA"` ou `"MASTERCARD"`, retorna `min(requested_installments, 21)`.
            
        - Caso contrário, retorna `min(requested_installments, 12)`.
            
4. **Endpoint `/g/create_charge` (seção 5)**
    
    - Verifica que `request.category == "G"`. Se não for, retorna `400 Bad Request`.
        
    - Busca o kit correspondente ao `tier` informado com `find_kit_for_tier()`. Se não existir, retorna `404`.
        
    - Calcula `price_total` chamando `calculate_kit_price(kit)`.
        
    - Ajusta `installmentCount` via `limit_installments(request.creditCardBrand, request.installmentCount)`.
        
    - Monta o JSON `asaas_payload` contendo:
        
        - `customer`: ID do cliente (string).
            
        - `billingType`: `"CREDIT_CARD"`.
            
        - `installmentCount`: valor ajustado.
            
        - `value`: preço total do kit.
            
        - `dueDate`: data de vencimento passada pelo usuário.
            
        - `description`: concatenação de texto passado + “(G – )”.
            
        - `externalReference`: string de controle (ex.: `"G_Padrão_CHARGE_cus_ABC123"`).
            
        - `creditCard`: objeto com `creditCardToken` (string).
            
        - `creditCardHolderInfo`: dados fixos do titular do cartão (para exemplificar; em produção, buscar do banco de dados).
            
    - Envia `POST` a `https://www.asaas.com/api/v3/payments?access_token=<ASAAS_API_TOKEN>`. Se o Asaas retornar código ≠ 200/201, devolve o erro (HTTPException). Caso contrário, devolve:
        
        ```json
        {
          "kit_composition": { ...dados do kit G... },
          "price_total": <valor numerico>,
          "requested_installments": <int>,
          "adjusted_installments": <int>,
          "asaas_response": { ...JSON completo do Asaas... }
        }
        ```
        
5. **Endpoint `/g/kits` (seção 6)**
    
    - Retorna o array completo `generation_tiers`, com quatro objetos (`SolarKitComponent`). Muito útil para front-ends exibirem as opções disponíveis ao usuário.
        

---

## 4. Template em TypeScript (Node.js + Express)

```typescript
// server_g.ts

import express, { Request, Response } from "express";
import axios from "axios";
import { body, validationResult } from "express-validator";

const app = express();
app.use(express.json());

/**
 * === 1) TIPOS E DADOS DE COMPOSIÇÃO DO KIT G ===
 *
 * Em G, definimos quatro tiers de geração com seus multiplicadores,
 * potências de inversor recomendadas e fatores de perda.
 */

type ProjectCategory = "G"; // Apenas "G" é aceito aqui
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
  /** Categoria do projeto, fixo em "G" */
  category: ProjectCategory;
  /** Tier de geração (um dos quatro) */
  tier: GenerationTierName;
  /** Potência total do sistema em kWp (pré-calculada) */
  systemKwp: number;
  /** Potência nominal de cada painel (400 Wp) */
  panelWp: number;
  /** Quantidade de módulos de 400 Wp necessários (pré-calculado) */
  panelCount: number;
  /** Potência do inversor recomendada em kW */
  inverterKw: number;
  /** Fatores de perda padrão (informativo) */
  lossFactors: LossFactors;
}

// 1.1) Custos de componentes (ajustar conforme mercado)
const PANEL_COST: number = 800.0;            // R$ 800,00 por módulo de 400 Wp
const INVERTER_COST_PER_KW: number = 2000.0; // R$ 2 000,00 por kW de inversor

// 1.2) Array fixo das composições dos kits G (4 tiers)
//     - averageKwp = 50,0 kWp
//     - Multipliers: Padrão=1.15, Consciente=1.30, Moderado=1.45, Acelerado=1.60
//     - Recomendações inversor (kW): 55.0, 63.0, 72.0, 80.0
const gKits: SolarKitComponent[] = [
  {
    category: "G",
    tier: "Padrão",
    systemKwp: parseFloat((50.0 * 1.15).toFixed(2)), // 50 × 1.15 = 57.50 kWp
    panelWp: 400,
    panelCount: 144,    // ceil(57 500 / 400) = 144 módulos
    inverterKw: 55.0,   // recomendação Asaas para G – Padrão
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "G",
    tier: "Consciente",
    systemKwp: parseFloat((50.0 * 1.30).toFixed(2)), // 50 × 1.30 = 65.00 kWp
    panelWp: 400,
    panelCount: 163,    // ceil(65 000 / 400) = 163 módulos
    inverterKw: 63.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "G",
    tier: "Moderado",
    systemKwp: parseFloat((50.0 * 1.45).toFixed(2)), // 50 × 1.45 = 72.50 kWp
    panelWp: 400,
    panelCount: 182,    // ceil(72 500 / 400) = 182 módulos
    inverterKw: 72.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "G",
    tier: "Acelerado",
    systemKwp: parseFloat((50.0 * 1.60).toFixed(2)), // 50 × 1.60 = 80.00 kWp
    panelWp: 400,
    panelCount: 200,    // ceil(80 000 / 400) = 200 módulos
    inverterKw: 80.0,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  }
];

/**
 * === 2) TIPOS E VALIDAÇÕES PARA O BODY DE COBRANÇA ===
 *
 * O front-end envia um JSON com:
 * - category: "G"
 * - tier: "Padrão" | "Consciente" | "Moderado" | "Acelerado"
 * - customer_id: ID do cliente Asaas (string)
 * - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO")
 * - creditCardToken: token JWT do cartão (string)
 * - installmentCount: número de parcelas (int)
 * - dueDate: data de vencimento (AAAA-MM-DD)
 * - description (opcional): texto para descrição
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
 * - ASAAS_API_TOKEN: token real da Asaas (produção)
 * - HEADERS: cabeçalhos padrão para enviar JSON
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
 * Retorna a composição do kit G para o tier informado.
 * Se não encontrar, retorna undefined.
 */
function findKitByTier(tierName: GenerationTierName): SolarKitComponent | undefined {
  return gKits.find(kit => kit.tier === tierName);
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
 * Valida se string está no formato AAAA-MM-DD
 */
function isValidDate(dateString: string): boolean {
  const isoDatePattern = /^\d{4}-\d{2}-\d{2}$/;
  return isoDatePattern.test(dateString);
}

/**
 * Regras de validação com express-validator
 */
const chargeValidationRules = [
  body("category")
    .equals("G").withMessage("category deve ser 'G'"),
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
 * === 5) ENDPOINT Express: CRIAR COBRANÇA NO ASAAS PARA KIT G ===
 */
app.post(
  "/g/create_charge",
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
      description = "Cobrança de Kit Solar G"
    } = req.body as ChargeRequest;

    // 5.3) Garantir que category seja "G"
    if (category !== "G") {
      return res.status(400).json({
        error: "Para este endpoint, a categoria deve ser 'G'."
      });
    }

    // 5.4) Buscar a composição do kit G para o tier solicitado
    const kit = findKitByTier(tier);
    if (!kit) {
      return res.status(404).json({
        error: `Não encontramos nenhum kit G para o tier '${tier}'.`
      });
    }

    // 5.5) Calcular preço total do kit (módulos + inversor)
    const priceTotal = calculateKitPrice(kit);

    // 5.6) Ajustar installmentCount conforme bandeira do cartão
    const adjustedInstallments = limitInstallments(creditCardBrand, installmentCount);

    // 5.7) Montar payload JSON para a API Asaas
    const asaasPayload = {
      customer: customer_id,                       // ID do cliente no Asaas
      billingType: "CREDIT_CARD",                  // Cobrança via cartão de crédito
      installmentCount: adjustedInstallments,      // Parcelas ajustadas
      value: priceTotal,                           // Valor total do kit calculado
      dueDate: dueDate,                            // Data de vencimento da 1ª parcela
      description: `${description} (G - ${kit.tier})`,
      externalReference: `G_${kit.tier}_CHARGE_${customer_id}`,
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

      // 5.9) Em caso de sucesso, retornar dados ao cliente
      return res.status(201).json({
        kit_composition: kit,
        price_total: priceTotal,
        requested_installments: installmentCount,
        adjusted_installments: adjustedInstallments,
        asaas_response: response.data
      });
    } catch (error: any) {
      // Se Asaas retornar erro, repassar o código e o JSON de erro
      if (error.response && error.response.data) {
        return res.status(error.response.status).json({ error: error.response.data });
      }
      // Caso contrário, erro interno de rede ou timeout
      return res.status(500).json({ error: "Erro interno ao chamar a API Asaas." });
    }
  }
);

/**
 * === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO DE KITS G ===
 *
 * GET /g/kits retorna lista completa dos kits G (4 tiers),
 * permitindo ao front-end exibir as opções disponíveis ao usuário.
 */
app.get("/g/kits", (req: Request, res: Response) => {
  return res.json(gKits);
});

// Inicia servidor na porta 3000 (ou via variável de ambiente PORT)
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

### Explicação do Código TypeScript para “G”

1. **Declaração de tipos e array `gKits` (seção 1)**
    
    - Cada objeto em `gKits` contém:
        
        - `category`: fixo **"G"**.
            
        - `tier`: **"Padrão"**, **"Consciente"**, **"Moderado"** ou **"Acelerado"**.
            
        - `systemKwp`: valor pré-calculado (por ex., 57.50 kWp para “Padrão”).
            
        - `panelWp`: sempre **400** (Wp por módulo).
            
        - `panelCount`: quantidade calculada (por ex., 144 para “Padrão”).
            
        - `inverterKw`: potência recomendada do inversor (55 kW, 63 kW, 72 kW ou 80 kW).
            
        - `lossFactors`: informativos (4 %, 3 %, 3 %, 4 %).
            
2. **Modelo de requisição `ChargeRequest` (seção 2)**
    
    - O front-end deve enviar JSON contendo:
        
        - **category** ("G")
            
        - **tier** ("Padrão" | "Consciente" | "Moderado" | "Acelerado")
            
        - **customer_id** (string, ID do cliente no Asaas)
            
        - **creditCardBrand** (string, bandeira do cartão)
            
        - **creditCardToken** (string, token do cartão)
            
        - **installmentCount** (int, número de parcelas)
            
        - **dueDate** (string, no formato "AAAA-MM-DD")
            
        - **description** (string opcional, descrição da cobrança)
            
3. **Funções auxiliares (seção 4)**
    
    - `findKitByTier(tierName)`: retorna o kit correspondente ao `tierName`. Se não encontrar, retorna `undefined`.
        
    - `calculateKitPrice(kit)`: realiza `(kit.panelCount × 800) + (kit.inverterKw × 2000)` e arredonda para duas casas decimais.
        
    - `limitInstallments(brand, requested)`:
        
        - Se `brand` for `"VISA"` ou `"MASTERCARD"`, retorna `Math.min(requested, 21)`.
            
        - Caso contrário, retorna `Math.min(requested, 12)`.
            
    - `isValidDate(dateString)`: valida string com regex no formato `"YYYY-MM-DD"`.
        
4. **Endpoint `POST /g/create_charge` (seção 5)**
    
    - Usa `express-validator` para checar:
        
        - `category === "G"`
            
        - `tier` válido
            
        - `customer_id`, `creditCardBrand`, `creditCardToken` strings
            
        - `installmentCount` inteiro positivo
            
        - `dueDate` no formato `"AAAA-MM-DD"`
            
        - `description` opcional (se recebido deve ser string)
            
    - Caso haja erro de validação, retorna `400 Bad Request` com lista de erros.
        
    - Garante que `category` seja exatamente `"G"`. Se não for, retorna `400`.
        
    - Usa `findKitByTier(tier)` para obter a composição do kit. Se não existir, retorna `404`.
        
    - Calcula `priceTotal = calculateKitPrice(kit)`.
        
    - Ajusta `installmentCount` com `limitInstallments(creditCardBrand, installmentCount)`.
        
    - Monta objeto `asaasPayload` contendo:
        
        ```jsonc
        {
          "customer": customer_id,
          "billingType": "CREDIT_CARD",
          "installmentCount": adjustedInstallments,
          "value": priceTotal,
          "dueDate": dueDate,
          "description": "<texto> (G – <tier>)",
          "externalReference": "G_<tier>_CHARGE_<customer_id>",
          "creditCard": { "creditCardToken": creditCardToken },
          "creditCardHolderInfo": { …dados fixos… }
        }
        ```
        
    - Chama `POST https://www.asaas.com/api/v3/payments?access_token=<ASAAS_API_TOKEN>`.
        
    - Se a Asaas retornar status ≠ 200/201, responde com o JSON de erro e o código.
        
    - Em caso de sucesso, responde `201 Created` com:
        
        ```json
        {
          "kit_composition": { …dados do kit G… },
          "price_total": <valor calculado>,
          "requested_installments": <valor solicitado>,
          "adjusted_installments": <valor ajustado>,
          "asaas_response": { …JSON completo do Asaas… }
        }
        ```
        
5. **Endpoint `GET /g/kits` (seção 6)**
    
    - Retorna o array `gKits`, permitindo ao front-end exibir todas as opções de tier para “G”.
        

---

## 5. Conclusão

- Os exemplos acima seguem o mesmo padrão dos templates para “XPP”, “PP”, “P” e “M”:
    
    1. **Definem um array fixo** com **dados pré-calculados** (`systemKwp`, `panelCount`, `inverterKw`, etc.) para cada tier.
        
    2. **Implementam** um endpoint `"POST /<categoria>/create_charge"` que:
        
        - Recebe os dados do cliente e do cartão (bandeira, token, parcelas desejadas, data de vencimento, etc.).
            
        - **Encontra** a composição correta do kit, **calcula o preço total**, e **ajusta** o número de parcelas com base na bandeira.
            
        - **Monta** o payload para a API Asaas (`/payments?access_token=<token>`).
            
        - **Envia** a requisição para gerar a cobrança, tratando erros ou retornando sucesso.
            
    3. **Implementam** um endpoint `"GET /<categoria>/kits"` que retorna a lista de composições para consulta pelo front-end.
        
- Para cada **categoria de projeto solar** (“XPP”, “PP”, “P”, “M”, **“G”**, e assim por diante “GG”, “XG” e “XGG”), basta copiar esse padrão, ajustando:
    
    1. **averageKwp** (média de geração).
        
    2. **Potência recomendada do inversor** para cada tier.
        
    3. **Cálculo dinâmico ou pré-gerado** de `systemKwp` e `panelCount`.
        
    4. **Valores dos inversores** (kW) conforme tabelas comerciais.
        
- O controle de **parcelamento** segue sempre a mesma regra:
    
    - **Visa/Mastercard** → até **21×**.
        
    - **Demais bandeiras** (Elo, Amex, Hipercard etc.) → até **12×**.
        

Pronto! Com esses dois templates, você já dispõe da base completa para gerar endpoints de cobrança para **kits solares “G”**, garantindo que as regras de parcelamento do Asaas sejam respeitadas.