/**
 * AWS Configuration para Sistema de Monitoramento de Distribuidores
 * 
 * Gerencia conexões e configurações dos serviços AWS:
 * - ElastiCache (Redis) - Cache de estados
 * - RDS PostgreSQL - Histórico persistente
 * - SNS/SQS - Event streaming
 * - CloudWatch - Logs e métricas
 */

import { createClient, RedisClientType } from 'redis';
import { SNSClient } from '@aws-sdk/client-sns';
import { SQSClient } from '@aws-sdk/client-sqs';
import { CloudWatchClient } from '@aws-sdk/client-cloudwatch';
import { CloudWatchLogsClient } from '@aws-sdk/client-cloudwatch-logs';
import { Pool } from 'pg';
import { Logger } from '@medusajs/framework/logger';

/**
 * Configuração AWS para o sistema de monitoramento
 */
export interface AWSMonitoringConfig {
  // ElastiCache (Redis)
  redis: {
    url: string;
    host?: string;
    port?: number;
    password?: string;
    tls?: boolean;
  };

  // RDS PostgreSQL
  database: {
    url: string;
    host?: string;
    port?: number;
    database?: string;
    user?: string;
    password?: string;
    ssl?: boolean;
  };

  // SNS para eventos
  sns: {
    region: string;
    topicArn: string;
    credentials?: {
      accessKeyId: string;
      secretAccessKey: string;
    };
  };

  // SQS para filas (opcional)
  sqs?: {
    region: string;
    queueUrl: string;
    credentials?: {
      accessKeyId: string;
      secretAccessKey: string;
    };
  };

  // CloudWatch
  cloudwatch: {
    region: string;
    logGroupName: string;
    logStreamName?: string;
    namespace?: string;
    credentials?: {
      accessKeyId: string;
      secretAccessKey: string;
    };
  };
}

/**
 * Cliente AWS para sistema de monitoramento
 */
export class AWSMonitoringClient {
  private redisClient: RedisClientType;
  private dbPool: Pool;
  private snsClient: SNSClient;
  private sqsClient?: SQSClient;
  private cloudwatchClient: CloudWatchClient;
  private cloudwatchLogsClient: CloudWatchLogsClient;
  private logger: Logger;
  private config: AWSMonitoringConfig;

  constructor(config: AWSMonitoringConfig, logger: Logger) {
    this.config = config;
    this.logger = logger;

    // Inicializar clientes (lazy initialization)
    this.redisClient = null as any;
    this.dbPool = null as any;
    this.snsClient = null as any;
    this.cloudwatchClient = null as any;
    this.cloudwatchLogsClient = null as any;
  }

  /**
   * Conecta a todos os serviços AWS
   */
  async connect(): Promise<void> {
    try {
      // Conectar ao ElastiCache (Redis)
      await this.connectRedis();

      // Conectar ao RDS (PostgreSQL)
      await this.connectDatabase();

      // Inicializar clientes AWS SDK
      this.initializeAWSClients();

      this.logger.info('AWS Monitoring Client connected successfully');
    } catch (error) {
      this.logger.error('Failed to connect AWS Monitoring Client:', error);
      throw error;
    }
  }

  /**
   * Conecta ao ElastiCache (Redis)
   */
  private async connectRedis(): Promise<void> {
    try {
      this.redisClient = createClient({
        url: this.config.redis.url,
        socket: {
          tls: this.config.redis.tls,
          rejectUnauthorized: false // Para desenvolvimento - em prod, usar certificado válido
        }
      });

      this.redisClient.on('error', (err) => {
        this.logger.error('Redis Client Error:', err);
      });

      this.redisClient.on('connect', () => {
        this.logger.debug('Redis Client connected');
      });

      await this.redisClient.connect();

      this.logger.info('Connected to AWS ElastiCache (Redis)');
    } catch (error) {
      this.logger.error('Failed to connect to ElastiCache:', error);
      throw error;
    }
  }

  /**
   * Conecta ao RDS (PostgreSQL)
   */
  private async connectDatabase(): Promise<void> {
    try {
      this.dbPool = new Pool({
        connectionString: this.config.database.url,
        ssl: this.config.database.ssl ? { rejectUnauthorized: false } : false,
        max: 20,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 10000
      });

      // Testar conexão
      const client = await this.dbPool.connect();
      await client.query('SELECT NOW()');
      client.release();

      this.logger.info('Connected to AWS RDS (PostgreSQL)');
    } catch (error) {
      this.logger.error('Failed to connect to RDS:', error);
      throw error;
    }
  }

