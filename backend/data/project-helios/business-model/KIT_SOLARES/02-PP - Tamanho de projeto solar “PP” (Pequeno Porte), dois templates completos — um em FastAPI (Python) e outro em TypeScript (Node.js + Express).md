A seguir, apresento, para o **tamanho de projeto solar “PP” (Pequeno Porte)**, dois templates completos — um em **FastAPI (Python)** e outro em **TypeScript (Node.js + Express)** — que ilustram:

1. **Cálculo automático dos valores** (painéis + inversor) de cada tier de geração (“Padrão”, “Consciente”, “Moderado” e “Acelerado”) para a categoria **PP**.
    
2. **Lógica de limitação de parcelas** baseada na bandeira do cartão de crédito: até **21× para Visa e Mastercard** e até **12× para as demais bandeiras** (conforme documentação Asaas).
    
3. **Payload JSON de cobrança** para envio ao Asaas, incluindo `installmentCount` corretamente ajustado.
    
4. Comentários detalhados em cada trecho de código, sem abreviações, para facilitar a leitura e integração.
    

---

## 1. Template em FastAPI (Python) para “PP”

```python
# fastapi_pp.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import httpx

app = FastAPI(
    title="API de Cobrança de Kit Solar PP",
    description=(
        "Este serviço calcula o valor do kit solar para projetos PP e "
        "cria a cobrança no Asaas, limitando em até 21 parcelas para Visa e Mastercard, "
        "e até 12 parcelas para demais bandeiras."
    ),
    version="1.0.0"
)

#
# === 1) DEFINIÇÃO DOS DADOS DE COMPOSIÇÃO DO KIT PP ===
#

# 1.1) Tipos auxiliares para facilitar validações
ProjectCategory = Literal["PP"]  # Somente "PP" neste template
GenerationTierName = Literal["Padrão", "Consciente", "Moderado", "Acelerado"]

class LossFactors(BaseModel):
    """
    Fatores de perda do sistema fotovoltaico (valores percentuais):
    - temperatura: perda de energia por aumento de temperatura do módulo (%)
    - shading: perda de energia por sombreamento (%)
    - soiling: perda de energia por sujeira/poeira (%)
    - mismatchLidDc: perdas combinadas (mismatch + LID + fios DC) (%)
    """
    temperature: float = Field(..., description="Perda por temperatura (%)")
    shading: float = Field(..., description="Perda por sombreamento (%)")
    soiling: float = Field(..., description="Perda por sujidade (%)")
    mismatchLidDc: float = Field(..., description="Perda por mismatch + LID + fio DC (%)")

class SolarKitComponent(BaseModel):
    """
    Representa a composição do kit solar PP para um determinado tier:
    - category: sempre "PP"
    - tier: um dos quatro níveis de geração (Padrão, Consciente, Moderado, Acelerado)
    - systemKwp: potência total projetada do sistema em kWp (considera multiplier)
    - panelWp: potência nominal de cada painel (400 Wp)
    - panelCount: número de módulos de 400 Wp necessários (arredondado para cima)
    - inverterKw: potência recomendada do inversor em kW
    - lossFactors: fatores de perda padrão (valor informativo)
    """
    category: ProjectCategory
    tier: GenerationTierName
    systemKwp: float
    panelWp: int
    panelCount: int
    inverterKw: float
    lossFactors: LossFactors

# 1.2) Constantes de precificação
PANEL_COST: float = 800.00           # R$ 800,00 por módulo de 400 Wp
INVERTER_COST_PER_KW: float = 2000.00  # R$ 2.000,00 por kW de inversor

# 1.3) Lista de tiers de geração PP com seus multiplicadores
#
#   - averageKwp para PP = 2,0 kWp
#   - multiplicadores:
#       * Padrão     => 1.15
#       * Consciente => 1.30
#       * Moderado   => 1.45
#       * Acelerado  => 1.60
#   - cálculo de panelCount: ceil(systemKwp * 1000 / 400)
#   - recomendações de inversor (kW) para PP:
#       * Padrão     => 2.3 kW
#       * Consciente => 2.6 kW
#       * Moderado   => 2.9 kW
#       * Acelerado  => 3.2 kW
#
generation_tiers: List[SolarKitComponent] = [
    # Tier Padrão: multiplier = 1.15
    SolarKitComponent(
        category="PP",
        tier="Padrão",
        systemKwp=round(2.0 * 1.15, 2),   # 2.0 kWp × 1.15 = 2.30 kWp
        panelWp=400,
        panelCount=6,                     # ceil(2300 / 400) = ceil(5.75) = 6 módulos
        inverterKw=2.3,                   # conforme recomendação Asaas
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Consciente: multiplier = 1.30
    SolarKitComponent(
        category="PP",
        tier="Consciente",
        systemKwp=round(2.0 * 1.30, 2),   # 2.0 kWp × 1.30 = 2.60 kWp
        panelWp=400,
        panelCount=7,                     # ceil(2600 / 400) = ceil(6.5) = 7 módulos
        inverterKw=2.6,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Moderado: multiplier = 1.45
    SolarKitComponent(
        category="PP",
        tier="Moderado",
        systemKwp=round(2.0 * 1.45, 2),   # 2.0 kWp × 1.45 = 2.90 kWp
        panelWp=400,
        panelCount=8,                     # ceil(2900 / 400) = ceil(7.25) = 8 módulos
        inverterKw=2.9,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Acelerado: multiplier = 1.60
    SolarKitComponent(
        category="PP",
        tier="Acelerado",
        systemKwp=round(2.0 * 1.60, 2),   # 2.0 kWp × 1.60 = 3.20 kWp
        panelWp=400,
        panelCount=8,                     # ceil(3200 / 400) = ceil(8.0) = 8 módulos
        inverterKw=3.2,
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
    - category: deve ser "PP" (este template é específico para PP)
    - tier: um dos quatro níveis de geração (Padrão, Consciente, Moderado, Acelerado)
    - customer_id: ID do cliente já cadastrado no Asaas (ex.: "cus_ABC123xyz")
    - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO", "AMEX" etc.)
    - creditCardToken: token de cartão já obtido anteriormente (ex.: "tkn_abc123xyz")
    - installmentCount: número desejado de parcelas (int); será limitado conforme bandeira
    - dueDate: data de vencimento da primeira parcela no formato "AAAA-MM-DD"
    - description (opcional): descrição livre para a cobrança; se ausente, usa padrão interno
    """
    category: ProjectCategory = Field(..., description='Categoria do projeto, neste caso "PP"')
    tier: GenerationTierName = Field(..., description="Nível de geração desejado para cálculo do kit")
    customer_id: str = Field(..., description="ID do cliente no Asaas, ex.: 'cus_ABC123xyz'")
    creditCardBrand: str = Field(..., description="Bandeira do cartão, ex.: 'VISA', 'MASTERCARD', 'ELO'")
    creditCardToken: str = Field(..., description="Token de cartão já gerado, ex.: 'tkn_abc123xyz'")
    installmentCount: int = Field(..., description="Número de parcelas solicitado pelo cliente")
    dueDate: str = Field(..., description='Data de vencimento da primeira parcela no formato "AAAA-MM-DD"')
    description: str = Field(
        default="Cobrança de Kit Solar PP",
        description="Descrição da cobrança; padrão se não informado"
    )

#
# === 3) PARÂMETROS DA API DO ASAAS ===
#

ASAAS_BASE_URL: str = "https://www.asaas.com/api/v3"
# Sua chave de API fornecida pelo Asaas (token real)
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
    Retorna a composição do kit PP para o tier informado.
    Levanta HTTPException com código 404 se não encontrar.
    """
    for kit in generation_tiers:
        if kit.tier == tier_name:
            return kit
    raise HTTPException(
        status_code=404,
        detail=f"Não foi possível encontrar o kit PP para o tier '{tier_name}'."
    )

def calculate_kit_price(kit: SolarKitComponent) -> float:
    """
    Calcula o preço total do kit solar:
    - Total de módulos × Custo unitário de módulo (PANEL_COST)
    - Mais potência de inversor (em kW) × Custo por kW de inversor (INVERTER_COST_PER_KW)
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
# === 5) ENDPOINT FASTAPI: CRIAR COBRANÇA NO ASAAS PARA KIT PP ===
#

@app.post("/pp/create_charge")
async def create_pp_charge(request: ChargeRequest):
    # --- 5.1) Validar categoria PP (reforço, apesar de o modelo já garantir) ---
    if request.category != "PP":
        raise HTTPException(
            status_code=400,
            detail="Esta rota só suporta projetos solares de tamanho 'PP'."
        )

    # --- 5.2) Buscar a composição do kit PP para o tier solicitado ---
    kit = find_kit_for_tier(request.tier)

    # --- 5.3) Calcular preço total do kit (painéis + inversor) ---
    price_total = calculate_kit_price(kit)

    # --- 5.4) Ajustar installmentCount com base na bandeira do cartão ---
    adjusted_installments = limit_installments(
        brand=request.creditCardBrand,
        requested_installments=request.installmentCount
    )

    # --- 5.5) Montar o payload para envio ao Asaas ---
    asaas_payload = {
        "customer": request.customer_id,                 # ID do cliente já existente no Asaas
        "billingType": "CREDIT_CARD",                    # Tipo de cobrança via cartão
        "installmentCount": adjusted_installments,       # Parcelas ajustadas
        "value": price_total,                            # Valor total calculado do kit
        "dueDate": request.dueDate,                      # Data de vencimento da 1ª parcela
        "description": f"{request.description} (PP - {kit.tier})",
        "externalReference": f"PP_{kit.tier}_CHARGE_{request.customer_id}",
        "creditCard": {
            "creditCardToken": request.creditCardToken    # Token JWT já obtido anteriormente
        },
        "creditCardHolderInfo": {
            # Informação de titular de cartão (pode ser parametrizada conforme necessidades)
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

    # --- 5.6) Realizar requisição ao Asaas ---
    url = f"{ASAAS_BASE_URL}/payments?access_token={ASAAS_API_TOKEN}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=asaas_payload, headers=HEADERS)

    # --- 5.7) Verificar resposta do Asaas ---
    if response.status_code not in (200, 201):
        # Erro retornado pelo Asaas (ex.: parcelamento acima do permitido em função da bandeira)
        raise HTTPException(
            status_code=response.status_code,
            detail={"error": response.json()}
        )

    # --- 5.8) Retornar resultado ao cliente ---
    return {
        "kit_composition": kit.dict(),
        "price_total": price_total,
        "requested_installments": request.installmentCount,
        "adjusted_installments": adjusted_installments,
        "asaas_response": response.json()
    }

#
# === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO PP (APENAS CONSULTA) ===
#

@app.get("/pp/kits", response_model=List[SolarKitComponent])
async def list_pp_kits():
    """
    Retorna a lista completa de composições de kit PP para os 4 tiers:
    - Útil para front-ends que queiram exibir opções ao usuário.
    """
    return generation_tiers
```

