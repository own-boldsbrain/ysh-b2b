#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { HfInference } from "@huggingface/inference";
import { listFiles, downloadFile } from "@huggingface/hub";
import { parse } from "csv-parse/sync";
import { z } from "zod";

// Environment variables
const HF_TOKEN = process.env.HF_TOKEN;
const HF_USERNAME = "fernando-bold";
const DATASET_REPO = `${HF_USERNAME}/aneel-datasets`;

// Hugging Face client
const hf = new HfInference(HF_TOKEN);

// Tool definitions
const tools: Tool[] = [
  {
    name: "list_aneel_datasets",
    description:
      "Lista todos os datasets ANEEL disponíveis no repositório Hugging Face. Retorna informações sobre arquivos CSV disponíveis, incluindo nome, tamanho e path.",
    inputSchema: {
      type: "object",
      properties: {
        filter: {
          type: "string",
          description:
            "Filtro opcional para buscar datasets específicos (ex: 'tarifa', 'concessionaria', 'geracao')",
        },
      },
    },
  },
  {
    name: "query_aneel_dataset",
    description:
      "Consulta um dataset ANEEL específico. Baixa e parseia o CSV, permitindo filtros por coluna. Ideal para buscar tarifas de energia, dados de concessionárias ou informações de geração distribuída.",
    inputSchema: {
      type: "object",
      properties: {
        filename: {
          type: "string",
          description: "Nome do arquivo CSV no repositório (ex: 'tarifas_energia.csv')",
        },
        filters: {
          type: "object",
          description:
            "Filtros opcionais por coluna. Ex: {'estado': 'SP', 'concessionaria': 'CPFL'}",
          additionalProperties: { type: "string" },
        },
        limit: {
          type: "number",
          description: "Número máximo de resultados a retornar (padrão: 100)",
          default: 100,
        },
      },
      required: ["filename"],
    },
  },
  {
    name: "get_tariff_data",
    description:
      "Consulta específica para dados de tarifas ANEEL. Retorna tarifas de energia por concessionária, estado e modalidade. Otimizado para cálculos do Project Helios.",
    inputSchema: {
      type: "object",
      properties: {
        concessionaria: {
          type: "string",
          description: "Nome da concessionária (ex: 'CPFL Paulista', 'CEMIG')",
        },
        estado: {
          type: "string",
          description: "Sigla do estado (ex: 'SP', 'MG', 'RJ')",
        },
        modalidade: {
          type: "string",
          description: "Modalidade tarifária (ex: 'Convencional', 'Branca')",
        },
        classe: {
          type: "string",
          description: "Classe de consumo (ex: 'Residencial', 'Comercial', 'Industrial')",
        },
      },
    },
  },
];

// Server initialization
const server = new Server(
  {
    name: "huggingface-aneel-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Helper: List files from Hugging Face repository
async function listHuggingFaceFiles(filter?: string): Promise<any[]> {
  const files = [];
  for await (const fileInfo of listFiles({
    repo: DATASET_REPO,
    credentials: { accessToken: HF_TOKEN },
  })) {
    if (fileInfo.type === "file" && fileInfo.path.endsWith(".csv")) {
      if (!filter || fileInfo.path.toLowerCase().includes(filter.toLowerCase())) {
        files.push({
          name: fileInfo.path,
          size: fileInfo.size,
          path: fileInfo.path,
        });
      }
    }
  }
  return files;
}

// Helper: Download and parse CSV from Hugging Face
async function downloadAndParseCSV(
  filename: string,
  filters?: Record<string, string>,
  limit: number = 100
): Promise<any[]> {
  try {
    const blob = await downloadFile({
      repo: DATASET_REPO,
      path: filename,
      credentials: { accessToken: HF_TOKEN },
    });

    if (!blob) {
      throw new Error(`File ${filename} not found`);
    }

    const csvText = await blob.text();
    const records = parse(csvText, {
      columns: true,
      skip_empty_lines: true,
      trim: true,
    });

    // Apply filters
    let filtered = records;
    if (filters && Object.keys(filters).length > 0) {
      filtered = records.filter((record: any) => {
        return Object.entries(filters).every(([key, value]) => {
          return record[key]?.toLowerCase().includes(value.toLowerCase());
        });
      });
    }

    // Apply limit
    return filtered.slice(0, limit);
  } catch (error) {
    throw new Error(`Failed to download/parse CSV: ${error}`);
  }
}

// Tool handlers
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "list_aneel_datasets": {
        const schema = z.object({
          filter: z.string().optional(),
        });
        const parsed = schema.parse(args);
        const files = await listHuggingFaceFiles(parsed.filter);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  total: files.length,
                  datasets: files,
                },
                null,
                2
              ),
            },
          ],
        };
      }

      case "query_aneel_dataset": {
        const schema = z.object({
          filename: z.string(),
          filters: z.record(z.string()).optional(),
          limit: z.number().default(100),
        });
        const parsed = schema.parse(args);
        const results = await downloadAndParseCSV(
          parsed.filename,
          parsed.filters,
          parsed.limit
        );
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  filename: parsed.filename,
                  filters: parsed.filters || {},
                  count: results.length,
                  data: results,
                },
                null,
                2
              ),
            },
          ],
        };
      }

      case "get_tariff_data": {
        const schema = z.object({
          concessionaria: z.string().optional(),
          estado: z.string().optional(),
          modalidade: z.string().optional(),
          classe: z.string().optional(),
        });
        const parsed = schema.parse(args);

        // Build filters from provided parameters
        const filters: Record<string, string> = {};
        if (parsed.concessionaria) filters.concessionaria = parsed.concessionaria;
        if (parsed.estado) filters.estado = parsed.estado;
        if (parsed.modalidade) filters.modalidade = parsed.modalidade;
        if (parsed.classe) filters.classe = parsed.classe;

        // Query the tariff dataset (assuming filename is 'tarifas_energia.csv')
        const results = await downloadAndParseCSV(
          "tarifas_energia.csv",
          filters,
          100
        );

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  query: parsed,
                  count: results.length,
                  tarifas: results,
                },
                null,
                2
              ),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            error: error instanceof Error ? error.message : String(error),
          }),
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Hugging Face ANEEL MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});
