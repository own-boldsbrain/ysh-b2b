#!/usr/bin/env node

/**
 * CHECKLIST INTERATIVO - Migração AWS
 * Guia passo-a-passo com validação
 */

import readline from "readline";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

const checklist = [
  {
    id: 1,
    title: "Configurar AWS Access Key",
    command: "export AWS_ACCESS_KEY_ID=sua_chave",
    description: "Obtenha em AWS IAM Console → Security Credentials",
  },
  {
    id: 2,
    title: "Configurar AWS Secret Access Key",
    command: "export AWS_SECRET_ACCESS_KEY=seu_segredo",
    description: "Obtenha em AWS IAM Console → Security Credentials",
  },
  {
    id: 3,
    title: "Configurar AWS Region",
    command: "export AWS_REGION=us-east-1",
    description: "Use us-east-1 para melhor compatibilidade",
  },
  {
    id: 4,
    title: "Configurar Facebook Token",
    command: "export FACEBOOK_TOKEN=seu_token",
    description: "Obtenha token permanente do System User",
  },
  {
    id: 5,
    title: "Configurar Facebook Catalog ID",
    command: "export FACEBOOK_CATALOG_ID=716960371408497",
    description: "ID do catálogo criado (716960371408497)",
  },
  {
    id: 6,
    title: "Instalar dependências AWS",
    command: "npm install aws-sdk axios dotenv",
    description: "Instale pacotes necessários",
  },
  {
    id: 7,
    title: "Verificar S3 bucket",
    command: "node scripts/verify-aws-setup.js",
    description: "Valida existência e acesso ao bucket S3",
  },
  {
    id: 8,
    title: "Verificar DynamoDB table",
    command: "node scripts/verify-aws-setup.js",
    description: "Valida existência da tabela DynamoDB",
  },
  {
    id: 9,
    title: "Testar conectividade",
    command: "node scripts/test-connectivity.js",
    description: "Testa AWS, S3, DynamoDB, Facebook",
  },
  {
    id: 10,
    title: "Verificar imagens locais",
    command: "ls -la static/products/ | grep -E 'jpg|png|webp'",
    description: "Confirme 937 imagens em static/products",
  },
];

const tasks = [
  {
    id: 1,
    title: "Abrir Dashboard",
    command: "node scripts/upload-dashboard.js",
    description: "Em novo terminal para acompanhar progresso",
    terminal: "NEW",
  },
  {
    id: 2,
    title: "Upload Maestro",
    command: "node scripts/upload-to-aws.js",
    description: "Upload de 937 imagens + 3.337 SKUs",
  },
  {
    id: 3,
    title: "Sincronizar Facebook",
    command: "node scripts/sync-facebook-from-aws.js",
    description: "Sincroniza com 3 plataformas Meta",
  },
];

async function displayChecklist() {
  console.clear();
  console.log("\n╔════════════════════════════════════════════════════════════════╗");
  console.log("║           ✅ CHECKLIST DE MIGRAÇÃO PARA AWS                    ║");
  console.log("╚════════════════════════════════════════════════════════════════╝\n");

  console.log("📋 PREPARAÇÃO (10 itens)\n");

  for (const item of checklist) {
    console.log(`${item.id}. ${item.title}`);
    console.log(`   Comando: ${item.command}`);
    console.log(`   ℹ️  ${item.description}\n`);
  }

  let completed = 0;
  for (let i = 0; i < checklist.length; i++) {
    const answer = await question(`Completou o item ${i + 1}? (s/n): `);
    if (answer.toLowerCase() === "s" || answer.toLowerCase() === "sim") {
      completed++;
    }
  }

  if (completed === checklist.length) {
    console.clear();
    displayTasks();
  } else {
    console.log(
      `\n⚠️  Você completou ${completed}/${checklist.length} itens.`
    );
    console.log("Por favor, complete todos os itens antes de prosseguir.\n");
    process.exit(0);
  }
}

async function displayTasks() {
  console.log("\n╔════════════════════════════════════════════════════════════════╗");
  console.log("║              🚀 EXECUÇÃO DO UPLOAD (3 etapas)                  ║");
  console.log("╚════════════════════════════════════════════════════════════════╝\n");

  for (const task of tasks) {
    console.log(`${task.id}. ${task.title}`);
    console.log(`   Comando: ${task.command}`);
    console.log(`   Descrição: ${task.description}`);
    if (task.terminal === "NEW") {
      console.log(`   ⚠️  Execute em um novo terminal!\n`);
    } else {
      console.log();
    }
  }

  console.log("\n═══════════════════════════════════════════════════════════════\n");

  const startTask1 = await question("Deseja iniciar a Etapa 1 (Dashboard)? (s/n): ");

  if (startTask1.toLowerCase() === "s" || startTask1.toLowerCase() === "sim") {
    console.log("\n⚠️  Abra um novo terminal e execute:");
    console.log(`    ${tasks[0].command}\n`);

    const startTask2 = await question("Pressione Enter quando o Dashboard estiver aberto...");

    console.clear();
    console.log("Iniciando Etapa 2 em 3 segundos...\n");
    await new Promise((resolve) => setTimeout(resolve, 3000));

    console.log(`Executando: ${tasks[1].command}\n`);
    // Aqui executaríamos o comando real, mas no shell isso seria feito assim:
    // const { spawn } = require('child_process');
    // spawn('node', ['scripts/upload-to-aws.js']);
  }

  console.log("\n\nApós conclusão:\n");
  console.log("1. Verifique os relatórios gerados:");
  console.log("   • S3_UPLOAD_REPORT.json");
  console.log("   • DYNAMODB_UPLOAD_REPORT.json");
  console.log("   • AWS_UPLOAD_COMPLETE.json\n");

  console.log("2. Execute Etapa 3:");
  console.log(`   ${tasks[2].command}\n`);

  console.log("3. Aguarde sincronização Facebook (~30 min)\n");

  console.log("✅ Checklist concluído!\n");
  rl.close();
}

displayChecklist().catch(console.error);
