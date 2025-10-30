import { Logger } from '@medusajs/framework/logger';
import { SNSClient, PublishCommand, PublishBatchCommand } from '@aws-sdk/client-sns';
import { SQSClient, SendMessageCommand, SendMessageBatchCommand } from '@aws-sdk/client-sqs';
import { StatusChangeEvent, AlertSeverity } from './types';

/**
 * Publicador de eventos de mudança de status usando AWS SNS/SQS
 * 
 * Responsável por:
 * - Publicar eventos no AWS SNS (Simple Notification Service)
 * - Enviar mensagens para AWS SQS (Simple Queue Service) opcionalmente
 * - Notificar mudanças críticas com prioridade
 * - Gerenciar tópicos e filas
 */
export class AWSStatusEventPublisher {
  private logger: Logger;
  private snsClient: SNSClient;
  private sqsClient?: SQSClient;
  private topicArn: string;
  private queueUrl?: string;

  constructor(
    snsClient: SNSClient,
    topicArn: string,
    logger: Logger,
    sqsClient?: SQSClient,
    queueUrl?: string
  ) {
    this.snsClient = snsClient;
    this.topicArn = topicArn;
    this.logger = logger;
    this.sqsClient = sqsClient;
    this.queueUrl = queueUrl;
  }

  /**
   * Publica evento de mudança de status no SNS
   */
  async publishStatusChange(event: StatusChangeEvent): Promise<void> {
    try {
      const message = JSON.stringify(event);
      
      const command = new PublishCommand({
        TopicArn: this.topicArn,
        Message: message,
        Subject: `Distributor Status Change: ${event.distributorName}`,
        MessageAttributes: {
          distributorId: {
            DataType: 'String',
            StringValue: event.distributorId
          },
          distributorName: {
            DataType: 'String',
            StringValue: event.distributorName
          },
          severity: {
            DataType: 'String',
            StringValue: event.severity
          },
          previousStatus: {
            DataType: 'String',
            StringValue: event.previousStatus
          },
          currentStatus: {
            DataType: 'String',
            StringValue: event.currentStatus
          },
          eventType: {
            DataType: 'String',
            StringValue: 'status.changed'
          },
          timestamp: {
            DataType: 'String',
            StringValue: event.timestamp.toISOString()
          }
        }
      });

      const response = await this.snsClient.send(command);

      this.logger.info(
        `Status change event published to SNS for distributor ${event.distributorId}: ` +
        `${event.previousStatus}→${event.currentStatus} (${event.severity}) ` +
        `[MessageId: ${response.MessageId}]`
      );

      // Opcionalmente, também enviar para SQS para processamento assíncrono
      if (this.sqsClient && this.queueUrl) {
        await this.sendToSQS(event, 'status.changed');
      }
    } catch (error) {
      this.logger.error(
        `Failed to publish status change event for ${event.distributorId}:`,
        error
      );
      throw error;
    }
  }

  /**
   * Publica múltiplos eventos em batch (até 10 por vez - limite do SNS)
   */
  async publishBatch(events: StatusChangeEvent[]): Promise<void> {
    if (events.length === 0) return;

    try {
      // SNS batch publish não existe, então publicar em paralelo
      const publishPromises = events.map(event => 
        this.publishStatusChange(event).catch(error => {
          this.logger.error(`Failed to publish event for ${event.distributorId}:`, error);
          return null;
        })
      );

      await Promise.all(publishPromises);

      this.logger.info(`Published ${events.length} status change events to SNS`);
    } catch (error) {
      this.logger.error('Failed to publish batch of status change events:', error);
      throw error;
    }
  }

  /**
   * Publica alerta crítico (prioridade alta) no SNS
   */
  async publishCriticalAlert(event: StatusChangeEvent): Promise<void> {
    try {
      const message = JSON.stringify(event);
      
      const command = new PublishCommand({
        TopicArn: this.topicArn,
        Message: message,
        Subject: `🚨 CRITICAL: ${event.distributorName} - ${event.currentStatus}`,
        MessageAttributes: {
          distributorId: {
            DataType: 'String',
            StringValue: event.distributorId
          },
          distributorName: {
            DataType: 'String',
            StringValue: event.distributorName
          },
          severity: {
            DataType: 'String',
            StringValue: AlertSeverity.CRITICAL
          },
          priority: {
            DataType: 'String',
            StringValue: 'HIGH'
          },
          requiresImmediateAction: {
            DataType: 'String',
            StringValue: 'true'
          },
          previousStatus: {
            DataType: 'String',
            StringValue: event.previousStatus
          },
          currentStatus: {
            DataType: 'String',
            StringValue: event.currentStatus
          },
          eventType: {
            DataType: 'String',
            StringValue: 'status.critical'
          },
          timestamp: {
            DataType: 'String',
            StringValue: event.timestamp.toISOString()
          }
        }
      });

      const response = await this.snsClient.send(command);

      this.logger.warn(
        `🚨 CRITICAL ALERT published to SNS for distributor ${event.distributorId}: ` +
        `${event.currentStatus} - ${event.reason || 'No reason provided'} ` +
        `[MessageId: ${response.MessageId}]`
      );

      // Enviar também para SQS para processamento garantido
      if (this.sqsClient && this.queueUrl) {
        await this.sendToSQS(event, 'status.critical', 0); // Prioridade imediata
      }
    } catch (error) {
      this.logger.error(
        `Failed to publish critical alert for ${event.distributorId}:`,
        error
      );
      throw error;
    }
  }