### Explicação detalhada do código FastAPI para “PP”

1. **Composição do Kit PP (seção 1)**
    
    - Declaramos uma lista fixa `generation_tiers` com quatro instâncias de `SolarKitComponent`, uma para cada tier de geração em “PP”.
        
    - Cada componente armazena:
        
        - `category`: fixo em `"PP"`.
            
        - `tier`: `"Padrão"`, `"Consciente"`, `"Moderado"` ou `"Acelerado"`.
            
        - `systemKwp`: potência total (por exemplo, 2,30 kWp para `"Padrão"`).
            
        - `panelWp`: 400 (constante de potência do módulo em Wp).
            
        - `panelCount`: número de módulos de 400 Wp arredondado para cima (por exemplo, 6).
            
        - `inverterKw`: potência recomendada (por exemplo, 2,3 kW para `"Padrão"`).
            
        - `lossFactors`: apenas informativo, não usado no cálculo de preço (4 %, 3 %, 3 % e 4 %).
            
2. **Modelo de requisição `ChargeRequest` (seção 2)**
    
    - Recebe:
        
        - `category` (deve ser “PP”),
            
        - `tier` (um dos quatro tiers),
            
        - `customer_id` (string, ID do cliente no Asaas),
            
        - `creditCardBrand` (string, ex.: “VISA”),
            
        - `creditCardToken` (string JWT),
            
        - `installmentCount` (int sugerido pelo usuário),
            
        - `dueDate` (“AAAA-MM-DD”),
            
        - `description` (string opcional, com padrão “Cobrança de Kit Solar PP”).
            
