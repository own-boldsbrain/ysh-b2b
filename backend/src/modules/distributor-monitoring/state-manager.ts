import { Logger } from '@medusajs/framework/logger';
import { RedisClientType } from 'redis';
import { Pool } from 'pg';
import { 
  DistributorStatusInfo, 
  DistributorStatus, 
  DistributorState,
  HealthMetrics,
  StatusHistory,
  StatusHistoryEntry 
} from './types';

/**
 * Gerenciador de estados dos distribuidores
 * 
 * Responsável por:
 * - Persistir estados no AWS ElastiCache (Redis)
 * - Recuperar estados atuais do cache
 * - Manter histórico no AWS RDS (PostgreSQL)
 */
export class DistributorStateManager {
  private logger: Logger;
  private redisClient: RedisClientType;
  private dbPool: Pool;

  constructor(
    redisClient: RedisClientType,
    dbPool: Pool,
    logger: Logger
  ) {
    this.redisClient = redisClient;
    this.dbPool = dbPool;
    this.logger = logger;
  }

  /**
   * Atualiza o estado de um distribuidor no cache
   */
  async updateState(statusInfo: DistributorStatusInfo): Promise<void> {
    const cacheKey = this.getCacheKey(statusInfo.distributorId);

    try {
      // Serializar para Redis
      const serialized = JSON.stringify({
        ...statusInfo,
        lastCheck: statusInfo.lastCheck.toISOString(),
        nextCheck: statusInfo.nextCheck.toISOString(),
        metrics: {
          ...statusInfo.metrics,
          lastSuccessfulRequest: statusInfo.metrics.lastSuccessfulRequest?.toISOString()
        }
      // Salvar no AWS ElastiCache (Redis) com TTL
      const ttl = 300; // 5 minutos default
      await this.redisClient.setEx(cacheKey, ttl, serialized);
      const ttl = 300; // 5 minutos default
      await this.redisClient.setex(cacheKey, ttl, serialized);

      this.logger.debug(`State updated in cache for distributor ${statusInfo.distributorId}`);
    } catch (error) {
      this.logger.error(`Failed to update state in cache for ${statusInfo.distributorId}:`, error);
      throw error;
    }
  }

  /**
   * Recupera o estado atual de um distribuidor do cache
   */
  async getState(distributorId: string): Promise<DistributorStatusInfo | null> {
    const cacheKey = this.getCacheKey(distributorId);

    try {
      const cached = await this.redisClient.get(cacheKey);
      
      if (!cached) {
        this.logger.debug(`No cached state found for distributor ${distributorId}`);
        return null;
      }

      const parsed = JSON.parse(cached);
      
      // Deserializar datas
      return {
        ...parsed,
        lastCheck: new Date(parsed.lastCheck),
        nextCheck: new Date(parsed.nextCheck),
        metrics: {
          ...parsed.metrics,
          lastSuccessfulRequest: parsed.metrics.lastSuccessfulRequest 
            ? new Date(parsed.metrics.lastSuccessfulRequest)
            : undefined
        }
      };
    } catch (error) {
      this.logger.error(`Failed to get state from cache for ${distributorId}:`, error);
      return null;
    }
  }

  /**
   * Recupera estados de todos os distribuidores
   */
  async getAllStates(): Promise<DistributorStatusInfo[]> {
    try {
      const pattern = 'distributor:status:*';
      const keys = await this.redisClient.keys(pattern);
      
      if (!keys || keys.length === 0) {
        return [];
      }

      const states: DistributorStatusInfo[] = [];
      
      for (const key of keys) {
        const cached = await this.redisClient.get(key);
        if (cached) {
          const parsed = JSON.parse(cached);
          states.push({
            ...parsed,
            lastCheck: new Date(parsed.lastCheck),
            nextCheck: new Date(parsed.nextCheck),
            metrics: {
              ...parsed.metrics,
              lastSuccessfulRequest: parsed.metrics.lastSuccessfulRequest 
                ? new Date(parsed.metrics.lastSuccessfulRequest)
                : undefined
            }
          });
        }
      }

      return states;
    } catch (error) {
      this.logger.error('Failed to get all states from cache:', error);
      return [];
    }
  }

  /**
  async persistHistoryEntry(
    distributorId: string,
    entry: StatusHistoryEntry
  ): Promise<void> {
    try {
      await this.dbPool.query(
        `INSERT INTO distributor_status_history 
         (distributor_id, timestamp, status, state, metrics, event_data)
         VALUES ($1, $2, $3, $4, $5, $6)`,
        [
          distributorId,
          entry.timestamp,
          entry.status,
          entry.state,
          JSON.stringify(entry.metrics),
          entry.event ? JSON.stringify(entry.event) : null
        ]
      );  entry.event ? JSON.stringify(entry.event) : null
        ]
      );

      this.logger.debug(`History entry persisted for distributor ${distributorId}`);
    } catch (error) {
      this.logger.error(`Failed to persist history entry for ${distributorId}:`, error);
      // Não propagar erro - histórico é importante mas não crítico
    }
  }

  /**
  async getHistory(
    distributorId: string,
    periodStart: Date,
    periodEnd: Date,
    limit: number = 1000
  ): Promise<StatusHistory> {
    try {
      const result = await this.dbPool.query(
    try {
      const result = await this.db.query(
        `SELECT timestamp, status, state, metrics, event_data
         FROM distributor_status_history
         WHERE distributor_id = $1
           AND timestamp >= $2
           AND timestamp <= $3
         ORDER BY timestamp DESC
         LIMIT $4`,
        [distributorId, periodStart, periodEnd, limit]
      );

      const entries: StatusHistoryEntry[] = result.rows.map((row: any) => ({
        timestamp: new Date(row.timestamp),
        status: row.status as DistributorStatus,
        state: row.state as DistributorState,
        metrics: JSON.parse(row.metrics) as HealthMetrics,
        event: row.event_data ? JSON.parse(row.event_data) : undefined
      }));

      return {
        distributorId,
        entries,
        totalEntries: entries.length,
        periodStart,
        periodEnd
      };
    } catch (error) {
      this.logger.error(`Failed to get history for ${distributorId}:`, error);
      return {
        distributorId,
        entries: [],
        totalEntries: 0,
        periodStart,
        periodEnd
      };
    }
  }

  /**
   * Limpa estado do cache (útil para testes ou reset)
   */
  async clearState(distributorId: string): Promise<void> {
    const cacheKey = this.getCacheKey(distributorId);
    
    try {
      await this.redisClient.del(cacheKey);
      this.logger.debug(`State cleared from cache for distributor ${distributorId}`);
    } catch (error) {
      this.logger.error(`Failed to clear state for ${distributorId}:`, error);
    }
  }

  /**
   * Calcula métricas agregadas a partir do histórico
   */
  async calculateAggregatedMetrics(
    distributorId: string,
    periodStart: Date,
    periodEnd: Date
  ): Promise<{
    averageResponseTime: number;
    averageSuccessRate: number;
    uptimePercentage: number;
    totalChecks: number;
  }> {
    try {
      const result = await this.dbPool.query(
        `SELECT 
           AVG((metrics->>'responseTime')::numeric) as avg_response_time,
           AVG((metrics->>'successRate')::numeric) as avg_success_rate,
           COUNT(*) as total_checks,
           SUM(CASE WHEN status = 'ONLINE' THEN 1 ELSE 0 END) as online_checks
         FROM distributor_status_history
         WHERE distributor_id = $1
           AND timestamp >= $2
           AND timestamp <= $3`,
        [distributorId, periodStart, periodEnd]
      );

      const row = result.rows[0];

      return {
        averageResponseTime: parseFloat(row.avg_response_time) || 0,
        averageSuccessRate: parseFloat(row.avg_success_rate) || 0,
        uptimePercentage: row.total_checks > 0 
          ? (row.online_checks / row.total_checks) * 100 
          : 0,
        totalChecks: parseInt(row.total_checks) || 0
      };
    } catch (error) {
      this.logger.error(`Failed to calculate metrics for ${distributorId}:`, error);
      return {
        averageResponseTime: 0,
        averageSuccessRate: 0,
        uptimePercentage: 0,
        totalChecks: 0
      };
    }
  }

  /**
   * Gera chave do AWS ElastiCache (Redis) para um distribuidor
   */
  private getCacheKey(distributorId: string): string {
    return `distributor:status:${distributorId}`;
  }
}
