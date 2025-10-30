---
id: overview
title: Visão Geral do Projeto
sidebar_label: Visão Geral
sidebar_position: 1
description: Introdução ao YSH B2B Platform - E-commerce B2B Solar com Medusa.js & Next.js
---

# YSH B2B Platform - Visão Geral

:::info
**Plataforma de E-commerce B2B** para energia solar construída com Medusa.js 2.4 e Next.js 15
:::

## 🌞 O que é YSH B2B?

Yello Solar Hub (YSH) é uma plataforma completa de e-commerce B2B para o mercado de energia solar, oferecendo:

- **E-commerce B2B Completo** - Gestão de empresas, funcionários, limites de gastos e aprovações
- **Sistema de Cotações** - RFQ (Request for Quote) com negociação e conversão para pedidos
- **Produtos Solares Especializados** - Catálogo técnico com kits, painéis, inversores e acessórios
- **Workflows de Aprovação** - Aprovações configuráveis por empresa/alçada
- **Suporte Multi-Região** - URLs por país, moedas e idiomas locais

## 📊 Stack Tecnológico

### Frontend
- **Next.js 15** - App Router com Server Components
- **React 19** - Biblioteca UI moderna
- **TypeScript 5** - Tipagem estática
- **Tailwind CSS** - Framework CSS utilitário
- **Radix UI** - Componentes acessíveis

### Backend
- **Medusa.js 2.4** - Plataforma headless de e-commerce
- **PostgreSQL 15** - Banco de dados principal
- **Redis 7** - Cache e sessões
- **Módulos B2B Custom** - Company, Quote, Approval

### Infraestrutura
- **Docker** - Containerização
- **AWS Free Tier** - Deploy econômico
- **Stack FOSS** - 100% Open Source (15+ serviços)

## 🎯 Funcionalidades Principais

### E-commerce B2B
✅ **Gestão de Empresas** - Hierarquia de empresas e colaboradores  
✅ **Limites de Gastos** - Controle por colaborador/empresa  
✅ **Aprovações** - Workflow de aprovação de carrinhos/pedidos  
✅ **Cotações** - Sistema RFQ com mensagens  
✅ **Bulk Add to Cart** - Adição em massa de produtos

### Solar-Specific
✅ **Viabilidade Técnica** - Análise de instalação solar  
✅ **Simulador de Economia** - Cálculo de ROI  
✅ **Sistema SKU Avançado** - SKUs parametrizados  
✅ **Análise de Crédito** - Integração BACEN para financiamento  
✅ **Geração de Propostas** - PDFs técnicos e comerciais

## 📈 Estatísticas

| Métrica | Valor |
|---------|-------|
| **Produtos no Catálogo** | 1,123+ |
| **Cobertura de Imagens** | ~73.6% |
| **Módulos Backend Custom** | 5 |
| **Workflows** | 12+ |
| **Rotas API Custom** | 25+ |
| **Componentes UI** | 80+ |

## 🚀 Próximos Passos

1. [**Setup Local com Docker**](../quickstart/local/docker-setup.md) - Começe em 15 minutos
2. [**Arquitetura Técnica**](../architecture/backend/structure.md) - Entenda a estrutura
3. [**Guia do Desenvolvedor**](../development/developer-guide.md) - Contribua com o projeto

## 📚 Recursos Adicionais

- [Medusa Documentation](https://docs.medusajs.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [GitHub Repository](https://github.com/own-boldsbrain/ysh-b2b)
