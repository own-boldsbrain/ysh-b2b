/**
 * Shared Error Classes
 * 
 * Hierarquia de erros customizados para padronizar tratamento de erros
 * em todos os domínios.
 */

export class AppError extends Error {
  public readonly statusCode: number;
  public readonly isOperational: boolean;
  public readonly context?: Record<string, any>;

  constructor(
    message: string,
    statusCode: number = 500,
    isOperational: boolean = true,
    context?: Record<string, any>
  ) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    this.context = context;

    Error.captureStackTrace(this, this.constructor);
  }
}

export class DomainError extends AppError {
  constructor(
    message: string,
    context?: Record<string, any>
  ) {
    super(message, 400, true, context);
  }
}

export class ValidationError extends AppError {
  constructor(
    message: string,
    context?: Record<string, any>
  ) {
    super(message, 400, true, context);
  }
}

export class NotFoundError extends AppError {
  constructor(
    resource: string,
    identifier?: string | number,
    context?: Record<string, any>
  ) {
    const message = identifier
      ? `${resource} with identifier '${identifier}' not found`
      : `${resource} not found`;
    super(message, 404, true, context);
  }
}

export class UnauthorizedError extends AppError {
  constructor(
    message: string = "Unauthorized access",
    context?: Record<string, any>
  ) {
    super(message, 401, true, context);
  }
}

export class ForbiddenError extends AppError {
  constructor(
    message: string = "Forbidden access",
    context?: Record<string, any>
  ) {
    super(message, 403, true, context);
  }
}

export class ConflictError extends AppError {
  constructor(
    message: string,
    context?: Record<string, any>
  ) {
    super(message, 409, true, context);
  }
}

export class InternalServerError extends AppError {
  constructor(
    message: string = "Internal server error",
    context?: Record<string, any>
  ) {
    super(message, 500, false, context);
  }
}

export class ExternalServiceError extends AppError {
  constructor(
    service: string,
    message: string,
    context?: Record<string, any>
  ) {
    super(`External service '${service}' error: ${message}`, 502, true, context);
  }
}

export class RateLimitError extends AppError {
  constructor(
    message: string = "Rate limit exceeded",
    context?: Record<string, any>
  ) {
    super(message, 429, true, context);
  }
}

/**
 * Error Handler Utility
 */
export function isOperationalError(error: Error): boolean {
  if (error instanceof AppError) {
    return error.isOperational;
  }
  return false;
}

export function formatErrorResponse(error: AppError) {
  return {
    error: {
      message: error.message,
      statusCode: error.statusCode,
      context: error.context,
      ...(process.env.NODE_ENV === "development" && {
        stack: error.stack,
      }),
    },
  };
}
