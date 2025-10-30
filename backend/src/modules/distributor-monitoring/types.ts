/**
 * Distributor Monitoring Types
 * 
 * Define todos os tipos relacionados ao monitoramento de status e estados de distribuidores
 */

/**
 * Status operacional do distribuidor
 */
export enum DistributorStatus {
  ONLINE = 'ONLINE',
  OFFLINE = 'OFFLINE',
  TIMEOUT = 'TIMEOUT',
  ERROR = 'ERROR'
}

/**
 * Estado funcional do distribuidor
 */
export enum DistributorState {
  DISPONIVEL = 'DISPONÍVEL',        // Operacional e aceitando pedidos
  DEGRADADO = 'DEGRADADO',          // Operacional mas com performance reduzida
  INDISPONIVEL = 'INDISPONÍVEL',    // Sistema offline ou não responsivo
  MANUTENCAO = 'MANUTENÇÃO',        // Fora de operação programada
  LIMITADO = 'LIMITADO'             // Operacional mas com restrições
}

/**
 * Severidade de um problema detectado
 */
export enum AlertSeverity {
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

/**
 * Métricas de saúde de um distribuidor
 */
export interface HealthMetrics {
  responseTime: number;              // Latência média em ms
  successRate: number;               // Taxa de sucesso (0-100)
  errorRate: number;                 // Taxa de erro (0-100)
  availability: number;              // Disponibilidade histórica (0-100)
  requestsPerMinute: number;         // Throughput
  lastSuccessfulRequest?: Date;      // Último request bem-sucedido
  consecutiveFailures: number;       // Falhas consecutivas
}

/**
 * Informações completas sobre o estado de um distribuidor
 */
export interface DistributorStatusInfo {
  distributorId: string;
  distributorName: string;
  status: DistributorStatus;
  state: DistributorState;
  metrics: HealthMetrics;
  lastCheck: Date;
  nextCheck: Date;
  metadata?: {
    apiEndpoint?: string;
    version?: string;
    region?: string;
    [key: string]: any;
  };
}

/**
 * Evento de mudança de status
 */
export interface StatusChangeEvent {
  distributorId: string;
  distributorName: string;
  previousStatus: DistributorStatus;
  currentStatus: DistributorStatus;
  previousState: DistributorState;
  currentState: DistributorState;
  timestamp: Date;
  reason?: string;
  metrics: HealthMetrics;
  severity: AlertSeverity;
}

/**
 * Resultado de um health check
 */
export interface HealthCheckResult {
  success: boolean;
  status: DistributorStatus;
  responseTime: number;
  timestamp: Date;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata?: {
    httpStatusCode?: number;
    headers?: Record<string, string>;
    [key: string]: any;
  };
}

/**
 * Configuração de monitoramento para um distribuidor
 */
export interface MonitoringConfig {
  distributorId: string;
  distributorName: string;
  healthCheckUrl: string;
  checkIntervalMs: number;           // Intervalo entre checks (default: 60000 = 1 min)
  timeoutMs: number;                 // Timeout para health check (default: 5000)
  consecutiveFailuresThreshold: number; // Falhas consecutivas para marcar como OFFLINE
  degradedPerformanceThreshold: number; // % de performance para estado DEGRADADO
  cacheTTLSeconds: number;           // TTL no Redis (default: 300 = 5 min)
  enabled: boolean;
  metadata?: Record<string, any>;
}

/**
 * Histórico de status de um distribuidor
 */
export interface StatusHistory {
  distributorId: string;
  entries: StatusHistoryEntry[];
  totalEntries: number;
  periodStart: Date;
  periodEnd: Date;
}

/**
 * Entrada no histórico de status
 */
export interface StatusHistoryEntry {
  timestamp: Date;
  status: DistributorStatus;
  state: DistributorState;
  metrics: HealthMetrics;
  event?: StatusChangeEvent;
}

/**
 * Relatório de disponibilidade de um distribuidor
 */
export interface AvailabilityReport {
  distributorId: string;
  distributorName: string;
  periodStart: Date;
  periodEnd: Date;
  uptimePercentage: number;
  totalChecks: number;
  successfulChecks: number;
  failedChecks: number;
  averageResponseTime: number;
  incidents: {
    count: number;
    totalDowntimeMs: number;
    details: Array<{
      start: Date;
      end: Date;
      durationMs: number;
      reason: string;
    }>;
  };
}