  /**
   * Inicializa clientes AWS SDK
   */
  private initializeAWSClients(): void {
    const awsConfig = {
      region: this.config.sns.region,
      credentials: this.config.sns.credentials
    };

    // SNS Client
    this.snsClient = new SNSClient(awsConfig);
    this.logger.info('AWS SNS Client initialized');

    // SQS Client (opcional)
    if (this.config.sqs) {
      this.sqsClient = new SQSClient({
        region: this.config.sqs.region,
        credentials: this.config.sqs.credentials
      });
      this.logger.info('AWS SQS Client initialized');
    }

    // CloudWatch Clients
    this.cloudwatchClient = new CloudWatchClient({
      region: this.config.cloudwatch.region,
      credentials: this.config.cloudwatch.credentials
    });

    this.cloudwatchLogsClient = new CloudWatchLogsClient({
      region: this.config.cloudwatch.region,
      credentials: this.config.cloudwatch.credentials
    });

    this.logger.info('AWS CloudWatch Clients initialized');
  }

  /**
   * Desconecta de todos os serviços
   */
  async disconnect(): Promise<void> {
    try {
      // Desconectar Redis
      if (this.redisClient) {
        await this.redisClient.quit();
        this.logger.info('Redis disconnected');
      }

      // Desconectar Database
      if (this.dbPool) {
        await this.dbPool.end();
        this.logger.info('Database pool closed');
      }

      // Destruir clientes AWS SDK
      if (this.snsClient) {
        this.snsClient.destroy();
      }

      if (this.sqsClient) {
        this.sqsClient.destroy();
      }

      if (this.cloudwatchClient) {
        this.cloudwatchClient.destroy();
      }

      if (this.cloudwatchLogsClient) {
        this.cloudwatchLogsClient.destroy();
      }

      this.logger.info('AWS Monitoring Client disconnected');
    } catch (error) {
      this.logger.error('Error disconnecting AWS Monitoring Client:', error);
    }
  }

  /**
   * Health check de todos os serviços
   */
  async healthCheck(): Promise<{
    redis: boolean;
    database: boolean;
    sns: boolean;
    cloudwatch: boolean;
  }> {
    const health = {
      redis: false,
      database: false,
      sns: false,
      cloudwatch: false
    };

    // Check Redis
    try {
      await this.redisClient.ping();
      health.redis = true;
    } catch (error) {
      this.logger.error('Redis health check failed:', error);
    }

    // Check Database
    try {
      const client = await this.dbPool.connect();
      await client.query('SELECT 1');
      client.release();
      health.database = true;
    } catch (error) {
      this.logger.error('Database health check failed:', error);
    }

    // Check SNS (simples - verifica se cliente está inicializado)
    health.sns = this.snsClient !== null;

    // Check CloudWatch
    health.cloudwatch = this.cloudwatchClient !== null;

    return health;
  }

  // Getters para os clientes
  getRedisClient(): RedisClientType {
    return this.redisClient;
  }

  getDatabasePool(): Pool {
    return this.dbPool;
  }

  getSNSClient(): SNSClient {
    return this.snsClient;
  }

  getSQSClient(): SQSClient | undefined {
    return this.sqsClient;
  }

  getCloudWatchClient(): CloudWatchClient {
    return this.cloudwatchClient;
  }

  getCloudWatchLogsClient(): CloudWatchLogsClient {
    return this.cloudwatchLogsClient;
  }
}

/**
 * Factory para criar configuração AWS a partir de variáveis de ambiente
 */
export function createAWSConfigFromEnv(): AWSMonitoringConfig {
  return {
    redis: {
      url: process.env.REDIS_URL || 'redis://localhost:6379',
      tls: process.env.REDIS_TLS === 'true'
    },
    database: {
      url: process.env.DATABASE_URL || 'postgresql://localhost:5432/medusa_db',
      ssl: process.env.DATABASE_SSL === 'true'
    },
    sns: {
      region: process.env.AWS_REGION || 'us-east-1',
      topicArn: process.env.AWS_SNS_TOPIC_ARN || '',
      credentials: process.env.AWS_ACCESS_KEY_ID ? {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || ''
      } : undefined
    },
    sqs: process.env.AWS_SQS_QUEUE_URL ? {
      region: process.env.AWS_REGION || 'us-east-1',
      queueUrl: process.env.AWS_SQS_QUEUE_URL,
      credentials: process.env.AWS_ACCESS_KEY_ID ? {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || ''
      } : undefined
    } : undefined,
    cloudwatch: {
      region: process.env.AWS_REGION || 'us-east-1',
      logGroupName: process.env.AWS_CLOUDWATCH_LOG_GROUP || '/ysh-b2b/distributor-monitoring',
      logStreamName: process.env.AWS_CLOUDWATCH_LOG_STREAM,
      namespace: process.env.AWS_CLOUDWATCH_NAMESPACE || 'YSH-B2B/DistributorMonitoring',
      credentials: process.env.AWS_ACCESS_KEY_ID ? {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || ''
      } : undefined
    }
  };
}
