import { Logger } from '@medusajs/framework/logger';
import axios, { AxiosInstance } from 'axios';
import {
  MonitoringConfig,
  HealthCheckResult,
  DistributorStatus,
  DistributorState,
  DistributorStatusInfo,
  StatusChangeEvent,
  AlertSeverity,
  HealthMetrics
} from './types';
import { DistributorStateManager } from './state-manager';
import { StatusEventPublisher } from './event-publisher';

/**
 * Serviço de Monitoramento de Status dos Distribuidores
 * 
 * Responsabilidades:
 * - Executar health checks periódicos
 * - Avaliar estado baseado em métricas
 * - Atualizar cache (Redis)
 * - Publicar eventos de mudança (Service Bus)
 * - Persistir histórico (PostgreSQL)
 */
export class DistributorStatusMonitor {
  private logger: Logger;
  private stateManager: DistributorStateManager;
  private eventPublisher: StatusEventPublisher;
  private httpClient: AxiosInstance;
  private monitoringConfigs: Map<string, MonitoringConfig>;
  private activeMonitors: Map<string, NodeJS.Timeout>;
  private isRunning: boolean = false;

  constructor(
    stateManager: DistributorStateManager,
    eventPublisher: StatusEventPublisher,
    logger: Logger
  ) {
    this.stateManager = stateManager;
    this.eventPublisher = eventPublisher;
    this.logger = logger;
    this.monitoringConfigs = new Map();
    this.activeMonitors = new Map();
    
    this.httpClient = axios.create({
      timeout: 5000,
      headers: {
        'User-Agent': 'YSH-B2B-Monitor/1.0'
      }
    });
  }

  /**
   * Inicia monitoramento de todos os distribuidores configurados
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      this.logger.warn('Monitor already running');
      return;
    }

    this.isRunning = true;
    this.logger.info('Starting distributor status monitor...');

    // Carregar configurações (mock - em prod viria do DB)
    await this.loadMonitoringConfigs();

    // Iniciar monitoramento de cada distribuidor
    for (const [distributorId, config] of this.monitoringConfigs.entries()) {
      if (config.enabled) {
        this.startMonitoring(distributorId, config);
      }
    }

    this.logger.info(
      `Monitor started. Monitoring ${this.activeMonitors.size} distributors`
    );
  }

  /**
   * Para o monitoramento de todos os distribuidores
   */
  async stop(): Promise<void> {
    if (!this.isRunning) {
      return;
    }

    this.logger.info('Stopping distributor status monitor...');

    // Parar todos os timers
    for (const [distributorId, timer] of this.activeMonitors.entries()) {
      clearInterval(timer);
      this.logger.debug(`Stopped monitoring ${distributorId}`);
    }

    this.activeMonitors.clear();
    this.isRunning = false;

    this.logger.info('Monitor stopped');
  }

  /**
   * Inicia monitoramento de um distribuidor específico
   */
  private startMonitoring(
    distributorId: string,
    config: MonitoringConfig
  ): void {
    // Executar primeiro check imediatamente
    this.performHealthCheck(distributorId, config);

    // Agendar checks periódicos
    const timer = setInterval(
      () => this.performHealthCheck(distributorId, config),
      config.checkIntervalMs
    );

    this.activeMonitors.set(distributorId, timer);

    this.logger.info(
      `Started monitoring ${config.distributorName} (${distributorId}) ` +
      `with interval ${config.checkIntervalMs}ms`
    );
  }

