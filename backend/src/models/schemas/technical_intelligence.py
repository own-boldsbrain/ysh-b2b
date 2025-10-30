#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
technical_intelligence.py
=========================
Schema consolidado de inteligência técnica e estratégica para SKUs.

Integra:
- Specs técnicas do equipamento (power, voltage, efficiency, MPPT)
- KPIs solares (NASA POWER: GHI/DNI/DHI, temperatura, vento)
- Performance real (PVLIB: IV curves, POA, yield, capacity factor)
- ROI/Payback/Manutenção (análise financeira estratégica)
- Vida útil e degradação (análise temporal)
- Certificações e compliance (INMETRO, IEC, NBR, ABNT)

Objetivo: Fornecer base de dados completa para decisões técnicas e estratégicas,
acessível tanto para engenheiros quanto para gestores/investidores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


# ==================== Enums ====================


class EquipmentCategory(str, Enum):
    """Categoria de equipamento fotovoltaico."""
    INVERTER = "inversores"
    PANEL = "paineis_solares"
    STRUCTURE = "estruturas"
    BATTERY = "baterias"
    STRING_BOX = "string_box"
    MONITORING = "monitoramento"


class PowerRange(str, Enum):
    """Faixa de potência para classificação."""
    RESIDENTIAL = "residential"  # < 10 kW
    COMMERCIAL_SMALL = "commercial_small"  # 10-50 kW
    COMMERCIAL_MEDIUM = "commercial_medium"  # 50-100 kW
    COMMERCIAL_LARGE = "commercial_large"  # 100-500 kW
    INDUSTRIAL = "industrial"  # > 500 kW


class ApplicationType(str, Enum):
    """Tipo de aplicação recomendada."""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    RURAL = "rural"
    RETROFIT = "retrofit"
    OFF_GRID = "off_grid"


class CertificationStatus(str, Enum):
    """Status de certificação."""
    CERTIFIED = "certified"
    COMPLIANT = "compliant"
    PENDING = "pending"
    EXPIRED = "expired"
    NOT_APPLICABLE = "not_applicable"


# ==================== Specs Técnicas ====================


class EquipmentSpecs(BaseModel):
    """Especificações técnicas base do equipamento."""
    
    # Identificação
    sku: str = Field(..., description="SKU único do produto")
    manufacturer: str = Field(..., description="Fabricante")
    model: str = Field(..., description="Modelo")
    category: EquipmentCategory = Field(..., description="Categoria do equipamento")
    
    # Características elétricas principais
    power_kw: float = Field(..., gt=0, description="Potência nominal (kW)")
    voltage_v: int = Field(..., gt=0, description="Tensão nominal (V)")
    mppt_count: Optional[int] = Field(None, ge=0, description="Número de MPPTs")
    efficiency_percent: Optional[float] = Field(None, ge=0, le=100, description="Eficiência nominal (%)")
    
    # Características físicas
    dimensions_mm: Optional[Dict[str, float]] = Field(
        None,
        description="Dimensões (altura, largura, profundidade) em mm"
    )
    weight_kg: Optional[float] = Field(None, gt=0, description="Peso (kg)")
    ip_rating: Optional[str] = Field(None, description="Grau de proteção IP")
    
    # Condições operacionais
    temp_range_c: Optional[Dict[str, float]] = Field(
        None,
        description="Faixa de temperatura operacional (min, max) em °C"
    )
    humidity_range_pct: Optional[Dict[str, float]] = Field(
        None,
        description="Faixa de umidade relativa (min, max) em %"
    )
    altitude_max_m: Optional[int] = Field(None, ge=0, description="Altitude máxima (m)")
    
    # Preço e disponibilidade
    price_brl: float = Field(..., gt=0, description="Preço de referência (BRL)")
    availability: bool = Field(True, description="Disponibilidade em estoque")
    lead_time_days: Optional[int] = Field(None, ge=0, description="Prazo de entrega (dias)")
    
    # Imagens e documentação
    image_url: Optional[str] = Field(None, description="URL da imagem principal")
    datasheet_url: Optional[str] = Field(None, description="URL do datasheet técnico")
    
    class Config:
        use_enum_values = True


