#!/usr/bin/env node

/**
 * Orchestrador de Pipeline End-to-End
 * - Executa todo o fluxo de extração e upload
 * - Controla dependências entre etapas
 * - Gera relatório consolidado
 */

import { spawn } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const ROOT_PATH = path.join(__dirname, "..");

const PIPELINE_STEPS = [
  {
    id: 1,
    name: "Catalogar URLs Remotas",
    script: "catalog-remote-images.js",
    description: "Escaneia inventários e lista todas as URLs externas",
    required: true,
  },
  {
    id: 2,
    name: "Download Imagens Remotas",
    script: "download-remote-images.js",
    description: "Baixa imagens de URLs externas organizadas por fabricante",
    required: true,
  },
  {
    id: 3,
    name: "Atualizar Mapeamento",
    script: "update-image-map.js",
    description: "Gera mapeamento SKU → Imagens com URLs S3",
    required: true,
  },
  {
    id: 4,
    name: "Upload Imagens S3",
    script: "upload-images-s3.js",
    description: "Envia imagens locais para bucket S3",
    required: false,
  },
  {
    id: 5,
    name: "Upload SKUs DynamoDB",
    script: "upload-to-dynamodb.js",
    description: "Envia catálogo de SKUs para DynamoDB",
    required: false,
  },
  {
    id: 6,
    name: "Validação End-to-End",
    script: "validate-e2e.js",
    description: "Testa conectividade e integridade dos dados",
    required: false,
  },
];

function runScript(scriptPath) {
  return new Promise((resolve, reject) => {
    console.log(`\n▶️  Executando: ${path.basename(scriptPath)}\n`);

    const child = spawn("node", [scriptPath], {
      cwd: ROOT_PATH,
      stdio: "inherit",
      shell: true,
    });

    child.on("exit", (code) => {
      if (code === 0) {
        console.log(`\n✅ Concluído: ${path.basename(scriptPath)}\n`);
        resolve({ success: true, code });
      } else {
        console.log(`\n⚠️  Falhou: ${path.basename(scriptPath)} (código: ${code})\n`);
        resolve({ success: false, code });
      }
    });

    child.on("error", (error) => {
      console.error(`\n❌ Erro: ${path.basename(scriptPath)}\n`);
      console.error(error.message);
      reject(error);
    });
  });
}

async function runPipeline() {
  console.log("\n🚀 PIPELINE END-TO-END - EXTRAÇÃO E UPLOAD\n");
  console.log("═".repeat(70));

  const results = {
    timestamp_start: new Date().toISOString(),
    timestamp_end: null,
    steps: [],
    summary: {
      total_steps: PIPELINE_STEPS.length,
      completed: 0,
      failed: 0,
      skipped: 0,
    },
  };

  try {
    for (const step of PIPELINE_STEPS) {
      console.log("\n" + "─".repeat(70));
      console.log(`\n📋 ETAPA ${step.id}/${PIPELINE_STEPS.length}: ${step.name}\n`);
      console.log(`   ${step.description}`);

      const scriptPath = path.join(__dirname, step.script);

      if (!fs.existsSync(scriptPath)) {
        console.log(`\n⚠️  Script não encontrado: ${step.script}\n`);
        results.steps.push({
          step_id: step.id,
          name: step.name,
          status: "skipped",
          reason: "Script não encontrado",
        });
        results.summary.skipped++;
        continue;
      }

      const startTime = Date.now();

      try {
        const result = await runScript(scriptPath);

        const duration = ((Date.now() - startTime) / 1000).toFixed(2);

        results.steps.push({
          step_id: step.id,
          name: step.name,
          status: result.success ? "success" : "failed",
          exit_code: result.code,
          duration_seconds: parseFloat(duration),
        });

        if (result.success) {
          results.summary.completed++;
        } else {
          results.summary.failed++;

          if (step.required) {
            console.log("\n❌ ETAPA CRÍTICA FALHOU - ABORTANDO PIPELINE\n");
            break;
          }
        }
      } catch (error) {
        console.error(`\n❌ Erro na execução: ${error.message}\n`);

        results.steps.push({
          step_id: step.id,
          name: step.name,
          status: "error",
          error: error.message,
        });

        results.summary.failed++;

        if (step.required) {
          console.log("\n❌ ETAPA CRÍTICA FALHOU - ABORTANDO PIPELINE\n");
          break;
        }
      }
    }

    results.timestamp_end = new Date().toISOString();

    // Gerar relatório final
    console.log("\n" + "═".repeat(70));
    console.log("\n📊 RESULTADO DO PIPELINE\n");

    const totalDuration = results.steps.reduce((sum, step) => {
      return sum + (step.duration_seconds || 0);
    }, 0);

    console.log(`Estatísticas:`);
    console.log(`   • Total de etapas: ${results.summary.total_steps}`);
    console.log(`   • Concluídas: ${results.summary.completed}`);
    console.log(`   • Falhas: ${results.summary.failed}`);
    console.log(`   • Ignoradas: ${results.summary.skipped}`);
    console.log(`   • Duração total: ${totalDuration.toFixed(2)}s\n`);

    console.log(`Detalhes:`);
    for (const step of results.steps) {
      const icon =
        step.status === "success" ? "✓" : step.status === "failed" ? "✗" : "⊘";
      const duration = step.duration_seconds ? ` (${step.duration_seconds}s)` : "";
      console.log(`   ${icon} ${step.name}${duration}`);
    }

    console.log("");

    // Salvar relatório
    const reportPath = path.join(ROOT_PATH, "PIPELINE_EXECUTION_REPORT.json");
    fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));

    console.log(`📄 Relatório salvo: PIPELINE_EXECUTION_REPORT.json\n`);

    // Status final
    const successRate =
      (results.summary.completed / results.summary.total_steps) * 100;

    if (results.summary.failed === 0) {
      console.log("✅ PIPELINE CONCLUÍDO COM SUCESSO!\n");
      process.exit(0);
    } else if (successRate >= 50) {
      console.log("⚠️  PIPELINE CONCLUÍDO COM AVISOS\n");
      process.exit(0);
    } else {
      console.log("❌ PIPELINE FALHOU\n");
      process.exit(1);
    }
  } catch (error) {
    console.error("\n❌ ERRO CRÍTICO NO PIPELINE:\n");
    console.error(error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Executar pipeline
runPipeline().catch(console.error);
