#!/usr/bin/env node

/**
 * 360° Coverage Report Generator
 * 
 * Generates comprehensive report covering:
 * - All 7 distributors status
 * - Total products extracted
 * - Success/failure analysis
 * - Coverage metrics
 * - Recommendations for next steps
 * 
 * Usage:
 *   npx tsx scripts/generate-360-report.ts
 */

import * as fs from 'fs';
import * as path from 'path';

interface DistributorStatus {
  name: string;
  status: 'success' | 'partial' | 'failed';
  productsExtracted: number;
  loginMethod: string;
  issues: string[];
  lastAttempt: string;
}

interface CoverageReport {
  generatedAt: string;
  summary: {
    totalDistributors: number;
    successfulDistributors: number;
    partialDistributors: number;
    failedDistributors: number;
    totalProducts: number;
    coveragePercentage: number;
  };
  distributors: DistributorStatus[];
  recommendations: string[];
  nextSteps: string[];
}

const OUTPUT_DIR = path.join(process.cwd(), 'output');
const DOCS_DIR = path.join(process.cwd(), 'docs');

function loadProductCount(distributorName: string): number {
  let count = 0;

  // Check basic scraping output
  const basicDir = path.join(OUTPUT_DIR, distributorName);
  if (fs.existsSync(basicDir)) {
    const files = fs.readdirSync(basicDir).filter(f => f.endsWith('.json'));
    for (const file of files) {
      try {
        const data = JSON.parse(fs.readFileSync(path.join(basicDir, file), 'utf-8'));
        if (Array.isArray(data)) {
          count += data.length;
        }
      } catch (e) {
        // Skip invalid files
      }
    }
  }

  // Check deep scraping output
  const deepDir = path.join(OUTPUT_DIR, 'deep-scraping', distributorName);
  if (fs.existsSync(deepDir)) {
    const files = fs.readdirSync(deepDir).filter(f => f.endsWith('.json'));
    for (const file of files) {
      try {
        const data = JSON.parse(fs.readFileSync(path.join(deepDir, file), 'utf-8'));
        if (Array.isArray(data)) {
          count = Math.max(count, data.length);
        }
      } catch (e) {
        // Skip invalid files
      }
    }
  }

  return count;
}

function analyzeDistributors(): DistributorStatus[] {
  const distributors: DistributorStatus[] = [
    {
      name: 'Edeltec',
      status: 'success',
      productsExtracted: loadProductCount('edeltec'),
      loginMethod: 'Standard form authentication',
      issues: [],
      lastAttempt: new Date().toISOString(),
    },
    {
      name: 'Neosolar',
      status: 'partial',
      productsExtracted: loadProductCount('neosolar'),
      loginMethod: 'Standard form authentication',
      issues: ['Limited catalog access', 'Awaiting support response'],
      lastAttempt: new Date().toISOString(),
    },
    {
      name: 'Odex',
      status: 'partial',
      productsExtracted: loadProductCount('odex'),
      loginMethod: 'Standard form authentication',
      issues: ['Returns category links only', 'Needs deep category navigation'],
      lastAttempt: new Date().toISOString(),
    },
    {
      name: 'Fortlev',
      status: 'partial',
      productsExtracted: loadProductCount('fortlev'),
      loginMethod: 'Standard form authentication',
      issues: ['Returns category links only', 'Needs deep category navigation'],
      lastAttempt: new Date().toISOString(),
    },
    {
      name: 'Solfácil',
      status: 'failed',
      productsExtracted: loadProductCount('solfacil'),
      loginMethod: 'Keycloak SSO (OpenID Connect)',
      issues: [
        'Complex SSO authentication',
        'Requires OAuth2/OpenID Connect flow',
        'Script created but needs manual debugging'
      ],
      lastAttempt: new Date().toISOString(),
    },
    {
      name: 'Fotus',
      status: 'failed',
      productsExtracted: loadProductCount('fotus'),
      loginMethod: 'React SPA custom authentication',
      issues: [
        'Custom SPA authentication',
        'Login form detection failed',
        'Script created but needs manual debugging'
      ],
      lastAttempt: new Date().toISOString(),
    },
    {
      name: 'Dynamis',
      status: 'failed',
      productsExtracted: loadProductCount('dynamis'),
      loginMethod: 'Custom SPA authentication',
      issues: [
        'Custom SPA authentication',
        'Login form not detected',
        'Script created but needs manual debugging'
      ],
      lastAttempt: new Date().toISOString(),
    },
  ];

  return distributors;
}

