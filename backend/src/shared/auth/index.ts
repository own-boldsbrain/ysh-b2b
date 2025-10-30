/**
 * Shared Authentication & Authorization Utilities
 * 
 * Helpers para autenticação, autorização e controle de acesso.
 */

import { UnauthorizedError, ForbiddenError } from "../errors";

/**
 * User Context
 */
export interface AuthContext {
  userId: string;
  email: string;
  customerId?: string;
  companyId?: string;
  roles: string[];
  permissions: string[];
  metadata?: Record<string, any>;
}

/**
 * Role Types
 */
export const Roles = {
  SUPER_ADMIN: "super_admin",
  ADMIN: "admin",
  COMPANY_OWNER: "company_owner",
  COMPANY_ADMIN: "company_admin",
  COMPANY_MEMBER: "company_member",
  CUSTOMER: "customer",
} as const;

export type RoleType = typeof Roles[keyof typeof Roles];

/**
 * Permission Types
 */
export const Permissions = {
  // Catalog
  CATALOG_READ: "catalog:read",
  CATALOG_WRITE: "catalog:write",
  CATALOG_ADMIN: "catalog:admin",

  // Quotes
  QUOTE_READ: "quote:read",
  QUOTE_CREATE: "quote:create",
  QUOTE_UPDATE: "quote:update",
  QUOTE_DELETE: "quote:delete",
  QUOTE_APPROVE: "quote:approve",

  // Approvals
  APPROVAL_READ: "approval:read",
  APPROVAL_APPROVE: "approval:approve",
  APPROVAL_REJECT: "approval:reject",
  APPROVAL_ADMIN: "approval:admin",

  // Company
  COMPANY_READ: "company:read",
  COMPANY_UPDATE: "company:update",
  COMPANY_MANAGE_MEMBERS: "company:manage_members",
  COMPANY_ADMIN: "company:admin",

  // Orders
  ORDER_READ: "order:read",
  ORDER_CREATE: "order:create",
  ORDER_UPDATE: "order:update",
  ORDER_CANCEL: "order:cancel",
  ORDER_ADMIN: "order:admin",

  // Pricing
  PRICING_READ: "pricing:read",
  PRICING_ADMIN: "pricing:admin",

  // System
  SYSTEM_ADMIN: "system:admin",
} as const;

export type PermissionType = typeof Permissions[keyof typeof Permissions];

/**
 * Role-Permission Mapping
 */
export const RolePermissions: Record<RoleType, PermissionType[]> = {
  [Roles.SUPER_ADMIN]: [Permissions.SYSTEM_ADMIN],
  [Roles.ADMIN]: [
    Permissions.CATALOG_ADMIN,
    Permissions.QUOTE_APPROVE,
    Permissions.APPROVAL_ADMIN,
    Permissions.ORDER_ADMIN,
    Permissions.PRICING_ADMIN,
  ],
  [Roles.COMPANY_OWNER]: [
    Permissions.CATALOG_READ,
    Permissions.QUOTE_READ,
    Permissions.QUOTE_CREATE,
    Permissions.QUOTE_UPDATE,
    Permissions.QUOTE_DELETE,
    Permissions.APPROVAL_READ,
    Permissions.APPROVAL_APPROVE,
    Permissions.COMPANY_ADMIN,
    Permissions.ORDER_READ,
    Permissions.ORDER_CREATE,
    Permissions.ORDER_UPDATE,
    Permissions.ORDER_CANCEL,
    Permissions.PRICING_READ,
  ],
  [Roles.COMPANY_ADMIN]: [
    Permissions.CATALOG_READ,
    Permissions.QUOTE_READ,
    Permissions.QUOTE_CREATE,
    Permissions.QUOTE_UPDATE,
    Permissions.APPROVAL_READ,
    Permissions.COMPANY_READ,
    Permissions.COMPANY_UPDATE,
    Permissions.COMPANY_MANAGE_MEMBERS,
    Permissions.ORDER_READ,
    Permissions.ORDER_CREATE,
    Permissions.PRICING_READ,
  ],
  [Roles.COMPANY_MEMBER]: [
    Permissions.CATALOG_READ,
    Permissions.QUOTE_READ,
    Permissions.QUOTE_CREATE,
    Permissions.APPROVAL_READ,
    Permissions.COMPANY_READ,
    Permissions.ORDER_READ,
    Permissions.ORDER_CREATE,
    Permissions.PRICING_READ,
  ],
  [Roles.CUSTOMER]: [
    Permissions.CATALOG_READ,
    Permissions.QUOTE_READ,
    Permissions.ORDER_READ,
    Permissions.PRICING_READ,
  ],
};