  /**
   * Executa health check em um distribuidor
   */
  private async performHealthCheck(
    distributorId: string,
    config: MonitoringConfig
  ): Promise<void> {
    const startTime = Date.now();

    try {
      // Executar health check HTTP
      const checkResult = await this.executeHealthCheck(config);

      // Recuperar estado anterior
      const previousState = await this.stateManager.getState(distributorId);

      // Calcular métricas atualizadas
      const metrics = this.calculateMetrics(
        checkResult,
        previousState?.metrics
      );

      // Determinar novo status e estado
      const newStatus = checkResult.status;
      const newState = this.determineState(metrics, config);

      // Criar info de status atualizado
      const statusInfo: DistributorStatusInfo = {
        distributorId,
        distributorName: config.distributorName,
        status: newStatus,
        state: newState,
        metrics,
        lastCheck: new Date(),
        nextCheck: new Date(Date.now() + config.checkIntervalMs),
        metadata: config.metadata
      };

      // Atualizar cache
      await this.stateManager.updateState(statusInfo);

      // Persistir no histórico
      await this.stateManager.persistHistoryEntry(distributorId, {
        timestamp: statusInfo.lastCheck,
        status: newStatus,
        state: newState,
        metrics
      });

      // Verificar se houve mudança de estado
      if (previousState) {
        await this.checkAndPublishStatusChange(
          previousState,
          statusInfo,
          checkResult.error?.message
        );
      }

      this.logger.debug(
        `Health check completed for ${config.distributorName}: ` +
        `${newStatus} / ${newState} (${checkResult.responseTime}ms)`
      );
    } catch (error) {
      this.logger.error(
        `Health check failed for ${config.distributorName}:`,
        error
      );
    }
  }

