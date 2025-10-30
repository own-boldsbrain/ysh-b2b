import { Logger } from '@medusajs/framework/logger';
import {
  CloudWatchClient,
  PutMetricDataCommand,
  MetricDatum,
  StandardUnit
} from '@aws-sdk/client-cloudwatch';
import {
  CloudWatchLogsClient,
  CreateLogStreamCommand,
  PutLogEventsCommand,
  InputLogEvent
} from '@aws-sdk/client-cloudwatch-logs';
import { DistributorStatusInfo, HealthMetrics } from './types';

/**
 * Cliente AWS CloudWatch para logs e métricas
 * 
 * Responsável por:
 * - Enviar logs estruturados para CloudWatch Logs
 * - Publicar métricas customizadas no CloudWatch Metrics
 * - Rastrear performance e disponibilidade dos distribuidores
 */
export class AWSCloudWatchLogger {
  private logger: Logger;
  private cloudwatchClient: CloudWatchClient;
  private cloudwatchLogsClient: CloudWatchLogsClient;
  private logGroupName: string;
  private logStreamName: string;
  private namespace: string;
  private logSequenceToken?: string;

  constructor(
    cloudwatchClient: CloudWatchClient,
    cloudwatchLogsClient: CloudWatchLogsClient,
    logGroupName: string,
    logStreamName: string,
    namespace: string,
    logger: Logger
  ) {
    this.cloudwatchClient = cloudwatchClient;
    this.cloudwatchLogsClient = cloudwatchLogsClient;
    this.logGroupName = logGroupName;
    this.logStreamName = logStreamName;
    this.namespace = namespace;
    this.logger = logger;
  }

  /**
   * Inicializa o log stream no CloudWatch Logs
   */
  async initialize(): Promise<void> {
    try {
      const command = new CreateLogStreamCommand({
        logGroupName: this.logGroupName,
        logStreamName: this.logStreamName
      });

      await this.cloudwatchLogsClient.send(command);
      this.logger.info(`CloudWatch log stream created: ${this.logStreamName}`);
    } catch (error: any) {
      // Ignorar erro se stream já existe
      if (error.name !== 'ResourceAlreadyExistsException') {
        this.logger.error('Failed to create CloudWatch log stream:', error);
        throw error;
      }
      this.logger.debug(`CloudWatch log stream already exists: ${this.logStreamName}`);
    }
  }

  /**
   * Envia log estruturado para CloudWatch Logs
   */
  async logEvent(
    message: string,
    level: 'INFO' | 'WARN' | 'ERROR' | 'DEBUG',
    metadata?: Record<string, any>
  ): Promise<void> {
    try {
      const logEvent: InputLogEvent = {
        message: JSON.stringify({
          timestamp: new Date().toISOString(),
          level,
          message,
          ...metadata
        }),
        timestamp: Date.now()
      };

      const command = new PutLogEventsCommand({
        logGroupName: this.logGroupName,
        logStreamName: this.logStreamName,
        logEvents: [logEvent],
        sequenceToken: this.logSequenceToken
      });

      const response = await this.cloudwatchLogsClient.send(command);
      this.logSequenceToken = response.nextSequenceToken;

      this.logger.debug(`Log event sent to CloudWatch: ${level} - ${message}`);
    } catch (error) {
      this.logger.error('Failed to send log event to CloudWatch:', error);
      // Não propagar erro - logging não deve quebrar aplicação
    }
  }

