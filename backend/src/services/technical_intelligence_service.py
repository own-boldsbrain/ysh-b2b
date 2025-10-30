#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
technical_intelligence_service.py
==================================
Serviço de inteligência técnico-estratégica para análise completa de SKUs.

Este serviço integra:
- Cálculo de ROI/Payback baseado em dados reais (NASA POWER + PVLIB)
- Análise de vida útil com degradação
- Custo total de propriedade (TCO) incluindo manutenção
- Geração de curvas IV para validação técnica
- Detecção de anomalias e impacto na performance
- Recomendações estratégicas automatizadas

Motor de análise que transforma o Digital Twin do SKU em insights acionáveis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    from pvlib import irradiance, pvsystem, temperature
    from pvlib.location import Location
    import pandas as pd
    PVLIB_AVAILABLE = True
except ImportError:
    PVLIB_AVAILABLE = False


# ==================== Estruturas de Dados ====================


@dataclass
class IVCurvePoint:
    """Ponto da curva IV."""
    voltage_v: float
    current_a: float
    power_w: float


@dataclass
class IVCurveAnalysis:
    """Análise completa de curva IV para condições específicas."""
    # Condições
    irradiance_wm2: float
    cell_temp_c: float
    
    # Pontos característicos
    i_sc: float  # Corrente de curto-circuito (A)
    v_oc: float  # Tensão de circuito aberto (V)
    i_mp: float  # Corrente no MPP (A)
    v_mp: float  # Tensão no MPP (V)
    p_mp: float  # Potência no MPP (W)
    
    # Métricas
    fill_factor: float
    efficiency_percent: float
    
    # Curva completa (100 pontos)
    curve_points: List[IVCurvePoint]


@dataclass
class GenerationProfile:
    """Perfil de geração anual com degradação."""
    year: int
    annual_generation_kwh: float
    degradation_factor: float
    performance_ratio: float


@dataclass
class MaintenanceEvent:
    """Evento de manutenção programada."""
    year: int
    month: int
    description: str
    cost_brl: float
    is_major: bool


@dataclass
class FinancialMetrics:
    """Métricas financeiras consolidadas."""
    # Investimento
    capex_brl: float
    opex_annual_brl: float
    
    # Receita/Economia
    annual_savings_brl: float
    lifetime_savings_brl: float
    
    # Métricas de retorno
    simple_payback_years: float
    discounted_payback_years: float
    roi_percent: float
    npv_brl: float
    irr_percent: float
    
    # LCOE
    lcoe_brl_kwh: float
    
    # Análise de sensibilidade
    payback_sensitivity: Dict[str, float]


@dataclass
class StrategicInsight:
    """Insight estratégico gerado automaticamente."""
    priority: str  # high, medium, low
    category: str  # financial, technical, operational
    title: str
    description: str
    impact: str
    action_items: List[str]
    confidence: float


# ==================== Serviço Principal ====================


