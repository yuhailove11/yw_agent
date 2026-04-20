"""Dify 统一认证中心 SSO 交换服务。"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select

from extensions.ext_database import db
from models import Account, PlatformAuthUserBinding, PlatformAuthWorkspaceBinding, Tenant, TenantAccountJoin
from models.account import AccountStatus, TenantAccountRole
from services.account_service import AccountService, TenantService
from services.platform_auth.client import platform_auth_client


@dataclass(slots=True)
class ExchangeResult:
    account: Account
    tenant: Tenant


class PlatformAuthSsoService:
    @staticmethod
    def _normalize_workspace_role(role_codes: list[str]) -> str:
        if "workspace_owner" in role_codes:
            return TenantAccountRole.OWNER
        if "workspace_admin" in role_codes:
            return TenantAccountRole.ADMIN
        if "workspace_developer" in role_codes:
            return TenantAccountRole.EDITOR
        return TenantAccountRole.NORMAL

    @staticmethod
    def _get_or_create_account(platform_user: dict) -> Account:
        platform_user_id = str(platform_user["id"])
        username = str(platform_user.get("username") or platform_user_id)
        email = str(platform_user.get("email") or f"{username}@platform.local").lower()
        display_name = str(platform_user.get("display_name") or username)

        binding = db.session.scalar(
            select(PlatformAuthUserBinding)
            .where(
                PlatformAuthUserBinding.platform_user_id == platform_user_id,
                PlatformAuthUserBinding.system_code == "dify",
            )
            .limit(1)
        )
        if binding:
            account = db.session.get(Account, binding.account_id)
            if account:
                account.name = display_name
                account.email = email
                account.status = AccountStatus.ACTIVE
                db.session.commit()
                return account

        account = db.session.scalar(select(Account).where(Account.email == email).limit(1))
        if account is None:
            account = AccountService.create_account(
                email=email,
                name=display_name,
                interface_language="zh-Hans",
                password=None,
                is_setup=True,
            )
            account.status = AccountStatus.ACTIVE
            db.session.commit()
        else:
            account.name = display_name
            account.status = AccountStatus.ACTIVE
            db.session.commit()

        local_binding = binding
        if local_binding is None:
            local_binding = PlatformAuthUserBinding(
                platform_user_id=platform_user_id,
                system_code="dify",
                account_id=account.id,
                platform_username=username,
                status="active",
            )
            db.session.add(local_binding)
        else:
            local_binding.account_id = account.id
            local_binding.platform_username = username
            local_binding.status = "active"
        db.session.commit()
        platform_auth_client.upsert_user_binding(platform_user_id, account.id, username)
        return account

    @staticmethod
    def _get_or_create_workspace(platform_workspace: dict) -> Tenant:
        platform_workspace_id = str(platform_workspace["id"])
        platform_workspace_code = str(platform_workspace.get("code") or platform_workspace_id)
        platform_workspace_name = str(platform_workspace.get("name") or platform_workspace_code)

        binding = db.session.scalar(
            select(PlatformAuthWorkspaceBinding)
            .where(
                PlatformAuthWorkspaceBinding.platform_workspace_id == platform_workspace_id,
                PlatformAuthWorkspaceBinding.system_code == "dify",
            )
            .limit(1)
        )
        if binding:
            tenant = db.session.get(Tenant, binding.tenant_id)
            if tenant:
                tenant.name = platform_workspace_name
                db.session.commit()
                return tenant

        tenant = TenantService.create_tenant(name=platform_workspace_name, is_setup=True)
        local_binding = binding
        if local_binding is None:
            local_binding = PlatformAuthWorkspaceBinding(
                platform_workspace_id=platform_workspace_id,
                system_code="dify",
                tenant_id=tenant.id,
                platform_workspace_code=platform_workspace_code,
                platform_workspace_name=platform_workspace_name,
                status="active",
            )
            db.session.add(local_binding)
        else:
            local_binding.tenant_id = tenant.id
            local_binding.platform_workspace_code = platform_workspace_code
            local_binding.platform_workspace_name = platform_workspace_name
            local_binding.status = "active"
        db.session.commit()
        platform_auth_client.upsert_workspace_binding(
            platform_workspace_id,
            tenant.id,
            platform_workspace_code,
            platform_workspace_name,
        )
        return tenant

    @staticmethod
    def _ensure_membership(account: Account, tenant: Tenant, role: str) -> None:
        join = db.session.scalar(
            select(TenantAccountJoin)
            .where(TenantAccountJoin.account_id == account.id, TenantAccountJoin.tenant_id == tenant.id)
            .limit(1)
        )
        if join is None:
            TenantService.create_tenant_member(tenant, account, role=role)
        else:
            join.role = TenantAccountRole(role)
            db.session.commit()

    @staticmethod
    def exchange(ticket: str) -> ExchangeResult:
        if not platform_auth_client.enabled:
            raise ValueError("统一认证中心接入未启用")
        payload = platform_auth_client.consume_ticket(ticket)
        platform_user = payload["user"]
        platform_workspace = payload["workspace"]
        workspace_roles = list(payload.get("workspace_roles") or [])

        account = PlatformAuthSsoService._get_or_create_account(platform_user)
        tenant = PlatformAuthSsoService._get_or_create_workspace(platform_workspace)
        local_role = PlatformAuthSsoService._normalize_workspace_role(workspace_roles)
        PlatformAuthSsoService._ensure_membership(account, tenant, local_role)
        TenantService.switch_tenant(account, tenant.id)
        return ExchangeResult(account=account, tenant=tenant)