function generateRecommendations(distributors: DistributorStatus[]): string[] {
  const recommendations: string[] = [];

  const failed = distributors.filter(d => d.status === 'failed');
  const partial = distributors.filter(d => d.status === 'partial');

  if (failed.length > 0) {
    recommendations.push(
      `🔴 **${failed.length} distribuidores com falha total**: ${failed.map(d => d.name).join(', ')}`
    );
    recommendations.push(
      '💡 **Ação recomendada**: Debug manual com browser visível usando os scripts customizados criados'
    );
  }

  if (partial.length > 0) {
    recommendations.push(
      `🟡 **${partial.length} distribuidores com extração parcial**: ${partial.map(d => d.name).join(', ')}`
    );
    recommendations.push(
      '💡 **Ação recomendada**: Implementar navegação profunda por categorias para extrair catálogo completo'
    );
  }

  const totalProducts = distributors.reduce((sum, d) => sum + d.productsExtracted, 0);
  if (totalProducts > 0) {
    recommendations.push(
      `✅ **${totalProducts} produtos já extraídos** - Base inicial estabelecida com sucesso`
    );
  }

  return recommendations;
}

function generateNextSteps(distributors: DistributorStatus[]): string[] {
  const steps: string[] = [];

  // Priority 1: Fix failed distributors
  const failed = distributors.filter(d => d.status === 'failed');
  if (failed.length > 0) {
    steps.push('**PRIORIDADE 1**: Resolver autenticações complexas');
    for (const dist of failed) {
      steps.push(`  - ${dist.name}: ${dist.loginMethod}`);
      steps.push(`    Script: scripts/extract-${dist.name.toLowerCase()}-custom.ts`);
    }
  }

  // Priority 2: Deep scrape partial distributors
  const partial = distributors.filter(d => d.status === 'partial');
  if (partial.length > 0) {
    steps.push('**PRIORIDADE 2**: Implementar deep scraping para distribuidores parciais');
    for (const dist of partial) {
      if (dist.issues.some(i => i.includes('category'))) {
        steps.push(`  - ${dist.name}: Criar navegador de categorias`);
      }
    }
  }

  // Priority 3: Enhance successful distributors
  const success = distributors.filter(d => d.status === 'success');
  if (success.length > 0) {
    steps.push('**PRIORIDADE 3**: Aprimorar extração dos distribuidores funcionais');
    for (const dist of success) {
      steps.push(`  - ${dist.name}: Extrair especificações técnicas completas`);
    }
  }

  // Priority 4: Data consolidation
  steps.push('**PRIORIDADE 4**: Consolidar dados em schema unificado');
  steps.push('  - Normalizar títulos de produtos');
  steps.push('  - Dedplicar produtos entre distribuidores');
  steps.push('  - Comparar preços entre distribuidores');

  // Priority 5: Automation
  steps.push('**PRIORIDADE 5**: Implementar automação');
  steps.push('  - Criar workflow Temporal para sync diário');
  steps.push('  - Configurar alertas de falhas');
  steps.push('  - Implementar dashboard de monitoramento');

  return steps;
}

