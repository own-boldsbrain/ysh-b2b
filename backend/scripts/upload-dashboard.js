#!/usr/bin/env node

/**
 * Dashboard de monitoramento do upload para AWS
 * Rastreia progresso de S3 + DynamoDB + Facebook em tempo real
 */

import AWS from "aws-sdk";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { spawn } from "child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class UploadDashboard {
  constructor() {
    this.metrics = {
      s3: {
        total: 937,
        uploaded: 0,
        failed: 0,
        startTime: null,
        endTime: null,
      },
      dynamodb: {
        total: 3337,
        uploaded: 0,
        failed: 0,
        startTime: null,
        endTime: null,
      },
      facebook: {
        total: 3337,
        synced: 0,
        failed: 0,
        startTime: null,
        endTime: null,
      },
    };
  }

  formatBytes(bytes) {
    const sizes = ["B", "KB", "MB", "GB"];
    if (bytes === 0) return "0 B";
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + " " + sizes[i];
  }

  formatDuration(ms) {
    if (!ms) return "-";
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    }
    return `${seconds}s`;
  }

  getProgressBar(current, total, width = 20) {
    const percentage = (current / total) * 100;
    const filled = Math.round((percentage / 100) * width);
    const empty = width - filled;

    return (
      "[" +
      "█".repeat(filled) +
      "░".repeat(empty) +
      "] " +
      percentage.toFixed(1) +
      "%"
    );
  }

  displayMetrics() {
    console.clear();

    console.log("\n╔════════════════════════════════════════════════════════════════╗");
    console.log("║         📊 DASHBOARD DE UPLOAD AWS - YSH CATALOG              ║");
    console.log("╚════════════════════════════════════════════════════════════════╝\n");

    // S3 Metrics
    console.log("📸 S3 - UPLOAD DE IMAGENS");
    console.log("─".repeat(66));

    const s3Percent = (this.metrics.s3.uploaded / this.metrics.s3.total) * 100;
    console.log(`Status: ${this.metrics.s3.uploaded}/${this.metrics.s3.total} imagens`);
    console.log(this.getProgressBar(this.metrics.s3.uploaded, this.metrics.s3.total));

    if (this.metrics.s3.startTime) {
      const duration = this.metrics.s3.endTime
        ? this.metrics.s3.endTime - this.metrics.s3.startTime
        : Date.now() - this.metrics.s3.startTime;
      const rate = (this.metrics.s3.uploaded / (duration / 1000)).toFixed(1);
      console.log(
        `Tempo: ${this.formatDuration(duration)} | Taxa: ${rate} img/s`
      );
    }

    if (this.metrics.s3.failed > 0) {
      console.log(`❌ Erros: ${this.metrics.s3.failed}`);
    }

    console.log();

    // DynamoDB Metrics
    console.log("📦 DYNAMODB - UPLOAD DE SKUs");
    console.log("─".repeat(66));

    const dbPercent = (this.metrics.dynamodb.uploaded / this.metrics.dynamodb.total) * 100;
    console.log(`Status: ${this.metrics.dynamodb.uploaded}/${this.metrics.dynamodb.total} SKUs`);
    console.log(this.getProgressBar(this.metrics.dynamodb.uploaded, this.metrics.dynamodb.total));

    if (this.metrics.dynamodb.startTime) {
      const duration = this.metrics.dynamodb.endTime
        ? this.metrics.dynamodb.endTime - this.metrics.dynamodb.startTime
        : Date.now() - this.metrics.dynamodb.startTime;
      const rate = (this.metrics.dynamodb.uploaded / (duration / 1000)).toFixed(1);
      console.log(
        `Tempo: ${this.formatDuration(duration)} | Taxa: ${rate} SKU/s`
      );
    }

    if (this.metrics.dynamodb.failed > 0) {
      console.log(`❌ Erros: ${this.metrics.dynamodb.failed}`);
    }

    console.log();

    // Facebook Metrics
    console.log("📱 FACEBOOK - SINCRONIZAÇÃO");
    console.log("─".repeat(66));

    const fbPercent = (this.metrics.facebook.synced / this.metrics.facebook.total) * 100;
    console.log(`Status: ${this.metrics.facebook.synced}/${this.metrics.facebook.total} produtos`);
    console.log(this.getProgressBar(this.metrics.facebook.synced, this.metrics.facebook.total));

    if (this.metrics.facebook.startTime) {
      const duration = this.metrics.facebook.endTime
        ? this.metrics.facebook.endTime - this.metrics.facebook.startTime
        : Date.now() - this.metrics.facebook.startTime;
      const rate = (this.metrics.facebook.synced / (duration / 1000)).toFixed(1);
      console.log(
        `Tempo: ${this.formatDuration(duration)} | Taxa: ${rate} prod/s`
      );
    }

    if (this.metrics.facebook.failed > 0) {
      console.log(`❌ Erros: ${this.metrics.facebook.failed}`);
    }

    console.log();

    // Overall Stats
    console.log("📊 RESUMO GERAL");
    console.log("─".repeat(66));

    const totalItems = this.metrics.s3.total + this.metrics.dynamodb.total;
    const totalUploaded = this.metrics.s3.uploaded + this.metrics.dynamodb.uploaded;
    const overallPercent = (totalUploaded / totalItems) * 100;

    console.log(`Total: ${totalUploaded}/${totalItems} itens`);
    console.log(this.getProgressBar(totalUploaded, totalItems));
    console.log(`Percentual: ${overallPercent.toFixed(1)}%\n`);

    // Status line
    if (this.isComplete()) {
      console.log(
        "🎉 UPLOAD CONCLUÍDO COM SUCESSO! Verifique relatórios gerados.\n"
      );
    } else if (this.isRunning()) {
      console.log("⏳ Upload em progresso... (Ctrl+C para cancelar)\n");
    } else {
      console.log("⏸️  Aguardando início... (Ctrl+C para sair)\n");
    }
  }

  isRunning() {
    return (
      this.metrics.s3.startTime && !this.metrics.dynamodb.endTime ||
      (this.metrics.dynamodb.startTime && !this.metrics.dynamodb.endTime)
    );
  }

  isComplete() {
    return (
      this.metrics.s3.endTime &&
      this.metrics.dynamodb.endTime &&
      this.metrics.s3.failed === 0 &&
      this.metrics.dynamodb.failed === 0
    );
  }

  loadReports() {
    // Tentar carregar S3 Report
    try {
      const s3ReportPath = path.join(__dirname, "../S3_UPLOAD_REPORT.json");
      if (fs.existsSync(s3ReportPath)) {
        const s3Report = JSON.parse(fs.readFileSync(s3ReportPath, "utf8"));
        this.metrics.s3.uploaded = s3Report.uploaded_count || 0;
        this.metrics.s3.failed = s3Report.error_count || 0;
        if (s3Report.timestamp) {
          this.metrics.s3.endTime = new Date(s3Report.timestamp).getTime();
        }
      }
    } catch (error) {
      // Ignorar erros ao carregar reports
    }

    // Tentar carregar DynamoDB Report
    try {
      const dbReportPath = path.join(
        __dirname,
        "../DYNAMODB_UPLOAD_REPORT.json"
      );
      if (fs.existsSync(dbReportPath)) {
        const dbReport = JSON.parse(fs.readFileSync(dbReportPath, "utf8"));
        this.metrics.dynamodb.uploaded = dbReport.uploaded_count || 0;
        this.metrics.dynamodb.failed = dbReport.error_count || 0;
        if (dbReport.timestamp) {
          this.metrics.dynamodb.endTime = new Date(dbReport.timestamp).getTime();
        }
      }
    } catch (error) {
      // Ignorar erros ao carregar reports
    }

    // Tentar carregar Facebook Report
    try {
      const fbReportPath = path.join(
        __dirname,
        "../FACEBOOK_SYNC_FROM_AWS.json"
      );
      if (fs.existsSync(fbReportPath)) {
        const fbReport = JSON.parse(fs.readFileSync(fbReportPath, "utf8"));
        this.metrics.facebook.synced =
          fbReport.successful || fbReport.synced_products?.length || 0;
        this.metrics.facebook.failed = fbReport.failed || 0;
        if (fbReport.timestamp) {
          this.metrics.facebook.endTime = new Date(fbReport.timestamp).getTime();
        }
      }
    } catch (error) {
      // Ignorar erros ao carregar reports
    }
  }

  start() {
    console.log("🚀 Iniciando monitoramento...\n");

    // Marcar tempo inicial
    this.metrics.s3.startTime = Date.now();

    setInterval(() => {
      this.loadReports();
      this.displayMetrics();
    }, 1000);

    // Exibir primeiro
    this.displayMetrics();
  }
}

// Iniciar dashboard
const dashboard = new UploadDashboard();
dashboard.start();

// Lidar com Ctrl+C
process.on("SIGINT", () => {
  console.log("\n\n📊 Dashboard fechado. Verifique os relatórios:\n");
  console.log("  • S3_UPLOAD_REPORT.json");
  console.log("  • DYNAMODB_UPLOAD_REPORT.json");
  console.log("  • FACEBOOK_SYNC_FROM_AWS.json\n");
  process.exit(0);
});