# ==================== KPIs Solares (NASA POWER) ====================


class SolarKPIs(BaseModel):
    """KPIs solares obtidos do NASA POWER para localização específica."""
    
    # Localização
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    
    # Irradiância anual média (kWh/m²/ano)
    ghi_annual_kwhm2: Optional[float] = Field(None, ge=0, description="Global Horizontal Irradiance")
    dni_annual_kwhm2: Optional[float] = Field(None, ge=0, description="Direct Normal Irradiance")
    dhi_annual_kwhm2: Optional[float] = Field(None, ge=0, description="Diffuse Horizontal Irradiance")
    
    # Condições meteorológicas médias
    temp_avg_c: Optional[float] = Field(None, description="Temperatura média anual (°C)")
    wind_speed_avg_ms: Optional[float] = Field(None, ge=0, description="Velocidade média do vento (m/s)")
    
    # Metadados
    data_source: str = Field("NASA-POWER", description="Fonte dos dados solares")
    years_range: Optional[str] = Field(None, description="Período dos dados (ex: 2001-2024)")
    fetch_date: Optional[datetime] = Field(None, description="Data da última atualização")
    
    class Config:
        use_enum_values = True


# ==================== Performance Real (PVLIB) ====================


class IVCurveData(BaseModel):
    """Dados de curva IV calculada para condições específicas."""
    
    # Condições de operação
    irradiance_wm2: float = Field(..., ge=0, description="Irradiância efetiva (W/m²)")
    cell_temp_c: float = Field(..., description="Temperatura da célula (°C)")
    
    # Pontos característicos da curva IV
    i_sc: float = Field(..., ge=0, description="Corrente de curto-circuito (A)")
    v_oc: float = Field(..., ge=0, description="Tensão de circuito aberto (V)")
    i_mp: float = Field(..., ge=0, description="Corrente no MPP (A)")
    v_mp: float = Field(..., ge=0, description="Tensão no MPP (V)")
    p_mp: float = Field(..., ge=0, description="Potência no MPP (W)")
    
    # Fill factor
    fill_factor: Optional[float] = Field(None, ge=0, le=1, description="Fill Factor (adimensional)")
    
    class Config:
        use_enum_values = True


class PerformanceMetrics(BaseModel):
    """Métricas de performance real calculadas com PVLIB."""
    
    # Yield e capacity factor
    specific_yield_kwhkwp_y: Optional[float] = Field(
        None,
        ge=0,
        description="Yield específico anual (kWh/kWp/ano)"
    )
    capacity_factor_pct: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Capacity Factor (%)"
    )
    
    # Ângulos ótimos
    optimal_tilt_deg: Optional[float] = Field(None, ge=0, le=90, description="Inclinação ótima (°)")
    optimal_azimuth_deg: Optional[float] = Field(None, ge=0, le=360, description="Azimute ótimo (°)")
    
    # Geração mensal (kWh)
    monthly_generation_kwh: Optional[Dict[str, float]] = Field(
        None,
        description="Geração mensal (jan-dez) em kWh"
    )
    
    # Curvas IV para diferentes condições
    iv_curves: Optional[List[IVCurveData]] = Field(
        None,
        description="Curvas IV calculadas para diferentes condições"
    )
    
    # Perdas
    system_losses_pct: float = Field(14.0, ge=0, le=100, description="Perdas totais do sistema (%)")
    
    # Metadados
    calculation_method: str = Field("PVLIB-PVWatts", description="Método de cálculo")
    calculation_date: Optional[datetime] = Field(None, description="Data do cálculo")
    
    class Config:
        use_enum_values = True


# ==================== Análise Financeira Estratégica ====================