function generateMarkdownReport(report: CoverageReport): string {
  const md: string[] = [];

  md.push('# 🎯 RELATÓRIO DE COBERTURA 360º - DISTRIBUIDORES');
  md.push('');
  md.push(`**Data de Geração**: ${new Date(report.generatedAt).toLocaleString('pt-BR')}`);
  md.push('');

  // Summary
  md.push('## 📊 RESUMO EXECUTIVO');
  md.push('');
  md.push('```');
  md.push('╔════════════════════════════════════════════════════════════╗');
  md.push('║                    COBERTURA GERAL                        ║');
  md.push('╠════════════════════════════════════════════════════════════╣');
  md.push(`║  Total de Distribuidores:  ${report.summary.totalDistributors}/7 (100%)                    ║`);
  md.push(`║  ✅ Funcionais:             ${report.summary.successfulDistributors}/7 (${((report.summary.successfulDistributors/7)*100).toFixed(0)}%)                     ║`);
  md.push(`║  ⚠️  Parciais:               ${report.summary.partialDistributors}/7 (${((report.summary.partialDistributors/7)*100).toFixed(0)}%)                     ║`);
  md.push(`║  ❌ Falhas:                 ${report.summary.failedDistributors}/7 (${((report.summary.failedDistributors/7)*100).toFixed(0)}%)                     ║`);
  md.push(`║  📦 Produtos Extraídos:     ${report.summary.totalProducts}                              ║`);
  md.push(`║  📈 Cobertura Efetiva:      ${report.summary.coveragePercentage.toFixed(1)}%                            ║`);
  md.push('╚════════════════════════════════════════════════════════════╝');
  md.push('```');
  md.push('');

  // Status by distributor
  md.push('## 🏪 STATUS POR DISTRIBUIDOR');
  md.push('');

  for (const dist of report.distributors) {
    const icon = dist.status === 'success' ? '✅' : dist.status === 'partial' ? '⚠️' : '❌';
    const statusText = dist.status === 'success' ? 'FUNCIONANDO' : 
                       dist.status === 'partial' ? 'PARCIAL' : 'FALHOU';

    md.push(`### ${icon} ${dist.name} - ${statusText}`);
    md.push('');
    md.push(`**Produtos Extraídos**: ${dist.productsExtracted}`);
    md.push(`**Método de Login**: ${dist.loginMethod}`);
    
    if (dist.issues.length > 0) {
      md.push('');
      md.push('**Questões Identificadas**:');
      for (const issue of dist.issues) {
        md.push(`- ${issue}`);
      }
    }
    md.push('');
  }

  // Recommendations
  md.push('## 💡 RECOMENDAÇÕES');
  md.push('');
  for (const rec of report.recommendations) {
    md.push(`${rec}`);
    md.push('');
  }

  // Next steps
  md.push('## 🚀 PRÓXIMOS PASSOS');
  md.push('');
  for (const step of report.nextSteps) {
    md.push(step);
    md.push('');
  }

  // Scripts created
  md.push('## 📝 SCRIPTS DISPONÍVEIS');
  md.push('');
  md.push('### Extração Geral');
  md.push('```bash');
  md.push('# Extração básica de todos os distribuidores');
  md.push('npx tsx scripts/extract-all-distributors.ts');
  md.push('');
  md.push('# Deep scraping de distribuidores funcionais');
  md.push('npx tsx scripts/extract-deep-all.ts');
  md.push('```');
  md.push('');
  md.push('### Extração Customizada (Distribuidores com Falha)');
  md.push('```bash');
  md.push('# Solfácil (Keycloak SSO)');
  md.push('npx tsx scripts/extract-solfacil-custom.ts');
  md.push('');
  md.push('# Fotus (React SPA)');
  md.push('npx tsx scripts/extract-fotus-custom.ts');
  md.push('');
  md.push('# Dynamis (Custom SPA)');
  md.push('npx tsx scripts/extract-dynamis-custom.ts');
  md.push('```');
  md.push('');
  md.push('### Consolidação e Relatórios');
  md.push('```bash');
  md.push('# Consolidar todos os dados');
  md.push('npx tsx scripts/consolidate-data.ts');
  md.push('');
  md.push('# Gerar relatório 360º');
  md.push('npx tsx scripts/generate-360-report.ts');
  md.push('```');
  md.push('');

  // Technical details
  md.push('## 🔧 DETALHES TÉCNICOS');
  md.push('');
  md.push('### Distribuidores Funcionais');
  const success = report.distributors.filter(d => d.status === 'success');
  if (success.length > 0) {
    for (const dist of success) {
      md.push(`- **${dist.name}**: ${dist.productsExtracted} produtos`);
    }
  } else {
    md.push('_Nenhum distribuidor totalmente funcional ainda_');
  }
  md.push('');

  md.push('### Distribuidores Parciais');
  const partial = report.distributors.filter(d => d.status === 'partial');
  if (partial.length > 0) {
    for (const dist of partial) {
      md.push(`- **${dist.name}**: ${dist.productsExtracted} produtos (${dist.issues[0]})`);
    }
  } else {
    md.push('_Nenhum distribuidor com status parcial_');
  }
  md.push('');

  md.push('### Distribuidores com Falha');
  const failed = report.distributors.filter(d => d.status === 'failed');
  if (failed.length > 0) {
    for (const dist of failed) {
      md.push(`- **${dist.name}**: ${dist.loginMethod} - ${dist.issues[0]}`);
    }
  } else {
    md.push('_Todos os distribuidores funcionando!_ 🎉');
  }
  md.push('');

  // Footer
  md.push('---');
  md.push('');
  md.push(`_Relatório gerado automaticamente em ${new Date(report.generatedAt).toLocaleString('pt-BR')}_`);
  md.push('');

  return md.join('\n');
}