  /**
   * Publica métricas de status do distribuidor
   */
  async publishDistributorMetrics(statusInfo: DistributorStatusInfo): Promise<void> {
    try {
      const metrics: MetricDatum[] = [
        // Response Time
        {
          MetricName: 'ResponseTime',
          Value: statusInfo.metrics.responseTime,
          Unit: StandardUnit.Milliseconds,
          Timestamp: new Date(),
          Dimensions: [
            {
              Name: 'DistributorId',
              Value: statusInfo.distributorId
            },
            {
              Name: 'DistributorName',
              Value: statusInfo.distributorName
            }
          ]
        },
        // Success Rate
        {
          MetricName: 'SuccessRate',
          Value: statusInfo.metrics.successRate,
          Unit: StandardUnit.Percent,
          Timestamp: new Date(),
          Dimensions: [
            {
              Name: 'DistributorId',
              Value: statusInfo.distributorId
            },
            {
              Name: 'DistributorName',
              Value: statusInfo.distributorName
            }
          ]
        },
        // Error Rate
        {
          MetricName: 'ErrorRate',
          Value: statusInfo.metrics.errorRate,
          Unit: StandardUnit.Percent,
          Timestamp: new Date(),
          Dimensions: [
            {
              Name: 'DistributorId',
              Value: statusInfo.distributorId
            },
            {
              Name: 'DistributorName',
              Value: statusInfo.distributorName
            }
          ]
        },
        // Availability
        {
          MetricName: 'Availability',
          Value: statusInfo.metrics.availability,
          Unit: StandardUnit.Percent,
          Timestamp: new Date(),
          Dimensions: [
            {
              Name: 'DistributorId',
              Value: statusInfo.distributorId
            },
            {
              Name: 'DistributorName',
              Value: statusInfo.distributorName
            }
          ]
        },
        // Consecutive Failures
        {
          MetricName: 'ConsecutiveFailures',
          Value: statusInfo.metrics.consecutiveFailures,
          Unit: StandardUnit.Count,
          Timestamp: new Date(),
          Dimensions: [
            {
              Name: 'DistributorId',
              Value: statusInfo.distributorId
            },
            {
              Name: 'DistributorName',
              Value: statusInfo.distributorName
            }
          ]
        },
        // Status (1 = ONLINE, 0 = OFFLINE)
        {
          MetricName: 'Status',
          Value: statusInfo.status === 'ONLINE' ? 1 : 0,
          Unit: StandardUnit.None,
          Timestamp: new Date(),
          Dimensions: [
            {
              Name: 'DistributorId',
              Value: statusInfo.distributorId
            },
            {
              Name: 'DistributorName',
              Value: statusInfo.distributorName
            },
            {
              Name: 'Status',
              Value: statusInfo.status
            }
          ]
        },
        // State (1 = DISPONÍVEL, 0.5 = DEGRADADO, 0 = INDISPONÍVEL)
        {
          MetricName: 'State',
          Value: this.getStateValue(statusInfo.state),
          Unit: StandardUnit.None,
          Timestamp: new Date(),
          Dimensions: [
            {
              Name: 'DistributorId',
              Value: statusInfo.distributorId
            },
            {
              Name: 'DistributorName',
              Value: statusInfo.distributorName
            },
            {
              Name: 'State',
              Value: statusInfo.state
            }
          ]
        }
      ];

      const command = new PutMetricDataCommand({
        Namespace: this.namespace,
        MetricData: metrics
      });

      await this.cloudwatchClient.send(command);

      this.logger.debug(
        `Metrics published to CloudWatch for distributor ${statusInfo.distributorId}`
      );
    } catch (error) {
      this.logger.error(
        `Failed to publish metrics for ${statusInfo.distributorId}:`,
        error
      );
      // Não propagar erro - métricas não devem quebrar aplicação
    }
  }

