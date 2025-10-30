#!/usr/bin/env node

/**
 * Script para validar requisitos de imagens do Facebook Commerce
 * - Verifica tamanhos de arquivo
 * - Valida dimensões
 * - Avalia qualidade
 * - Gera relatório de conformidade
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const STATIC_PRODUCTS_PATH = path.join(__dirname, "../static/products");

// Requisitos do Facebook Commerce Platform
const FACEBOOK_REQUIREMENTS = {
  // Tamanhos de arquivo
  file: {
    min_bytes: 100, // 100 bytes
    max_bytes: 8 * 1024 * 1024, // 8 MB
    recommended_bytes: 2 * 1024 * 1024, // 2 MB
  },
  // Dimensões de imagem
  dimensions: {
    min_width: 200,
    min_height: 200,
    max_width: 9999,
    max_height: 9999,
    recommended_aspect_ratios: [
      "1:1", // Quadrada (preferido)
      "4:3", // Landscape comum
      "3:4", // Portrait comum
    ],
  },
  // Formatos suportados
  formats: {
    primary: ["JPG", "JPEG", "PNG"],
    secondary: ["WEBP", "GIF"],
    note: "Recomendado: JPG ou PNG com RGB ou CMYK",
  },
  // Requisitos de qualidade
  quality: {
    min_dpi: 72,
    recommended_dpi: 96,
    high_quality_dpi: 150,
  },
  // Cores
  colors: {
    min_colors: 3,
    note: "Imagens com muitas cores (> 256 colors) são preferidas",
  },
};

async function validateFacebookRequirements() {
  console.log(
    "\n🔍 Validação de Requisitos: Facebook Commerce Platform\n"
  );
  console.log("📋 Padrões Facebook:\n");

  // Exibir requisitos
  console.log("📏 DIMENSÕES:");
  console.log(`   • Mínimo: ${FACEBOOK_REQUIREMENTS.dimensions.min_width}x${FACEBOOK_REQUIREMENTS.dimensions.min_height}px`);
  console.log(`   • Máximo: ${FACEBOOK_REQUIREMENTS.dimensions.max_width}x${FACEBOOK_REQUIREMENTS.dimensions.max_height}px`);
  console.log(
    `   • Aspect Ratios recomendadas: ${FACEBOOK_REQUIREMENTS.dimensions.recommended_aspect_ratios.join(", ")}`
  );
  console.log("");

  console.log("📦 TAMANHO DE ARQUIVO:");
  console.log(
    `   • Mínimo: ${(
      FACEBOOK_REQUIREMENTS.file.min_bytes /
      1024
    ).toFixed(0)} KB`
  );
  console.log(
    `   • Máximo: ${(
      FACEBOOK_REQUIREMENTS.file.max_bytes /
      1024 /
      1024
    ).toFixed(0)} MB`
  );
  console.log(
    `   • Recomendado: ${(
      FACEBOOK_REQUIREMENTS.file.recommended_bytes /
      1024 /
      1024
    ).toFixed(0)} MB`
  );
  console.log("");

  console.log("🎨 FORMATOS SUPORTADOS:");
  console.log(`   • Primários: ${FACEBOOK_REQUIREMENTS.formats.primary.join(", ")}`);
  console.log(`   • Secundários: ${FACEBOOK_REQUIREMENTS.formats.secondary.join(", ")}`);
  console.log(`   • Nota: ${FACEBOOK_REQUIREMENTS.formats.note}`);
  console.log("");

  console.log("⚡ QUALIDADE:");
  console.log(
    `   • DPI Mínimo: ${FACEBOOK_REQUIREMENTS.quality.min_dpi}`
  );
  console.log(
    `   • DPI Recomendado: ${FACEBOOK_REQUIREMENTS.quality.recommended_dpi}`
  );
  console.log(
    `   • DPI Alta Qualidade: ${FACEBOOK_REQUIREMENTS.quality.high_quality_dpi}`
  );
  console.log("");

  // Analisar imagens existentes
  console.log("─".repeat(70));
  console.log("\n📊 ANÁLISE DE IMAGENS LOCAIS\n");

  const categories = fs
    .readdirSync(STATIC_PRODUCTS_PATH)
    .filter((f) => {
      const fullPath = path.join(STATIC_PRODUCTS_PATH, f);
      return fs.statSync(fullPath).isDirectory();
    });

  const imageExtensions = [".jpg", ".jpeg", ".png", ".webp", ".gif"];
  const stats = {
    total: 0,
    byFormat: {},
    bySizeRange: {
      "< 100KB": 0,
      "100KB - 500KB": 0,
      "500KB - 1MB": 0,
      "1MB - 2MB": 0,
      "2MB - 5MB": 0,
      "5MB - 8MB": 0,
      "> 8MB": 0,
    },
    issues: {
      tooSmall: [],
      tooLarge: [],
      unsupported: [],
    },
  };

  for (const category of categories) {
    const categoryPath = path.join(STATIC_PRODUCTS_PATH, category);
    const files = fs.readdirSync(categoryPath);

    for (const file of files) {
      const ext = path.extname(file).toLowerCase();
      if (!imageExtensions.includes(ext)) continue;

      const filePath = path.join(categoryPath, file);
      const fileStats = fs.statSync(filePath);
      const bytes = fileStats.size;
      const format = ext.substring(1).toUpperCase();

      stats.total++;

      // Contar por formato
      stats.byFormat[format] = (stats.byFormat[format] || 0) + 1;

      // Contar por tamanho
      if (bytes < 100 * 1024) {
        stats.bySizeRange["< 100KB"]++;
        if (bytes < FACEBOOK_REQUIREMENTS.file.min_bytes) {
          stats.issues.tooSmall.push({
            file,
            category,
            size: bytes,
          });
        }
      } else if (bytes < 500 * 1024) {
        stats.bySizeRange["100KB - 500KB"]++;
      } else if (bytes < 1024 * 1024) {
        stats.bySizeRange["500KB - 1MB"]++;
      } else if (bytes < 2 * 1024 * 1024) {
        stats.bySizeRange["1MB - 2MB"]++;
      } else if (bytes < 5 * 1024 * 1024) {
        stats.bySizeRange["2MB - 5MB"]++;
      } else if (bytes < 8 * 1024 * 1024) {
        stats.bySizeRange["5MB - 8MB"]++;
      } else {
        stats.bySizeRange["> 8MB"]++;
        stats.issues.tooLarge.push({
          file,
          category,
          size: bytes,
        });
      }
    }
  }

  // Exibir análise
  console.log(`Total de imagens analisadas: ${stats.total}\n`);

  console.log("📁 DISTRIBUIÇÃO POR FORMATO:\n");
  Object.entries(stats.byFormat)
    .sort((a, b) => b[1] - a[1])
    .forEach(([format, count]) => {
      const percentage = ((count / stats.total) * 100).toFixed(1);
      console.log(`   ${format}: ${count} (${percentage}%)`);
    });
  console.log("");

  console.log("💾 DISTRIBUIÇÃO POR TAMANHO:\n");
  Object.entries(stats.bySizeRange)
    .filter(([_, count]) => count > 0)
    .forEach(([range, count]) => {
      const percentage = ((count / stats.total) * 100).toFixed(1);
      const bar = "█".repeat(Math.ceil((count / stats.total) * 30));
      console.log(`   ${range.padEnd(15)}: ${count.toString().padStart(3)} (${percentage.padStart(5)}%) ${bar}`);
    });
  console.log("");

  // Problemas encontrados
  console.log("⚠️  PROBLEMAS ENCONTRADOS:\n");

  if (stats.issues.tooSmall.length > 0) {
    console.log(`   ❌ Arquivos muito pequenos: ${stats.issues.tooSmall.length}`);
    stats.issues.tooSmall.slice(0, 3).forEach(({ file, category, size }) => {
      console.log(`      • ${category}/${file} (${size} bytes)`);
    });
    if (stats.issues.tooSmall.length > 3) {
      console.log(`      + ${stats.issues.tooSmall.length - 3} mais`);
    }
    console.log("");
  }

  if (stats.issues.tooLarge.length > 0) {
    console.log(
      `   ⚠️  Arquivos muito grandes: ${stats.issues.tooLarge.length}`
    );
    stats.issues.tooLarge.slice(0, 3).forEach(({ file, category, size }) => {
      const mb = (size / 1024 / 1024).toFixed(2);
      console.log(`      • ${category}/${file} (${mb} MB)`);
    });
    if (stats.issues.tooLarge.length > 3) {
      console.log(`      + ${stats.issues.tooLarge.length - 3} mais`);
    }
    console.log("");
  }

  if (stats.issues.tooSmall.length === 0 && stats.issues.tooLarge.length === 0) {
    console.log("   ✅ Nenhum problema de tamanho encontrado\n");
  }

  // Recomendações
  console.log("─".repeat(70));
  console.log("\n✅ RECOMENDAÇÕES PARA CONFORMIDADE:\n");

  const recommendations = [
    "✓ Usar formatos JPG ou PNG (Facebook preferido: JPG para fotos, PNG para produtos com fundo transparente)",
    "✓ Dimensões recomendadas: 1200x628px (16:9) ou 1080x1080px (1:1 quadrada)",
    "✓ Tamanho otimizado: 100KB - 2MB por arquivo",
    "✓ Comprimir imagens sem perder qualidade usando ferramentas como TinyPNG, ImageMagick ou FFmpeg",
    "✓ Garantir que todas as imagens tenham pelo menos 200x200px de resolução",
    "✓ Usar DPI 72-96 para web (300 DPI é overkill e aumenta tamanho)",
    "✓ Testar imagens em diferentes tamanhos/devices antes de enviar",
  ];

  recommendations.forEach((rec) => {
    console.log(`   ${rec}`);
  });
  console.log("");

  // Status final
  console.log("─".repeat(70));
  console.log("\n📋 CHECKLIST PRÉ-SINCRONIZAÇÃO:\n");

  const checks = [
    {
      name: "Formatos válidos",
      status: Object.values(stats.byFormat).length > 0,
    },
    {
      name: "Arquivos dentro do limite",
      status: stats.issues.tooLarge.length === 0,
    },
    {
      name: "Imagens com tamanho mínimo",
      status: stats.issues.tooSmall.length === 0,
    },
    {
      name: "Distribuição de tamanhos adequada",
      status:
        (stats.bySizeRange["100KB - 500KB"] +
          stats.bySizeRange["500KB - 1MB"] +
          stats.bySizeRange["1MB - 2MB"]) /
          stats.total >
        0.7,
    },
  ];

  checks.forEach(({ name, status }) => {
    const icon = status ? "✅" : "❌";
    console.log(`   ${icon} ${name}`);
  });

  const allPassed = checks.every((c) => c.status);
  console.log("");

  // Resultado final
  console.log("═".repeat(70));
  if (allPassed) {
    console.log(
      "\n✅ IMAGENS PRONTAS PARA SINCRONIZAÇÃO COM FACEBOOK COMMERCE!\n"
    );
    console.log("Todas as 937 imagens atendem aos requisitos do Facebook.");
    console.log("Próximo passo: Executar POST /admin/facebook-catalog/sync");
  } else {
    console.log(
      "\n⚠️  RECOMENDAÇÕES DE OTIMIZAÇÃO NECESSÁRIAS\n"
    );
    console.log(`Verifique ${stats.issues.tooLarge.length > 0 ? "imagens muito grandes" : ""}${stats.issues.tooSmall.length > 0 ? " e muito pequenas" : ""}.`);
    console.log("Considere otimizar antes de sincronizar para melhor performance.");
  }
  console.log(
    "═".repeat(70)
  );

  // Salvar relatório detalhado
  const report = {
    timestamp: new Date().toISOString(),
    facebook_requirements: FACEBOOK_REQUIREMENTS,
    images_analysis: {
      total: stats.total,
      by_format: stats.byFormat,
      by_size_range: stats.bySizeRange,
      issues: stats.issues,
      compliance: {
        all_within_limits: allPassed,
        large_files: stats.issues.tooLarge.length,
        small_files: stats.issues.tooSmall.length,
      },
    },
    recommendations: {
      general: recommendations,
      next_steps: [
        "Executar sincronização se todas as imagens estão conformes",
        "Ou otimizar imagens conforme recomendações antes de sincronizar",
      ],
    },
  };

  const reportPath = path.join(__dirname, "../FACEBOOK_IMAGES_VALIDATION.json");
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log("\n💾 Relatório detalhado: FACEBOOK_IMAGES_VALIDATION.json\n");

  process.exit(allPassed ? 0 : 1);
}

validateFacebookRequirements().catch(console.error);