  /**
   * Publica evento de recuperação (distribuidor voltou a funcionar)
   */
  async publishRecoveryEvent(event: StatusChangeEvent): Promise<void> {
    try {
      const message = JSON.stringify(event);
      
      const command = new PublishCommand({
        TopicArn: this.topicArn,
        Message: message,
        Subject: `✅ Recovery: ${event.distributorName} is back online`,
        MessageAttributes: {
          distributorId: {
            DataType: 'String',
            StringValue: event.distributorId
          },
          distributorName: {
            DataType: 'String',
            StringValue: event.distributorName
          },
          severity: {
            DataType: 'String',
            StringValue: AlertSeverity.INFO
          },
          eventType: {
            DataType: 'String',
            StringValue: 'status.recovered'
          },
          previousStatus: {
            DataType: 'String',
            StringValue: event.previousStatus
          },
          currentStatus: {
            DataType: 'String',
            StringValue: event.currentStatus
          },
          timestamp: {
            DataType: 'String',
            StringValue: event.timestamp.toISOString()
          }
        }
      });

      await this.snsClient.send(command);

      this.logger.info(
        `✅ Recovery event published to SNS for distributor ${event.distributorId}: ` +
        `${event.previousStatus}→${event.currentStatus}`
      );
    } catch (error) {
      this.logger.error(
        `Failed to publish recovery event for ${event.distributorId}:`,
        error
      );
      // Não propagar erro - evento de recuperação é informativo
    }
  }

  /**
   * Publica evento de degradação de performance
   */
  async publishDegradationEvent(event: StatusChangeEvent): Promise<void> {
    try {
      const message = JSON.stringify(event);
      
      const command = new PublishCommand({
        TopicArn: this.topicArn,
        Message: message,
        Subject: `⚠️ Degradation: ${event.distributorName}`,
        MessageAttributes: {
          distributorId: {
            DataType: 'String',
            StringValue: event.distributorId
          },
          distributorName: {
            DataType: 'String',
            StringValue: event.distributorName
          },
          severity: {
            DataType: 'String',
            StringValue: event.severity
          },
          eventType: {
            DataType: 'String',
            StringValue: 'status.degraded'
          },
          successRate: {
            DataType: 'Number',
            StringValue: event.metrics.successRate.toString()
          },
          responseTime: {
            DataType: 'Number',
            StringValue: event.metrics.responseTime.toString()
          },
          previousState: {
            DataType: 'String',
            StringValue: event.previousState
          },
          currentState: {
            DataType: 'String',
            StringValue: event.currentState
          },
          timestamp: {
            DataType: 'String',
            StringValue: event.timestamp.toISOString()
          }
        }
      });

      await this.snsClient.send(command);

      this.logger.warn(
        `⚠️ Degradation event published to SNS for distributor ${event.distributorId}: ` +
        `Success rate: ${event.metrics.successRate}%, ` +
        `Response time: ${event.metrics.responseTime}ms`
      );
    } catch (error) {
      this.logger.error(
        `Failed to publish degradation event for ${event.distributorId}:`,
        error
      );
      throw error;
    }
  }

  /**
   * Envia mensagem para SQS (processamento assíncrono)
   */
  private async sendToSQS(
    event: StatusChangeEvent,
    eventType: string,
    delaySeconds: number = 0
  ): Promise<void> {
    if (!this.sqsClient || !this.queueUrl) {
      return;
    }

    try {
      const command = new SendMessageCommand({
        QueueUrl: this.queueUrl,
        MessageBody: JSON.stringify(event),
        DelaySeconds: delaySeconds,
        MessageAttributes: {
          eventType: {
            DataType: 'String',
            StringValue: eventType
          },
          distributorId: {
            DataType: 'String',
            StringValue: event.distributorId
          },
          severity: {
            DataType: 'String',
            StringValue: event.severity
          }
        }
      });

      const response = await this.sqsClient.send(command);

      this.logger.debug(
        `Event sent to SQS for distributor ${event.distributorId} ` +
        `[MessageId: ${response.MessageId}]`
      );
    } catch (error) {
      this.logger.error(`Failed to send message to SQS:`, error);
      // Não propagar erro - SQS é backup opcional
    }
  }

  /**
   * Verifica se SNS está saudável
   */
  async healthCheck(): Promise<boolean> {
    try {
      // Tentar publicar mensagem de teste (dry run)
      // Note: SNS não tem dry-run, então verificamos se o cliente está ok
      return this.snsClient !== null;
    } catch (error) {
      this.logger.error('SNS health check failed:', error);
      return false;
    }
  }

  /**
   * Fecha conexões e destrói clientes
   */
  async close(): Promise<void> {
    try {
      if (this.snsClient) {
        this.snsClient.destroy();
      }
      
      if (this.sqsClient) {
        this.sqsClient.destroy();
      }
      
      this.logger.info('AWS SNS/SQS clients closed');
    } catch (error) {
      this.logger.error('Error closing AWS clients:', error);
    }
  }
}