class FinancialAnalysis(BaseModel):
    """Análise financeira e ROI para pessoas não-técnicas."""
    
    # Investimento inicial
    equipment_cost_brl: float = Field(..., gt=0, description="Custo do equipamento (BRL)")
    installation_cost_brl: Optional[float] = Field(None, ge=0, description="Custo de instalação (BRL)")
    total_investment_brl: float = Field(..., gt=0, description="Investimento total (BRL)")
    
    # Geração e economia
    annual_generation_kwh: float = Field(..., ge=0, description="Geração anual estimada (kWh)")
    energy_tariff_brl_kwh: float = Field(..., gt=0, description="Tarifa de energia (BRL/kWh)")
    annual_savings_brl: float = Field(..., ge=0, description="Economia anual estimada (BRL)")
    
    # ROI e Payback
    roi_percent: Optional[float] = Field(None, description="ROI total ao final da vida útil (%)")
    simple_payback_years: Optional[float] = Field(None, ge=0, description="Payback simples (anos)")
    discounted_payback_years: Optional[float] = Field(None, ge=0, description="Payback descontado (anos)")
    
    # Análise de sensibilidade
    npv_brl: Optional[float] = Field(None, description="Valor Presente Líquido (BRL)")
    irr_percent: Optional[float] = Field(None, description="Taxa Interna de Retorno (%)")
    
    # Manutenção
    annual_maintenance_cost_brl: Optional[float] = Field(
        None,
        ge=0,
        description="Custo anual de manutenção (BRL)"
    )
    maintenance_schedule: Optional[List[str]] = Field(
        None,
        description="Cronograma de manutenção preventiva"
    )
    
    # Degradação
    degradation_rate_pct_year: float = Field(
        0.5,
        ge=0,
        le=5,
        description="Taxa de degradação anual (%)"
    )
    
    class Config:
        use_enum_values = True


# ==================== Vida Útil e Garantias ====================


class LifecycleData(BaseModel):
    """Dados de vida útil, degradação e garantias."""
    
    # Vida útil
    design_life_years: int = Field(..., gt=0, description="Vida útil de projeto (anos)")
    expected_life_years: int = Field(..., gt=0, description="Vida útil esperada (anos)")
    
    # Garantias
    warranty_product_years: Optional[int] = Field(None, ge=0, description="Garantia de produto (anos)")
    warranty_performance_years: Optional[int] = Field(None, ge=0, description="Garantia de performance (anos)")
    warranty_performance_pct: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="% de performance garantida ao final da garantia"
    )
    
    # Degradação
    degradation_rate_year1_pct: Optional[float] = Field(
        None,
        ge=0,
        le=10,
        description="Taxa de degradação no primeiro ano (%)"
    )
    degradation_rate_annual_pct: float = Field(
        0.5,
        ge=0,
        le=5,
        description="Taxa de degradação anual após primeiro ano (%)"
    )
    
    # Performance ao longo do tempo (anos: % de performance)
    performance_timeline: Optional[Dict[int, float]] = Field(
        None,
        description="Performance estimada ao longo dos anos (ano: % performance)"
    )
    
    # Manutenções programadas
    major_maintenance_years: Optional[List[int]] = Field(
        None,
        description="Anos em que manutenções maiores são recomendadas"
    )
    
    class Config:
        use_enum_values = True


# ==================== Certificações e Compliance ====================


class Certification(BaseModel):
    """Certificação individual."""
    
    name: str = Field(..., description="Nome da certificação")
    issuer: str = Field(..., description="Órgão emissor")
    status: CertificationStatus = Field(..., description="Status da certificação")
    certificate_number: Optional[str] = Field(None, description="Número do certificado")
    issue_date: Optional[datetime] = Field(None, description="Data de emissão")
    expiry_date: Optional[datetime] = Field(None, description="Data de expiração")
    document_url: Optional[str] = Field(None, description="URL do documento")
    
    class Config:
        use_enum_values = True