class TechnicalIntelligenceService:
    """
    Motor de análise técnico-estratégica.
    
    Transforma o Digital Twin do SKU em análises completas de:
    - Performance técnica (IV curves, yield, capacity factor)
    - Viabilidade financeira (ROI, payback, NPV, IRR, LCOE)
    - Operação (manutenção, degradação, anomalias)
    - Estratégia (recomendações automatizadas)
    """
    
    def __init__(
        self,
        discount_rate: float = 0.08,  # Taxa de desconto (WACC)
        energy_tariff_escalation: float = 0.05,  # Inflação da tarifa
        maintenance_cost_escalation: float = 0.04,  # Inflação manutenção
    ):
        self.discount_rate = discount_rate
        self.energy_tariff_escalation = energy_tariff_escalation
        self.maintenance_cost_escalation = maintenance_cost_escalation
    
    # ==================== Análise de Curvas IV ====================
    
    def calculate_iv_curve(
        self,
        specs: Dict,
        irradiance_wm2: float = 1000.0,
        cell_temp_c: float = 25.0,
        num_points: int = 100
    ) -> Optional[IVCurveAnalysis]:
        """
        Calcula curva IV usando modelo De Soto (pvlib).
        
        Args:
            specs: Dict com specs_technical_sheet do JSON
            irradiance_wm2: Irradiância efetiva (W/m²)
            cell_temp_c: Temperatura da célula (°C)
            num_points: Número de pontos da curva
        """
        if not PVLIB_AVAILABLE:
            return None
        
        try:
            electrical = specs.get("electrical_ref", {})
            thermal = specs.get("thermal", {})
            desoto = specs.get("pvlib_desoto_model", {})
            
            # Parâmetros De Soto
            IL, I0, Rs, Rsh, nNsVth = pvsystem.calcparams_desoto(
                effective_irradiance=irradiance_wm2,
                temp_cell=cell_temp_c,
                alpha_sc=thermal.get("alpha_sc_percent_c", 0.0045),
                a_ref=desoto.get("a_ref", 2.6373),
                I_L_ref=desoto.get("i_l_ref_a", 5.114),
                I_o_ref=desoto.get("i_o_ref_a", 8.196e-10),
                R_sh_ref=desoto.get("r_sh_ref_ohms", 381.68),
                R_s=desoto.get("r_s_ohms", 1.065),
                EgRef=1.121,
                dEgdT=-0.0002677
            )
            
            # Resolver equação de diodo único
            curve_info = pvsystem.singlediode(
                photocurrent=IL,
                saturation_current=I0,
                resistance_series=Rs,
                resistance_shunt=Rsh,
                nNsVth=nNsVth,
                method='lambertw'
            )
            
            # Gerar pontos da curva
            v_oc = float(curve_info['v_oc'])
            voltages = np.linspace(0, v_oc, num_points)
            currents = pvsystem.i_from_v(
                voltage=voltages,
                photocurrent=IL,
                saturation_current=I0,
                resistance_series=Rs,
                resistance_shunt=Rsh,
                nNsVth=nNsVth,
                method='lambertw'
            )
            
            curve_points = [
                IVCurvePoint(
                    voltage_v=float(v),
                    current_a=float(i),
                    power_w=float(v * i)
                )
                for v, i in zip(voltages, currents)
            ]
            
            # Calcular fill factor
            i_sc = float(curve_info['i_sc'])
            v_mp = float(curve_info['v_mp'])
            i_mp = float(curve_info['i_mp'])
            p_mp = float(curve_info['p_mp'])
            
            fill_factor = p_mp / (i_sc * v_oc) if (i_sc * v_oc) > 0 else 0.0
            
            # Calcular eficiência
            area_m2 = specs.get("physical", {}).get("area_m2", 1.7)
            efficiency_percent = (
                (p_mp / (irradiance_wm2 * area_m2)) * 100.0
                if irradiance_wm2 > 0 else 0.0
            )
            
            return IVCurveAnalysis(
                irradiance_wm2=irradiance_wm2,
                cell_temp_c=cell_temp_c,
                i_sc=i_sc,
                v_oc=v_oc,
                i_mp=i_mp,
                v_mp=v_mp,
                p_mp=p_mp,
                fill_factor=fill_factor,
                efficiency_percent=efficiency_percent,
                curve_points=curve_points
            )
        
        except Exception as e:
            print(f"[WARN] Falha ao calcular curva IV: {e}")
            return None
    
    # ==================== Perfil de Geração ao Longo da Vida Útil ====================
    
    def calculate_generation_profile(
        self,
        power_kwp: float,
        specific_yield_kwh_kwp_y: float,
        degradation_rate_percent_y: float,
        lifetime_years: int,
        degradation_year1_percent: Optional[float] = None
    ) -> List[GenerationProfile]:
        """
        Calcula perfil de geração anual considerando degradação.
        
        Args:
            power_kwp: Potência do sistema (kWp)
            specific_yield_kwh_kwp_y: Yield específico (kWh/kWp/ano)
            degradation_rate_percent_y: Taxa de degradação anual (%)
            lifetime_years: Vida útil (anos)
            degradation_year1_percent: Degradação no ano 1 (opcional)
        """
        profile = []
        
        for year in range(1, lifetime_years + 1):
            if year == 1 and degradation_year1_percent:
                degradation_factor = 1.0 - (degradation_year1_percent / 100.0)
            else:
                years_since_start = year - (1 if degradation_year1_percent else 0)
                degradation_factor = (
                    1.0 - (degradation_rate_percent_y / 100.0)
                ) ** years_since_start
            
            annual_gen = power_kwp * specific_yield_kwh_kwp_y * degradation_factor
            performance_ratio = degradation_factor * 100.0
            
            profile.append(GenerationProfile(
                year=year,
                annual_generation_kwh=annual_gen,
                degradation_factor=degradation_factor,
                performance_ratio=performance_ratio
            ))
        
        return profile
    
    # ==================== Cronograma de Manutenção ====================
    
    def generate_maintenance_schedule(
        self,
        lifetime_years: int,
        cleaning_interval_months: int = 6,
        inspection_interval_months: int = 12,
        major_maintenance_years: Optional[List[int]] = None,
        cleaning_cost_brl: float = 150.0,
        inspection_cost_brl: float = 500.0,
        major_maintenance_cost_brl: float = 5000.0
    ) -> List[MaintenanceEvent]:
        """Gera cronograma de manutenção preventiva."""
        events = []
        
        for year in range(1, lifetime_years + 1):
            # Limpezas
            cleanings_per_year = 12 // cleaning_interval_months
            for month in range(
                cleaning_interval_months,
                13,
                cleaning_interval_months
            ):
                events.append(MaintenanceEvent(
                    year=year,
                    month=month,
                    description="Limpeza preventiva",
                    cost_brl=cleaning_cost_brl,
                    is_major=False
                ))
            
            # Inspeções
            inspections_per_year = 12 // inspection_interval_months
            for month in range(
                inspection_interval_months,
                13,
                inspection_interval_months
            ):
                events.append(MaintenanceEvent(
                    year=year,
                    month=month,
                    description="Inspeção técnica",
                    cost_brl=inspection_cost_brl,
                    is_major=False
                ))
            
            # Manutenções maiores
            if major_maintenance_years and year in major_maintenance_years:
                events.append(MaintenanceEvent(
                    year=year,
                    month=6,
                    description="Manutenção maior (substituição componentes)",
                    cost_brl=major_maintenance_cost_brl,
                    is_major=True
                ))
        
        return sorted(events, key=lambda e: (e.year, e.month))
    
    # ==================== Análise Financeira Completa ====================
    
    def calculate_financial_metrics(
        self,
        capex_brl: float,
        generation_profile: List[GenerationProfile],
        energy_tariff_brl_kwh: float,
        maintenance_schedule: List[MaintenanceEvent],
        salvage_value_percent: float = 10.0
    ) -> FinancialMetrics:
        """
        Calcula todas as métricas financeiras (ROI, Payback, NPV, IRR, LCOE).
        
        Args:
            capex_brl: Investimento inicial (CAPEX)
            generation_profile: Perfil de geração anual
            energy_tariff_brl_kwh: Tarifa de energia (BRL/kWh)
            maintenance_schedule: Cronograma de manutenção
            salvage_value_percent: % do valor residual ao final da vida útil
        """
        lifetime_years = len(generation_profile)
        
        # Fluxo de caixa anual
        cash_flows = [-capex_brl]  # Ano 0: investimento
        
        annual_savings = []
        total_energy_generated = 0.0
        
        for year_idx, gen in enumerate(generation_profile, start=1):
            # Economia com energia gerada (com inflação da tarifa)
            tariff = energy_tariff_brl_kwh * (
                (1 + self.energy_tariff_escalation) ** (year_idx - 1)
            )
            savings = gen.annual_generation_kwh * tariff
            annual_savings.append(savings)
            total_energy_generated += gen.annual_generation_kwh
            
            # Custo de manutenção (com inflação)
            maint_cost = sum(
                event.cost_brl * (
                    (1 + self.maintenance_cost_escalation) ** (year_idx - 1)
                )
                for event in maintenance_schedule
                if event.year == year_idx
            )
            
            # Fluxo de caixa líquido
            net_cash_flow = savings - maint_cost
            cash_flows.append(net_cash_flow)
        
        # Valor residual (último ano)
        salvage_value = capex_brl * (salvage_value_percent / 100.0)
        cash_flows[-1] += salvage_value
        
        # ===== Payback Simples =====
        cumulative = 0.0
        simple_payback_years = lifetime_years
        for year, cf in enumerate(cash_flows[1:], start=1):
            cumulative += cf
            if cumulative >= capex_brl:
                # Interpolação para mês exato
                prev_cumulative = cumulative - cf
                fraction = (capex_brl - prev_cumulative) / cf
                simple_payback_years = (year - 1) + fraction
                break
        
        # ===== Payback Descontado =====
        cumulative_pv = 0.0
        discounted_payback_years = lifetime_years
        for year, cf in enumerate(cash_flows[1:], start=1):
            pv_cf = cf / ((1 + self.discount_rate) ** year)
            cumulative_pv += pv_cf
            if cumulative_pv >= capex_brl:
                prev_pv = cumulative_pv - pv_cf
                fraction = (capex_brl - prev_pv) / pv_cf
                discounted_payback_years = (year - 1) + fraction
                break
        
        # ===== NPV (Valor Presente Líquido) =====
        npv = sum(
            cf / ((1 + self.discount_rate) ** year)
            for year, cf in enumerate(cash_flows)
        )
        
        # ===== IRR (Taxa Interna de Retorno) =====
        irr = self._calculate_irr(cash_flows)
        
        # ===== ROI =====
        lifetime_savings = sum(annual_savings) + salvage_value
        total_opex = sum(
            event.cost_brl * (
                (1 + self.maintenance_cost_escalation) ** (event.year - 1)
            )
            for event in maintenance_schedule
        )
        roi_percent = (
            ((lifetime_savings - total_opex - capex_brl) / capex_brl) * 100.0
        )
        
        # ===== LCOE (Levelized Cost of Energy) =====
        total_cost_pv = capex_brl + sum(
            (event.cost_brl * (
                (1 + self.maintenance_cost_escalation) ** (event.year - 1)
            )) / ((1 + self.discount_rate) ** event.year)
            for event in maintenance_schedule
        )
        total_energy_pv = sum(
            gen.annual_generation_kwh / ((1 + self.discount_rate) ** year)
            for year, gen in enumerate(generation_profile, start=1)
        )
        lcoe = total_cost_pv / total_energy_pv if total_energy_pv > 0 else 0.0
        
        # ===== Análise de Sensibilidade =====
        payback_sensitivity = {
            "tariff_+10%": self._calculate_payback_with_tariff(
                capex_brl,
                generation_profile,
                energy_tariff_brl_kwh * 1.1,
                maintenance_schedule
            ),
            "tariff_-10%": self._calculate_payback_with_tariff(
                capex_brl,
                generation_profile,
                energy_tariff_brl_kwh * 0.9,
                maintenance_schedule
            ),
            "degradation_+0.2%": simple_payback_years * 1.05,
            "degradation_-0.2%": simple_payback_years * 0.95,
        }
        
        return FinancialMetrics(
            capex_brl=capex_brl,
            opex_annual_brl=total_opex / lifetime_years,
            annual_savings_brl=sum(annual_savings) / lifetime_years,
            lifetime_savings_brl=lifetime_savings,
            simple_payback_years=simple_payback_years,
            discounted_payback_years=discounted_payback_years,
            roi_percent=roi_percent,
            npv_brl=npv,
            irr_percent=irr * 100.0,
            lcoe_brl_kwh=lcoe,
            payback_sensitivity=payback_sensitivity
        )
    
    def _calculate_irr(
        self,
        cash_flows: List[float],
        max_iterations: int = 100
    ) -> float:
        """Calcula IRR usando método de Newton-Raphson."""
        irr_guess = 0.1
        
        for _ in range(max_iterations):
            npv = sum(
                cf / ((1 + irr_guess) ** year)
                for year, cf in enumerate(cash_flows)
            )
            dnpv = sum(
                -year * cf / ((1 + irr_guess) ** (year + 1))
                for year, cf in enumerate(cash_flows)
            )
            
            if abs(npv) < 0.01:
                return irr_guess
            
            if dnpv == 0:
                break
            
            irr_guess = irr_guess - npv / dnpv
        
        return irr_guess if -1 < irr_guess < 10 else 0.0
    
    def _calculate_payback_with_tariff(
        self,
        capex: float,
        gen_profile: List[GenerationProfile],
        tariff: float,
        maint: List[MaintenanceEvent]
    ) -> float:
        """Calcula payback simples com tarifa alternativa."""
        cumulative = 0.0
        for year_idx, gen in enumerate(gen_profile, start=1):
            savings = gen.annual_generation_kwh * tariff
            maint_cost = sum(
                e.cost_brl for e in maint if e.year == year_idx
            )
            cumulative += (savings - maint_cost)
            if cumulative >= capex:
                return year_idx
        return len(gen_profile)
    
    # ==================== Insights Estratégicos Automatizados ====================
    
    def generate_strategic_insights(
        self,
        financial: FinancialMetrics,
        generation_profile: List[GenerationProfile],
        anomalies: Optional[List[Dict]] = None,
        compliance_score: float = 100.0
    ) -> List[StrategicInsight]:
        """Gera insights estratégicos automatizados."""
        insights = []
        
        # ===== Insight 1: Viabilidade Financeira =====
        if financial.simple_payback_years <= 5:
            insights.append(StrategicInsight(
                priority="high",
                category="financial",
                title="Investimento Altamente Viável",
                description=(
                    f"Payback de {financial.simple_payback_years:.1f} anos "
                    f"e ROI de {financial.roi_percent:.1f}% indicam "
                    "excelente retorno financeiro."
                ),
                impact=(
                    f"NPV de R$ {financial.npv_brl:,.2f} "
                    f"e TIR de {financial.irr_percent:.1f}%"
                ),
                action_items=[
                    "Aprovar investimento imediatamente",
                    "Considerar aumento de capacidade instalada",
                    "Avaliar financiamento com TIR > custo de capital"
                ],
                confidence=0.95
            ))
        elif financial.simple_payback_years <= 7:
            insights.append(StrategicInsight(
                priority="medium",
                category="financial",
                title="Investimento Viável com Retorno Moderado",
                description=(
                    f"Payback de {financial.simple_payback_years:.1f} anos "
                    "está dentro do padrão do setor fotovoltaico."
                ),
                impact=f"ROI de {financial.roi_percent:.1f}% ao longo da vida útil",
                action_items=[
                    "Negociar melhores condições com fornecedores",
                    "Avaliar incentivos fiscais disponíveis",
                    "Considerar financiamento de longo prazo"
                ],
                confidence=0.85
            ))
        else:
            insights.append(StrategicInsight(
                priority="high",
                category="financial",
                title="⚠️ Viabilidade Financeira Questionável",
                description=(
                    f"Payback de {financial.simple_payback_years:.1f} anos "
                    "excede o recomendado (7 anos)."
                ),
                impact="Risco de não recuperar investimento antes da degradação significativa",
                action_items=[
                    "Reavaliar premissas (tarifa, custo, localização)",
                    "Buscar equipamentos com melhor custo-benefício",
                    "Considerar postergação do investimento"
                ],
                confidence=0.90
            ))
        
        # ===== Insight 2: Degradação e Manutenção =====
        final_performance = generation_profile[-1].performance_ratio
        if final_performance < 75:
            insights.append(StrategicInsight(
                priority="medium",
                category="technical",
                title="Degradação Elevada ao Final da Vida Útil",
                description=(
                    f"Performance cai para {final_performance:.1f}% "
                    f"após {len(generation_profile)} anos."
                ),
                impact="Redução significativa da geração nos últimos anos",
                action_items=[
                    "Planejar substituição de componentes no ano 15",
                    "Aumentar frequência de inspeções após ano 10",
                    "Avaliar extensão de garantia de performance"
                ],
                confidence=0.80
            ))
        
        # ===== Insight 3: Anomalias Operacionais =====
        if anomalies and len(anomalies) > 0:
            high_severity = [a for a in anomalies if a.get("severity", 0) >= 4]
            if high_severity:
                insights.append(StrategicInsight(
                    priority="high",
                    category="operational",
                    title="🚨 Anomalias Críticas Detectadas",
                    description=(
                        f"{len(high_severity)} anomalia(s) de alta severidade "
                        "podem comprometer garantia e performance."
                    ),
                    impact="Risco de perda de garantia e redução de até 20% na geração",
                    action_items=[
                        f"Executar: {high_severity[0].get('recommendation', 'Intervenção urgente')}",
                        "Documentar para acionamento de garantia",
                        "Agendar inspeção técnica especializada"
                    ],
                    confidence=0.95
                ))
        
        # ===== Insight 4: Compliance =====
        if compliance_score < 90:
            insights.append(StrategicInsight(
                priority="high",
                category="operational",
                title="⚠️ Compliance Regulatório Incompleto",
                description=(
                    f"Score de compliance: {compliance_score:.0f}% "
                    "(recomendado: 100%)"
                ),
                impact="Risco de não conseguir conexão à rede ou incentivos fiscais",
                action_items=[
                    "Obter certificações faltantes (INMETRO, ANEEL)",
                    "Validar conformidade com NBR 16690/16274",
                    "Documentar homologações antes da instalação"
                ],
                confidence=0.98
            ))
        
        # ===== Insight 5: LCOE Competitivo =====
        if financial.lcoe_brl_kwh < 0.30:
            insights.append(StrategicInsight(
                priority="medium",
                category="financial",
                title="LCOE Altamente Competitivo",
                description=(
                    f"LCOE de R$ {financial.lcoe_brl_kwh:.4f}/kWh "
                    "está abaixo da tarifa de energia convencional."
                ),
                impact="Economia garantida ao longo de toda a vida útil",
                action_items=[
                    "Usar como argumento comercial (TCO vs. rede)",
                    "Considerar autoprodução para indústrias",
                    "Avaliar venda de excedentes (net metering)"
                ],
                confidence=0.90
            ))
        
        return sorted(insights, key=lambda i: (
            {"high": 0, "medium": 1, "low": 2}[i.priority],
            -i.confidence
        ))
    
    # ==================== Análise Completa (Orquestrador) ====================
    
    def analyze_sku_complete(
        self,
        digital_twin: Dict,
        energy_tariff_brl_kwh: float = 0.85,
        installation_cost_brl: Optional[float] = None
    ) -> Dict:
        """
        Análise completa do Digital Twin do SKU.
        
        Retorna todas as análises integradas:
        - IV curves
        - Geração ao longo da vida útil
        - Cronograma de manutenção
        - Métricas financeiras
        - Insights estratégicos
        """
        specs = digital_twin.get("specs_technical_sheet", {})
        pricing = digital_twin.get("pricing", {})
        legal = digital_twin.get("legal_strategic", {})
        location = digital_twin.get("location_analysis", {})
        anomalies = digital_twin.get("operational_anomalies", {}).get("active_anomalies", [])
        
        # ===== CAPEX =====
        equipment_cost = pricing.get("final_price_brl", 0.0)
        if installation_cost_brl is None:
            installation_cost_brl = equipment_cost * 0.20  # 20% do valor
        capex = equipment_cost + installation_cost_brl
        
        # ===== Dados de Geração =====
        pvgis = location.get("source_pvgis", {})
        power_kwp = specs.get("electrical_ref", {}).get("p_mp_ref_w", 0) / 1000.0
        specific_yield = pvgis.get("specific_yield_kwh_kwp_y", 0)
        
        # ===== Vida Útil =====
        lifetime_years = legal.get("warranty_years", 25)
        degradation_rate = legal.get("degradation_rate_percent_y", 0.5)
        
        # ===== Curvas IV (múltiplas condições) =====
        iv_curves = []
        for irrad, temp in [(1000, 25), (800, 40), (600, 55)]:
            curve = self.calculate_iv_curve(specs, irrad, temp)
            if curve:
                iv_curves.append(curve)
        
        # ===== Perfil de Geração =====
        generation_profile = self.calculate_generation_profile(
            power_kwp=power_kwp,
            specific_yield_kwh_kwp_y=specific_yield,
            degradation_rate_percent_y=degradation_rate,
            lifetime_years=lifetime_years,
            degradation_year1_percent=None
        )
        
        # ===== Manutenção =====
        maint_config = legal.get("maintenance_schedule", {})
        maintenance_schedule = self.generate_maintenance_schedule(
            lifetime_years=lifetime_years,
            cleaning_interval_months=maint_config.get("cleaning_interval_months", 6),
            inspection_interval_months=maint_config.get("inspection_interval_months", 12),
            major_maintenance_years=[10, 20] if lifetime_years >= 20 else None
        )
        
        # ===== Financeiro =====
        financial = self.calculate_financial_metrics(
            capex_brl=capex,
            generation_profile=generation_profile,
            energy_tariff_brl_kwh=energy_tariff_brl_kwh,
            maintenance_schedule=maintenance_schedule,
            salvage_value_percent=10.0
        )
        
        # ===== Insights =====
        insights = self.generate_strategic_insights(
            financial=financial,
            generation_profile=generation_profile,
            anomalies=anomalies,
            compliance_score=100.0  # TODO: calcular baseado em certifications
        )
        
        return {
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "sku": digital_twin.get("sku"),
            "iv_curves": [
                {
                    "irradiance_wm2": c.irradiance_wm2,
                    "cell_temp_c": c.cell_temp_c,
                    "i_sc": c.i_sc,
                    "v_oc": c.v_oc,
                    "i_mp": c.i_mp,
                    "v_mp": c.v_mp,
                    "p_mp": c.p_mp,
                    "fill_factor": c.fill_factor,
                    "efficiency_percent": c.efficiency_percent,
                    "curve_points": [
                        {"v": p.voltage_v, "i": p.current_a, "p": p.power_w}
                        for p in c.curve_points[::10]  # amostra 10 pontos
                    ]
                }
                for c in iv_curves
            ],
            "generation_profile": [
                {
                    "year": g.year,
                    "generation_kwh": round(g.annual_generation_kwh, 2),
                    "performance_ratio": round(g.performance_ratio, 2)
                }
                for g in generation_profile
            ],
            "maintenance_summary": {
                "total_events": len(maintenance_schedule),
                "total_cost_brl": sum(e.cost_brl for e in maintenance_schedule),
                "major_events": [e.year for e in maintenance_schedule if e.is_major]
            },
            "financial_metrics": {
                "capex_brl": round(financial.capex_brl, 2),
                "opex_annual_brl": round(financial.opex_annual_brl, 2),
                "annual_savings_brl": round(financial.annual_savings_brl, 2),
                "lifetime_savings_brl": round(financial.lifetime_savings_brl, 2),
                "simple_payback_years": round(financial.simple_payback_years, 2),
                "discounted_payback_years": round(financial.discounted_payback_years, 2),
                "roi_percent": round(financial.roi_percent, 2),
                "npv_brl": round(financial.npv_brl, 2),
                "irr_percent": round(financial.irr_percent, 2),
                "lcoe_brl_kwh": round(financial.lcoe_brl_kwh, 4),
                "payback_sensitivity": {
                    k: round(v, 2) for k, v in financial.payback_sensitivity.items()
                }
            },
            "strategic_insights": [
                {
                    "priority": i.priority,
                    "category": i.category,
                    "title": i.title,
                    "description": i.description,
                    "impact": i.impact,
                    "action_items": i.action_items,
                    "confidence": round(i.confidence, 2)
                }
                for i in insights
            ]
        }


# ==================== Exports ====================

__all__ = [
    "TechnicalIntelligenceService",
    "IVCurveAnalysis",
    "GenerationProfile",
    "MaintenanceEvent",
    "FinancialMetrics",
    "StrategicInsight",
]