3. **Função `limit_installments` (seção 4)**
    
    - Se a bandeira (`brand`) for **VISA** ou **MASTERCARD**, retorna o mínimo entre o solicitado e 21.
        
    - Caso contrário (ELO, AMEX, HIPERCARD, etc.), retorna o mínimo entre o solicitado e 12. Isso garante que nunca geraremos pedidos com mais parcelas que o permitido.
        
4. **Endpoint `/pp/create_charge` (seção 5)**
    
    - Valida `category` == `"PP"`; se não, retorna 400.
        
    - Encontra a composição do kit para o `tier` informado; se não achar, retorna 404.
        
    - Calcula `price_total` via `calculate_kit_price()`.
        
    - Ajusta `installmentCount` usando `limit_installments()`.
        
    - Monta `asaas_payload` com os campos obrigatórios para o Asaas:
        
        - `customer`, `billingType`, `installmentCount`, `value`, `dueDate`, `description`, `externalReference`, `creditCard` (token) e `creditCardHolderInfo` (dados fixos ou parametrizados).
            
    - Chama `POST /payments?access_token=...` no Asaas.
        
    - Caso o Asaas retorne código diferente de 200 ou 201, devolve HTTPException com o JSON de erro.
        
    - Se tudo der certo, retorna o JSON contendo:
        
        - `kit_composition` (dados do kit encontrado),
            
        - `price_total` (valor calculado),
            
        - `requested_installments` (parcelas solicitadas),
            
        - `adjusted_installments` (parcelas ajustadas),
            
        - `asaas_response` (retorno completo do Asaas, para auditoria).
            