class ComplianceData(BaseModel):
    """Dados de compliance e certificações regulatórias."""
    
    # Certificações brasileiras obrigatórias
    inmetro: Optional[Certification] = Field(None, description="Certificação INMETRO")
    aneel: Optional[Certification] = Field(None, description="Certificação ANEEL")
    
    # Normas técnicas brasileiras
    nbr_16690: Optional[Certification] = Field(None, description="NBR 16690 (Instalações elétricas FV)")
    nbr_16274: Optional[Certification] = Field(None, description="NBR 16274 (Sistemas FV - Requisitos)")
    
    # Normas internacionais
    iec_61727: Optional[Certification] = Field(None, description="IEC 61727 (Grid-connected systems)")
    iec_62116: Optional[Certification] = Field(None, description="IEC 62116 (Anti-islanding)")
    
    # Certificações adicionais
    additional_certs: Optional[List[Certification]] = Field(
        None,
        description="Certificações adicionais (UL, CE, TÜV, etc.)"
    )
    
    # Compliance geral
    is_compliant: bool = Field(True, description="Está em compliance com todas as normas?")
    compliance_notes: Optional[str] = Field(None, description="Observações sobre compliance")
    
    class Config:
        use_enum_values = True


# ==================== Recomendações Estratégicas ====================


class StrategicRecommendation(BaseModel):
    """Recomendação estratégica baseada em análise técnica e financeira."""
    
    # Classificação
    priority: str = Field(..., description="Prioridade (high, medium, low)")
    category: str = Field(..., description="Categoria (financial, technical, operational)")
    
    # Conteúdo
    title: str = Field(..., description="Título da recomendação")
    description: str = Field(..., description="Descrição detalhada")
    impact: str = Field(..., description="Impacto esperado")
    
    # Ação
    action_items: List[str] = Field(default_factory=list, description="Itens de ação")
    responsible: Optional[str] = Field(None, description="Responsável pela ação")
    deadline: Optional[datetime] = Field(None, description="Prazo")
    
    class Config:
        use_enum_values = True


# ==================== Schema Consolidado ====================


