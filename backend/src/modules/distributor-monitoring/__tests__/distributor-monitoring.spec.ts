import { 
  DistributorStatusMonitor 
} from '../status-monitor';
import { 
  DistributorStateManager 
} from '../state-manager';
import { 
  StatusEventPublisher 
} from '../event-publisher';
import {
  DistributorStatus,
  DistributorState,
  AlertSeverity,
  MonitoringConfig
} from '../types';

describe('Distributor Monitoring System', () => {
  let monitor: DistributorStatusMonitor;
  let stateManager: DistributorStateManager;
  let eventPublisher: StatusEventPublisher;
  let mockRedis: any;
  let mockDb: any;
  let mockServiceBus: any;
  let mockLogger: any;

  beforeEach(() => {
    // Mock Redis
    mockRedis = {
      setex: jest.fn().mockResolvedValue('OK'),
      get: jest.fn().mockResolvedValue(null),
      del: jest.fn().mockResolvedValue(1),
      keys: jest.fn().mockResolvedValue([])
    };

    // Mock Database
    mockDb = {
      query: jest.fn().mockResolvedValue({ rows: [] })
    };

    // Mock Service Bus
    mockServiceBus = {
      createSender: jest.fn().mockReturnValue({
        sendMessages: jest.fn().mockResolvedValue(undefined),
        close: jest.fn().mockResolvedValue(undefined)
      }),
      close: jest.fn().mockResolvedValue(undefined)
    };

    // Mock Logger
    mockLogger = {
      info: jest.fn(),
      debug: jest.fn(),
      warn: jest.fn(),
      error: jest.fn()
    };

    // Criar instâncias
    stateManager = new DistributorStateManager(mockRedis, mockDb, mockLogger);
    eventPublisher = new StatusEventPublisher(mockServiceBus, 'status-events', mockLogger);
    monitor = new DistributorStatusMonitor(stateManager, eventPublisher, mockLogger);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('DistributorStateManager', () => {
    describe('updateState', () => {
      it('deve atualizar estado no Redis com TTL', async () => {
        const statusInfo = {
          distributorId: 'dist-1',
          distributorName: 'Test Distributor',
          status: DistributorStatus.ONLINE,
          state: DistributorState.DISPONIVEL,
          metrics: {
            responseTime: 150,
            successRate: 98,
            errorRate: 2,
            availability: 99.5,
            requestsPerMinute: 10,
            consecutiveFailures: 0
          },
          lastCheck: new Date('2025-10-21T10:00:00Z'),
          nextCheck: new Date('2025-10-21T10:01:00Z')
        };

        await stateManager.updateState(statusInfo);

        expect(mockRedis.setex).toHaveBeenCalledWith(
          'distributor:status:dist-1',
          300,
          expect.stringContaining('"distributorId":"dist-1"')
        );
      });

      it('deve serializar datas corretamente', async () => {
        const statusInfo = {
          distributorId: 'dist-1',
          distributorName: 'Test Distributor',
          status: DistributorStatus.ONLINE,
          state: DistributorState.DISPONIVEL,
          metrics: {
            responseTime: 150,
            successRate: 98,
            errorRate: 2,
            availability: 99.5,
            requestsPerMinute: 10,
            consecutiveFailures: 0,
            lastSuccessfulRequest: new Date('2025-10-21T09:59:00Z')
          },
          lastCheck: new Date('2025-10-21T10:00:00Z'),
          nextCheck: new Date('2025-10-21T10:01:00Z')
        };

        await stateManager.updateState(statusInfo);

        const serializedCall = mockRedis.setex.mock.calls[0][2];
        const parsed = JSON.parse(serializedCall);

        expect(parsed.lastCheck).toBe('2025-10-21T10:00:00.000Z');
        expect(parsed.nextCheck).toBe('2025-10-21T10:01:00.000Z');
        expect(parsed.metrics.lastSuccessfulRequest).toBe('2025-10-21T09:59:00.000Z');
      });
    });

    describe('getState', () => {
      it('deve recuperar estado do Redis', async () => {
        const cachedData = {
          distributorId: 'dist-1',
          distributorName: 'Test Distributor',
          status: 'ONLINE',
          state: 'DISPONÍVEL',
          metrics: {
            responseTime: 150,
            successRate: 98,
            errorRate: 2,
            availability: 99.5,
            requestsPerMinute: 10,
            consecutiveFailures: 0
          },
          lastCheck: '2025-10-21T10:00:00.000Z',
          nextCheck: '2025-10-21T10:01:00.000Z'
        };

        mockRedis.get.mockResolvedValue(JSON.stringify(cachedData));

        const result = await stateManager.getState('dist-1');

        expect(result).toBeDefined();
        expect(result?.distributorId).toBe('dist-1');
        expect(result?.lastCheck).toBeInstanceOf(Date);
        expect(result?.nextCheck).toBeInstanceOf(Date);
      });

      it('deve retornar null se não houver cache', async () => {
        mockRedis.get.mockResolvedValue(null);

        const result = await stateManager.getState('dist-1');

        expect(result).toBeNull();
      });
    });

    describe('getAllStates', () => {
      it('deve recuperar todos os estados do Redis', async () => {
        mockRedis.keys.mockResolvedValue([
          'distributor:status:dist-1',
          'distributor:status:dist-2'
        ]);

        const state1 = {
          distributorId: 'dist-1',
          status: 'ONLINE',
          state: 'DISPONÍVEL',
          lastCheck: '2025-10-21T10:00:00.000Z',
          nextCheck: '2025-10-21T10:01:00.000Z',
          metrics: { responseTime: 100, successRate: 99, errorRate: 1, availability: 99, requestsPerMinute: 5, consecutiveFailures: 0 }
        };

        const state2 = {
          distributorId: 'dist-2',
          status: 'OFFLINE',
          state: 'INDISPONÍVEL',
          lastCheck: '2025-10-21T10:00:00.000Z',
          nextCheck: '2025-10-21T10:01:00.000Z',
          metrics: { responseTime: 0, successRate: 0, errorRate: 100, availability: 50, requestsPerMinute: 0, consecutiveFailures: 5 }
        };

        mockRedis.get
          .mockResolvedValueOnce(JSON.stringify(state1))
          .mockResolvedValueOnce(JSON.stringify(state2));

        const results = await stateManager.getAllStates();

        expect(results).toHaveLength(2);
        expect(results[0].distributorId).toBe('dist-1');
        expect(results[1].distributorId).toBe('dist-2');
      });
    });

    describe('persistHistoryEntry', () => {
      it('deve persistir entrada no histórico', async () => {
        const entry = {
          timestamp: new Date('2025-10-21T10:00:00Z'),
          status: DistributorStatus.ONLINE,
          state: DistributorState.DISPONIVEL,
          metrics: {
            responseTime: 150,
            successRate: 98,
            errorRate: 2,
            availability: 99.5,
            requestsPerMinute: 10,
            consecutiveFailures: 0
          }
        };

        await stateManager.persistHistoryEntry('dist-1', entry);

        expect(mockDb.query).toHaveBeenCalledWith(
          expect.stringContaining('INSERT INTO distributor_status_history'),
          expect.arrayContaining(['dist-1'])
        );
      });
    });

    describe('calculateAggregatedMetrics', () => {
      it('deve calcular métricas agregadas do histórico', async () => {
        mockDb.query.mockResolvedValue({
          rows: [{
            avg_response_time: '250.5',
            avg_success_rate: '95.2',
            total_checks: '100',
            online_checks: '92'
          }]
        });

        const result = await stateManager.calculateAggregatedMetrics(
          'dist-1',
          new Date('2025-10-20T00:00:00Z'),
          new Date('2025-10-21T00:00:00Z')
        );

        expect(result.averageResponseTime).toBe(250.5);
        expect(result.averageSuccessRate).toBe(95.2);
        expect(result.uptimePercentage).toBe(92);
        expect(result.totalChecks).toBe(100);
      });
    });
  });

  describe('StatusEventPublisher', () => {
    describe('publishStatusChange', () => {
      it('deve publicar evento de mudança de status', async () => {
        const event = {
          distributorId: 'dist-1',
          distributorName: 'Test Distributor',
          previousStatus: DistributorStatus.ONLINE,
          currentStatus: DistributorStatus.OFFLINE,
          previousState: DistributorState.DISPONIVEL,
          currentState: DistributorState.INDISPONIVEL,
          timestamp: new Date('2025-10-21T10:00:00Z'),
          reason: 'Connection timeout',
          metrics: {
            responseTime: 0,
            successRate: 0,
            errorRate: 100,
            availability: 50,
            requestsPerMinute: 0,
            consecutiveFailures: 5
          },
          severity: AlertSeverity.CRITICAL
        };

        await eventPublisher.publishStatusChange(event);

        const sender = mockServiceBus.createSender();
        expect(sender.sendMessages).toHaveBeenCalledWith(
          expect.objectContaining({
            body: event,
            label: 'distributor.status.changed',
            userProperties: expect.objectContaining({
              distributorId: 'dist-1',
              severity: AlertSeverity.CRITICAL
            })
          })
        );
      });
    });

    describe('publishCriticalAlert', () => {
      it('deve publicar alerta crítico com prioridade alta', async () => {
        const event = {
          distributorId: 'dist-1',
          distributorName: 'Test Distributor',
          previousStatus: DistributorStatus.ONLINE,
          currentStatus: DistributorStatus.OFFLINE,
          previousState: DistributorState.DISPONIVEL,
          currentState: DistributorState.INDISPONIVEL,
          timestamp: new Date(),
          reason: 'Complete system failure',
          metrics: {
            responseTime: 0,
            successRate: 0,
            errorRate: 100,
            availability: 0,
            requestsPerMinute: 0,
            consecutiveFailures: 10
          },
          severity: AlertSeverity.CRITICAL
        };

        await eventPublisher.publishCriticalAlert(event);

        const sender = mockServiceBus.createSender();
        expect(sender.sendMessages).toHaveBeenCalledWith(
          expect.objectContaining({
            label: 'distributor.status.critical',
            userProperties: expect.objectContaining({
              priority: 'HIGH',
              requiresImmedateAction: true
            })
          })
        );
      });
    });

    describe('publishRecoveryEvent', () => {
      it('deve publicar evento de recuperação', async () => {
        const event = {
          distributorId: 'dist-1',
          distributorName: 'Test Distributor',
          previousStatus: DistributorStatus.OFFLINE,
          currentStatus: DistributorStatus.ONLINE,
          previousState: DistributorState.INDISPONIVEL,
          currentState: DistributorState.DISPONIVEL,
          timestamp: new Date(),
          metrics: {
            responseTime: 150,
            successRate: 100,
            errorRate: 0,
            availability: 99,
            requestsPerMinute: 10,
            consecutiveFailures: 0
          },
          severity: AlertSeverity.INFO
        };

        await eventPublisher.publishRecoveryEvent(event);

        const sender = mockServiceBus.createSender();
        expect(sender.sendMessages).toHaveBeenCalledWith(
          expect.objectContaining({
            label: 'distributor.status.recovered',
            userProperties: expect.objectContaining({
              eventType: 'RECOVERY'
            })
          })
        );
      });
    });

    describe('publishBatch', () => {
      it('deve publicar múltiplos eventos em batch', async () => {
        const events = [
          {
            distributorId: 'dist-1',
            distributorName: 'Distributor 1',
            previousStatus: DistributorStatus.ONLINE,
            currentStatus: DistributorStatus.OFFLINE,
            previousState: DistributorState.DISPONIVEL,
            currentState: DistributorState.INDISPONIVEL,
            timestamp: new Date(),
            metrics: {} as any,
            severity: AlertSeverity.CRITICAL
          },
          {
            distributorId: 'dist-2',
            distributorName: 'Distributor 2',
            previousStatus: DistributorStatus.ONLINE,
            currentStatus: DistributorStatus.ONLINE,
            previousState: DistributorState.DISPONIVEL,
            currentState: DistributorState.DEGRADADO,
            timestamp: new Date(),
            metrics: {} as any,
            severity: AlertSeverity.WARNING
          }
        ];

        await eventPublisher.publishBatch(events);

        const sender = mockServiceBus.createSender();
        expect(sender.sendMessages).toHaveBeenCalledWith(
          expect.arrayContaining([
            expect.objectContaining({ body: events[0] }),
            expect.objectContaining({ body: events[1] })
          ])
        );
      });
    });
  });

  describe('Integration Tests', () => {
    it('deve executar fluxo completo de monitoramento', async () => {
      // 1. Salvar estado inicial
      const initialState = {
        distributorId: 'dist-1',
        distributorName: 'Test Distributor',
        status: DistributorStatus.ONLINE,
        state: DistributorState.DISPONIVEL,
        metrics: {
          responseTime: 150,
          successRate: 98,
          errorRate: 2,
          availability: 99.5,
          requestsPerMinute: 10,
          consecutiveFailures: 0
        },
        lastCheck: new Date(),
        nextCheck: new Date(Date.now() + 60000)
      };

      await stateManager.updateState(initialState);

      // 2. Recuperar estado
      mockRedis.get.mockResolvedValue(JSON.stringify({
        ...initialState,
        lastCheck: initialState.lastCheck.toISOString(),
        nextCheck: initialState.nextCheck.toISOString()
      }));

      const retrieved = await stateManager.getState('dist-1');
      expect(retrieved).toBeDefined();
      expect(retrieved?.status).toBe(DistributorStatus.ONLINE);

      // 3. Simular mudança para OFFLINE
      const updatedState = {
        ...initialState,
        status: DistributorStatus.OFFLINE,
        state: DistributorState.INDISPONIVEL,
        metrics: {
          ...initialState.metrics,
          successRate: 0,
          errorRate: 100,
          consecutiveFailures: 5
        }
      };

      await stateManager.updateState(updatedState);

      // 4. Publicar evento de mudança crítica
      const event = {
        distributorId: 'dist-1',
        distributorName: 'Test Distributor',
        previousStatus: DistributorStatus.ONLINE,
        currentStatus: DistributorStatus.OFFLINE,
        previousState: DistributorState.DISPONIVEL,
        currentState: DistributorState.INDISPONIVEL,
        timestamp: new Date(),
        reason: 'Health check failed',
        metrics: updatedState.metrics,
        severity: AlertSeverity.CRITICAL
      };

      await eventPublisher.publishCriticalAlert(event);

      // 5. Persistir no histórico
      await stateManager.persistHistoryEntry('dist-1', {
        timestamp: new Date(),
        status: updatedState.status,
        state: updatedState.state,
        metrics: updatedState.metrics,
        event
      });

      // Verificações
      expect(mockRedis.setex).toHaveBeenCalledTimes(2); // Initial + updated
      expect(mockServiceBus.createSender).toHaveBeenCalled();
      expect(mockDb.query).toHaveBeenCalled();
    });
  });
});