5. **Endpoint `/pp/kits` (seção 6)**
    
    - Retorna `generation_tiers` completo, para front-ends exibirem as opções de tier PP disponíveis ao usuário.
        

---

## 2. Template em TypeScript (Node.js + Express) para “PP”

```typescript
// server_pp.ts

import express, { Request, Response } from "express";
import axios from "axios";
import { body, validationResult } from "express-validator";

const app = express();
app.use(express.json());

/**
 * === 1) TIPOS E DADOS DE COMPOSIÇÃO DO KIT PP ===
 *
 * Em PP, definimos quatro tiers de geração com seus multiplicadores,
 * potências de inversor recomendadas e fatores de perda.
 */

type ProjectCategory = "PP"; // Neste template, apenas "PP" é aceito
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
  /** Categoria do projeto solar, fixo em "PP" */
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

// 1.1) Custo de componentes (ajustar conforme necessidade real)
const PANEL_COST: number = 800.0;            // R$ 800,00 por módulo de 400 Wp
const INVERTER_COST_PER_KW: number = 2000.0; // R$ 2.000,00 por kW de inversor

// 1.2) Lista de composições dos kits PP (4 tiers)
//     - averageKwp para PP = 2,0 kWp
//     - Multiplicadores: 1.15 (Padrão), 1.30 (Consciente), 1.45 (Moderado), 1.60 (Acelerado)
//     - Recomendações de inversor (kW) para PP: 2.3, 2.6, 2.9, 3.2
const ppKits: SolarKitComponent[] = [
  {
    category: "PP",
    tier: "Padrão",
    systemKwp: parseFloat((2.0 * 1.15).toFixed(2)), // 2,0 × 1.15 = 2,30 kWp
    panelWp: 400,
    panelCount: 6,      // ceil(2 300 / 400) = ceil(5,75) = 6 módulos
    inverterKw: 2.3,    // recomendado pelo Asaas
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "PP",
    tier: "Consciente",
    systemKwp: parseFloat((2.0 * 1.30).toFixed(2)), // 2,0 × 1.30 = 2,60 kWp
    panelWp: 400,
    panelCount: 7,      // ceil(2 600 / 400) = ceil(6,50) = 7 módulos
    inverterKw: 2.6,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "PP",
    tier: "Moderado",
    systemKwp: parseFloat((2.0 * 1.45).toFixed(2)), // 2,0 × 1.45 = 2,90 kWp
    panelWp: 400,
    panelCount: 8,      // ceil(2 900 / 400) = ceil(7,25) = 8 módulos
    inverterKw: 2.9,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "PP",
    tier: "Acelerado",
    systemKwp: parseFloat((2.0 * 1.60).toFixed(2)), // 2,0 × 1.60 = 3,20 kWp
    panelWp: 400,
    panelCount: 8,      // ceil(3 200 / 400) = ceil(8,0) = 8 módulos
    inverterKw: 3.2,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  }
];

/**
 * === 2) TIPOS E VALIDAÇÕES PARA O BODY DE COBRANÇA ===
 *
 * O front-end deve enviar um JSON contendo:
 * - category: "PP"
 * - tier: "Padrão" | "Consciente" | "Moderado" | "Acelerado"
 * - customer_id: ID do cliente cadastrado no Asaas (string)
 * - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO")
 * - creditCardToken: token JWT do cartão já gerado (ex.: "tkn_abc123xyz")
 * - installmentCount: número de parcelas (int); será ajustado conforme bandeira
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
  description?: string;   // Texto livre para descrição da cobrança
}

/**
 * === 3) PARÂMETROS DA API DO ASAAS ===
 *
 * - ASAAS_BASE_URL: endpoint base de produção da Asaas
 * - ASAAS_API_TOKEN: token real fornecido pela Asaas (string)
 * - HEADERS: cabeçalhos padrão para requisição (JSON)
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
 * Retorna a composição do kit PP para o tier informado.
 * Se não encontrar o tier, retorna undefined.
 */
function findKitByTier(tierName: GenerationTierName): SolarKitComponent | undefined {
  return ppKits.find((kit) => kit.tier === tierName);
}

/**
 * Calcula o preço total do kit:
 * (quantidade de módulos × custo unitário) + (potência de inversor (kW) × custo por kW)
 */
function calculateKitPrice(kit: SolarKitComponent): number {
  const pricePanels = kit.panelCount * PANEL_COST;
  const priceInverter = kit.inverterKw * INVERTER_COST_PER_KW;
  return parseFloat((pricePanels + priceInverter).toFixed(2));
}

/**
 * Limita o número de parcelas conforme bandeira do cartão:
 * - Visa e Mastercard: até 21×
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
 * Valida se uma string segue o padrão AAAA-MM-DD (data)
 */
function isValidDate(dateString: string): boolean {
  const isoDatePattern = /^\d{4}-\d{2}-\d{2}$/;
  return isoDatePattern.test(dateString);
}

/**
 * Formulário de validação de campos via express-validator
 */
const chargeValidationRules = [
  body("category")
    .equals("PP").withMessage("category deve ser 'PP'"),
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
 * === 5) ENDPOINT Express: CRIAR COBRANÇA NO ASAAS PARA KIT PP ===
 */
app.post(
  "/pp/create_charge",
  chargeValidationRules,
  async (req: Request, res: Response) => {
    // 5.1) Checar erros de validação
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
      description = "Cobrança de Kit Solar PP"
    } = req.body as ChargeRequest;

    // 5.3) Garantir que category seja "PP"
    if (category !== "PP") {
      return res.status(400).json({
        error: "Para este endpoint, a categoria deve ser 'PP'."
      });
    }

    // 5.4) Buscar a composição do kit PP para o tier solicitado
    const kit = findKitByTier(tier);
    if (!kit) {
      return res.status(404).json({
        error: `Não encontramos nenhum kit PP para o tier '${tier}'.`
      });
    }

    // 5.5) Calcular preço total do kit (módulos + inversor)
    const priceTotal = calculateKitPrice(kit);

    // 5.6) Ajustar installmentCount com base na bandeira do cartão
    const adjustedInstallments = limitInstallments(creditCardBrand, installmentCount);

    // 5.7) Montar o payload JSON conforme exigências Asaas
    const asaasPayload = {
      customer: customer_id,                       // ID do cliente cadastrado no Asaas
      billingType: "CREDIT_CARD",                  // Cobrança via cartão de crédito
      installmentCount: adjustedInstallments,      // Parcelas ajustadas (≤21 ou ≤12)
      value: priceTotal,                           // Valor total calculado do kit
      dueDate: dueDate,                            // Data de vencimento da 1ª parcela
      description: `${description} (PP - ${kit.tier})`,
      externalReference: `PP_${kit.tier}_CHARGE_${customer_id}`,
      creditCard: {
        creditCardToken: creditCardToken           // Token do cartão já obtido anteriormente
      },
      creditCardHolderInfo: {
        // Dados obrigatórios de titular de cartão
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

    // 5.8) Executar requisição ao Asaas
    try {
      const asaasUrl = `${ASAAS_BASE_URL}/payments?access_token=${ASAAS_API_TOKEN}`;
      const response = await axios.post(asaasUrl, asaasPayload, { headers: HEADERS });

      // 5.9) Se sucesso (status 200 ou 201), retornar JSON contendo
      // composição do kit, preço, parcelas solicitadas/ajustadas e resposta do Asaas
      return res.status(201).json({
        kit_composition: kit,
        price_total: priceTotal,
        requested_installments: installmentCount,
        adjusted_installments: adjustedInstallments,
        asaas_response: response.data
      });
    } catch (error: any) {
      // 5.10) Em caso de erro do Asaas (ex.: parcela acima do permitido),
      // devolver o código e o payload de erro para diagnóstico
      if (error.response && error.response.data) {
        return res.status(error.response.status).json({ error: error.response.data });
      }
      // Caso seja erro interno de rede ou timeout
      return res.status(500).json({ error: "Erro interno ao chamar a API Asaas." });
    }
  }
);

/**
 * === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO DE KITS PP ===
 *
 * Rota GET /pp/kits retorna a lista completa de composições PP
 * (útil para front-ends exibirem opções ao usuário).
 */
app.get("/pp/kits", (req: Request, res: Response) => {
  return res.json(ppKits);
});

// Inicia o servidor na porta 3000 (ou conforme variável de ambiente PORT)
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

### Explicação detalhada do código TypeScript para “PP”

1. **Declaração de tipos e array `ppKits` (seção 1)**
    
    - Cada item de `ppKits` contém:
        
        - `category`: fixo em `"PP"`.
            
        - `tier`: `"Padrão"`, `"Consciente"`, `"Moderado"` ou `"Acelerado"`.
            
        - `systemKwp`: calculado (por ex. 2,30 kWp para `"Padrão"`).
            
        - `panelWp`: sempre 400 (Wp por módulo).
            
        - `panelCount`: número de módulos de 400 Wp arredondado para cima (por ex. 6).
            
        - `inverterKw`: potência recomendada (por ex. 2,3 kW para `"Padrão"`).
            
        - `lossFactors`: apenas informativo (4 %, 3 %, 3 % e 4 %), não usado no cálculo de preço.
            
2. **Modelo de requisição `ChargeRequest` (seção 2)**
    
    - O front-end envia JSON contendo:
        
        - `category` (deve ser “PP”),
            
        - `tier` (um dos quatro tiers),
            
        - `customer_id` (string, ID do cliente no Asaas),
            
        - `creditCardBrand` (string, ex.: “VISA”),
            
        - `creditCardToken` (string JWT),
            
        - `installmentCount` (int sugerido pelo usuário),
            
        - `dueDate` (“AAAA-MM-DD”),
            
        - `description` (string opcional, com padrão “Cobrança de Kit Solar PP”).
            
3. **Funções auxiliares (seção 4)**
    
    - `findKitByTier(tierName)`: retorna o item de `ppKits` que corresponde ao `tierName`.
        
    - `calculateKitPrice(kit)`: realiza `(panelCount × PANEL_COST) + (inverterKw × INVERTER_COST_PER_KW)` e arredonda a duas casas.
        
    - `limitInstallments(brand, requested)`:
        
        - Se `brand` for “VISA” ou “MASTERCARD”, retorna `Math.min(requested, 21)`.
            
        - Caso contrário, retorna `Math.min(requested, 12)`.
            
    - `isValidDate(dateString)`: valida formato “AAAA-MM-DD” com regex.
        
4. **Endpoint `POST /pp/create_charge` (seção 5)**
    
    - Usa `express-validator` para checar formato e presença dos campos obrigatórios.
        
    - Se `category !== "PP"`, retorna 400.
        
    - Procura a composição do kit para o `tier` informado; se não achar, retorna 404.
        
    - Calcula `priceTotal` via `calculateKitPrice()`.
        
    - Ajusta `installmentCount` usando `limitInstallments()`.
        
    - Monta `asaasPayload` com:
        
        - `customer`, `billingType`, `installmentCount`, `value`, `dueDate`, `description`, `externalReference`, `creditCard` (token) e `creditCardHolderInfo`.
            
    - Chama `POST` em `https://www.asaas.com/api/v3/payments?access_token={ASAAS_API_TOKEN}`.
        
    - Se a resposta não for `200` ou `201`, devolve o erro do Asaas.
        
    - Caso contrário, retorna `201 Created` com JSON contendo:
        
        - `kit_composition`,
            
        - `price_total`,
            
        - `requested_installments`,
            
        - `adjusted_installments`,
            
        - `asaas_response`.
            
