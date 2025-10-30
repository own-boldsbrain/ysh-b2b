#!/usr/bin/env node

/**
 * Script para monitorar progresso de sincronização
 * - Verifica status da batch
 * - Exibe estatísticas em tempo real
 * - Detecta conclusão e erros
 */

import axios from "axios";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuração
const API_BASE = process.env.API_BASE || "http://localhost:3000";
const STATUS_API_URL = `${API_BASE}/admin/facebook-catalog/syncs`;
const CHECK_INTERVAL = 10000; // 10 segundos
const MAX_CHECKS = 360; // 60 minutos máximo

let checkCount = 0;

async function monitorSync() {
  console.log("\n📊 MONITORAMENTO DE SINCRONIZAÇÃO\n");
  console.log("═".repeat(70));
  console.log(
    `Iniciado: ${new Date().toLocaleString("pt-BR")}`
  );
  console.log("Verificação a cada 10 segundos (máximo 60 minutos)\n");

  const startTime = Date.now();

  async function checkStatus() {
    checkCount++;
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;

    try {
      const response = await axios.get(STATUS_API_URL, {
        timeout: 10000,
      });

      const syncs = response.data || [];
      const lastSync = syncs[0]; // Mais recente

      if (!lastSync) {
        console.log(
          `[${minutes}m${seconds}s] ⏳ Aguardando dados de sincronização...`
        );
        return;
      }

      const status = lastSync.status || "PROCESSING";
      const icon =
        status === "COMPLETED"
          ? "✅"
          : status === "FAILED"
            ? "❌"
            : "⏳";

      console.log(
        `[${minutes}m${seconds}s] ${icon} Status: ${status}`
      );

      if (lastSync.items_created || lastSync.items_updated) {
        console.log(
          `           Criados: ${lastSync.items_created || 0} | Atualizados: ${lastSync.items_updated || 0}`
        );
      }

      if (lastSync.items_failed) {
        console.log(
          `           ⚠️  Erros: ${lastSync.items_failed}`
        );
      }

      if (lastSync.platforms) {
        console.log(
          `           📱 Plataformas: ${JSON.stringify(lastSync.platforms)}`
        );
      }

      // Se completou, parar
      if (status === "COMPLETED" || status === "FAILED") {
        console.log("\n═".repeat(70));
        console.log(
          `\n✅ SINCRONIZAÇÃO ${status === "COMPLETED" ? "CONCLUÍDA" : "FALHOU"}!\n`
        );

        console.log("📊 RESUMO FINAL:\n");
        console.log(`   Status: ${status}`);
        console.log(`   Produtos Criados: ${lastSync.items_created || 0}`);
        console.log(`   Produtos Atualizados: ${lastSync.items_updated || 0}`);
        console.log(`   Produtos com Erro: ${lastSync.items_failed || 0}`);
        console.log(
          `   Tempo Total: ${minutes}m${seconds}s`
        );

        if (lastSync.error_message) {
          console.log(`\n   ⚠️  Erro: ${lastSync.error_message}`);
        }

        // Salvar relatório final
        const report = {
          timestamp: new Date().toISOString(),
          sync_completed: true,
          status: status,
          total_time_seconds: elapsed,
          items_created: lastSync.items_created || 0,
          items_updated: lastSync.items_updated || 0,
          items_failed: lastSync.items_failed || 0,
          platforms: lastSync.platforms,
          next_steps:
            status === "COMPLETED"
              ? [
                  "Verificar Facebook Commerce Manager",
                  "Validar Instagram Shopping",
                  "Testar WhatsApp Business Catalog",
                  "Monitorar métricas de desempenho",
                ]
              : [
                  "Verificar logs de erro",
                  "Corrigir problemas identificados",
                  "Reexecutar sincronização",
                ],
        };

        const reportPath = path.join(
          __dirname,
          "../SYNC_COMPLETION_REPORT.json"
        );
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        console.log("\n💾 Relatório salvo: SYNC_COMPLETION_REPORT.json\n");

        process.exit(status === "COMPLETED" ? 0 : 1);
      }

      // Continuar verificando
      if (checkCount < MAX_CHECKS) {
        setTimeout(checkStatus, CHECK_INTERVAL);
      } else {
        console.log(
          "\n⚠️  Tempo máximo de verificação excedido (60 minutos)"
        );
        console.log(
          "Acesse o dashboard ou verifique logs para mais informações"
        );
        process.exit(1);
      }
    } catch (error) {
      console.error(
        `[${minutes}m${seconds}s] ❌ Erro ao verificar: ${error.message}`
      );

      if (checkCount < MAX_CHECKS) {
        setTimeout(checkStatus, CHECK_INTERVAL);
      } else {
        process.exit(1);
      }
    }
  }

  checkStatus();
}

monitorSync().catch(console.error);
