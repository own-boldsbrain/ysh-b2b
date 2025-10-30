/**
 * Shared Validation Utilities
 * 
 * Validators e schemas Zod reutilizáveis entre domínios.
 */

import { z } from "zod";
import { ValidationError } from "../errors";

/**
 * Common Zod Schemas
 */
export const IdSchema = z.string().uuid("Invalid UUID format");

export const PaginationSchema = z.object({
  limit: z.coerce.number().int().min(1).max(100).default(20),
  offset: z.coerce.number().int().min(0).default(0),
});

export const DateRangeSchema = z.object({
  start_date: z.coerce.date().optional(),
  end_date: z.coerce.date().optional(),
}).refine(
  (data) => {
    if (data.start_date && data.end_date) {
      return data.start_date <= data.end_date;
    }
    return true;
  },
  { message: "start_date must be before or equal to end_date" }
);

export const EmailSchema = z.string().email("Invalid email format");

export const PhoneSchema = z.string().regex(
  /^\+?[1-9]\d{1,14}$/,
  "Invalid phone number format"
);

export const CNPJSchema = z.string().regex(
  /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/,
  "Invalid CNPJ format (XX.XXX.XXX/XXXX-XX)"
);

export const CPFSchema = z.string().regex(
  /^\d{3}\.\d{3}\.\d{3}-\d{2}$/,
  "Invalid CPF format (XXX.XXX.XXX-XX)"
);

export const CurrencySchema = z.number().nonnegative("Amount must be positive");

export const PercentageSchema = z.number().min(0).max(100, "Percentage must be between 0 and 100");

/**
 * Validation Helpers
 */
export function validateSchema<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): T {
  try {
    return schema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new ValidationError(
        "Validation failed",
        { errors: error.errors }
      );
    }
    throw error;
  }
}

export async function validateSchemaAsync<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): Promise<T> {
  try {
    return await schema.parseAsync(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      throw new ValidationError(
        "Validation failed",
        { errors: error.errors }
      );
    }
    throw error;
  }
}

export function createValidator<T>(schema: z.ZodSchema<T>) {
  return (data: unknown): T => validateSchema(schema, data);
}

/**
 * Custom Validators
 */
export function validateCNPJ(cnpj: string): boolean {
  const cleaned = cnpj.replace(/[^\d]/g, "");
  
  if (cleaned.length !== 14) return false;
  
  // Check if all digits are the same
  if (/^(\d)\1{13}$/.test(cleaned)) return false;
  
  // Validate check digits
  let sum = 0;
  let pos = 5;
  
  for (let i = 0; i < 12; i++) {
    sum += parseInt(cleaned.charAt(i)) * pos--;
    if (pos < 2) pos = 9;
  }
  
  let result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  if (result !== parseInt(cleaned.charAt(12))) return false;
  
  sum = 0;
  pos = 6;
  
  for (let i = 0; i < 13; i++) {
    sum += parseInt(cleaned.charAt(i)) * pos--;
    if (pos < 2) pos = 9;
  }
  
  result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  return result === parseInt(cleaned.charAt(13));
}

export function validateCPF(cpf: string): boolean {
  const cleaned = cpf.replace(/[^\d]/g, "");
  
  if (cleaned.length !== 11) return false;
  
  // Check if all digits are the same
  if (/^(\d)\1{10}$/.test(cleaned)) return false;
  
  // Validate first check digit
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cleaned.charAt(i)) * (10 - i);
  }
  
  let result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  if (result !== parseInt(cleaned.charAt(9))) return false;
  
  // Validate second check digit
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cleaned.charAt(i)) * (11 - i);
  }
  
  result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  return result === parseInt(cleaned.charAt(10));
}

/**
 * Sanitization
 */
export function sanitizeString(input: string): string {
  return input.trim().replace(/\s+/g, " ");
}

export function sanitizeCNPJ(cnpj: string): string {
  return cnpj.replace(/[^\d]/g, "");
}

export function sanitizeCPF(cpf: string): string {
  return cpf.replace(/[^\d]/g, "");
}

export function sanitizePhone(phone: string): string {
  return phone.replace(/[^\d+]/g, "");
}