class TechnicalIntelligenceSKU(BaseModel):
    """
    Schema consolidado de inteligência técnica e estratégica para SKUs.
    
    Integra todas as camadas de informação:
    - Specs técnicas
    - KPIs solares (NASA POWER)
    - Performance real (PVLIB)
    - ROI/Payback/Manutenção
    - Vida útil e degradação
    - Certificações e compliance
    - Recomendações estratégicas
    """
    
    # ===== Camada 1: Identificação e Specs Técnicas =====
    specs: EquipmentSpecs = Field(..., description="Especificações técnicas do equipamento")
    
    # ===== Camada 2: Contexto Solar (Localização) =====
    solar_kpis: Optional[SolarKPIs] = Field(
        None,
        description="KPIs solares para localização específica (NASA POWER)"
    )
    
    # ===== Camada 3: Performance Real (Simulações) =====
    performance: Optional[PerformanceMetrics] = Field(
        None,
        description="Métricas de performance calculadas com PVLIB"
    )
    
    # ===== Camada 4: Análise Financeira =====
    financial: Optional[FinancialAnalysis] = Field(
        None,
        description="Análise financeira e ROI"
    )
    
    # ===== Camada 5: Vida Útil e Degradação =====
    lifecycle: Optional[LifecycleData] = Field(
        None,
        description="Dados de vida útil, degradação e garantias"
    )
    
    # ===== Camada 6: Certificações e Compliance =====
    compliance: Optional[ComplianceData] = Field(
        None,
        description="Certificações e compliance regulatório"
    )
    
    # ===== Camada 7: Recomendações Estratégicas =====
    recommendations: Optional[List[StrategicRecommendation]] = Field(
        None,
        description="Recomendações estratégicas baseadas em análise completa"
    )
    
    # ===== Metadados =====
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criação")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Última atualização")
    data_version: str = Field("1.0.0", description="Versão do schema de dados")
    
    # ===== Métodos auxiliares =====
    
    def get_power_range(self) -> PowerRange:
        """Classifica o equipamento por faixa de potência."""
        power = self.specs.power_kw
        if power < 10:
            return PowerRange.RESIDENTIAL
        elif power < 50:
            return PowerRange.COMMERCIAL_SMALL
        elif power < 100:
            return PowerRange.COMMERCIAL_MEDIUM
        elif power < 500:
            return PowerRange.COMMERCIAL_LARGE
        else:
            return PowerRange.INDUSTRIAL
    
    def get_recommended_applications(self) -> List[ApplicationType]:
        """Retorna aplicações recomendadas baseado na potência."""
        power_range = self.get_power_range()
        mapping = {
            PowerRange.RESIDENTIAL: [ApplicationType.RESIDENTIAL, ApplicationType.RETROFIT],
            PowerRange.COMMERCIAL_SMALL: [ApplicationType.COMMERCIAL, ApplicationType.RURAL],
            PowerRange.COMMERCIAL_MEDIUM: [ApplicationType.COMMERCIAL, ApplicationType.INDUSTRIAL],
            PowerRange.COMMERCIAL_LARGE: [ApplicationType.INDUSTRIAL, ApplicationType.COMMERCIAL],
            PowerRange.INDUSTRIAL: [ApplicationType.INDUSTRIAL],
        }
        return mapping.get(power_range, [])
    
    def calculate_lifetime_energy_kwh(self) -> Optional[float]:
        """Calcula energia total gerada ao longo da vida útil (considerando degradação)."""
        if not self.performance or not self.lifecycle:
            return None
        
        annual_gen = self.performance.specific_yield_kwhkwp_y
        if not annual_gen:
            return None
        
        life_years = self.lifecycle.expected_life_years
        degradation_rate = self.lifecycle.degradation_rate_annual_pct / 100.0
        
        total_energy = 0.0
        for year in range(1, life_years + 1):
            degradation_factor = (1 - degradation_rate) ** (year - 1)
            total_energy += annual_gen * self.specs.power_kw * degradation_factor
        
        return total_energy
    
    def calculate_lcoe_brl_kwh(self) -> Optional[float]:
        """Calcula LCOE (Levelized Cost of Energy) em BRL/kWh."""
        if not self.financial or not self.lifecycle:
            return None
        
        lifetime_energy = self.calculate_lifetime_energy_kwh()
        if not lifetime_energy:
            return None
        
        total_cost = self.financial.total_investment_brl
        if self.financial.annual_maintenance_cost_brl:
            total_cost += (
                self.financial.annual_maintenance_cost_brl
                * self.lifecycle.expected_life_years
            )
        
        return total_cost / lifetime_energy
    
    def is_investment_viable(self, max_payback_years: float = 7.0) -> bool:
        """Verifica se o investimento é viável baseado no payback."""
        if not self.financial or not self.financial.simple_payback_years:
            return False
        return self.financial.simple_payback_years <= max_payback_years
    
    def get_compliance_score(self) -> float:
        """Retorna score de compliance (0-100)."""
        if not self.compliance:
            return 0.0
        
        required_certs = [
            self.compliance.inmetro,
            self.compliance.aneel,
            self.compliance.nbr_16690,
            self.compliance.iec_61727,
        ]
        
        valid_count = sum(
            1 for cert in required_certs
            if cert and cert.status == CertificationStatus.CERTIFIED
        )
        
        return (valid_count / len(required_certs)) * 100.0
    
    class Config:
        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat()}


# ==================== Exports ====================

__all__ = [
    # Enums
    "EquipmentCategory",
    "PowerRange",
    "ApplicationType",
    "CertificationStatus",
    # Models
    "EquipmentSpecs",
    "SolarKPIs",
    "IVCurveData",
    "PerformanceMetrics",
    "FinancialAnalysis",
    "LifecycleData",
    "Certification",
    "ComplianceData",
    "StrategicRecommendation",
    "TechnicalIntelligenceSKU",
]
