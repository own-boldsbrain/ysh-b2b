import { Logger } from '@medusajs/framework/logger';
import { StatusChangeEvent, AlertSeverity } from './types';

/**
 * Publicador de eventos de mudança de status
 * 
 * Responsável por:
 * - Publicar eventos no Azure Service Bus
 * - Notificar mudanças críticas
 * - Gerenciar tópicos e filas
 */
export class StatusEventPublisher {
  private logger: Logger;
  private serviceBusClient: any; // TODO: Type with actual Service Bus client
  private topicName: string;

  constructor(
    serviceBusClient: any,
    topicName: string,
    logger: Logger
  ) {
    this.serviceBusClient = serviceBusClient;
    this.topicName = topicName;
    this.logger = logger;
  }

  /**
   * Publica evento de mudança de status
   */
  async publishStatusChange(event: StatusChangeEvent): Promise<void> {
    try {
      const sender = this.serviceBusClient.createSender(this.topicName);

      const message = {
        body: event,
        contentType: 'application/json',
        label: 'distributor.status.changed',
        messageId: `${event.distributorId}-${event.timestamp.getTime()}`,
        userProperties: {
          distributorId: event.distributorId,
          distributorName: event.distributorName,
          severity: event.severity,
          previousStatus: event.previousStatus,
          currentStatus: event.currentStatus,
          previousState: event.previousState,
          currentState: event.currentState
        }
      };

      await sender.sendMessages(message);
      await sender.close();

      this.logger.info(
        `Status change event published for distributor ${event.distributorId}: ` +
        `${event.previousStatus}→${event.currentStatus} (${event.severity})`
      );
    } catch (error) {
      this.logger.error(
        `Failed to publish status change event for ${event.distributorId}:`,
        error
      );
      throw error;
    }
  }

  /**
   * Publica múltiplos eventos em batch
   */
  async publishBatch(events: StatusChangeEvent[]): Promise<void> {
    if (events.length === 0) return;

    try {
      const sender = this.serviceBusClient.createSender(this.topicName);

      const messages = events.map(event => ({
        body: event,
        contentType: 'application/json',
        label: 'distributor.status.changed',
        messageId: `${event.distributorId}-${event.timestamp.getTime()}`,
        userProperties: {
          distributorId: event.distributorId,
          distributorName: event.distributorName,
          severity: event.severity,
          previousStatus: event.previousStatus,
          currentStatus: event.currentStatus
        }
      }));

      await sender.sendMessages(messages);
      await sender.close();

      this.logger.info(`Published ${events.length} status change events in batch`);
    } catch (error) {
      this.logger.error('Failed to publish batch of status change events:', error);
      throw error;
    }
  }

  /**
   * Publica alerta crítico (prioridade alta)
   */
  async publishCriticalAlert(event: StatusChangeEvent): Promise<void> {
    try {
      const sender = this.serviceBusClient.createSender(this.topicName);

      const message = {
        body: event,
        contentType: 'application/json',
        label: 'distributor.status.critical',
        messageId: `critical-${event.distributorId}-${event.timestamp.getTime()}`,
        userProperties: {
          distributorId: event.distributorId,
          distributorName: event.distributorName,
          severity: AlertSeverity.CRITICAL,
          priority: 'HIGH',
          requiresImmedateAction: true,
          previousStatus: event.previousStatus,
          currentStatus: event.currentStatus
        },
        timeToLive: 3600000 // 1 hora
      };

      await sender.sendMessages(message);
      await sender.close();

      this.logger.warn(
        `🚨 CRITICAL ALERT published for distributor ${event.distributorId}: ` +
        `${event.currentStatus} - ${event.reason || 'No reason provided'}`
      );
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
      const sender = this.serviceBusClient.createSender(this.topicName);

      const message = {
        body: event,
        contentType: 'application/json',
        label: 'distributor.status.recovered',
        messageId: `recovery-${event.distributorId}-${event.timestamp.getTime()}`,
        userProperties: {
          distributorId: event.distributorId,
          distributorName: event.distributorName,
          severity: AlertSeverity.INFO,
          eventType: 'RECOVERY',
          previousStatus: event.previousStatus,
          currentStatus: event.currentStatus
        }
      };

      await sender.sendMessages(message);
      await sender.close();

      this.logger.info(
        `✅ Recovery event published for distributor ${event.distributorId}: ` +
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
      const sender = this.serviceBusClient.createSender(this.topicName);

      const message = {
        body: event,
        contentType: 'application/json',
        label: 'distributor.status.degraded',
        messageId: `degraded-${event.distributorId}-${event.timestamp.getTime()}`,
        userProperties: {
          distributorId: event.distributorId,
          distributorName: event.distributorName,
          severity: event.severity,
          eventType: 'DEGRADATION',
          successRate: event.metrics.successRate,
          responseTime: event.metrics.responseTime,
          previousState: event.previousState,
          currentState: event.currentState
        }
      };

      await sender.sendMessages(message);
      await sender.close();

      this.logger.warn(
        `⚠️  Degradation event published for distributor ${event.distributorId}: ` +
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
   * Verifica se Service Bus está saudável
   */
  async healthCheck(): Promise<boolean> {
    try {
      // Tentar criar sender como teste de conectividade
      const sender = this.serviceBusClient.createSender(this.topicName);
      await sender.close();
      return true;
    } catch (error) {
      this.logger.error('Service Bus health check failed:', error);
      return false;
    }
  }

  /**
   * Fecha conexões
   */
  async close(): Promise<void> {
    try {
      await this.serviceBusClient.close();
      this.logger.info('Service Bus client closed');
    } catch (error) {
      this.logger.error('Error closing Service Bus client:', error);
    }
  }
}
