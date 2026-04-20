"""统一认证中心客户端。

只负责和统一平台交互，不承载 Dify 本地账号逻辑。
"""

from __future__ import annotations

from typing import Any

import httpx

from configs import dify_config


class PlatformAuthClient:
    @property
    def enabled(self) -> bool:
        return dify_config.PLATFORM_AUTH_ENABLED

    def _request(self, method: str, path: str, json_data: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{dify_config.PLATFORM_API_BASE_URL.rstrip('/')}{path}"
        with httpx.Client(timeout=10.0) as client:
            response = client.request(
                method,
                url,
                headers={
                    "Content-Type": "application/json",
                    "X-Internal-Api-Key": dify_config.PLATFORM_API_KEY,
                },
                json=json_data,
            )
            response.raise_for_status()
            return response.json()

    def consume_ticket(self, ticket: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/internal/sso/consume",
            {
                "client_id": dify_config.PLATFORM_AUTH_CLIENT_ID,
                "client_secret": dify_config.PLATFORM_AUTH_CLIENT_SECRET,
                "ticket": ticket,
                "target_system": "dify",
            },
        )

    def upsert_user_binding(
        self,
        platform_user_id: str,
        account_id: str,
        platform_username: str | None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/internal/bindings/users",
            {
                "platform_user_id": platform_user_id,
                "system_code": "dify",
                "external_user_id": account_id,
                "external_username": platform_username,
            },
        )

    def upsert_workspace_binding(
        self,
        platform_workspace_id: str,
        tenant_id: str,
        platform_workspace_code: str | None,
        platform_workspace_name: str | None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/internal/bindings/workspaces",
            {
                "platform_workspace_id": platform_workspace_id,
                "system_code": "dify",
                "external_workspace_id": tenant_id,
                "external_workspace_name": platform_workspace_name,
            },
        )


platform_auth_client = PlatformAuthClient()
