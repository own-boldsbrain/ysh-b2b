A seguir apresento, para o **tamanho de projeto solar “XPP” (Extra Pequeno Porte)**, dois templates completos — um em **FastAPI (Python)** e outro em **TypeScript (Node.js + Express)** — que ilustram:

1. **Cálculo automático dos valores** (painéis + inversor) de cada tier de geração (“Padrão”, “Consciente”, “Moderado” e “Acelerado”).
    
2. **Lógica de limitação de parcelas** baseada na bandeira do cartão de crédito: até **21× para Visa e Mastercard**, e até **12× para todas as demais bandeiras** (conforme documentação Asaas) ([Asaas - Documentação API](https://docs.asaas.com/changelog/parcelamentos-no-cart%C3%A3o-de-cr%C3%A9dito-em-21x?utm_source=chatgpt.com "Parcelamentos no cartão de crédito em 21x"), [Asaas - Documentação API](https://docs.asaas.com/reference/criar-parcelamento?utm_source=chatgpt.com "Criar parcelamento - Asaas - Documentação API")).
    
3. **Payload JSON de cobrança** para envio ao Asaas, incluindo `installmentCount` limitado corretamente.
    
4. Comentários detalhados em cada trecho de código, sem abreviações ou exceções, para facilitar a leitura e integração.
    

---

## 1. Template em FastAPI (Python)

```python
# fastapi_xpp.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Literal
import httpx

app = FastAPI(
    title="API de Cobrança de Kit Solar XPP",
    description=(
        "Este serviço calcula o valor do kit solar para projetos XPP e "
        "cria a cobrança no Asaas, limitando em até 21 parcelas para Visa e Mastercard, "
        "e até 12 parcelas para demais bandeiras."
    ),
    version="1.0.0"
)

#
# === 1) DEFINIÇÃO DOS DADOS DE COMPOSIÇÃO DO KIT XPP ===
#

# 1.1) Tipos auxiliares para facilitar validações
ProjectCategory = Literal["XPP"]  # Somente "XPP" neste template
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
    Representa a composição do kit solar XPP para um determinado tier:
    - category: sempre "XPP"
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

# 1.3) Lista de tiers de geração XPP com seus multiplicadores
generation_tiers: List[SolarKitComponent] = [
    # Tier Padrão: multiplier = 1.15
    SolarKitComponent(
        category="XPP",
        tier="Padrão",
        systemKwp=round(1.0 * 1.15, 2),   # 1.0 kWp × 1.15 = 1.15 kWp
        panelWp=400,
        panelCount=3,                     # ceil(1150 / 400) = 3 módulos
        inverterKw=1.2,                   # conforme recomendação Asaas
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Consciente: multiplier = 1.30
    SolarKitComponent(
        category="XPP",
        tier="Consciente",
        systemKwp=round(1.0 * 1.30, 2),   # 1.0 kWp × 1.30 = 1.30 kWp
        panelWp=400,
        panelCount=4,                     # ceil(1300 / 400) = 4 módulos
        inverterKw=1.4,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Moderado: multiplier = 1.45
    SolarKitComponent(
        category="XPP",
        tier="Moderado",
        systemKwp=round(1.0 * 1.45, 2),   # 1.0 kWp × 1.45 = 1.45 kWp
        panelWp=400,
        panelCount=4,                     # ceil(1450 / 400) = 4 módulos
        inverterKw=1.5,
        lossFactors=LossFactors(
            temperature=4.0, shading=3.0, soiling=3.0, mismatchLidDc=4.0
        )
    ),
    # Tier Acelerado: multiplier = 1.60
    SolarKitComponent(
        category="XPP",
        tier="Acelerado",
        systemKwp=round(1.0 * 1.60, 2),   # 1.0 kWp × 1.60 = 1.60 kWp
        panelWp=400,
        panelCount=4,                     # ceil(1600 / 400) = 4 módulos
        inverterKw=1.6,
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
    - category: deve ser "XPP" (este template é específico para XPP)
    - tier: um dos quatro níveis de geração (Padrão, Consciente, Moderado, Acelerado)
    - customer_id: ID do cliente já cadastrado no Asaas (ex.: "cus_ABC123xyz")
    - creditCardBrand: bandeira do cartão (ex.: "VISA", "MASTERCARD", "ELO", "AMEX" etc.)
    - creditCardToken: token de cartão já obtido anteriormente (ex.: "tkn_abc123xyz")
    - installmentCount: número desejado de parcelas (int); será limitado conforme bandeira
    - dueDate: data de vencimento da primeira parcela no formato "AAAA-MM-DD"
    - description (opcional): descrição livre para a cobrança; se ausente, usa padrão interno
    """
    category: ProjectCategory = Field(..., description='Categoria do projeto, neste caso "XPP"')
    tier: GenerationTierName = Field(..., description="Nível de geração desejado para cálculo do kit")
    customer_id: str = Field(..., description="ID do cliente no Asaas, ex.: 'cus_ABC123xyz'")
    creditCardBrand: str = Field(..., description="Bandeira do cartão, ex.: 'VISA', 'MASTERCARD', 'ELO'")
    creditCardToken: str = Field(..., description="Token de cartão já gerado, ex.: 'tkn_abc123xyz'")
    installmentCount: int = Field(..., description="Número de parcelas solicitado pelo cliente")
    dueDate: str = Field(..., description='Data de vencimento da primeira parcela no formato "AAAA-MM-DD"')
    description: str = Field(
        default="Cobrança de Kit Solar XPP",
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
    Retorna a composição do kit XPP para o tier informado.
    Levanta HTTPException com código 404 se não encontrar.
    """
    for kit in generation_tiers:
        if kit.tier == tier_name:
            return kit
    raise HTTPException(
        status_code=404,
        detail=f"Não foi possível encontrar o kit XPP para o tier '{tier_name}'."
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
    - Visa ou Mastercard: até 21× :contentReference[oaicite:1]{index=1}
    - Demais bandeiras (Elo, Amex, Hipercard etc.): até 12×
    Retorna o valor ajustado (se for maior que o permitido, retorna o máximo).
    """
    brand_upper = brand.strip().upper()
    if brand_upper in ["VISA", "MASTERCARD"]:
        # Para Visa e Mastercard, o Asaas permite até 21 parcelas :contentReference[oaicite:2]{index=2}
        return min(requested_installments, 21)
    # Para outras bandeiras, o limite é de 12×
    return min(requested_installments, 12)

#
# === 5) ENDPOINT FASTAPI: CRIAR COBRANÇA NO ASAAS PARA KIT XPP ===
#

@app.post("/xpp/create_charge")
async def create_xpp_charge(request: ChargeRequest):
    # --- 5.1) Validar categoria XPP (aqui redundante, mas reforça o contrato da API) ---
    if request.category != "XPP":
        raise HTTPException(
            status_code=400,
            detail="Esta rota só suporta projetos solares de tamanho 'XPP'."
        )

    # --- 5.2) Buscar a composição do kit XPP para o tier solicitado ---
    kit = find_kit_for_tier(request.tier)

    # --- 5.3) Calcular preço total do kit (painéis + inversor) ---
    price_total = calculate_kit_price(kit)

    # --- 5.4) Ajustar/installmentCount com base na bandeira do cartão ---
    # Se o cliente solicitou mais do que o permitido, limitamos:
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
        "description": f"{request.description} (XPP - {kit.tier})",
        "externalReference": f"XPP_{kit.tier}_CHARGE_{request.customer_id}",
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
# === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO XPP (APENAS CONSULTA) ===
#

@app.get("/xpp/kits", response_model=List[SolarKitComponent])
async def list_xpp_kits():
    """
    Retorna a lista completa de composições de kit XPP para os 4 tiers:
    - Útil para front-ends que queiram exibir opções ao usuário.
    """
    return generation_tiers
```

### Explicação detalhada do código FastAPI

1. **Composição do Kit XPP (seção 1)**
    
    - Declaramos uma lista fixa `generation_tiers` com quatro instâncias de `SolarKitComponent`, uma para cada tier de geração em “XPP”.
        
    - Cada componente armazena:
        
        - `systemKwp`: potência total (por ex., 1,15 kWp para Padrão).
            
        - `panelWp`: 400 (constante de potência do módulo em Wp).
            
        - `panelCount`: calculado manualmente (ex: 3 módulos para 1,15 kWp).
            
        - `inverterKw`: recomendação do Asaas (1,2 kW para Padrão, etc.).
            
        - `lossFactors`: apenas informativo (não usado no cálculo de preço diretamente).
            
2. **Modelo de requisição `ChargeRequest` (seção 2)**
    
    - Recebe `category` (deve ser “XPP”), `tier` (um dos quatro tiers), `customer_id` (string), `creditCardBrand` (string com bandeira, ex. “VISA”), `creditCardToken` (string JWT), `installmentCount` (int sugerido pelo usuário), `dueDate` (“AAAA-MM-DD”) e `description` (padrão “Cobrança de Kit Solar XPP”).
        
3. **Função `limit_installments` (seção 4)**
    
    - Se a bandeira (`brand`) for **VISA** ou **MASTERCARD**, retorna o mínimo entre o solicitado e 21 (`min(requested, 21)`), de acordo com a documentação Asaas ([Asaas - Documentação API](https://docs.asaas.com/changelog/parcelamentos-no-cart%C3%A3o-de-cr%C3%A9dito-em-21x?utm_source=chatgpt.com "Parcelamentos no cartão de crédito em 21x"), [Asaas - Documentação API](https://docs.asaas.com/reference/criar-parcelamento?utm_source=chatgpt.com "Criar parcelamento - Asaas - Documentação API")).
        
    - Caso contrário (qualquer outra bandeira como ELO, AMEX, HIPERCARD), retorna `min(requested, 12)`. Ou seja, bloqueia acima de 12×.
        
4. **Endpoint `/xpp/create_charge` (seção 5)**
    
    - Verifica se `category` é “XPP”; caso contrário, retorna erro 400.
        
    - Encontra a composição do kit para o `tier` informado (ou retorna 404 caso não exista).
        
    - Calcula `price_total` como (`panelCount × PANEL_COST`) + (`inverterKw × INVERTER_COST_PER_KW`).
        
    - Ajusta `installmentCount` usando `limit_installments()` para aplicar as regras de bandeira.
        
    - Monta o `asaas_payload` com todos os campos necessários para o Asaas, incluindo `installmentCount` ajustado e `value` igual a `price_total`.
        
    - Chama `POST /payments?access_token=...` no Asaas com um timeout de 60 segundos (para evitar duplicidade por timeout).
        
    - Se o Asaas retornar código diferente de 200 ou 201, devolve HTTPException com o JSON de erro do Asaas.
        
    - Caso contrário, retorna um JSON contendo:
        
        - `kit_composition`: dados do kit encontrado.
            
        - `price_total`: valor calculado.
            
        - `requested_installments`: parcelas originalmente solicitadas.
            
        - `adjusted_installments`: parcelas ajustadas conforme bandeira.
            
        - `asaas_response`: JSON completo retornado pelo Asaas para auditoria.
            
5. **Endpoint `/xpp/kits` (seção 6)**
    
    - Útil para consultar a lista completa de kits XPP (Padrão, Consciente, Moderado, Acelerado) e exibir no front-end as opções disponíveis.
        

---

## 2. Template em TypeScript (Node.js + Express)

```typescript
// server_xpp.ts

import express, { Request, Response } from "express";
import axios from "axios";
import { body, validationResult } from "express-validator";

const app = express();
app.use(express.json());

/**
 * === 1) TIPOS E DADOS DE COMPOSIÇÃO DO KIT XPP ===
 *
 * Em XPP, definimos quatro tiers de geração com seus multiplicadores,
 * potências de inversor recomendadas e fatores de perda.
 */

type ProjectCategory = "XPP"; // Neste template, apenas "XPP" é aceito
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
  /** Categoria do projeto solar, fixo em "XPP" */
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

// 1.2) Lista de composições dos kits XPP (4 tiers)
const xppKits: SolarKitComponent[] = [
  {
    category: "XPP",
    tier: "Padrão",
    systemKwp: parseFloat((1.0 * 1.15).toFixed(2)), // 1,0 × 1.15 = 1,15 kWp
    panelWp: 400,
    panelCount: 3,      // ceil(1150 / 400) = 3 módulos
    inverterKw: 1.2,    // recomendado pelo Asaas
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "XPP",
    tier: "Consciente",
    systemKwp: parseFloat((1.0 * 1.30).toFixed(2)), // 1,0 × 1.30 = 1,30 kWp
    panelWp: 400,
    panelCount: 4,      // ceil(1300 / 400) = 4 módulos
    inverterKw: 1.4,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "XPP",
    tier: "Moderado",
    systemKwp: parseFloat((1.0 * 1.45).toFixed(2)), // 1,0 × 1.45 = 1,45 kWp
    panelWp: 400,
    panelCount: 4,      // ceil(1450 / 400) = 4 módulos
    inverterKw: 1.5,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  },
  {
    category: "XPP",
    tier: "Acelerado",
    systemKwp: parseFloat((1.0 * 1.60).toFixed(2)), // 1,0 × 1.60 = 1,60 kWp
    panelWp: 400,
    panelCount: 4,      // ceil(1600 / 400) = 4 módulos
    inverterKw: 1.6,
    lossFactors: { temperature: 4.0, shading: 3.0, soiling: 3.0, mismatchLidDc: 4.0 }
  }
];

/**
 * === 2) TIPOS E VALIDAÇÕES PARA O BODY DE COBRANÇA ===
 *
 * O front-end deve enviar um JSON contendo:
 * - category: "XPP"
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
 * Retorna a composição do kit XPP para o tier informado.
 * Se não encontrar o tier, retorna undefined.
 */
function findKitByTier(tierName: GenerationTierName): SolarKitComponent | undefined {
  return xppKits.find((kit) => kit.tier === tierName);
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
 * - Visa e Mastercard: até 21× (permitido pela Asaas) :contentReference[oaicite:4]{index=4}
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
 * (opcional, mas recomendado para garantir payload correto)
 */
const chargeValidationRules = [
  body("category")
    .equals("XPP").withMessage("category deve ser 'XPP'"),
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
 * === 5) ENDPOINT Express: CRIAR COBRANÇA NO ASAAS PARA KIT XPP ===
 */
app.post(
  "/xpp/create_charge",
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
      description = "Cobrança de Kit Solar XPP"
    } = req.body as ChargeRequest;

    // 5.3) Garantir que category seja "XPP"
    if (category !== "XPP") {
      return res.status(400).json({
        error: "Para este endpoint, a categoria deve ser 'XPP'."
      });
    }

    // 5.4) Buscar a composição do kit XPP para o tier solicitado
    const kit = findKitByTier(tier);
    if (!kit) {
      return res.status(404).json({
        error: `Não encontramos nenhum kit XPP para o tier '${tier}'.`
      });
    }

    // 5.5) Calcular preço total do kit (módulos + inversor)
    const priceTotal = calculateKitPrice(kit);

    // 5.6) Ajustar/installmentCount com base na bandeira do cartão
    const adjustedInstallments = limitInstallments(creditCardBrand, installmentCount);

    // 5.7) Montar o payload JSON conforme exigências Asaas
    const asaasPayload = {
      customer: customer_id,                       // ID do cliente cadastrado no Asaas
      billingType: "CREDIT_CARD",                  // Cobrança via cartão de crédito
      installmentCount: adjustedInstallments,      // Parcelas ajustadas (<=21 ou <=12)
      value: priceTotal,                           // Valor total calculado do kit
      dueDate: dueDate,                            // Data de vencimento da 1ª parcela
      description: `${description} (XPP - ${kit.tier})`,
      externalReference: `XPP_${kit.tier}_CHARGE_${customer_id}`,
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
 * === 6) ENDPOINT OPCIONAL: LISTAR COMPOSIÇÃO DE KITS XPP ===
 *
 * Rota GET /xpp/kits retorna a lista completa de composições XPP
 * (útil para front-ends exibirem opções ao usuário).
 */
app.get("/xpp/kits", (req: Request, res: Response) => {
  return res.json(xppKits);
});

// Inicia o servidor na porta 3000 (ou conforme variável de ambiente PORT)
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
```

### Explicação detalhada do código TypeScript

1. **Declaração de tipos e array `xppKits` (seção 1)**
    
    - Cada item de `xppKits` contém:
        
        - `category`: fixo em `"XPP"`.
            
        - `tier`: `"Padrão"`, `"Consciente"`, `"Moderado"` ou `"Acelerado"`.
            
        - `systemKwp`: calculado (por ex. 1,15 kWp para `"Padrão"`).
            
        - `panelWp`: sempre 400 (Watt-Peak).
            
        - `panelCount`: número de módulos de 400 Wp arredondado para cima (ex.: 3).
            
        - `inverterKw`: potência recomendada (ex.: 1,2 kW para `"Padrão"`).
            
        - `lossFactors`: apenas informativo, não usado em cálculos de preço.
            
2. **Modelo de requisição `ChargeRequest` (seção 2)**
    
    - O front-end envia JSON contendo `category`, `tier`, `customer_id`, `creditCardBrand`, `creditCardToken`, `installmentCount`, `dueDate` e `description` (opcional).
        
3. **Funções auxiliares (seção 4)**
    
    - `findKitByTier(tierName)`: retorna o item de `xppKits` que bate com o `tierName`. Retorna `undefined` se não achar.
        
    - `calculateKitPrice(kit)`: realiza `(panelCount × PANEL_COST) + (inverterKw × INVERTER_COST_PER_KW)` e arredonda a duas casas.
        
    - `limitInstallments(brand, requested)`:
        
        - Se `brand` for `"VISA"` ou `"MASTERCARD"` (∴ até 21× permitido) ([Asaas - Documentação API](https://docs.asaas.com/changelog/parcelamentos-no-cart%C3%A3o-de-cr%C3%A9dito-em-21x?utm_source=chatgpt.com "Parcelamentos no cartão de crédito em 21x"), [Asaas - Documentação API](https://docs.asaas.com/reference/criar-parcelamento?utm_source=chatgpt.com "Criar parcelamento - Asaas - Documentação API")), retorna `Math.min(requested, 21)`.
            
        - Caso contrário, retorna `Math.min(requested, 12)`.
            
    - `isValidDate(dateString)`: valida formato `AAAA-MM-DD` usando regex.
        
4. **Endpoint `POST /xpp/create_charge` (seção 5)**
    
    - Usa `express-validator` para checar formato e presença dos campos (evitar suposições).
        
    - Se `category !== "XPP"`, retorna 400 (bad request).
        
    - Procura o kit XPP correspondente ao `tier`; se não achar, retorna 404.
        
    - Calcula `priceTotal` via `calculateKitPrice()`.
        
    - Ajusta `installmentCount` via `limitInstallments(creditCardBrand, requested)` para obedecer as regras de bandeira ([Asaas - Documentação API](https://docs.asaas.com/changelog/parcelamentos-no-cart%C3%A3o-de-cr%C3%A9dito-em-21x?utm_source=chatgpt.com "Parcelamentos no cartão de crédito em 21x"), [Asaas - Documentação API](https://docs.asaas.com/reference/criar-parcelamento?utm_source=chatgpt.com "Criar parcelamento - Asaas - Documentação API")).
        
    - Constrói `asaasPayload` com todos os campos necessários para criação de cobrança no Asaas, incluindo:
        
        - `customer`: ID do cliente (string).
            
        - `billingType`: sempre `"CREDIT_CARD"`.
            
        - `installmentCount`: valor ajustado.
            
        - `value`: valor total calculado do kit.
            
        - `dueDate`: data informada pelo front-end.
            
        - `description`: texto (ex.: “Cobrança de Kit Solar XPP (XPP - Padrão)”).
            
        - `externalReference`: string de controle interno (“XPP_{tier}_CHARGE_{customer_id}”).
            
        - `creditCard`: com `creditCardToken`.
            
        - `creditCardHolderInfo`: substitua pelos dados reais do titular do cartão.
            
    - Faz `POST` a `https://www.asaas.com/api/v3/payments?access_token={ASAAS_API_TOKEN}`, enviando `asaasPayload` como JSON.
        
    - Se a resposta do Asaas não for `200` ou `201`, retorna o erro para o front-end (código e corpo JSON).
        
    - Caso contrário, retorna `201 Created` com JSON composto por:
        
        - `kit_composition`: objeto do kit encontrado.
            
        - `price_total`: valor calculado do kit.
            
        - `requested_installments`: parcelas originalmente solicitadas.
            
        - `adjusted_installments`: parcelas ajustadas de fato (≤21 ou ≤12).
            
        - `asaas_response`: corpo JSON completo da resposta Asaas (para auditoria).
            
5. **Endpoint `GET /xpp/kits` (seção 6)**
    
    - Retorna `xppKits` completo, para front-ends exibirem as opções de tier disponíveis.
        

---

## 3. Referências e Citações

1. **Limite de parcelamento – Visa e Mastercard até 21×, demais até 12×**
    
    - “Desde o dia 22/01, estamos permitindo a criação de parcelamentos no cartão de crédito em até 21x para cartões de bandeira Visa e Master. Anteriormente, era suportado parcelamentos de até 12 parcelas para todas as bandeiras. Para outras bandeiras exceto Visa e Master, o limite continua sendo de 12 parcelas.” ([Asaas - Documentação API](https://docs.asaas.com/changelog/parcelamentos-no-cart%C3%A3o-de-cr%C3%A9dito-em-21x?utm_source=chatgpt.com "Parcelamentos no cartão de crédito em 21x"), [Asaas - Documentação API](https://docs.asaas.com/reference/criar-parcelamento?utm_source=chatgpt.com "Criar parcelamento - Asaas - Documentação API"))
        
    - “Para outras bandeiras, exceto Visa e Master, o limite continua sendo de 12 parcelas.” ([Asaas - Documentação API](https://docs.asaas.com/docs/criar-uma-cobranca-parcelada?utm_source=chatgpt.com "Criar uma cobrança parcelada - Asaas - Documentação API"), [Asaas - Documentação API](https://docs.asaas.com/reference/criar-cobranca-com-cartao-de-credito?utm_source=chatgpt.com "Criar cobrança com cartão de crédito"))
        
2. **Documentação de criação de cobrança parcelada (Asaas)**
    
    - “É permitido a criação de parcelamentos no cartão de crédito em até 21x para cartões de bandeira Visa e Master. Anteriormente, era suportado parcelamentos de até 12 parcelas para todas as bandeiras.” ([Asaas - Documentação API](https://docs.asaas.com/reference/criar-parcelamento?utm_source=chatgpt.com "Criar parcelamento - Asaas - Documentação API"), [Asaas - Documentação API](https://docs.asaas.com/reference/criar-cobranca-com-cartao-de-credito?utm_source=chatgpt.com "Criar cobrança com cartão de crédito"))
        

---

### Conclusão

- **Este template** cobre **exclusivamente** a categoria de projeto **“XPP”** e embarca toda a **lógica de precificação** (painéis + inversor) e **limitação de parcelas** (21× para Visa/Master, 12× para demais) ([Asaas - Documentação API](https://docs.asaas.com/changelog/parcelamentos-no-cart%C3%A3o-de-cr%C3%A9dito-em-21x?utm_source=chatgpt.com "Parcelamentos no cartão de crédito em 21x"), [Asaas - Documentação API](https://docs.asaas.com/reference/criar-parcelamento?utm_source=chatgpt.com "Criar parcelamento - Asaas - Documentação API")).
    
- **FastAPI (Python)** e **Express (TypeScript)** mostram, passo a passo, como:
    
    1. **Receber requisitado** com `category="XPP"`, `tier` e dados de cartão.
        
    2. **Encontrar o kit** e calcular o preço.
        
    3. **Ajustar parcelas** de acordo com bandeira do cartão.
        
    4. **Montar payload** para Asaas (`/payments?access_token=...`).
        
    5. **Enviar requisição** e tratar resposta (sucesso ou erro).
        
- Os **comentários detalhados** explicam cada linha, sem abreviações nem exceções, facilitando a compreensão e manutenção futura.
    
- Basta **replicar este padrão** para outras categorias (PP, P, M etc.), trocando apenas os dados de composição (`averageKwp`, `inverterKw`, `panelCount`, valores de `panelWp` se necessário etc.).
    

Com estes dois exemplos, você tem a base completa para gerar endpoints de cobrança para kits solares XPP, respeitando integralmente as regras de parcelamento definidas pela Asaas.