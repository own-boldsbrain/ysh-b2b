/**
 * Shared Event System
 * 
 * Sistema de eventos de domínio com suporte a versionamento,
 * metadados e integração com Medusa EventBus.
 */

// Type for Medusa EventBus (will be injected via DI)
export interface IEventBusService {
  emit(eventName: string, data: any): Promise<void>;
}

/**
 * Base Domain Event
 */
export interface DomainEvent<T = any> {
  eventId: string;
  eventType: string;
  eventVersion: string;
  occurredAt: Date;
  aggregateId: string;
  aggregateType: string;
  payload: T;
  metadata?: Record<string, any>;
  causationId?: string;
  correlationId?: string;
}

/**
 * Event Builder
 */
export class DomainEventBuilder<T = any> {
  private event: Partial<DomainEvent<T>> = {
    eventId: crypto.randomUUID(),
    eventVersion: "v1",
    occurredAt: new Date(),
    metadata: {},
  };

  withEventType(eventType: string): this {
    this.event.eventType = eventType;
    return this;
  }

  withEventVersion(version: string): this {
    this.event.eventVersion = version;
    return this;
  }

  withAggregateId(aggregateId: string): this {
    this.event.aggregateId = aggregateId;
    return this;
  }

  withAggregateType(aggregateType: string): this {
    this.event.aggregateType = aggregateType;
    return this;
  }

  withPayload(payload: T): this {
    this.event.payload = payload;
    return this;
  }

  withMetadata(metadata: Record<string, any>): this {
    this.event.metadata = { ...this.event.metadata, ...metadata };
    return this;
  }

  withCausationId(causationId: string): this {
    this.event.causationId = causationId;
    return this;
  }

  withCorrelationId(correlationId: string): this {
    this.event.correlationId = correlationId;
    return this;
  }

  build(): DomainEvent<T> {
    if (!this.event.eventType) {
      throw new Error("eventType is required");
    }
    if (!this.event.aggregateId) {
      throw new Error("aggregateId is required");
    }
    if (!this.event.aggregateType) {
      throw new Error("aggregateType is required");
    }
    if (this.event.payload === undefined) {
      throw new Error("payload is required");
    }

    return this.event as DomainEvent<T>;
  }
}

/**
 * Event Publisher (Medusa Integration)
 */
export class EventPublisher {
  constructor(private readonly eventBus: IEventBusService) {}

  async publish<T>(event: DomainEvent<T>): Promise<void> {
    await this.eventBus.emit(event.eventType, {
      id: event.eventId,
      ...event,
    });
  }

  async publishBatch<T>(events: DomainEvent<T>[]): Promise<void> {
    await Promise.all(events.map((event) => this.publish(event)));
  }
}

/**
 * Event Subscriber Helper
 */
export interface EventHandler<T = any> {
  handle(event: DomainEvent<T>): Promise<void>;
}

export function createEventHandler<T>(
  handler: (event: DomainEvent<T>) => Promise<void>
): EventHandler<T> {
  return {
    handle: handler,
  };
}

/**
 * Common Event Types
 */
export const EventTypes = {
  // Catalog
  CATALOG_PRODUCT_CREATED: "catalog.product.created",
  CATALOG_PRODUCT_UPDATED: "catalog.product.updated",
  CATALOG_PRODUCT_DELETED: "catalog.product.deleted",
  CATALOG_SYNC_STARTED: "catalog.sync.started",
  CATALOG_SYNC_COMPLETED: "catalog.sync.completed",
  CATALOG_SYNC_FAILED: "catalog.sync.failed",

  // Pricing
  PRICING_RULE_CREATED: "pricing.rule.created",
  PRICING_RULE_UPDATED: "pricing.rule.updated",
  PRICING_CALCULATED: "pricing.calculated",

  // Quotes
  QUOTE_CREATED: "quote.created",
  QUOTE_UPDATED: "quote.updated",
  QUOTE_SENT: "quote.sent",
  QUOTE_ACCEPTED: "quote.accepted",
  QUOTE_REJECTED: "quote.rejected",
  QUOTE_EXPIRED: "quote.expired",

  // Approvals
  APPROVAL_REQUESTED: "approval.requested",
  APPROVAL_APPROVED: "approval.approved",
  APPROVAL_REJECTED: "approval.rejected",
  APPROVAL_ESCALATED: "approval.escalated",

  // Company
  COMPANY_CREATED: "company.created",
  COMPANY_UPDATED: "company.updated",
  COMPANY_EMPLOYEE_ADDED: "company.employee.added",
  COMPANY_EMPLOYEE_REMOVED: "company.employee.removed",
  COMPANY_LIMIT_EXCEEDED: "company.limit.exceeded",

  // Orders
  ORDER_PLACED: "order.placed",
  ORDER_CONFIRMED: "order.confirmed",
  ORDER_CANCELLED: "order.cancelled",
  ORDER_FULFILLED: "order.fulfilled",

  // Financing
  FINANCING_SIMULATION_REQUESTED: "financing.simulation.requested",
  FINANCING_SIMULATION_COMPLETED: "financing.simulation.completed",
  FINANCING_APPROVED: "financing.approved",
  FINANCING_REJECTED: "financing.rejected",

  // Solar
  SOLAR_SIMULATION_REQUESTED: "solar.simulation.requested",
  SOLAR_SIMULATION_COMPLETED: "solar.simulation.completed",

  // Integrations
  DISTRIBUTOR_SYNC_STARTED: "distributor.sync.started",
  DISTRIBUTOR_SYNC_COMPLETED: "distributor.sync.completed",
  DISTRIBUTOR_SYNC_FAILED: "distributor.sync.failed",
} as const;

/**
 * Type Guards
 */
export function isDomainEvent(obj: any): obj is DomainEvent {
  return (
    typeof obj === "object" &&
    typeof obj.eventId === "string" &&
    typeof obj.eventType === "string" &&
    typeof obj.aggregateId === "string" &&
    typeof obj.aggregateType === "string" &&
    obj.payload !== undefined
  );
}
