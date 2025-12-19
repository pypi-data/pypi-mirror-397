"""
Netrun RBAC - Multi-tenant Role-Based Access Control with PostgreSQL RLS

Extracted from Intirkast SaaS platform (85% code reuse, 12h time savings)

Features:
- Role hierarchy enforcement (owner > admin > member > viewer)
- FastAPI dependency injection for route protection
- PostgreSQL Row-Level Security (RLS) policy generators
- Tenant context management
- Resource ownership validation
- Project-agnostic with placeholder configuration

Usage:
    from netrun.rbac import require_role, require_roles, TenantContext, RLSPolicyGenerator

    @app.get("/api/admin/dashboard")
    async def admin_dashboard(user: dict = Depends(require_role("admin"))):
        return {"message": "Admin access granted"}
"""

from .dependencies import (
    require_role,
    require_roles,
    require_owner,
    require_admin,
    require_member,
    check_resource_ownership,
)
from .models import Role, Permission, RoleHierarchy
from .policies import RLSPolicyGenerator
from .tenant import TenantContext, set_tenant_context, clear_tenant_context
from .exceptions import (
    RBACException,
    InsufficientPermissionsError,
    TenantIsolationError,
    ResourceOwnershipError,
)

__version__ = "2.0.0"
__all__ = [
    # Dependencies
    "require_role",
    "require_roles",
    "require_owner",
    "require_admin",
    "require_member",
    "check_resource_ownership",
    # Models
    "Role",
    "Permission",
    "RoleHierarchy",
    # Policies
    "RLSPolicyGenerator",
    # Tenant Context
    "TenantContext",
    "set_tenant_context",
    "clear_tenant_context",
    # Exceptions
    "RBACException",
    "InsufficientPermissionsError",
    "TenantIsolationError",
    "ResourceOwnershipError",
]