5. **Endpoint `GET /pp/kits` (seção 6)**
    
    - Retorna `ppKits` completo, para front-ends exibirem as opções de tier disponíveis.
        

---

### 3. Resumo dos Valores Calculados para “PP”

Para cada **tier** em “PP” (baseado em `averageKwp = 2,0 kWp`):

|Tier|systemKwp (kWp)|panelCount|inverterKw (kW)|Painéis (R$ = panelCount×800)|Inversor (R$ = inverterKw×2000)|Preço Total (R$)|
|---|---|---|---|---|---|---|
|Padrão|2,30|6|2,3|6 × 800 = 4 800|2,3 × 2 000 = 4 600|9 400|
|Consciente|2,60|7|2,6|7 × 800 = 5 600|2,6 × 2 000 = 5 200|10 800|
|Moderado|2,90|8|2,9|8 × 800 = 6 400|2,9 × 2 000 = 5 800|12 200|
|Acelerado|3,20|8|3,2|8 × 800 = 6 400|3,2 × 2 000 = 6 400|12 800|

- **Como calcular**:
    
    1. `systemKwp = averageKwp (2,0) × multiplier` (1.15, 1.30, 1.45 ou 1.60).
        
    2. `panelCount = ceil(systemKwp × 1000 / 400)`.
        
    3. `inverterKw` conforme recomendado (`2.3`, `2.6`, `2.9` ou `3.2`).
        
    4. `Preço total = (panelCount × 800) + (inverterKw × 2000)`.
        