/**
 * Authorization Checks
 */
export function hasRole(context: AuthContext, role: RoleType): boolean {
  return context.roles.includes(role);
}

export function hasAnyRole(context: AuthContext, roles: RoleType[]): boolean {
  return roles.some((role) => context.roles.includes(role));
}

export function hasAllRoles(context: AuthContext, roles: RoleType[]): boolean {
  return roles.every((role) => context.roles.includes(role));
}

export function hasPermission(
  context: AuthContext,
  permission: PermissionType
): boolean {
  // Super admin has all permissions
  if (context.roles.includes(Roles.SUPER_ADMIN)) {
    return true;
  }

  return context.permissions.includes(permission);
}

export function hasAnyPermission(
  context: AuthContext,
  permissions: PermissionType[]
): boolean {
  if (context.roles.includes(Roles.SUPER_ADMIN)) {
    return true;
  }

  return permissions.some((permission) =>
    context.permissions.includes(permission)
  );
}

export function hasAllPermissions(
  context: AuthContext,
  permissions: PermissionType[]
): boolean {
  if (context.roles.includes(Roles.SUPER_ADMIN)) {
    return true;
  }

  return permissions.every((permission) =>
    context.permissions.includes(permission)
  );
}

/**
 * Authorization Guards (throw errors)
 */
export function requireAuth(context?: AuthContext): asserts context is AuthContext {
  if (!context || !context.userId) {
    throw new UnauthorizedError("Authentication required");
  }
}

export function requireRole(context: AuthContext, role: RoleType): void {
  if (!hasRole(context, role)) {
    throw new ForbiddenError(`Role '${role}' required`);
  }
}

export function requireAnyRole(context: AuthContext, roles: RoleType[]): void {
  if (!hasAnyRole(context, roles)) {
    throw new ForbiddenError(`One of roles [${roles.join(", ")}] required`);
  }
}

export function requirePermission(
  context: AuthContext,
  permission: PermissionType
): void {
  if (!hasPermission(context, permission)) {
    throw new ForbiddenError(`Permission '${permission}' required`);
  }
}

export function requireAnyPermission(
  context: AuthContext,
  permissions: PermissionType[]
): void {
  if (!hasAnyPermission(context, permissions)) {
    throw new ForbiddenError(
      `One of permissions [${permissions.join(", ")}] required`
    );
  }
}

/**
 * Resource Ownership
 */
export function isResourceOwner(
  context: AuthContext,
  resourceOwnerId: string
): boolean {
  return context.userId === resourceOwnerId;
}

export function requireResourceOwnership(
  context: AuthContext,
  resourceOwnerId: string
): void {
  if (!isResourceOwner(context, resourceOwnerId) && !hasRole(context, Roles.SUPER_ADMIN)) {
    throw new ForbiddenError("You don't have access to this resource");
  }
}

/**
 * Company Context
 */
export function isCompanyMember(
  context: AuthContext,
  companyId: string
): boolean {
  return context.companyId === companyId;
}

export function requireCompanyMembership(
  context: AuthContext,
  companyId: string
): void {
  if (!isCompanyMember(context, companyId) && !hasRole(context, Roles.SUPER_ADMIN)) {
    throw new ForbiddenError("You are not a member of this company");
  }
}

/**
 * Helper to get permissions from roles
 */
export function getPermissionsFromRoles(roles: RoleType[]): PermissionType[] {
  const permissions = new Set<PermissionType>();

  roles.forEach((role) => {
    const rolePerms = RolePermissions[role] || [];
    rolePerms.forEach((perm) => permissions.add(perm));
  });

  return Array.from(permissions);
}

/**
 * Create Auth Context
 */
export function createAuthContext(
  userId: string,
  email: string,
  roles: RoleType[],
  options?: {
    customerId?: string;
    companyId?: string;
    metadata?: Record<string, any>;
  }
): AuthContext {
  return {
    userId,
    email,
    customerId: options?.customerId,
    companyId: options?.companyId,
    roles,
    permissions: getPermissionsFromRoles(roles),
    metadata: options?.metadata,
  };
}