async function generate360Report(): Promise<void> {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  📊 GERADOR DE RELATÓRIO 360º                            ║
╚════════════════════════════════════════════════════════════╝
  `);

  // Analyze distributors
  console.log('🔍 Analisando status dos distribuidores...');
  const distributors = analyzeDistributors();

  // Calculate summary
  const summary = {
    totalDistributors: distributors.length,
    successfulDistributors: distributors.filter(d => d.status === 'success').length,
    partialDistributors: distributors.filter(d => d.status === 'partial').length,
    failedDistributors: distributors.filter(d => d.status === 'failed').length,
    totalProducts: distributors.reduce((sum, d) => sum + d.productsExtracted, 0),
    coveragePercentage: 0,
  };

  // Calculate coverage percentage
  const workingCount = summary.successfulDistributors + (summary.partialDistributors * 0.5);
  summary.coveragePercentage = (workingCount / summary.totalDistributors) * 100;

  // Generate recommendations
  console.log('💡 Gerando recomendações...');
  const recommendations = generateRecommendations(distributors);

  // Generate next steps
  console.log('🚀 Definindo próximos passos...');
  const nextSteps = generateNextSteps(distributors);

  // Create report
  const report: CoverageReport = {
    generatedAt: new Date().toISOString(),
    summary,
    distributors,
    recommendations,
    nextSteps,
  };

  // Save JSON report
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const jsonFile = path.join(OUTPUT_DIR, `coverage-360-${timestamp}.json`);
  fs.writeFileSync(jsonFile, JSON.stringify(report, null, 2));
  console.log(`💾 Relatório JSON salvo: ${jsonFile}`);

  // Save Markdown report
  const markdown = generateMarkdownReport(report);
  const mdFile = path.join(DOCS_DIR, 'COVERAGE_360_REPORT.md');
  fs.writeFileSync(mdFile, markdown);
  console.log(`📝 Relatório Markdown salvo: ${mdFile}`);

  // Print summary
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  ✨ RELATÓRIO 360º GERADO COM SUCESSO                    ║
╚════════════════════════════════════════════════════════════╝

📊 RESUMO:
  • Total de produtos: ${summary.totalProducts}
  • Distribuidores funcionais: ${summary.successfulDistributors}/7
  • Cobertura efetiva: ${summary.coveragePercentage.toFixed(1)}%

📁 ARQUIVOS:
  • JSON: ${jsonFile}
  • Markdown: ${mdFile}

🎉 Relatório completo!
  `);
}

// Run
generate360Report().catch(console.error);