- **Parcelamento** (exemplos):
    
    - Se o **cartão for VISA** e o cliente pedir `installmentCount = 24`, o código ajustará para `21`.
        
    - Se for **ELO** e o cliente pedir `installmentCount = 15`, ajustará para `12`.
        

---

### 4. Exemplos de Uso

#### 4.1. Exemplo de requisição para criar cobrança “PP – Padrão” com 18× em Mastercard

```bash
POST /pp/create_charge
Host: localhost:3000
Content-Type: application/json

{
  "category": "PP",
  "tier": "Padrão",
  "customer_id": "cus_EXEMPLO_CLIENTE_PP",
  "creditCardBrand": "MASTERCARD",
  "creditCardToken": "tkn_EXEMPLO_TOKEN_CLIENTE",
  "installmentCount": 18,
  "dueDate": "2025-06-10",
  "description": "Kit PP Tier Padrão - 18x"
}
```

- **Fluxo interno**:
    
    1. `findKitByTier("Padrão")` → kit com `systemKwp=2,30`, `panelCount=6`, `inverterKw=2,3`.
        
    2. `calculateKitPrice(...)` → `(6×800) + (2,3×2000) = 4 800 + 4 600 = 9 400`.
        
    3. `limitInstallments("MASTERCARD", 18)` → `min(18,21) = 18` (sem ajuste).
        
    4. Monta payload e chama Asaas:
        
        ```jsonc
        {
          "customer": "cus_EXEMPLO_CLIENTE_PP",
          "billingType": "CREDIT_CARD",
          "installmentCount": 18,
          "value": 9400.00,
          "dueDate": "2025-06-10",
          "description": "Kit PP Tier Padrão - 18x (PP - Padrão)",
          "externalReference": "PP_Padrão_CHARGE_cus_EXEMPLO_CLIENTE_PP",
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
        
    5. O Asaas retornará JSON indicando status da cobrança. O endpoint devolve esse JSON junto com detalhes de kit e preços.
        

#### 4.2. Exemplo de requisição para criar cobrança “PP – Consciente” com 15× em ELO

```bash
POST /pp/create_charge
Host: localhost:3000
Content-Type: application/json