  /**
   * Publica métricas agregadas de múltiplos distribuidores
   */
  async publishAggregatedMetrics(
    distributors: DistributorStatusInfo[]
  ): Promise<void> {
    if (distributors.length === 0) return;

    try {
      // Calcular métricas agregadas
      const totalDistributors = distributors.length;
      const onlineDistributors = distributors.filter(d => d.status === 'ONLINE').length;
      const availableDistributors = distributors.filter(d => d.state === 'DISPONÍVEL').length;
      const degradedDistributors = distributors.filter(d => d.state === 'DEGRADADO').length;
      const unavailableDistributors = distributors.filter(d => d.state === 'INDISPONÍVEL').length;

      const avgResponseTime = distributors.reduce((sum, d) => sum + d.metrics.responseTime, 0) / totalDistributors;
      const avgSuccessRate = distributors.reduce((sum, d) => sum + d.metrics.successRate, 0) / totalDistributors;
      const avgAvailability = distributors.reduce((sum, d) => sum + d.metrics.availability, 0) / totalDistributors;

      const metrics: MetricDatum[] = [
        {
          MetricName: 'TotalDistributors',
          Value: totalDistributors,
          Unit: StandardUnit.Count,
          Timestamp: new Date()
        },
        {
          MetricName: 'OnlineDistributors',
          Value: onlineDistributors,
          Unit: StandardUnit.Count,
          Timestamp: new Date()
        },
        {
          MetricName: 'AvailableDistributors',
          Value: availableDistributors,
          Unit: StandardUnit.Count,
          Timestamp: new Date()
        },
        {
          MetricName: 'DegradedDistributors',
          Value: degradedDistributors,
          Unit: StandardUnit.Count,
          Timestamp: new Date()
        },
        {
          MetricName: 'UnavailableDistributors',
          Value: unavailableDistributors,
          Unit: StandardUnit.Count,
          Timestamp: new Date()
        },
        {
          MetricName: 'OverallHealth',
          Value: (onlineDistributors / totalDistributors) * 100,
          Unit: StandardUnit.Percent,
          Timestamp: new Date()
        },
        {
          MetricName: 'AverageResponseTime',
          Value: avgResponseTime,
          Unit: StandardUnit.Milliseconds,
          Timestamp: new Date()
        },
        {
          MetricName: 'AverageSuccessRate',
          Value: avgSuccessRate,
          Unit: StandardUnit.Percent,
          Timestamp: new Date()
        },
        {
          MetricName: 'AverageAvailability',
          Value: avgAvailability,
          Unit: StandardUnit.Percent,
          Timestamp: new Date()
        }
      ];

      const command = new PutMetricDataCommand({
        Namespace: this.namespace,
        MetricData: metrics
      });

      await this.cloudwatchClient.send(command);

      this.logger.debug('Aggregated metrics published to CloudWatch');
    } catch (error) {
      this.logger.error('Failed to publish aggregated metrics:', error);
    }
  }

  /**
   * Publica métrica customizada
   */
  async publishCustomMetric(
    metricName: string,
    value: number,
    unit: StandardUnit,
    dimensions?: Record<string, string>
  ): Promise<void> {
    try {
      const metricDimensions = dimensions
        ? Object.entries(dimensions).map(([key, value]) => ({
            Name: key,
            Value: value
          }))
        : undefined;

      const command = new PutMetricDataCommand({
        Namespace: this.namespace,
        MetricData: [
          {
            MetricName: metricName,
            Value: value,
            Unit: unit,
            Timestamp: new Date(),
            Dimensions: metricDimensions
          }
        ]
      });

      await this.cloudwatchClient.send(command);

      this.logger.debug(`Custom metric published: ${metricName} = ${value}`);
    } catch (error) {
      this.logger.error(`Failed to publish custom metric ${metricName}:`, error);
    }
  }

  /**
   * Converte estado para valor numérico para métricas
   */
  private getStateValue(state: string): number {
    switch (state) {
      case 'DISPONÍVEL':
        return 1;
      case 'DEGRADADO':
        return 0.5;
      case 'INDISPONÍVEL':
        return 0;
      case 'MANUTENÇÃO':
        return -1;
      case 'LIMITADO':
        return 0.3;
      default:
        return 0;
    }
  }

  /**
   * Health check do CloudWatch
   */
  async healthCheck(): Promise<boolean> {
    try {
      return this.cloudwatchClient !== null && this.cloudwatchLogsClient !== null;
    } catch (error) {
      this.logger.error('CloudWatch health check failed:', error);
      return false;
    }
  }
}