  /**
   * Executa requisição HTTP de health check
   */
  private async executeHealthCheck(
    config: MonitoringConfig
  ): Promise<HealthCheckResult> {
    const startTime = Date.now();

    try {
      const response = await this.httpClient.get(config.healthCheckUrl, {
        timeout: config.timeoutMs
      });

      const responseTime = Date.now() - startTime;

      return {
        success: response.status >= 200 && response.status < 300,
        status: DistributorStatus.ONLINE,
        responseTime,
        timestamp: new Date(),
        metadata: {
          httpStatusCode: response.status,
          headers: response.headers as Record<string, string>
        }
      };
    } catch (error: any) {
      const responseTime = Date.now() - startTime;

      // Determinar tipo de erro
      let status = DistributorStatus.ERROR;
      let errorCode = 'UNKNOWN_ERROR';
      let errorMessage = 'Unknown error occurred';

      if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
        status = DistributorStatus.TIMEOUT;
        errorCode = 'TIMEOUT';
        errorMessage = `Request timeout after ${config.timeoutMs}ms`;
      } else if (error.code === 'ECONNREFUSED') {
        status = DistributorStatus.OFFLINE;
        errorCode = 'CONNECTION_REFUSED';
        errorMessage = 'Connection refused';
      } else if (error.response) {
        status = DistributorStatus.ERROR;
        errorCode = `HTTP_${error.response.status}`;
        errorMessage = `HTTP ${error.response.status}: ${error.response.statusText}`;
      }

      return {
        success: false,
        status,
        responseTime,
        timestamp: new Date(),
        error: {
          code: errorCode,
          message: errorMessage,
          details: {
            originalError: error.message,
            code: error.code
          }
        },
        metadata: {
          httpStatusCode: error.response?.status
        }
      };
    }
  }

  /**
   * Calcula métricas atualizadas baseado no resultado do check
   */
  private calculateMetrics(
    checkResult: HealthCheckResult,
    previousMetrics?: HealthMetrics
  ): HealthMetrics {
    const isSuccess = checkResult.success;
    const consecutiveFailures = isSuccess 
      ? 0 
      : (previousMetrics?.consecutiveFailures || 0) + 1;

    // Calcular taxas usando média móvel exponencial (alpha = 0.2)
    const alpha = 0.2;
    const successRate = previousMetrics
      ? previousMetrics.successRate * (1 - alpha) + (isSuccess ? 100 : 0) * alpha
      : (isSuccess ? 100 : 0);

    const errorRate = 100 - successRate;

    // Calcular média móvel de response time
    const responseTime = previousMetrics
      ? previousMetrics.responseTime * (1 - alpha) + checkResult.responseTime * alpha
      : checkResult.responseTime;

    // Disponibilidade histórica (simplificado)
    const availability = successRate; // Em prod, calcular dos últimos N dias

    return {
      responseTime: Math.round(responseTime),
      successRate: Math.round(successRate * 100) / 100,
      errorRate: Math.round(errorRate * 100) / 100,
      availability: Math.round(availability * 100) / 100,
      requestsPerMinute: 0, // TODO: Calcular baseado em throughput real
      lastSuccessfulRequest: isSuccess ? new Date() : previousMetrics?.lastSuccessfulRequest,
      consecutiveFailures
    };
  }

  /**
   * Determina o estado funcional baseado nas métricas
   */
  private determineState(
    metrics: HealthMetrics,
    config: MonitoringConfig
  ): DistributorState {
    // Verificar falhas consecutivas
    if (metrics.consecutiveFailures >= config.consecutiveFailuresThreshold) {
      return DistributorState.INDISPONIVEL;
    }

    // Verificar performance degradada
    if (metrics.successRate < config.degradedPerformanceThreshold) {
      return DistributorState.DEGRADADO;
    }

    // Verificar response time alto (> 5s = degradado)
    if (metrics.responseTime > 5000) {
      return DistributorState.DEGRADADO;
    }

    // Tudo OK
    return DistributorState.DISPONIVEL;
  }

  /**
   * Verifica mudança de estado e publica evento se necessário
   */
  private async checkAndPublishStatusChange(
    previousState: DistributorStatusInfo,
    currentState: DistributorStatusInfo,
    reason?: string
  ): Promise<void> {
    const statusChanged = previousState.status !== currentState.status;
    const stateChanged = previousState.state !== currentState.state;

    if (!statusChanged && !stateChanged) {
      return; // Sem mudanças
    }

    // Determinar severidade
    const severity = this.determineSeverity(
      previousState.status,
      currentState.status,
      previousState.state,
      currentState.state
    );

    // Criar evento
    const event: StatusChangeEvent = {
      distributorId: currentState.distributorId,
      distributorName: currentState.distributorName,
      previousStatus: previousState.status,
      currentStatus: currentState.status,
      previousState: previousState.state,
      currentState: currentState.state,
      timestamp: new Date(),
      reason,
      metrics: currentState.metrics,
      severity
    };

    // Publicar evento apropriado
    if (severity === AlertSeverity.CRITICAL) {
      await this.eventPublisher.publishCriticalAlert(event);
    } else if (currentState.state === DistributorState.DISPONIVEL && 
               previousState.state !== DistributorState.DISPONIVEL) {
      await this.eventPublisher.publishRecoveryEvent(event);
    } else if (currentState.state === DistributorState.DEGRADADO) {
      await this.eventPublisher.publishDegradationEvent(event);
    } else {
      await this.eventPublisher.publishStatusChange(event);
    }
  }

  /**
   * Determina severidade de uma mudança de estado
   */
  private determineSeverity(
    prevStatus: DistributorStatus,
    currStatus: DistributorStatus,
    prevState: DistributorState,
    currState: DistributorState
  ): AlertSeverity {
    // ONLINE → OFFLINE é crítico
    if (prevStatus === DistributorStatus.ONLINE && 
        currStatus === DistributorStatus.OFFLINE) {
      return AlertSeverity.CRITICAL;
    }

    // DISPONÍVEL → INDISPONÍVEL é crítico
    if (prevState === DistributorState.DISPONIVEL && 
        currState === DistributorState.INDISPONIVEL) {
      return AlertSeverity.CRITICAL;
    }

    // DEGRADADO é warning
    if (currState === DistributorState.DEGRADADO) {
      return AlertSeverity.WARNING;
    }

    // Timeout é error
    if (currStatus === DistributorStatus.TIMEOUT) {
      return AlertSeverity.ERROR;
    }

    // Recuperação é info
    if (currState === DistributorState.DISPONIVEL && 
        prevState !== DistributorState.DISPONIVEL) {
      return AlertSeverity.INFO;
    }

    return AlertSeverity.WARNING;
  }

  /**
   * Carrega configurações de monitoramento (mock)
   * Em produção, viria do banco de dados
   */
  private async loadMonitoringConfigs(): Promise<void> {
    // Mock de configurações - em prod, buscar do DB
    const mockConfigs: MonitoringConfig[] = [
      {
        distributorId: 'dist-a',
        distributorName: 'Distribuidor A',
        healthCheckUrl: 'https://api.distribuidor-a.com/health',
        checkIntervalMs: 60000, // 1 minuto
        timeoutMs: 5000,
        consecutiveFailuresThreshold: 3,
        degradedPerformanceThreshold: 80,
        cacheTTLSeconds: 300,
        enabled: true
      },
      {
        distributorId: 'dist-b',
        distributorName: 'Distribuidor B',
        healthCheckUrl: 'https://api.distribuidor-b.com/health',
        checkIntervalMs: 60000,
        timeoutMs: 5000,
        consecutiveFailuresThreshold: 3,
        degradedPerformanceThreshold: 75,
        cacheTTLSeconds: 300,
        enabled: true
      },
      {
        distributorId: 'dist-c',
        distributorName: 'Distribuidor C',
        healthCheckUrl: 'https://api.distribuidor-c.com/health',
        checkIntervalMs: 120000, // 2 minutos (menos crítico)
        timeoutMs: 5000,
        consecutiveFailuresThreshold: 5,
        degradedPerformanceThreshold: 70,
        cacheTTLSeconds: 300,
        enabled: true
      },
      {
        distributorId: 'dist-d',
        distributorName: 'Distribuidor D',
        healthCheckUrl: 'https://api.distribuidor-d.com/health',
        checkIntervalMs: 60000,
        timeoutMs: 5000,
        consecutiveFailuresThreshold: 3,
        degradedPerformanceThreshold: 85,
        cacheTTLSeconds: 300,
        enabled: true
      }
    ];

    mockConfigs.forEach(config => {
      this.monitoringConfigs.set(config.distributorId, config);
    });

    this.logger.info(`Loaded ${mockConfigs.length} monitoring configurations`);
  }

  /**
   * Adiciona ou atualiza configuração de monitoramento
   */
  async updateMonitoringConfig(config: MonitoringConfig): Promise<void> {
    const wasMonitoring = this.activeMonitors.has(config.distributorId);

    // Atualizar config
    this.monitoringConfigs.set(config.distributorId, config);

    // Se já estava monitorando, reiniciar
    if (wasMonitoring) {
      const timer = this.activeMonitors.get(config.distributorId);
      if (timer) {
        clearInterval(timer);
      }
      
      if (config.enabled) {
        this.startMonitoring(config.distributorId, config);
      } else {
        this.activeMonitors.delete(config.distributorId);
      }
    } else if (config.enabled) {
      // Se não estava monitorando mas agora está habilitado, iniciar
      this.startMonitoring(config.distributorId, config);
    }

    this.logger.info(`Updated monitoring config for ${config.distributorName}`);
  }

  /**
   * Remove configuração de monitoramento
   */
  async removeMonitoringConfig(distributorId: string): Promise<void> {
    const timer = this.activeMonitors.get(distributorId);
    if (timer) {
      clearInterval(timer);
      this.activeMonitors.delete(distributorId);
    }

    this.monitoringConfigs.delete(distributorId);

    this.logger.info(`Removed monitoring config for ${distributorId}`);
  }

  /**
   * Retorna status atual de todos os distribuidores
   */
  async getAllDistributorStatus(): Promise<DistributorStatusInfo[]> {
    return this.stateManager.getAllStates();
  }

  /**
   * Retorna status de um distribuidor específico
   */
  async getDistributorStatus(distributorId: string): Promise<DistributorStatusInfo | null> {
    return this.stateManager.getState(distributorId);
  }
}