{
  "category": "PP",
  "tier": "Consciente",
  "customer_id": "cus_EXEMPLO_CLIENTE_PP",
  "creditCardBrand": "ELO",
  "creditCardToken": "tkn_EXEMPLO_TOKEN_CLIENTE",
  "installmentCount": 15,
  "dueDate": "2025-06-15",
  "description": "Kit PP Tier Consciente - 15x"
}
```

- **Fluxo interno**:
    
    1. `findKitByTier("Consciente")` → kit com `systemKwp=2,60`, `panelCount=7`, `inverterKw=2,6`.
        
    2. `calculateKitPrice(...)` → `(7×800) + (2,6×2000) = 5 600 + 5 200 = 10 800`.
        
    3. `limitInstallments("ELO", 15)` → `min(15,12) = 12` (ajustado para 12).
        
    4. Monta payload e chama Asaas:
        
        ```jsonc
        {
          "customer": "cus_EXEMPLO_CLIENTE_PP",
          "billingType": "CREDIT_CARD",
          "installmentCount": 12,
          "value": 10800.00,
          "dueDate": "2025-06-15",
          "description": "Kit PP Tier Consciente - 12x (ajustado) (PP - Consciente)",
          "externalReference": "PP_Consciente_CHARGE_cus_EXEMPLO_CLIENTE_PP",
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
        
    5. O endpoint retorna JSON com detalhes do kit, preço total e resposta do Asaas.
        

---

### 5. Resumo Final para “PP”

- **Categoria “PP”** utiliza **averageKwp = 2,0 kWp**.
    
- **Tiers de Geração (multipliers)**:
    
    - Padrão → 1.15 (2,30 kWp → 6 módulos de 400 Wp, inversor 2,3 kW)
        
    - Consciente → 1.30 (2,60 kWp → 7 módulos de 400 Wp, inversor 2,6 kW)
        
    - Moderado → 1.45 (2,90 kWp → 8 módulos de 400 Wp, inversor 2,9 kW)
        
    - Acelerado → 1.60 (3,20 kWp → 8 módulos de 400 Wp, inversor 3,2 kW)
        
- **Preço por Tier**:
    
    |Tier|panels × 800 (R$)|inverter × 2000 (R$)|Total (R$)|
    |---|---|---|---|
    |Padrão|6 × 800 = 4 800|2,3 × 2000 = 4 600|9 400|
    |Consciente|7 × 800 = 5 600|2,6 × 2000 = 5 200|10 800|
    |Moderado|8 × 800 = 6 400|2,9 × 2000 = 5 800|12 200|
    |Acelerado|8 × 800 = 6 400|3,2 × 2000 = 6 400|12 800|
    
- **Limitação de Parcelas**:
    
    - **Visa/Mastercard** → até 21×.
        
    - **Demais bandeiras** → até 12×.
        
- **Endpoints gerados**:
    
    - `POST /pp/create_charge` → cria a cobrança no Asaas para kits PP, aplicando todas as regras de cálculo e limitação de parcelas.
        
    - `GET /pp/kits` → lista as composições de kit PP para cada tier, permitindo ao front-end exibir as opções.
        

Com esses dois templates (FastAPI e TypeScript/Express), você tem a base completa para gerar endpoints de cobrança para **kits solares PP**, assegurando que apenas Visa e Mastercard possam parcelar em até 21 vezes e que as demais bandeiras fiquem limitadas a 12 parcelas.