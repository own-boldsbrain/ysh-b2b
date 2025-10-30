/**
 * Shared TypeScript Types
 * 
 * Types e interfaces comuns entre domínios.
 */

/**
 * Common Types
 */
export type UUID = string;

export type Timestamp = Date | string;

export type Nullable<T> = T | null;

export type Optional<T> = T | undefined;

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type DeepReadonly<T> = {
  readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

export type ValueOf<T> = T[keyof T];

export type Prettify<T> = {
  [K in keyof T]: T[K];
} & {};

/**
 * Response Types
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: ErrorResponse;
  metadata?: ResponseMetadata;
}

export interface ErrorResponse {
  message: string;
  code?: string;
  statusCode: number;
  details?: Record<string, any>;
}

export interface ResponseMetadata {
  timestamp: string;
  requestId?: string;
  version?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMetadata;
}

export interface PaginationMetadata {
  total: number;
  limit: number;
  offset: number;
  hasMore: boolean;
  nextOffset?: number;
}

/**
 * Request Types
 */
export interface PaginationParams {
  limit?: number;
  offset?: number;
}

export interface SortParams {
  sortBy?: string;
  sortOrder?: "asc" | "desc";
}

export interface FilterParams {
  [key: string]: any;
}

export interface SearchParams {
  query?: string;
  filters?: FilterParams;
  pagination?: PaginationParams;
  sort?: SortParams;
}

/**
 * Entity Base Types
 */
export interface BaseEntity {
  id: string;
  created_at: Date;
  updated_at: Date;
  deleted_at?: Date | null;
}

export interface AuditableEntity extends BaseEntity {
  created_by?: string;
  updated_by?: string;
  deleted_by?: string;
}

/**
 * Domain Types
 */
export interface DomainContext {
  userId?: string;
  customerId?: string;
  companyId?: string;
  roles?: string[];
  permissions?: string[];
  metadata?: Record<string, any>;
}

export interface Command<T = any> {
  type: string;
  payload: T;
  context?: DomainContext;
  idempotencyKey?: string;
}

export interface Query<T = any> {
  type: string;
  params: T;
  context?: DomainContext;
}

export interface CommandResult<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  events?: DomainEvent[];
}

export interface QueryResult<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

/**
 * Event Types (mirrored from events/index.ts for convenience)
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
 * Value Objects
 */
export interface Money {
  amount: number;
  currency: string;
}

export interface Address {
  street: string;
  number: string;
  complement?: string;
  neighborhood: string;
  city: string;
  state: string;
  country: string;
  postalCode: string;
}

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface DateRange {
  start: Date;
  end: Date;
}

export interface TimeRange {
  startTime: string; // HH:mm format
  endTime: string; // HH:mm format
}

/**
 * Status Enums (as const for type safety)
 */
export const EntityStatus = {
  ACTIVE: "active",
  INACTIVE: "inactive",
  PENDING: "pending",
  ARCHIVED: "archived",
} as const;

export type EntityStatusType = ValueOf<typeof EntityStatus>;

export const ApprovalStatus = {
  PENDING: "pending",
  APPROVED: "approved",
  REJECTED: "rejected",
  ESCALATED: "escalated",
} as const;

export type ApprovalStatusType = ValueOf<typeof ApprovalStatus>;

export const OrderStatus = {
  DRAFT: "draft",
  PENDING: "pending",
  CONFIRMED: "confirmed",
  PROCESSING: "processing",
  SHIPPED: "shipped",
  DELIVERED: "delivered",
  CANCELLED: "cancelled",
} as const;

export type OrderStatusType = ValueOf<typeof OrderStatus>;

export const PaymentStatus = {
  PENDING: "pending",
  AUTHORIZED: "authorized",
  CAPTURED: "captured",
  FAILED: "failed",
  REFUNDED: "refunded",
} as const;

export type PaymentStatusType = ValueOf<typeof PaymentStatus>;

/**
 * Utility Types for API
 */
export type CreateDTO<T> = Omit<T, "id" | "created_at" | "updated_at">;

export type UpdateDTO<T> = Partial<CreateDTO<T>>;

export type ResponseDTO<T> = T & {
  _links?: Record<string, string>;
};

/**
 * Feature Flag Types
 */
export interface FeatureFlag {
  name: string;
  enabled: boolean;
  rolloutPercentage?: number;
  metadata?: Record<string, any>;
}

/**
 * Health Check Types
 */
export interface HealthCheckResult {
  status: "healthy" | "unhealthy" | "degraded";
  checks: Record<string, ComponentHealth>;
  timestamp: string;
}

export interface ComponentHealth {
  status: "up" | "down" | "degraded";
  message?: string;
  details?: Record<string, any>;
}

/**
 * Configuration Types
 */
export interface AppConfig {
  env: "development" | "staging" | "production";
  port: number;
  database: DatabaseConfig;
  redis: RedisConfig;
  features: Record<string, boolean>;
}

export interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  ssl?: boolean;
}

export interface RedisConfig {
  host: string;
  port: number;
  password?: string;
  db?: number;
}
