"""统一平台注册中心客户端。"""

from __future__ import annotations

from typing import Any

import httpx

from configs import dify_config


class PlatformGovernanceClient:
    def __init__(self) -> None:
        self._base_url = dify_config.PLATFORM_API_BASE_URL.rstrip("/")
        self._headers = {
            "X-Internal-Api-Key": dify_config.PLATFORM_API_KEY,
            "Content-Type": "application/json",
        }

    @property
    def enabled(self) -> bool:
        return dify_config.PLATFORM_GOVERNANCE_ENABLED

    def _request(self, method: str, path: str, json_data: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.enabled:
            return {"enabled": False}
        url = f"{self._base_url}{path}"
        with httpx.Client(timeout=10.0) as client:
            request_kwargs: dict[str, Any] = {"headers": self._headers}
            if json_data is not None:
                request_kwargs["json"] = json_data
            response = client.request(method, url, **request_kwargs)
            response.raise_for_status()
            return response.json()

    def sync_app(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/internal/sync/dify/apps", payload)

    def delete_app(self, app_id: str) -> dict[str, Any]:
        return self._request("DELETE", f"/internal/sync/dify/apps/{app_id}")

    def list_selectable_knowledge_bases(self, tenant_id: str) -> dict[str, Any]:
        return self._request("GET", f"/internal/resources/selectable/knowledge-bases?workspace_id={tenant_id}")

    def list_selectable_api_services(self, tenant_id: str) -> dict[str, Any]:
        return self._request("GET", f"/internal/resources/selectable/api-services?workspace_id={tenant_id}")

    def get_app_runtime_status(self, resource_code: str, tenant_id: str) -> dict[str, Any]:
        return self._request("GET", f"/internal/runtime/resources/{resource_code}?workspace_id={tenant_id}")

    def get_resource_runtime_status(
        self,
        resource_code: str,
        tenant_id: str,
        user_id: str | None = None,
        consumer: str | None = None,
    ) -> dict[str, Any]:
        query = f"/internal/runtime/resources/{resource_code}?workspace_id={tenant_id}"
        if user_id:
            query = f"{query}&user_id={user_id}"
        if consumer:
            query = f"{query}&consumer={consumer}"
        return self._request("GET", query)


platform_governance_client = PlatformGovernanceClient()
